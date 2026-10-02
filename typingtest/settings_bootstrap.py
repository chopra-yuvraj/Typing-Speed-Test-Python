"""Service wiring: settings, history, text bank, sounds + legacy import.

Kept separate from :mod:`typingtest.app` so the wiring can be unit- or
smoke-tested without parsing CLI arguments or entering the mainloop.
"""
from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from typing import Dict, TypedDict

from typingtest import config
from typingtest.sound import SoundManager
from typingtest.storage import HistoryManager, SettingsManager
from typingtest.textbank import TextBank

log = logging.getLogger(__name__)


class Services(TypedDict):
    settings: SettingsManager
    history: HistoryManager
    textbank: TextBank
    sounds: SoundManager


def build_services(root: tk.Tk) -> Services:
    """Construct all app services and run one-time migrations."""
    settings = SettingsManager()
    history = HistoryManager()

    # One-time migration of the v1 history file from the current directory.
    if not settings.get("legacy_imported", False):
        legacy = Path.cwd() / config.LEGACY_HISTORY_FILE
        if legacy.exists():
            imported = history.import_legacy(legacy)
            log.info("Imported %d legacy results from %s", imported, legacy)
        settings.set("legacy_imported", True)

    textbank = TextBank()
    sounds = SoundManager(enabled=bool(settings.get("sound", True)),
                          bell=root.bell)

    return Services(settings=settings, history=history, textbank=textbank,
                    sounds=sounds)
