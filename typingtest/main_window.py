"""Main application window."""
from __future__ import annotations

import logging
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from typingtest import __app_name__, __version__, config
from typingtest.core import (CharStatus, LiveStats, TypingEngine,
                             evaluate_achievements)
from typingtest.results import ResultsDialog
from typingtest.sound import SoundManager
from typingtest.storage import HistoryManager, SettingsManager
from typingtest.textbank import CUSTOM_CATEGORY, TextBank, TextEntry
from typingtest.themes import (FONT_MONO, FONT_TEXT, FONT_TITLE, FONT_UI,
                               FONT_UI_BOLD, Theme, get_theme)
from typingtest.widgets import Sparkline, StatCard, style_button

log = logging.getLogger(__name__)


class MainWindow:
    """Coordinates engine, storage, sounds and the themed UI."""

    def __init__(self,
                 root: tk.Tk,
                 *,
                 textbank: Optional[TextBank] = None,
                 history: Optional[HistoryManager] = None,
                 settings: Optional[SettingsManager] = None,
                 sounds: Optional[SoundManager] = None) -> None:
        self.root = root
        self.settings = settings or SettingsManager()
        self.history = history or HistoryManager()
        self.textbank = textbank or TextBank()
        self.sounds = sounds or SoundManager(
            enabled=bool(self.settings.get("sound", True)))

        self.theme: Theme = get_theme(self.settings.get("theme", "dark"))

        self._engine: Optional[TypingEngine] = None
        self._entry: Optional[TextEntry] = None
        self._tick_job: Optional[str] = None
        self._rendered_len = -1
        self._dashboard = None  # dashboard.Dashboard instance (lat)

        root.title(f"{__app_name__} v{__version__}")
        root.geometry(config.WINDOW_SIZE)
        root.minsize(*config.MIN_WINDOW_SIZE)

        self._build_menu()
        self._build()
        self.new_text()
        self._bind_shortcuts()

    # ==================================================================
    # Construction
    # ==================================================================

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export JSON…", accelerator="Ctrl+E",
                              command=lambda: self.export("json"))
        file_menu.add_command(label="Export CSV…",
                              command=lambda: self.export("csv"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        practice = tk.Menu(menubar, tearoff=0)
        practice.add_command(label="New text", accelerator="Ctrl+N",
                             command=self.new_text)
        practice.add_command(label="Restart", accelerator="Esc",
                             command=self.restart)
        practice.add_command(label="Practice custom text…",
                             command=self.add_custom_text)
        menubar.add_cascade(label="Practice", menu=practice)

        view = tk.Menu(menubar, tearoff=0)
        view.add_command(label="Dashboard", accelerator="Ctrl+D",
                         command=self.open_dashboard)
        view.add_command(label="Toggle theme", accelerator="Ctrl+T",
                         command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Keyboard shortcuts",
                              command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _build(self) -> None:
        """(Re)build every widget; called on start and on theme change."""
        t = self.theme
        if hasattr(self, "_container"):
            self._container.destroy()

        self._container = tk.Frame(self.root, bg=t.window_bg)
        self._container.pack(fill=tk.BOTH, expand=True)

        self._build_header()
        self._build_controls()
        self._build_stats()
        self._build_text_display()
        self._build_input()
        self._build_buttons()
        self._build_status_bar()

        self._configure_text_tags()
        self._rendered_len = -1
        if self._entry is not None:
            self._render_text(force=True)
            self._update_info_label()

        self.root.configure(bg=t.window_bg)

    # -- sections ---------------------------------------------------------

    def _build_header(self) -> None:
        t = self.theme
        header = tk.Frame(self._container, bg=t.window_bg)
        header.pack(fill=tk.X, padx=18, pady=(12, 4))

        tk.Label(header, text=f"⚡ {__app_name__}", font=FONT_TITLE,
                 fg=t.fg, bg=t.window_bg).pack(side=tk.LEFT)
        tk.Label(header, text=f"v{__version__}", font=FONT_MONO,
                 fg=t.fg_dim, bg=t.window_bg).pack(side=tk.LEFT, padx=8)

        theme_btn = tk.Button(header,
                              text="☀ Light" if t.name == "dark" else "🌙 Dark",
                              command=self.toggle_theme)
        style_button(theme_btn, t, kind="ghost", font=("Segoe UI", 9, "bold"))
        theme_btn.pack(side=tk.RIGHT)

    def _build_controls(self) -> None:
        t = self.theme
        bar = tk.Frame(self._container, bg=t.panel_bg,
                       highlightthickness=1,
                       highlightbackground=t.chart_grid)
        bar.pack(fill=tk.X, padx=18, pady=6)

        self._combo_style()

        def combo(values: List[str], current: str, width: int) -> ttk.Combobox:
            cb = ttk.Combobox(bar, values=values, state="readonly",
                              width=width, style="App.TCombobox",
                              font=FONT_UI)
            cb.set(current)
            return cb

        tk.Label(bar, text="Mode", font=FONT_UI, fg=t.fg_dim,
                 bg=t.panel_bg).pack(side=tk.LEFT, padx=(12, 3))
        self.mode_combo = combo(config.MODES,
                                self.settings.get("mode", config.MODE_COMPLETE), 13)
        self.mode_combo.pack(side=tk.LEFT, pady=8)
        self.mode_combo.bind("<<ComboboxSelected>>", lambda _e: self.restart())

        tk.Label(bar, text="Difficulty", font=FONT_UI, fg=t.fg_dim,
                 bg=t.panel_bg).pack(side=tk.LEFT, padx=(14, 3))
        self.diff_combo = combo(config.DIFFICULTIES,
                                self.settings.get("difficulty", "All"), 8)
        self.diff_combo.pack(side=tk.LEFT)
        self.diff_combo.bind("<<ComboboxSelected>>", lambda _e: self.new_text())

        tk.Label(bar, text="Category", font=FONT_UI, fg=t.fg_dim,
                 bg=t.panel_bg).pack(side=tk.LEFT, padx=(14, 3))
        self.cat_combo = combo(["All", *self.textbank.categories],
                               self.settings.get("category", "All"), 20)
        self.cat_combo.pack(side=tk.LEFT)
        self.cat_combo.bind("<<ComboboxSelected>>", lambda _e: self.new_text())

        self.info_label = tk.Label(bar, text="", font=FONT_UI_BOLD,
                                   fg=t.accent, bg=t.panel_bg)
        self.info_label.pack(side=tk.LEFT, padx=16)

        self.sound_var = tk.BooleanVar(
            value=bool(self.settings.get("sound", True)))
        snd = tk.Checkbutton(bar, text="🔊 Sound", variable=self.sound_var,
                             command=self._on_sound_toggle, font=FONT_UI,
                             fg=t.fg, bg=t.panel_bg, selectcolor=t.panel_alt,
                             activebackground=t.panel_bg,
                             activeforeground=t.fg)
        snd.pack(side=tk.RIGHT, padx=12)

    def _combo_style(self) -> None:
        t = self.theme
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TCombobox", fieldbackground=t.panel_alt,
                        background=t.panel_alt, foreground=t.fg,
                        arrowcolor=t.fg, bordercolor=t.chart_grid,
                        padding=3)
        style.map("App.TCombobox",
                  fieldbackground=[("readonly", t.panel_alt)],
                  foreground=[("readonly", t.fg)])

    def _build_stats(self) -> None:
        t = self.theme
        row = tk.Frame(self._container, bg=t.window_bg)
        row.pack(fill=tk.X, padx=18, pady=6)

        self.card_wpm = StatCard(row, "words per min", t, t.info)
        self.card_wpm.set("0.0")
        self.card_wpm.pack(side=tk.LEFT, padx=(0, 6))

        self.card_acc = StatCard(row, "accuracy %", t, t.success)
        self.card_acc.set("100.0")
        self.card_acc.pack(side=tk.LEFT, padx=6)

        self.card_prog = StatCard(row, "progress %", t, t.warning)
        self.card_prog.set("0.0")
        self.card_prog.pack(side=tk.LEFT, padx=6)

        self.card_time = StatCard(row, "time", t, t.danger)
        self.card_time.set("--")
        self.card_time.pack(side=tk.LEFT, padx=6)

        self.card_err = StatCard(row, "errors", t, t.fg_dim)
        self.card_err.set("0")
        self.card_err.pack(side=tk.LEFT, padx=6)

        self.sparkline = Sparkline(row, t)
        self.sparkline.pack(side=tk.LEFT, fill=tk.X, expand=True,
                            padx=(12, 0))

    def _build_text_display(self) -> None:
        t = self.theme
        frame = tk.Frame(self._container, bg=t.window_bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(6, 4))

        self.text_display = tk.Text(
            frame, font=FONT_TEXT, wrap=tk.WORD, bg=t.text_bg, fg=t.pending_fg,
            state=tk.DISABLED, relief=tk.FLAT, padx=14, pady=10, height=8,
            cursor="arrow", spacing1=4, spacing3=4)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL,
                               command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=scroll.set)
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_input(self) -> None:
        t = self.theme
        frame = tk.Frame(self._container, bg=t.window_bg)
        frame.pack(fill=tk.X, padx=18, pady=(4, 2))

        self.hint_label = tk.Label(
            frame, text="Start typing — the test begins automatically",
            font=FONT_UI, fg=t.fg_dim, bg=t.window_bg)
        self.hint_label.pack(anchor=tk.W)

        self.input_text = tk.Text(
            self._container, font=FONT_TEXT, wrap=tk.WORD,
            bg=t.text_bg, fg=t.fg, insertbackground=t.accent,
            relief=tk.FLAT, padx=14, pady=10, height=4,
            highlightthickness=1, highlightcolor=t.accent,
            highlightbackground=t.chart_grid)
        self.input_text.pack(fill=tk.X, padx=18, pady=(2, 4))
        self.input_text.bind("<KeyPress>", self._on_key_press)
        self.input_text.bind("<KeyRelease>", self.on_key_release)

    def _build_buttons(self) -> None:
        t = self.theme
        row = tk.Frame(self._container, bg=t.window_bg)
        row.pack(pady=10)

        self.start_btn = tk.Button(row, text="Start Test",
                                   command=self.toggle_test)
        style_button(self.start_btn, t, kind="success",
                     font=("Segoe UI", 11, "bold"))
        self.start_btn.pack(side=tk.LEFT, padx=5)

        new_btn = tk.Button(row, text="New Text (Ctrl+N)",
                            command=self.new_text)
        style_button(new_btn, t, kind="primary", font=("Segoe UI", 11, "bold"))
        new_btn.pack(side=tk.LEFT, padx=5)

        restart_btn = tk.Button(row, text="Restart (Esc)", command=self.restart)
        style_button(restart_btn, t, kind="ghost", font=("Segoe UI", 11, "bold"))
        restart_btn.pack(side=tk.LEFT, padx=5)

        dash_btn = tk.Button(row, text="Dashboard (Ctrl+D)",
                             command=self.open_dashboard)
        style_button(dash_btn, t, kind="ghost", font=("Segoe UI", 11, "bold"))
        dash_btn.pack(side=tk.LEFT, padx=5)

        export_btn = tk.Button(row, text="Export…",
                               command=lambda: self.export("json"))
        style_button(export_btn, t, kind="ghost", font=("Segoe UI", 11, "bold"))
        export_btn.pack(side=tk.LEFT, padx=5)

    def _build_status_bar(self) -> None:
        t = self.theme
        bar = tk.Frame(self._container, bg=t.panel_bg)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(
            bar, text="Ctrl+Enter start · Ctrl+N new text · Esc restart · "
                      "Ctrl+D dashboard · Ctrl+T theme",
            font=FONT_MONO, fg=t.fg_dim, bg=t.panel_bg, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10, pady=3)

    # ==================================================================
    # Shortcuts
    # ==================================================================

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda _e: self.new_text())
        self.root.bind("<Control-d>", lambda _e: self.open_dashboard())
        self.root.bind("<Control-t>", lambda _e: self.toggle_theme())
        self.root.bind("<Escape>", lambda _e: self.restart())
        self.root.bind("<Control-Return>", lambda _e: self.toggle_test())
        self.root.bind("<Control-e>", lambda _e: self.export("json"))

    # ==================================================================
    # Test lifecycle
    # ==================================================================

    @property
    def running(self) -> bool:
        return self._engine is not None and self._engine.running

    def _current_duration(self) -> Optional[int]:
        return config.MODE_DURATIONS.get(
            self.mode_combo.get(), None)

    def _save_filters(self) -> None:
        self.settings.set("mode", self.mode_combo.get(), save=False)
        self.settings.set("difficulty", self.diff_combo.get(), save=False)
        self.settings.set("category", self.cat_combo.get(), save=False)
        self.settings.save()

    def new_text(self) -> None:
        """Pick a fresh passage and reset."""
        self._save_filters()
        self.entry = self.textbank.pick(self.diff_combo.get(),
                                        self.cat_combo.get())
        self.restart()

    @property
    def entry(self) -> TextEntry:
        assert self._entry is not None
        return self._entry

    @entry.setter
    def entry(self, value: TextEntry) -> None:
        self._entry = value

    def restart(self) -> None:
        """Reset engine + UI for the current text (no new passage)."""
        self._cancel_tick()
        self._engine = TypingEngine(self.entry.text,
                                    time_limit=self._current_duration())
        self._rendered_len = -1
        self._render_text(force=True)
        self._update_info_label()

        self.input_text.config(state=tk.NORMAL)
        self.input_text.delete("1.0", tk.END)
        self.input_text.focus_set()

        self.start_btn.config(text="Start Test", state=tk.NORMAL)
        self._paint_stats(LiveStats(0, 0, 0, 100.0, 0, 0, 0, 0.0,
                                    self._current_duration()))
        self.sparkline.reset()
        self.hint_label.config(
            text="Start typing — the test begins automatically")

    def toggle_test(self) -> None:
        if self.running:
            self.finish_test()
        else:
            self.start_test()

    def start_test(self) -> None:
        assert self._engine is not None
        if not self._engine.running:
            self._engine.begin()
            self.start_btn.config(text="Stop")
            self.hint_label.config(text="Go!")
            self.input_text.config(state=tk.NORMAL)
            self.input_text.focus_set()
            self._schedule_tick()

    def finish_test(self, *, cancelled: bool = False) -> None:
        engine = self._engine
        if engine is None or not engine.running:
            return
        self._cancel_tick()
        self.input_text.config(state=tk.NORMAL)
        stats = engine.stats()
        if cancelled or stats.total_typed < 5:
            # too little typed to count — just reset quietly
            self.restart()
            return

        entry = self.entry
        result = engine.finish(
            text_id=entry.id, category=entry.category,
            difficulty=entry.difficulty, mode=self.mode_combo.get(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        result_dict = result.to_dict()

        # -- personal best & achievements ---------------------------------
        previous_best = self.history.best_wpm()
        previous_unlocked = set(self.history.unlocked_achievements())
        total_chars = (self.history.total_chars_typed()
                       + result.total_chars_typed)
        achieved = evaluate_achievements(self.history.tests() + [result_dict],
                                         total_chars,
                                         self.history.unlocked_achievements())
        all_unlocked = {a.key for a in achieved if a.unlocked}
        newly_unlocked = [a for a in achieved
                          if a.key in all_unlocked
                          and a.key not in previous_unlocked]
        is_pb = (self.history.count() > 0
                 and result.gross_wpm > previous_best)

        self.history.add_result(result_dict,
                                mistakes=engine.mistakes,
                                unlockable=all_unlocked)

        if is_pb or newly_unlocked:
            self.sounds.new_personal_best()
        else:
            self.sounds.success()

        self._paint_stats(stats)
        self.start_btn.config(text="Start Test")
        ResultsDialog(self.root, self.theme, result,
                      is_personal_best=is_pb,
                      new_achievements=newly_unlocked,
                      on_next=self._dialog_next,
                      on_retry=self._dialog_retry,
                      on_dashboard=self.open_dashboard)
        self.start_btn.config(text="Start Test")

    def _dialog_next(self) -> None:
        self.new_text()

    def _dialog_retry(self) -> None:
        self.restart()

    # ==================================================================
    # Typing events
    # ==================================================================

    def _on_key_press(self, event: tk.Event) -> None:
        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R",
                            "Alt_L", "Alt_R", "Caps_Lock"):
            return
        if event.state & 0x4 and event.keysym not in ("Return",):  # Ctrl held
            return
        engine = self._engine
        if engine is None:
            return "break"
        if not engine.running:
            if event.char and event.char.isprintable():
                self.start_test()
            else:
                return
        if event.keysym == "BackSpace":
            return  # allowed; sync happens on KeyRelease
        expected_index = len(self.input_text.get("1.0", "end-1c"))
        target = engine.target
        if expected_index >= len(target):
            return "break"  # text exhausted
        char = "\n" if event.keysym == "Return" else event.char
        if not char:
            return
        if char != target[expected_index]:
            engine.record_mistake(target[expected_index], char)
            self.sounds.error()
        else:
            self.sounds.click()

    def on_key_release(self, _event: tk.Event) -> None:
        self._sync_from_input()

    def _sync_from_input(self) -> None:
        engine = self._engine
        if engine is None or not engine.running:
            return
        content = self.input_text.get("1.0", "end-1c")
        if len(content) > len(engine.target):  # clamp overflow
            self.input_text.delete(f"1.{len(engine.target)}", tk.END)
            content = content[: len(engine.target)]
        engine.update(content)
        self._render_text()
        self._paint_stats(engine.stats())
        if engine.is_finished():
            self.finish_test()

    # ==================================================================
    # Live ticking
    # ==================================================================

    def _schedule_tick(self) -> None:
        self._tick_job = self.root.after(config.UI_TICK_MS, self._tick)

    def _cancel_tick(self) -> None:
        if self._tick_job is not None:
            try:
                self.root.after_cancel(self._tick_job)
            except tk.TclError:
                pass
            self._tick_job = None

    def _tick(self) -> None:
        engine = self._engine
        if engine is None or not engine.running:
            return
        stats = engine.stats()
        self._paint_stats(stats)
        if stats.elapsed >= 1.0:  # skip the meaningless early WPM spike
            self.sparkline.push(stats.gross_wpm)
        if engine.is_finished():
            self.finish_test()
            return
        self._schedule_tick()

    def _paint_stats(self, stats: LiveStats) -> None:
        finished = stats.total_typed > 0 and not self.running
        show_wpm = stats.elapsed >= 1.0 or finished
        self.card_wpm.set(f"{stats.gross_wpm:.1f}" if show_wpm else "—")
        self.card_acc.set(f"{stats.accuracy:.1f}")
        self.card_prog.set(f"{stats.progress:.1f}")
        self.card_err.set(str(stats.incorrect))
        if stats.remaining is not None:
            self.card_time.set(f"{stats.remaining:.0f}s")
        else:
            self.card_time.set(f"{stats.elapsed:.1f}s"
                               if stats.elapsed else "--")

    # ==================================================================
    # Text rendering
    # ==================================================================

    def _configure_text_tags(self) -> None:
        t = self.theme
        self.text_display.tag_configure(
            "correct", background=t.correct_bg, foreground=t.correct_fg)
        self.text_display.tag_configure(
            "incorrect", background=t.incorrect_bg, foreground=t.incorrect_fg,
            underline=True)
        self.text_display.tag_configure(
            "current", background=t.current_bg, foreground=t.fg)
        self.text_display.tag_configure("pending", foreground=t.pending_fg)

    def _render_text(self, force: bool = False) -> None:
        engine = self._engine
        if engine is None:
            return
        typed_len = len(engine.typed)
        if not force and typed_len == self._rendered_len:
            return
        self._rendered_len = typed_len
        statuses = engine.statuses
        tag_for = {
            CharStatus.PENDING: "pending",
            CharStatus.CORRECT: "correct",
            CharStatus.INCORRECT: "incorrect",
            CharStatus.CURRENT: "current",
        }
        widget = self.text_display
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        # Join same-tag runs to keep insert calls O(#runs) not O(#chars).
        run_tag, run_chars = None, []
        for ch, status in zip(engine.target, statuses):
            tag = tag_for[status]
            if tag != run_tag and run_chars:
                widget.insert(tk.END, "".join(run_chars), run_tag)
                run_chars = []
            run_tag = tag
            run_chars.append(ch)
        if run_chars:
            widget.insert(tk.END, "".join(run_chars), run_tag)
        widget.config(state=tk.DISABLED)

    def _update_info_label(self) -> None:
        e = self.entry
        self.info_label.config(
            text=f"{e.category} · {e.difficulty} · "
                 f"{e.word_count} words")

    # ==================================================================
    # Menu actions
    # ==================================================================

    def toggle_theme(self) -> None:
        """Switch dark ↔ light and rebuild the UI (test state is reset)."""
        if self.running:
            self.finish_test(cancelled=True)
        new_theme = "light" if self.theme.name == "dark" else "dark"
        self.settings.set("theme", new_theme)
        self.theme = get_theme(new_theme)
        self._build()
        self.restart()

    def _on_sound_toggle(self) -> None:
        enabled = self.sound_var.get()
        self.settings.set("sound", enabled)
        self.sounds.set_enabled(enabled)

    def open_dashboard(self) -> None:
        from typingtest.dashboard import Dashboard
        if self._dashboard is None or not self._dashboard.alive:
            self._dashboard = Dashboard(self.root, self.theme, self.history)
        self._dashboard.show()

    def add_custom_text(self) -> None:
        from typingtest.custom_text import CustomTextDialog
        CustomTextDialog(self.root, self.theme, self.textbank,
                         on_added=self._on_custom_added)

    def _on_custom_added(self, entry: TextEntry) -> None:
        # refresh category list and jump straight into the new text
        self.cat_combo.config(values=["All", *self.textbank.categories])
        self.cat_combo.set(CUSTOM_CATEGORY)
        self._save_filters()
        self.entry = entry
        self.restart()

    def export(self, fmt: str) -> None:
        if self.history.count() == 0:
            messagebox.showinfo("Export", "No test history to export yet!",
                                parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=f".{fmt}",
            filetypes=[("JSON files", "*.json")] if fmt == "json"
            else [("CSV files", "*.csv")],
            title=f"Export results as {fmt.upper()}")
        if not path:
            return
        try:
            if fmt == "json":
                self.history.export_json(Path(path))
            else:
                self.history.export_csv(Path(path))
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc), parent=self.root)
            return
        messagebox.showinfo("Export", f"Results exported to:\n{path}",
                            parent=self.root)

    def show_shortcuts(self) -> None:
        messagebox.showinfo(
            "Keyboard shortcuts",
            "Type anywhere — the test starts automatically.\n\n"
            "Ctrl+Enter   start / stop\n"
            "Ctrl+N       new text\n"
            "Esc          restart current text\n"
            "Ctrl+D       open dashboard\n"
            "Ctrl+T       toggle dark/light theme\n"
            "Ctrl+E       export results",
            parent=self.root)

    def show_about(self) -> None:
        messagebox.showinfo(
            f"About {__app_name__}",
            f"{__app_name__} v{__version__}\n\n"
            "Measure, analyse and improve your typing.\n"
            "Themes, difficulty levels, code snippets, live WPM graph,\n"
            "achievements and detailed statistics.\n\n"
            "Built with Python + Tkinter — no dependencies.",
            parent=self.root)
