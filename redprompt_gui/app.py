"""RedPrompt GUI application entry."""

from __future__ import annotations

import sys
from pathlib import Path

import customtkinter as ctk

from .process_view import ProcessView
from .report_view import ReportView
from .theme import COLORS, FONTS, apply_theme


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> None:
    root_dir = project_root()
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    apply_theme()
    app = ctk.CTk()
    app.title('RedPrompt — LLM Red-Team Assessment')
    app.geometry('1180x760')
    app.minsize(1000, 640)
    app.configure(fg_color=COLORS['bg'])

    banner = ctk.CTkFrame(app, fg_color=COLORS['surface'], height=56, corner_radius=0)
    banner.pack(fill='x')
    banner.pack_propagate(False)
    ctk.CTkLabel(
        banner,
        text='RedPrompt',
        font=FONTS['h1'],
        text_color=COLORS['accent'],
    ).pack(side='left', padx=20, pady=12)
    ctk.CTkLabel(
        banner,
        text='Cybersecurity / AI Engineering · Authorized testing only',
        font=FONTS['ui'],
        text_color=COLORS['muted'],
    ).pack(side='left', padx=8, pady=12)

    tabs = ctk.CTkTabview(
        app,
        fg_color=COLORS['bg'],
        segmented_button_fg_color=COLORS['panel'],
        segmented_button_selected_color=COLORS['accent'],
        segmented_button_selected_hover_color='#BE123C',
        segmented_button_unselected_color=COLORS['panel'],
        text_color=COLORS['text'],
    )
    tabs.pack(fill='both', expand=True, padx=12, pady=12)
    tabs.add('Process')
    tabs.add('Report')

    report = ReportView(tabs.tab('Report'))
    report.pack(fill='both', expand=True)

    def on_results(data: dict) -> None:
        report.load_from_run(data)
        tabs.set('Report')

    process = ProcessView(tabs.tab('Process'), project_root=root_dir, on_results=on_results)
    process.pack(fill='both', expand=True)

    app.mainloop()


if __name__ == '__main__':
    main()
