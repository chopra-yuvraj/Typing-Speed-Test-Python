"""Reusable themed tkinter widgets.

* :class:`StatCard` — labelled metric card (WPM / accuracy / ...).
* :class:`Sparkline` — live series plot used for the WPM-over-time graph.
* :class:`LineChart` / :class:`BarChart` — static charts for the dashboard.
* :func:`style_button` / :func:`apply_panel` — theme helpers.

All widgets repaint when :meth:`.apply_theme` is called, so the whole app
can switch dark/light without a restart.
"""
from __future__ import annotations

import tkinter as tk
from typing import Iterable, List, Optional, Tuple

from typingtest.themes import FONT_MONO, FONT_STAT_CAPTION, FONT_STAT_VALUE, Theme


class StatCard(tk.Frame):
    """A bordered card showing a value with a caption (e.g. "WPM 62.4")."""

    def __init__(self, master: tk.Misc, caption: str, theme: Theme,
                 accent: Optional[str] = None, width: int = 150) -> None:
        super().__init__(master, bg=theme.panel_bg,
                         highlightthickness=1,
                         highlightbackground=theme.chart_grid)
        self._theme = theme
        self._accent = accent or theme.accent
        self.configure(width=width, height=66)
        self.pack_propagate(False)
        self.value = tk.Label(self, text="—", font=FONT_STAT_VALUE,
                              bg=theme.panel_bg, fg=self._accent)
        self.value.pack(pady=(8, 0))
        self.caption = tk.Label(self, text=caption, font=FONT_STAT_CAPTION,
                                bg=theme.panel_bg, fg=theme.fg_dim)
        self.caption.pack()

    def set(self, text: str) -> None:
        self.value.config(text=text)

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        self.configure(bg=theme.panel_bg, highlightbackground=theme.chart_grid)
        self.value.config(bg=theme.panel_bg, fg=self._accent)
        self.caption.config(bg=theme.panel_bg, fg=theme.fg_dim)


class Sparkline(tk.Canvas):
    """Ring-buffer area chart for a live metric (e.g. WPM) with peak label."""

    def __init__(self, master: tk.Misc, theme: Theme,
                 height: int = 64, max_points: int = 240) -> None:
        super().__init__(master, height=height, bg=theme.panel_bg,
                         highlightthickness=1,
                         highlightbackground=theme.chart_grid)
        self._theme = theme
        self._max = max_points
        self._data: List[float] = []

    def push(self, value: float) -> None:
        self._data.append(value)
        if len(self._data) > self._max:
            del self._data[: len(self._data) - self._max]
        self.redraw()

    def reset(self) -> None:
        self._data.clear()
        self.delete("all")

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        self.configure(bg=theme.panel_bg, highlightbackground=theme.chart_grid)
        self.redraw()

    def redraw(self) -> None:
        self.delete("all")
        w = max(self.winfo_width(), 2)
        h = max(self.winfo_height(), 2)
        if not self._data:
            self.create_text(w / 2, h / 2, text="live WPM",
                             fill=self._theme.fg_dim, font=FONT_MONO)
            return
        peak = max(max(self._data), 1.0)
        n = len(self._data)
        step = (w - 4) / max(n - 1, 1)
        pts = []
        for i, v in enumerate(self._data):
            x = 2 + i * step
            y = h - 3 - (v / peak) * (h - 14)
            pts.append((x, y))
        # filled area then the stroke line on top
        poly = [(2, h - 2), *pts, (2 + (n - 1) * step, h - 2)]
        flat = [c for p in poly for c in p]
        self.create_polygon(*flat, fill=self._theme.chart_fill, outline="")
        line = [c for p in pts for c in p]
        if len(line) >= 4:
            self.create_line(*line, fill=self._theme.chart_line, width=2,
                             smooth=True)
        self.create_text(w - 6, 8, text=f"{self._data[-1]:.0f} wpm",
                         fill=self._theme.fg_dim, font=FONT_MONO, anchor="e")


