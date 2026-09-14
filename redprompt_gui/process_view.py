"""Process tab — configure target, run assessment, live log."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from typing import Callable

import customtkinter as ctk

import ai_pentest_suite as suite

from . import worker
from .theme import COLORS, FONTS


class ProcessView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        project_root: Path,
        on_results: Callable[[dict], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=COLORS['bg'], **kwargs)
        self.project_root = project_root
        self.on_results = on_results
        self.q: queue.Queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread: threading.Thread | None = None
        self._polling = False

        self._build()
        self._load_env_into_form()
        self.refresh_models()

    def _build(self) -> None:
        header = ctk.CTkLabel(
            self,
            text='Assessment Process',
            font=FONTS['h1'],
            text_color=COLORS['text'],
        )
        header.pack(anchor='w', padx=20, pady=(16, 4))
        ctk.CTkLabel(
            self,
            text='Authorize first · Configure Ollama target · Run suite · Review live log',
            font=FONTS['ui'],
            text_color=COLORS['muted'],
        ).pack(anchor='w', padx=20, pady=(0, 12))

        body = ctk.CTkFrame(self, fg_color=COLORS['surface'], corner_radius=8)
        body.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        form = ctk.CTkFrame(body, fg_color=COLORS['panel'], corner_radius=8)
        form.pack(fill='x', padx=12, pady=12)

        self.entries: dict[str, ctk.CTkEntry] = {}
        fields = [
            ('VLLM_BASE_URL', 'Endpoint (OpenAI-compatible)'),
            ('MODEL_NAME', 'Model'),
            ('API_KEY', 'API key'),
            ('COMPANY_NAME', 'Company'),
            ('CLASSIFICATION', 'Classification'),
            ('TESTER_IDENTITY', 'Tester'),
        ]
        for i, (key, label) in enumerate(fields):
            ctk.CTkLabel(form, text=label, text_color=COLORS['muted'], font=FONTS['ui']).grid(
                row=i, column=0, sticky='w', padx=12, pady=6
            )
            show = '*' if key == 'API_KEY' else None
            entry = ctk.CTkEntry(
                form,
                width=420,
                show=show,
                fg_color=COLORS['bg'],
                border_color=COLORS['border'],
                text_color=COLORS['text'],
            )
            entry.grid(row=i, column=1, sticky='ew', padx=12, pady=6)
            self.entries[key] = entry

        form.grid_columnconfigure(1, weight=1)

        # Model picker row
        model_row = ctk.CTkFrame(form, fg_color='transparent')
        model_row.grid(row=len(fields), column=0, columnspan=2, sticky='ew', padx=12, pady=6)
        ctk.CTkLabel(model_row, text='Ollama models', text_color=COLORS['muted']).pack(side='left')
        self.model_menu = ctk.CTkOptionMenu(
            model_row,
            values=['(refresh to list)'],
            command=self._on_model_pick,
            fg_color=COLORS['bg'],
            button_color=COLORS['accent'],
            button_hover_color='#BE123C',
            width=280,
        )
        self.model_menu.pack(side='left', padx=12)
        ctk.CTkButton(
            model_row,
            text='Refresh',
            width=90,
            fg_color=COLORS['border'],
            hover_color=COLORS['amber'],
            command=self.refresh_models,
        ).pack(side='left')

        opts = ctk.CTkFrame(body, fg_color=COLORS['panel'], corner_radius=8)
        opts.pack(fill='x', padx=12, pady=(0, 12))

        ctk.CTkLabel(opts, text='Runs per payload', text_color=COLORS['muted']).grid(
            row=0, column=0, padx=12, pady=10, sticky='w'
        )
        self.runs_var = tk.IntVar(value=1)
        self.runs_slider = ctk.CTkSlider(
            opts, from_=1, to=10, number_of_steps=9, variable=self.runs_var, width=180,
            progress_color=COLORS['accent'], button_color=COLORS['amber'],
        )
        self.runs_slider.grid(row=0, column=1, padx=8, pady=10)
        self.runs_label = ctk.CTkLabel(opts, text='1', text_color=COLORS['text'], width=30)
        self.runs_label.grid(row=0, column=2, padx=4)
        self.runs_var.trace_add('write', lambda *_: self.runs_label.configure(text=str(self.runs_var.get())))

        ctk.CTkLabel(opts, text='Rate limit (s)', text_color=COLORS['muted']).grid(
            row=0, column=3, padx=12, pady=10, sticky='w'
        )
        self.rate_entry = ctk.CTkEntry(opts, width=70, fg_color=COLORS['bg'], border_color=COLORS['border'])
        self.rate_entry.insert(0, '0')
        self.rate_entry.grid(row=0, column=4, padx=8, pady=10)

        self.judge_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            opts,
            text='Same-model judge (non-authoritative)',
            variable=self.judge_var,
            text_color=COLORS['muted'],
            fg_color=COLORS['accent'],
            hover_color='#BE123C',
        ).grid(row=0, column=5, padx=12, pady=10)

        actions = ctk.CTkFrame(body, fg_color='transparent')
        actions.pack(fill='x', padx=12, pady=(0, 8))

        self.start_btn = ctk.CTkButton(
            actions,
            text='Start Assessment',
            fg_color=COLORS['accent'],
            hover_color='#BE123C',
            font=FONTS['h2'],
            command=self.start_assessment,
            width=160,
        )
        self.start_btn.pack(side='left', padx=(0, 8))

        self.stop_btn = ctk.CTkButton(
            actions,
            text='Stop',
            fg_color=COLORS['border'],
            hover_color=COLORS['amber'],
            command=self.stop_assessment,
            state='disabled',
            width=90,
        )
        self.stop_btn.pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            actions,
            text='Self-test',
            fg_color=COLORS['info_bg'],
            hover_color=COLORS['info'],
            text_color=COLORS['text'],
            command=self.run_self_test,
            width=100,
        ).pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            actions,
            text='Load .env',
            fg_color=COLORS['border'],
            hover_color=COLORS['muted'],
            command=self._load_env_into_form,
            width=100,
        ).pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            actions,
            text='Open folder',
            fg_color=COLORS['border'],
            hover_color=COLORS['muted'],
            command=self._open_folder,
            width=110,
        ).pack(side='left')

        self.status_pill = ctk.CTkLabel(
            actions,
            text='● Idle',
            text_color=COLORS['ok'],
            font=FONTS['h2'],
        )
        self.status_pill.pack(side='right', padx=8)

        ctk.CTkLabel(
            body,
            text='Live process log',
            font=FONTS['h2'],
            text_color=COLORS['text'],
        ).pack(anchor='w', padx=16, pady=(4, 4))

        self.log_box = ctk.CTkTextbox(
            body,
            font=FONTS['mono'],
            fg_color=COLORS['bg'],
            text_color=COLORS['text'],
            border_color=COLORS['border'],
            border_width=1,
            wrap='word',
        )
        self.log_box.pack(fill='both', expand=True, padx=12, pady=(0, 12))
        self.log_box.configure(state='disabled')

    def _append_log(self, line: str) -> None:
        self.log_box.configure(state='normal')
        self.log_box.insert('end', line + '\n')
        self.log_box.see('end')
        self.log_box.configure(state='disabled')

    def _set_status(self, text: str) -> None:
        color = COLORS['ok']
        if text.lower().startswith('run'):
            color = COLORS['amber']
        elif 'error' in text.lower() or 'fail' in text.lower():
            color = COLORS['accent']
        self.status_pill.configure(text=f'● {text}', text_color=color)

    def _load_env_into_form(self) -> None:
        config = suite.load_env_config()
        # Friendly Ollama defaults when still on suite placeholders
        if 'localhost:8000' in config.get('VLLM_BASE_URL', ''):
            config['VLLM_BASE_URL'] = 'http://127.0.0.1:11434/v1'
        if not config.get('API_KEY') or 'placeholder' in config.get('API_KEY', ''):
            config['API_KEY'] = 'ollama'
        for key, entry in self.entries.items():
            entry.delete(0, 'end')
            entry.insert(0, config.get(key, ''))

    def refresh_models(self) -> None:
        models = worker.fetch_ollama_models()
        if not models:
            self.model_menu.configure(values=['(no models — pull with ollama)'])
            self._append_log('[info] No Ollama models found at http://127.0.0.1:11434')
            return
        self.model_menu.configure(values=models)
        self.model_menu.set(models[0])
        self.entries['MODEL_NAME'].delete(0, 'end')
        self.entries['MODEL_NAME'].insert(0, models[0])
        self._append_log(f"[info] Ollama models: {', '.join(models)}")

    def _on_model_pick(self, name: str) -> None:
        if name.startswith('('):
            return
        self.entries['MODEL_NAME'].delete(0, 'end')
        self.entries['MODEL_NAME'].insert(0, name)

    def _config_from_form(self) -> dict:
        config = suite.load_env_config()
        for key, entry in self.entries.items():
            config[key] = entry.get().strip()
        return config

    def _busy(self, busy: bool) -> None:
        self.start_btn.configure(state='disabled' if busy else 'normal')
        self.stop_btn.configure(state='normal' if busy else 'disabled')

    def start_assessment(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            return
        try:
            rate = float(self.rate_entry.get().strip() or '0')
        except ValueError:
            self._append_log('[error] Rate limit must be a number')
            return
        runs = int(self.runs_var.get())
        config = self._config_from_form()
        if not config.get('VLLM_BASE_URL') or not config.get('MODEL_NAME'):
            self._append_log('[error] Endpoint and model are required')
            return

        self.stop_event.clear()
        self._busy(True)
        self._set_status('Running')
        self._append_log('─' * 48)
        self._append_log(f"Starting · model={config['MODEL_NAME']} · runs={runs}")
        self.worker_thread = threading.Thread(
            target=worker.worker_run,
            args=(self.q, config, runs, rate, self.judge_var.get(), self.stop_event, self.project_root),
            daemon=True,
        )
        self.worker_thread.start()
        self._start_poll()

    def stop_assessment(self) -> None:
        self.stop_event.set()
        self._append_log('[STOP] Stop requested — finishing current request, then halting.')
        self._set_status('Stopping')

    def run_self_test(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            return
        self._busy(True)
        self._set_status('Self-test')
        self.worker_thread = threading.Thread(
            target=worker.worker_self_test,
            args=(self.q,),
            daemon=True,
        )
        self.worker_thread.start()
        self._start_poll()

    def _open_folder(self) -> None:
        import os
        os.startfile(self.project_root)  # noqa: S606 — local folder open on Windows

    def _start_poll(self) -> None:
        if not self._polling:
            self._polling = True
            self.after(100, self._poll_queue)

    def _poll_queue(self) -> None:
        try:
            while True:
                kind, *payload = self.q.get_nowait()
                if kind == 'log':
                    self._append_log(payload[0])
                elif kind == 'status':
                    self._set_status(payload[0])
                    if payload[0] == 'Idle':
                        self._busy(False)
                elif kind == 'done':
                    data = payload[0]
                    self._append_log(f"[done] CSV: {data['csv_path']}")
                    self._append_log(f"[done] JSON: {data['json_path']}")
                    self._append_log(
                        f"[summary] CRITICAL={data['summary']['CRITICAL']} "
                        f"WARNING={data['summary']['WARNING']} "
                        f"COVERAGE_GAP={data['summary']['COVERAGE_GAP']} "
                        f"PASSED={data['summary']['PASSED']}"
                    )
                    self.on_results(data)
                    self._busy(False)
                    self._set_status('Done')
                elif kind == 'self_test':
                    ok = payload[0]
                    self._append_log(f"[self-test] {'PASS' if ok else 'FAIL'}")
                    self._busy(False)
                    self._set_status('Idle')
                elif kind == 'error':
                    self._append_log(f'[error] {payload[0]}')
                    self._busy(False)
                    self._set_status('Error')
        except queue.Empty:
            pass

        alive = self.worker_thread is not None and self.worker_thread.is_alive()
        if alive or not self.q.empty():
            self.after(100, self._poll_queue)
        else:
            self._polling = False
