"""Central configuration constants for the application.

Everything here is pure data — no side effects on import, so it stays
safe to import from tests and CI environments without a display.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from typingtest import __app_name__

# ---------------------------------------------------------------------------
# Test modes
# ---------------------------------------------------------------------------

MODE_COMPLETE = "Complete Text"
MODE_60 = "60 seconds"
MODE_120 = "120 seconds"
MODE_300 = "300 seconds"

MODES = [MODE_COMPLETE, MODE_60, MODE_120, MODE_300]

# Mode label -> time limit in seconds (None = untimed / complete-the-text).
MODE_DURATIONS = {
    MODE_COMPLETE: None,
    MODE_60: 60,
    MODE_120: 120,
    MODE_300: 300,
}

DIFFICULTIES = ["All", "easy", "medium", "hard"]
DEFAULT_DIFFICULTY = "All"

# ---------------------------------------------------------------------------
# Default persisted settings
# ---------------------------------------------------------------------------

DEFAULT_SETTINGS = {
    "theme": "dark",
    "mode": MODE_COMPLETE,
    "difficulty": DEFAULT_DIFFICULTY,
    "category": "All",
    "sound": True,
    "legacy_imported": False,
}

# ---------------------------------------------------------------------------
# Data locations
# ---------------------------------------------------------------------------


def app_data_dir() -> Path:
    """Return the per-user data directory for the app, creating it lazily.

    Windows: ``%LOCALAPPDATA%\\TypingSpeedTest``
    macOS:   ``~/Library/Application Support/TypingSpeedTest``
    Linux:   ``$XDG_DATA_HOME/typing-speed-test`` or ``~/.local/share/...``
    """
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        path = root / "TypingSpeedTest"
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "TypingSpeedTest"
    else:
        xdg = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        path = Path(xdg) / "typing-speed-test"
    path.mkdir(parents=True, exist_ok=True)
    return path


if getattr(sys, "frozen", False):
    # PyInstaller bundle: data lands next to the package inside _MEIPASS.
    _PKG_ROOT = Path(getattr(sys, "_MEIPASS")) / "typingtest"
else:
    _PKG_ROOT = Path(__file__).resolve().parent
BUNDLED_TEXTS = _PKG_ROOT / "data" / "texts.json"

LEGACY_HISTORY_FILE = "advanced_typing_history.json"

# Filenames used inside :func:`app_data_dir`.
HISTORY_FILENAME = "history.json"
SETTINGS_FILENAME = "settings.json"
CUSTOM_TEXTS_FILENAME = "custom_texts.json"

WINDOW_TITLE = f"{__app_name__}"
WINDOW_SIZE = "1280x860"
MIN_WINDOW_SIZE = (1024, 720)

UI_TICK_MS = 100  # live-stat refresh rate while a test runs
