"""End-of-test results dialog: grade badge, stats grid, share + actions."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional, Sequence

from typingtest.core import Achievement, Grade, TestResult
from typingtest.themes import FONT_UI, FONT_UI_BOLD, Theme
from typingtest.widgets import apply_panel, style_button

_GRADE_COLORS = {
    "S": "#f5b301", "A": "#34c07c", "B": "#4f8cff",
    "C": "#e6a23c", "D": "#e05252",
}


class ResultsDialog:
    """Modal results window shown after every finished test."""

    def __init__(self,
                 parent: tk.Tk,
                 theme: Theme,
                 result: TestResult,
                 *,
                 is_personal_best: bool = False,
                 new_achievements: Sequence[Achievement] = (),
                 on_next: Optional[Callable[[], None]] = None,
                 on_retry: Optional[Callable[[], None]] = None,
                 on_dashboard: Optional[Callable[[], None]] = None) -> None:
        self._theme = theme
        self._result = result
        self._on_next = on_next
        self._on_retry = on_retry

        win = tk.Toplevel(parent)
        self.win = win
        win.title("Test Results")
        win.transient(parent)
        win.resizable(False, False)
        win.configure(bg=theme.window_bg)

        self._build(result, is_personal_best, new_achievements,
                    on_dashboard, parent)

        win.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - win.winfo_width()) // 2
        y = parent.winfo_rooty() + 60
        win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        win.grab_set()
        win.focus_set()

    # ------------------------------------------------------------------

    def _build(self, result: TestResult, is_pb: bool,
               new_achievements: Sequence[Achievement],
               on_dashboard: Optional[Callable[[], None]],
               parent: tk.Tk) -> None:
        t = self._theme
        win = self.win

        grade_color = _GRADE_COLORS.get(result.grade, t.accent)
        try:
            grade = Grade(result.grade)
            commentary = grade.commentary
        except ValueError:
            commentary = ""

        # -- grade hero ---------------------------------------------------
        hero = tk.Frame(win, bg=t.window_bg)
        hero.pack(fill=tk.X, padx=20, pady=(18, 6))

        badge = tk.Canvas(hero, width=84, height=84, bg=t.window_bg,
                          highlightthickness=0)
        badge.create_oval(4, 4, 80, 80, fill=grade_color, outline="")
        badge.create_text(42, 42, text=result.grade,
                          font=("Segoe UI", 30, "bold"), fill="#ffffff")
        badge.pack(side=tk.LEFT)

        right = tk.Frame(hero, bg=t.window_bg)
        right.pack(side=tk.LEFT, padx=16, fill=tk.X, expand=True)
        tk.Label(right, text=f"{result.gross_wpm:.1f} WPM",
                 font=("Segoe UI", 22, "bold"),
                 fg=t.fg, bg=t.window_bg).pack(anchor=tk.W)
        flags = []
        if is_pb:
            flags.append("🏆 New personal best!")
        flags.append(commentary)
        tk.Label(right, text="  ".join(flags), font=FONT_UI,
                 fg=t.warning if is_pb else t.fg_dim,
                 bg=t.window_bg).pack(anchor=tk.W)

        # -- achievement unlocks -------------------------------------------
        if new_achievements:
            tk.Label(win, text="Achievements unlocked:", font=FONT_UI_BOLD,
                     fg=t.fg, bg=t.window_bg).pack(anchor=tk.W, padx=24)
            for a in new_achievements:
                tk.Label(win, text=f"  {a.icon}  {a.title} — {a.description}",
                         font=FONT_UI, fg=t.success,
                         bg=t.window_bg).pack(anchor=tk.W, padx=24)

        # -- stats grid ------------------------------------------------------
        grid = tk.Frame(win, bg=t.panel_bg, highlightthickness=1,
                        highlightbackground=t.chart_grid)
        grid.pack(fill=tk.X, padx=20, pady=12)

        rows = [
            ("Mode", result.mode),
            ("Category", f"{result.category} · {result.difficulty}"),
            ("Time", f"{result.duration_seconds:.1f}s"),
            ("Gross WPM", f"{result.gross_wpm:.1f}"),
            ("Net WPM", f"{result.net_wpm:.1f}"),
            ("Accuracy", f"{result.accuracy:.1f}%"),
            ("Errors", str(result.errors)),
            ("Completion",
             f"{result.completion:.1f}% "
             f"({result.total_chars_typed}/{result.text_length} chars)"),
        ]
        for i, (label, value) in enumerate(rows):
            tk.Label(grid, text=label, font=FONT_UI, fg=t.fg_dim,
                     bg=t.panel_bg).grid(row=i, column=0, sticky=tk.W,
                                         padx=14, pady=2)
            tk.Label(grid, text=value, font=FONT_UI_BOLD, fg=t.fg,
                     bg=t.panel_bg).grid(row=i, column=1, sticky=tk.E,
                                         padx=14, pady=2)
        grid.columnconfigure(1, weight=1)

        # -- buttons ---------------------------------------------------------
        btns = tk.Frame(win, bg=t.window_bg)
        btns.pack(pady=(0, 14))

        copy_btn = tk.Button(btns, text="Copy summary",
                             command=self._copy_summary)
        style_button(copy_btn, t, kind="ghost", font=FONT_UI)
        copy_btn.pack(side=tk.LEFT, padx=4)

        if on_dashboard:
            dash_btn = tk.Button(btns, text="Dashboard",
                                 command=lambda: [self.win.destroy(),
                                                  on_dashboard()])
            style_button(dash_btn, t, kind="ghost", font=FONT_UI)
            dash_btn.pack(side=tk.LEFT, padx=4)

        retry_btn = tk.Button(btns, text="Retry",
                              command=lambda: [self.win.destroy(),
                                               self._fire(self._on_retry)])
        style_button(retry_btn, t, kind="primary", font=FONT_UI)
        retry_btn.pack(side=tk.LEFT, padx=4)

        next_btn = tk.Button(btns, text="Next text",
                             command=lambda: [self.win.destroy(),
                                              self._fire(self._on_next)])
        style_button(next_btn, t, kind="success", font=FONT_UI)
        next_btn.pack(side=tk.LEFT, padx=4)

        win.bind("<Escape>", lambda _e: win.destroy())
        apply_panel(win, t)

    # ------------------------------------------------------------------

    @staticmethod
    def _fire(cb: Optional[Callable[[], None]]) -> None:
        if cb:
            cb()

    def _copy_summary(self) -> None:
        r = self._result
        text = (
            f"Typing Speed Test — {r.gross_wpm:.1f} WPM "
            f"({r.accuracy:.1f}% acc, grade {r.grade}) "
            f"on '{r.category}' · {r.mode} · "
            f"{r.errors} errors · {r.completion:.0f}% complete"
        )
        self.win.clipboard_clear()
        self.win.clipboard_append(text)
