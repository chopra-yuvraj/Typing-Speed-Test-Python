"""Theme definitions (dark / light) for the whole UI."""
from __future__ import annotations

from dataclasses import dataclass

FONT_UI = ("Segoe UI", 10)
FONT_UI_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_STAT_VALUE = ("Consolas", 20, "bold")
FONT_STAT_CAPTION = ("Segoe UI", 9)
FONT_TEXT = ("Consolas", 13)
FONT_MONO = ("Consolas", 10)


@dataclass(frozen=True)
class Theme:
    """Color palette; every widget paints from this."""

    name: str
    window_bg: str
    panel_bg: str
    panel_alt: str
    fg: str
    fg_dim: str
    accent: str
    accent_hover: str
    on_accent: str
    success: str
    warning: str
    danger: str
    info: str
    chart_line: str
    chart_fill: str
    chart_grid: str
    badge_locked: str
    # text-display paint
    text_bg: str
    correct_fg: str
    correct_bg: str
    incorrect_fg: str
    incorrect_bg: str
    current_bg: str
    pending_fg: str


DARK = Theme(
    name="dark",
    window_bg="#1e2430",
    panel_bg="#2a3140",
    panel_alt="#333b4d",
    fg="#e8ecf1",
    fg_dim="#8d97a8",
    accent="#4f8cff",
    accent_hover="#3f7bf0",
    on_accent="#ffffff",
    success="#34c07c",
    warning="#e6a23c",
    danger="#e05252",
    info="#4f8cff",
    chart_line="#4f8cff",
    chart_fill="#2a3c5e",
    chart_grid="#3a4356",
    badge_locked="#444d5f",
    text_bg="#141923",
    correct_fg="#7ee2a8",
    correct_bg="#1f3d2b",
    incorrect_fg="#ff8f8f",
    incorrect_bg="#4d2330",
    current_bg="#3d5375",
    pending_fg="#97a1b3",
)

LIGHT = Theme(
    name="light",
    window_bg="#f2f4f8",
    panel_bg="#ffffff",
    panel_alt="#e8ecf3",
    fg="#1d2530",
    fg_dim="#5d6a7c",
    accent="#2563eb",
    accent_hover="#1d4ed8",
    on_accent="#ffffff",
    success="#16a34a",
    warning="#d97706",
    danger="#dc2626",
    info="#2563eb",
    chart_line="#2563eb",
    chart_fill="#dbe7ff",
    chart_grid="#d4dbe6",
    badge_locked="#c3cad6",
    text_bg="#ffffff",
    correct_fg="#15803d",
    correct_bg="#dcfce7",
    incorrect_fg="#b91c1c",
    incorrect_bg="#fee2e2",
    current_bg="#bfdbfe",
    pending_fg="#475569",
)

_THEMES = {"dark": DARK, "light": LIGHT}


def get_theme(name: str) -> Theme:
    """Look up a theme by name (defaults to dark for unknown values)."""
    return _THEMES.get(name, DARK)