class LineChart(tk.Canvas):
    """Static x/y line chart with axes + grid (WPM trend in dashboard)."""

    def __init__(self, master: tk.Misc, theme: Theme,
                 height: int = 180) -> None:
        super().__init__(master, height=height, bg=theme.panel_bg,
                         highlightthickness=1,
                         highlightbackground=theme.chart_grid)
        self._theme = theme
        self._points: List[Tuple[str, float]] = []
        self.bind("<Configure>", lambda _e: self.redraw())

    def set_data(self, points: Iterable[Tuple[str, float]]) -> None:
        self._points = list(points)
        self.redraw()

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        self.configure(bg=theme.panel_bg, highlightbackground=theme.chart_grid)
        self.redraw()

    def redraw(self) -> None:
        t = self._theme
        self.delete("all")
        w = max(self.winfo_width(), 40)
        h = max(self.winfo_height(), 40)
        pad_l, pad_r, pad_t, pad_b = 46, 12, 14, 22
        cw, ch = w - pad_l - pad_r, h - pad_t - pad_b
        if cw <= 0 or ch <= 0:
            return
        # gridlines
        for gy in range(5):
            y = pad_t + ch * gy / 4
            self.create_line(pad_l, y, w - pad_r, y, fill=t.chart_grid,
                             dash=(2, 4))
        vals = [v for _, v in self._points]
        if not vals:
            self.create_text(w / 2, h / 2, text="No data yet — take a test!",
                             fill=t.fg_dim, font=FONT_MONO)
            return
        vmax = max(max(vals), 1.0)
        vmin = 0.0
        for gy in range(5):
            val = vmax - (vmax - vmin) * gy / 4
            y = pad_t + ch * gy / 4
            self.create_text(pad_l - 6, y, text=f"{val:.0f}", anchor="e",
                             fill=t.fg_dim, font=FONT_MONO)
        n = len(vals)
        step = cw / max(n - 1, 1)
        pts = [(pad_l + i * step,
                pad_t + ch - (v - vmin) / (vmax - vmin) * ch
                if vmax > vmin else pad_t + ch / 2)
               for i, v in enumerate(vals)]
        if len(pts) == 1:
            x, y = pts[0]
            self.create_oval(x - 3, y - 3, x + 3, y + 3,
                             fill=t.chart_line, outline="")
        else:
            flat = [c for p in pts for c in p]
            self.create_line(*flat, fill=t.chart_line, width=2, smooth=True)
            for x, y in pts:
                self.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5,
                                 fill=t.chart_line, outline="")
        # x labels: first / middle / last
        if n >= 1:
            for i in sorted({0, n // 2, n - 1}):
                x = pad_l + i * step
                self.create_text(x, h - 10, text=self._points[i][0],
                                 fill=t.fg_dim, font=FONT_MONO)


class BarChart(tk.Canvas):
    """Horizontal labelled bars (per-category averages in dashboard)."""

    def __init__(self, master: tk.Misc, theme: Theme,
                 height: int = 180) -> None:
        super().__init__(master, height=height, bg=theme.panel_bg,
                         highlightthickness=1,
                         highlightbackground=theme.chart_grid)
        self._theme = theme
        self._rows: List[Tuple[str, float]] = []

    def set_data(self, rows: Iterable[Tuple[str, float]]) -> None:
        self._rows = list(rows)
        self.redraw()

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        self.configure(bg=theme.panel_bg, highlightbackground=theme.chart_grid)
        self.redraw()

    def redraw(self) -> None:
        t = self._theme
        self.delete("all")
        w = max(self.winfo_width(), 40)
        if not self._rows:
            self.create_text(w / 2, 40, text="No data yet",
                             fill=t.fg_dim, font=FONT_MONO)
            return
        vmax = max((v for _, v in self._rows), default=1.0) or 1.0
        label_w = 180
        row_h = 30
        for i, (label, value) in enumerate(self._rows):
            y = 10 + i * row_h
            self.create_text(label_w - 8, y + 10, text=label, anchor="e",
                             fill=t.fg, font=FONT_MONO)
            bar_w = (w - label_w - 60) * (value / vmax)
            self.create_rectangle(label_w, y, label_w + max(bar_w, 2),
                                  y + 20, fill=t.accent, outline="")
            self.create_text(label_w + max(bar_w, 2) + 6, y + 10,
                             text=f"{value:.1f}", anchor="w",
                             fill=t.fg_dim, font=FONT_MONO)


# ---------------------------------------------------------------------------
# Small helpers used all over the UI
# ---------------------------------------------------------------------------


def style_button(btn: tk.Button, theme: Theme, *, kind: str = "primary",
                 font: Tuple[str, ...] = ("Segoe UI", 10, "bold")) -> None:
    """Apply theme colors to a classic tk.Button (tk buttons ignore ttk
    styles, so we paint them manually)."""
    colors = {
        "primary": (theme.accent, theme.on_accent),
        "success": (theme.success, theme.on_accent),
        "danger": (theme.danger, theme.on_accent),
        "ghost": (theme.panel_alt, theme.fg),
    }
    bg, fg = colors[kind]
    btn.config(bg=bg, fg=fg, activebackground=theme.accent_hover,
               activeforeground=theme.on_accent, relief=tk.FLAT,
               font=font, cursor="hand2", padx=14, pady=6)


def apply_panel(widget: tk.Widget, theme: Theme, *,
                bg: Optional[str] = None) -> None:
    """Recursively repaint frames/labels for theme switches."""
    color = bg or theme.window_bg
    cls = widget.winfo_class()
    try:
        if cls in ("Frame", "Toplevel"):
            widget.config(bg=color)
        elif cls == "Label":
            widget.config(bg=color)
    except tk.TclError:
        pass
