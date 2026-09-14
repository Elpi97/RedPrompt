"""Report tab — summary, matrix, reasoning, and remediation for the AI team."""

from __future__ import annotations

import json
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from .remediation import finding_plain, lookup_remediation
from .theme import COLORS, FINDING_COLORS, FONTS


class ReportView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg'], **kwargs)
        self.last_json: Path | None = None
        self.payload_rows: list[dict] = []
        self.card_counts: dict[str, ctk.CTkLabel] = {}
        self._build()

    def _build(self) -> None:
        header = ctk.CTkLabel(
            self,
            text='Assessment Report',
            font=FONTS['h1'],
            text_color=COLORS['text'],
        )
        header.pack(anchor='w', padx=20, pady=(16, 4))
        ctk.CTkLabel(
            self,
            text='Simple findings · clear reasoning · practical fix steps',
            font=FONTS['ui'],
            text_color=COLORS['muted'],
        ).pack(anchor='w', padx=20, pady=(0, 8))

        howto = ctk.CTkFrame(self, fg_color=COLORS['panel'], corner_radius=8)
        howto.pack(fill='x', padx=16, pady=(0, 10))
        ctk.CTkLabel(
            howto,
            text='How to read this report',
            font=FONTS['h2'],
            text_color=COLORS['amber'],
            anchor='w',
        ).pack(anchor='w', padx=14, pady=(10, 2))
        ctk.CTkLabel(
            howto,
            text=(
                'Each row is one attack we tried. Color = how serious the result was. '
                'Click a row for a plain-language explanation and fix steps. '
                'Technical evidence stays at the bottom for engineers.'
            ),
            font=FONTS['ui'],
            text_color=COLORS['muted'],
            wraplength=1040,
            justify='left',
            anchor='w',
        ).pack(anchor='w', padx=14, pady=(0, 12))

        toolbar = ctk.CTkFrame(self, fg_color='transparent')
        toolbar.pack(fill='x', padx=16, pady=(0, 8))
        ctk.CTkButton(
            toolbar,
            text='Load JSON report',
            fg_color=COLORS['border'],
            hover_color=COLORS['info'],
            command=self.load_json_dialog,
            width=140,
        ).pack(side='left', padx=(0, 8))
        self.path_label = ctk.CTkLabel(
            toolbar, text='No report loaded', text_color=COLORS['muted'], font=FONTS['ui']
        )
        self.path_label.pack(side='left', padx=8)

        self.cards = ctk.CTkFrame(self, fg_color='transparent')
        self.cards.pack(fill='x', padx=16, pady=8)
        for key, bg in (
            ('CRITICAL', COLORS['danger_bg']),
            ('WARNING', COLORS['warn_bg']),
            ('COVERAGE_GAP', COLORS['info_bg']),
            ('PASSED', COLORS['ok_bg']),
        ):
            plain = finding_plain(key)
            card = ctk.CTkFrame(self.cards, fg_color=bg, corner_radius=8, height=96)
            card.pack(side='left', padx=6, fill='x', expand=True)
            card.pack_propagate(False)
            ctk.CTkLabel(
                card,
                text=plain['label'],
                text_color=FINDING_COLORS[key],
                font=FONTS['h2'],
            ).pack(pady=(10, 0))
            count = ctk.CTkLabel(card, text='0', text_color=COLORS['text'], font=FONTS['h1'])
            count.pack()
            self.card_counts[key] = count
            ctk.CTkLabel(
                card,
                text=plain['blurb'][:72] + ('…' if len(plain['blurb']) > 72 else ''),
                text_color=COLORS['muted'],
                font=('Segoe UI', 11),
            ).pack(pady=(0, 8))

        self.meta = ctk.CTkLabel(self, text='', text_color=COLORS['muted'], font=FONTS['ui'])
        self.meta.pack(anchor='w', padx=20, pady=(4, 8))

        split = ctk.CTkFrame(self, fg_color='transparent')
        split.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        left = ctk.CTkFrame(split, fg_color='transparent')
        left.pack(side='left', fill='both', expand=True, padx=(0, 8))
        ctk.CTkLabel(
            left, text='Findings', font=FONTS['h2'], text_color=COLORS['text']
        ).pack(anchor='w', pady=(0, 4))
        self.table = ctk.CTkScrollableFrame(
            left, fg_color=COLORS['surface'], corner_radius=8
        )
        self.table.pack(fill='both', expand=True)

        right = ctk.CTkFrame(split, fg_color=COLORS['surface'], corner_radius=8, width=420)
        right.pack(side='right', fill='both', expand=False, padx=(8, 0))
        right.pack_propagate(False)
        ctk.CTkLabel(
            right,
            text='Reasoning & remediation',
            font=FONTS['h2'],
            text_color=COLORS['amber'],
        ).pack(anchor='w', padx=14, pady=(12, 6))
        self.detail_scroll = ctk.CTkScrollableFrame(right, fg_color=COLORS['panel'], corner_radius=6)
        self.detail_scroll.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self._detail_placeholder()

    def _clear_detail(self) -> None:
        for child in self.detail_scroll.winfo_children():
            child.destroy()

    def _detail_placeholder(self) -> None:
        self._clear_detail()
        ctk.CTkLabel(
            self.detail_scroll,
            text='Select a row to see what it means and how to fix it.',
            text_color=COLORS['muted'],
            font=FONTS['ui'],
            wraplength=360,
            justify='left',
        ).pack(anchor='w', padx=8, pady=12)

    def _section(self, parent, title: str, body: str, accent: str | None = None) -> None:
        ctk.CTkLabel(
            parent,
            text=title,
            font=FONTS['h2'],
            text_color=accent or COLORS['info'],
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(12, 2))
        ctk.CTkLabel(
            parent,
            text=body,
            font=FONTS['ui'],
            text_color=COLORS['text'],
            wraplength=360,
            justify='left',
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(0, 4))

    def load_from_run(self, data: dict) -> None:
        """Populate from worker done payload."""
        summary = data.get('summary') or {}
        for key, lbl in self.card_counts.items():
            lbl.configure(text=str(summary.get(key, 0)))
        json_path = data.get('json_path')
        if json_path:
            self.last_json = Path(json_path)
            self.path_label.configure(text=str(self.last_json.name))
            self._render_results(data.get('results') or [], meta_from_file=False, raw=data)
        else:
            self._render_results(data.get('results') or [])

    def load_json_dialog(self) -> None:
        path = filedialog.askopenfilename(
            title='Open RedPrompt full results JSON',
            filetypes=[('JSON', '*.json'), ('All', '*.*')],
        )
        if not path:
            return
        self.load_json_path(Path(path))

    def load_json_path(self, path: Path) -> None:
        try:
            report = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            self.path_label.configure(text=f'Load failed: {exc}')
            return
        self.last_json = path
        self.path_label.configure(text=path.name)
        results = report.get('results') or []
        summary = {'CRITICAL': 0, 'WARNING': 0, 'COVERAGE_GAP': 0, 'PASSED': 0}
        for row in results:
            finding = row.get('consolidated_finding', '')
            if finding in summary:
                summary[finding] += 1
        for key, lbl in self.card_counts.items():
            lbl.configure(text=str(summary.get(key, 0)))
        self.meta.configure(
            text=(
                f"Model: {report.get('model', '?')} · "
                f"Target: {report.get('target', '?')} · "
                f"Runs: {report.get('runs_per_payload', '?')} · "
                f"Suite: {report.get('suite_version', '?')}"
            )
        )
        self._render_results(results)

    def _clear_table(self) -> None:
        for child in self.table.winfo_children():
            child.destroy()

    def _render_results(self, results: list, meta_from_file: bool = True, raw: dict | None = None) -> None:
        self._clear_table()
        self.payload_rows = results
        self._detail_placeholder()
        if raw and not meta_from_file:
            first = results[0] if results else {}
            self.meta.configure(
                text=(
                    f"Live run · {len(results)} attacks · "
                    f"example status: {finding_plain(first.get('consolidated_finding')).get('label', '-')}"
                )
            )

        header = ctk.CTkFrame(self.table, fg_color=COLORS['panel'])
        header.pack(fill='x', pady=(0, 4))
        for col, text, width in (
            (0, 'ID', 60),
            (1, 'Attack', 180),
            (2, 'Result', 130),
            (3, 'How often', 80),
            (4, 'Detail', 200),
        ):
            ctk.CTkLabel(
                header, text=text, width=width, anchor='w',
                text_color=COLORS['muted'], font=FONTS['ui'],
            ).grid(row=0, column=col, padx=6, pady=6, sticky='w')

        for idx, row in enumerate(results):
            finding = row.get('consolidated_finding', '')
            plain = finding_plain(finding)
            color = FINDING_COLORS.get(finding, COLORS['text'])
            line = ctk.CTkFrame(
                self.table, fg_color=COLORS['bg'] if idx % 2 == 0 else COLORS['panel']
            )
            line.pack(fill='x', pady=1)
            rate = row.get('vulnerability_rate', 0)
            rate_txt = f'{rate:.0%}' if isinstance(rate, float) else str(rate)
            rem = lookup_remediation(row.get('payload_id'), row.get('owasp_llm'))
            values = [
                row.get('payload_id', ''),
                (row.get('category') or rem.get('title', ''))[:26],
                plain['label'],
                rate_txt,
                (rem.get('title') or '')[:32],
            ]
            widths = [60, 180, 130, 80, 200]
            for col, (val, width) in enumerate(zip(values, widths)):
                lbl = ctk.CTkLabel(
                    line,
                    text=val,
                    width=width,
                    anchor='w',
                    text_color=color if col == 2 else COLORS['text'],
                    font=FONTS['ui'],
                )
                lbl.grid(row=0, column=col, padx=6, pady=6, sticky='w')
                lbl.bind('<Button-1>', lambda _e, i=idx: self._show_detail(i))
            line.bind('<Button-1>', lambda _e, i=idx: self._show_detail(i))

        if results:
            self._show_detail(0)

    def _show_detail(self, index: int) -> None:
        if index < 0 or index >= len(self.payload_rows):
            return
        row = self.payload_rows[index]
        finding = row.get('consolidated_finding', '')
        plain = finding_plain(finding)
        rem = lookup_remediation(row.get('payload_id'), row.get('owasp_llm'))
        color = FINDING_COLORS.get(finding, COLORS['amber'])

        self._clear_detail()

        ctk.CTkLabel(
            self.detail_scroll,
            text=f"{row.get('payload_id')} — {row.get('category', '')}",
            font=FONTS['h2'],
            text_color=COLORS['text'],
            wraplength=360,
            justify='left',
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(8, 2))

        chip = ctk.CTkFrame(self.detail_scroll, fg_color=COLORS['bg'], corner_radius=6)
        chip.pack(anchor='w', padx=8, pady=(0, 6))
        ctk.CTkLabel(
            chip,
            text=f"  {plain['label']}  ({finding})  ",
            text_color=color,
            font=FONTS['h2'],
        ).pack(padx=4, pady=4)

        ctk.CTkLabel(
            self.detail_scroll,
            text=plain['blurb'],
            font=FONTS['ui'],
            text_color=COLORS['muted'],
            wraplength=360,
            justify='left',
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(0, 4))

        ctk.CTkLabel(
            self.detail_scroll,
            text=(
                f"{row.get('ci_summary') or ''}\n"
                f"Tags: {row.get('owasp_llm')} · {row.get('mitre_atlas')} · {row.get('cwe')}"
            ),
            font=('Segoe UI', 11),
            text_color=COLORS['muted'],
            wraplength=360,
            justify='left',
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(0, 4))

        ctk.CTkLabel(
            self.detail_scroll,
            text=rem.get('title', 'Remediation'),
            font=FONTS['h2'],
            text_color=COLORS['amber'],
            wraplength=360,
            justify='left',
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(10, 2))

        self._section(self.detail_scroll, 'What happened', rem.get('what_happened', ''), COLORS['info'])
        self._section(self.detail_scroll, 'Why it matters', rem.get('why_it_matters', ''), COLORS['accent'])

        ctk.CTkLabel(
            self.detail_scroll,
            text='What to do',
            font=FONTS['h2'],
            text_color=COLORS['ok'],
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(12, 2))
        for i, step in enumerate(rem.get('what_to_do') or [], start=1):
            ctk.CTkLabel(
                self.detail_scroll,
                text=f'{i}. {step}',
                font=FONTS['ui'],
                text_color=COLORS['text'],
                wraplength=360,
                justify='left',
                anchor='w',
            ).pack(anchor='w', padx=8, pady=2)

        ctk.CTkLabel(
            self.detail_scroll,
            text='Evidence (for engineers)',
            font=FONTS['h2'],
            text_color=COLORS['muted'],
            anchor='w',
        ).pack(anchor='w', padx=8, pady=(16, 4))

        runs = row.get('runs') or row.get('_full_runs') or []
        if isinstance(runs, int):
            runs = row.get('_full_runs') or []
        evidence_lines = []
        for i, run in enumerate(runs, start=1):
            if not isinstance(run, dict):
                continue
            excerpt = (run.get('full_response') or run.get('output') or '')[:220]
            evidence_lines.append(
                f"Run {i}: {run.get('status')} score={run.get('compliance_score')}\n{excerpt}\n"
            )
        box = ctk.CTkTextbox(
            self.detail_scroll,
            height=120,
            font=FONTS['mono'],
            fg_color=COLORS['bg'],
            text_color=COLORS['muted'],
            border_color=COLORS['border'],
            border_width=1,
            wrap='word',
        )
        box.pack(fill='x', padx=8, pady=(0, 12))
        box.insert('1.0', '\n'.join(evidence_lines) if evidence_lines else 'No run excerpts in this report.')
        box.configure(state='disabled')
