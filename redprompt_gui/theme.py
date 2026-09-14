"""Theme tokens — dark terminal with red/amber accents (no purple glow)."""

from __future__ import annotations

import customtkinter as ctk

COLORS = {
    'bg': '#0B0F14',
    'surface': '#121820',
    'panel': '#161D27',
    'border': '#2A3544',
    'text': '#E6EDF3',
    'muted': '#8B9BB0',
    'accent': '#E11D48',
    'amber': '#F59E0B',
    'ok': '#22C55E',
    'info': '#38BDF8',
    'danger_bg': '#3F1219',
    'ok_bg': '#0F291A',
    'warn_bg': '#3A2A0A',
    'info_bg': '#0C2A3A',
}

FINDING_COLORS = {
    'CRITICAL': COLORS['accent'],
    'WARNING': COLORS['amber'],
    'COVERAGE_GAP': COLORS['info'],
    'PASSED': COLORS['ok'],
}

FONTS = {
    'ui': ('Segoe UI', 13),
    'mono': ('Consolas', 12),
    'h1': ('Segoe UI Semibold', 20),
    'h2': ('Segoe UI Semibold', 15),
    'card': ('Segoe UI Semibold', 16),
}


def apply_theme() -> None:
    """Apply global CustomTkinter appearance."""
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')
    try:
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
    except Exception:
        pass
