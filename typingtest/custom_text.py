"""Dialog for adding a custom practice passage."""
from __future__ import annotations

import logging
import tkinter as tk
from typing import Callable, Optional

from typingtest.textbank import (MAX_CUSTOM_CHARS, MIN_CUSTOM_CHARS,
                                 TextBank, TextEntry)
from typingtest.themes import FONT_UI, FONT_UI_BOLD, Theme
from typingtest.widgets import style_button

log = logging.getLogger(__name__)


class CustomTextDialog:
    """Modal editor that saves user-provided texts into the text bank."""

    def __init__(self, parent: tk.Tk, theme: Theme, textbank: TextBank,
                 on_added: Optional[Callable[[TextEntry], None]] = None) -> None:
        self._bank = textbank
        self._on_added = on_added
        t = theme

        win = tk.Toplevel(parent)
        self.win = win
        win.title("Practice custom text")
        win.configure(bg=t.window_bg)
        win.transient(parent)
        win.minsize(560, 420)

        tk.Label(win, text="Paste any text to practice on:",
                 font=FONT_UI_BOLD, fg=t.fg, bg=t.window_bg
                 ).pack(anchor=tk.W, padx=16, pady=(14, 4))

        frame = tk.Frame(win, bg=t.chart_grid)
        frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)
        self.editor = tk.Text(frame, font=("Consolas", 11), wrap=tk.WORD,
                              bg=t.text_bg, fg=t.fg,
                              insertbackground=t.accent, relief=tk.FLAT,
                              padx=10, pady=8, undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.editor.bind("<KeyRelease>", lambda _e: self._update_count())

        self.count_label = tk.Label(
            win, text=f"{MIN_CUSTOM_CHARS}–{MAX_CUSTOM_CHARS} characters",
            font=FONT_UI, fg=t.fg_dim, bg=t.window_bg)
        self.count_label.pack(anchor=tk.W, padx=16)

        self.error_label = tk.Label(win, text="", font=FONT_UI,
                                    fg=t.danger, bg=t.window_bg)
        self.error_label.pack(anchor=tk.W, padx=16)

        btns = tk.Frame(win, bg=t.window_bg)
        btns.pack(pady=12)
        save_btn = tk.Button(btns, text="Save & practice", command=self._save)
        style_button(save_btn, t, kind="success", font=FONT_UI)
        save_btn.pack(side=tk.LEFT, padx=4)
        cancel_btn = tk.Button(btns, text="Cancel", command=win.destroy)
        style_button(cancel_btn, t, kind="ghost", font=FONT_UI)
        cancel_btn.pack(side=tk.LEFT, padx=4)

        win.bind("<Escape>", lambda _e: win.destroy())
        self.editor.focus_set()
        win.grab_set()

    def _update_count(self) -> None:
        n = len(self.editor.get("1.0", "end-1c"))
        self.count_label.config(text=f"{n} / {MAX_CUSTOM_CHARS} characters")
        self.error_label.config(text="")

    def _save(self) -> None:
        text = self.editor.get("1.0", "end-1c")
        try:
            entry = self._bank.add_custom(text)
        except (ValueError, OSError) as exc:
            log.debug("custom text rejected: %s", exc)
            self.error_label.config(text=str(exc))
            return
        if self._on_added:
            self._on_added(entry)
        self.win.destroy()
