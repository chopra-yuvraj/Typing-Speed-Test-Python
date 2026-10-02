"""Statistics dashboard: lifetime analytics, charts, achievements, history."""
from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from typingtest.core import evaluate_achievements
from typingtest.storage import HistoryManager
from typingtest.themes import FONT_MONO, FONT_UI, FONT_UI_BOLD, Theme
from typingtest.widgets import (BarChart, LineChart, StatCard, apply_panel,
                                style_button)

log = logging.getLogger(__name__)

_HISTORY_COLUMNS = ("Date", "Mode", "Category", "WPM", "Acc %",
                    "Compl %", "Grade")
_TREND_POINTS = 30


class Dashboard:
    """A Toplevel that re-renders itself whenever history changes."""

    def __init__(self, parent: tk.Tk, theme: Theme,
                 history: HistoryManager) -> None:
        self._parent = parent
        self._theme = theme
        self._history = history
        self._win: Optional[tk.Toplevel] = None
        self._history.on_change(self._safe_refresh)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @property
    def alive(self) -> bool:
        return self._win is not None and bool(self._win.winfo_exists())

    def show(self) -> None:
        """Create the window on first use; lift it on subsequent calls."""
        if self._win is not None and self._win.winfo_exists():
            self._win.lift()
            self._win.focus_set()
            self.refresh()
            return
        self._build()

    def _build(self) -> None:
        t = self._theme
        win = tk.Toplevel(self._parent)
        self._win = win
        win.title("Dashboard — your statistics")
        win.configure(bg=t.window_bg)
        win.geometry("1080x780")
        win.minsize(900, 640)
        win.bind("<Escape>", lambda _e: win.destroy())

        header = tk.Frame(win, bg=t.window_bg)
        header.pack(fill=tk.X, padx=18, pady=(14, 4))
        tk.Label(header, text="📊 Dashboard", font=("Segoe UI", 18, "bold"),
                 fg=t.fg, bg=t.window_bg).pack(side=tk.LEFT)
        close_btn = tk.Button(header, text="Close", command=win.destroy)
        style_button(close_btn, t, kind="ghost", font=FONT_UI)
        close_btn.pack(side=tk.RIGHT)

        # -- summary cards --------------------------------------------------
        cards = tk.Frame(win, bg=t.window_bg)
        cards.pack(fill=tk.X, padx=18, pady=6)
        self.card_tests = StatCard(cards, "tests taken", t, t.info)
        self.card_best = StatCard(cards, "best WPM", t, t.success)
        self.card_avg = StatCard(cards, "average WPM", t, t.accent)
        self.card_acc = StatCard(cards, "avg accuracy %", t, t.warning)
        self.card_chars = StatCard(cards, "characters typed", t, t.danger)
        for c in (self.card_tests, self.card_best, self.card_avg,
                  self.card_acc, self.card_chars):
            c.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)

        # -- charts row -------------------------------------------------------
        charts = tk.Frame(win, bg=t.window_bg)
        charts.pack(fill=tk.BOTH, expand=True, padx=18, pady=6)

        left = tk.Frame(charts, bg=t.window_bg)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        tk.Label(left, text="WPM trend (recent tests)", font=FONT_UI_BOLD,
                 fg=t.fg, bg=t.window_bg).pack(anchor=tk.W)
        self.trend = LineChart(left, t)
        self.trend.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        right = tk.Frame(charts, bg=t.window_bg)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        tk.Label(right, text="Average WPM by category", font=FONT_UI_BOLD,
                 fg=t.fg, bg=t.window_bg).pack(anchor=tk.W)
        self.bars = BarChart(right, t)
        self.bars.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        # -- analysis row ------------------------------------------------------
        analysis = tk.Frame(win, bg=t.window_bg)
        analysis.pack(fill=tk.X, padx=18, pady=6)

        keys_frame = tk.Frame(analysis, bg=t.panel_bg, highlightthickness=1,
                              highlightbackground=t.chart_grid)
        keys_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        tk.Label(keys_frame, text="Keys to work on (most mistakes)",
                 font=FONT_UI_BOLD, fg=t.fg, bg=t.panel_bg
                 ).pack(anchor=tk.W, padx=12, pady=(8, 2))
        self.keys_label = tk.Label(keys_frame, text="", justify=tk.LEFT,
                                   font=FONT_MONO, fg=t.fg_dim,
                                   bg=t.panel_bg)
        self.keys_label.pack(anchor=tk.W, padx=12, pady=(0, 8))

        ach_frame = tk.Frame(analysis, bg=t.panel_bg, highlightthickness=1,
                             highlightbackground=t.chart_grid)
        ach_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        tk.Label(ach_frame, text="Achievements", font=FONT_UI_BOLD,
                 fg=t.fg, bg=t.panel_bg).pack(anchor=tk.W, padx=12,
                                              pady=(8, 2))
        self.ach_frame_inner = tk.Frame(ach_frame, bg=t.panel_bg)
        self.ach_frame_inner.pack(fill=tk.BOTH, expand=True, padx=8,
                                  pady=(0, 8))

        # -- history table ------------------------------------------------------
        tk.Label(win, text="Recent tests", font=FONT_UI_BOLD,
                 fg=t.fg, bg=t.window_bg).pack(anchor=tk.W, padx=18)
        table_frame = tk.Frame(win, bg=t.window_bg)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(2, 6))

        style = ttk.Style(win)
        style.configure("Dash.Treeview", background=t.panel_alt,
                        fieldbackground=t.panel_alt, foreground=t.fg,
                        rowheight=24)
        style.configure("Dash.Treeview.Heading", font=FONT_UI_BOLD,
                        background=t.panel_bg, foreground=t.fg)
        self.tree = ttk.Treeview(table_frame, columns=_HISTORY_COLUMNS,
                                 show="headings", height=8,
                                 style="Dash.Treeview")
        for col in _HISTORY_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90 if col != "Date" else 150,
                             anchor=tk.CENTER)
        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # -- actions ----------------------------------------------------------
        actions = tk.Frame(win, bg=t.window_bg)
        actions.pack(fill=tk.X, padx=18, pady=(0, 12))
        json_btn = tk.Button(actions, text="Export JSON",
                             command=lambda: self._export("json"))
        style_button(json_btn, t, kind="ghost", font=FONT_UI)
        json_btn.pack(side=tk.LEFT, padx=4)
        csv_btn = tk.Button(actions, text="Export CSV",
                            command=lambda: self._export("csv"))
        style_button(csv_btn, t, kind="ghost", font=FONT_UI)
        csv_btn.pack(side=tk.LEFT, padx=4)
        clear_btn = tk.Button(actions, text="Clear history…",
                              command=self._clear)
        style_button(clear_btn, t, kind="danger", font=FONT_UI)
        clear_btn.pack(side=tk.RIGHT, padx=4)

        apply_panel(win, t)
        self.refresh()

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def _safe_refresh(self) -> None:
        try:
            self.refresh()
        except tk.TclError:
            pass  # window was destroyed between event and refresh

    def refresh(self) -> None:
        if self._win is None or not self._win.winfo_exists():
            return
        history = self._history
        tests = history.tests()
        avgs = history.averages()

        self.card_tests.set(str(len(tests)))
        self.card_best.set(f"{history.best_wpm():.1f}")
        self.card_avg.set(f"{avgs['wpm']:.1f}")
        self.card_acc.set(f"{avgs['accuracy']:.1f}")
        total_chars = history.total_chars_typed()
        self.card_chars.set(f"{total_chars:,}")

        # trend: last N tests labelled #1..#n
        recent = tests[-_TREND_POINTS:]
        self.trend.set_data([(f"#{i + 1}", t.get("wpm", 0.0))
                             for i, t in enumerate(recent)])

        # per-category bars (top 8 by avg wpm)
        cats = history.per_category()
        rows = sorted(cats.items(), key=lambda kv: kv[1]["wpm"],
                      reverse=True)[:8]
        self.bars.set_data([(f"{k} ({v['tests']}×)", v["wpm"])
                            for k, v in rows])

        # error-prone keys
        mistakes = history.mistakes()
        if mistakes:
            pretty = {repr(k)[1:-1] if k.strip() else "space": v
                      for k, v in mistakes.most_common(8)}
            self.keys_label.config(
                text="\n".join(f"  '{k}'  —  {v}×" for k, v in pretty.items()))
        else:
            self.keys_label.config(text="  No mistakes recorded yet. Nice!")

        # achievements
        for child in self.ach_frame_inner.winfo_children():
            child.destroy()
        achievements = evaluate_achievements(
            tests, total_chars, history.unlocked_achievements())
        for i, a in enumerate(achievements):
            color = self._theme.fg if a.unlocked else self._theme.badge_locked
            tk.Label(self.ach_frame_inner,
                     text=f"{a.icon} {a.title}" + ("" if a.unlocked else " 🔒"),
                     font=FONT_UI_BOLD, fg=color,
                     bg=self._theme.panel_bg
                     ).grid(row=i, column=0, sticky=tk.W, padx=6)
            tk.Label(self.ach_frame_inner, text=a.description,
                     font=FONT_UI, fg=self._theme.fg_dim,
                     bg=self._theme.panel_bg
                     ).grid(row=i, column=1, sticky=tk.W, padx=6)

        # history table
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in reversed(tests[-100:]):
            self.tree.insert("", tk.END, values=(
                t.get("date", ""),
                t.get("test_mode", ""),
                t.get("category", ""),
                f"{t.get('wpm', 0.0):.1f}",
                f"{t.get('accuracy', 0.0):.1f}",
                f"{t.get('completion', 0.0):.1f}",
                t.get("grade", ""),
            ))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _export(self, fmt: str) -> None:
        if self._history.count() == 0:
            messagebox.showinfo("Export", "No test history to export yet!",
                                parent=self._win)
            return
        path = filedialog.asksaveasfilename(
            parent=self._win, defaultextension=f".{fmt}",
            filetypes=[("JSON files", "*.json")] if fmt == "json"
            else [("CSV files", "*.csv")],
            title=f"Export results as {fmt.upper()}")
        if not path:
            return
        try:
            if fmt == "json":
                self._history.export_json(Path(path))
            else:
                self._history.export_csv(Path(path))
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc), parent=self._win)
            return
        messagebox.showinfo("Export", f"Results exported to:\n{path}",
                            parent=self._win)

    def _clear(self) -> None:
        if not messagebox.askyesno(
                "Clear history",
                "Delete all saved test results and mistake statistics?\n"
                "This cannot be undone.", parent=self._win):
            return
        self._history.clear()
