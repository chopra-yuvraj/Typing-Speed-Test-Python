"""Persistence layer: settings, test history, and safe JSON I/O.

Design goals
------------
* **Atomic writes** — writes go to a temp file then ``os.replace`` so a
  crash mid-write can never corrupt the user's history.
* **Corruption recovery** — a broken JSON file is moved aside
  (``*.corrupt``) instead of crashing the app.
* **Versioned schema** — bumping ``SCHEMA_VERSION`` later won't break old
  files; unknown fields are preserved on read.
* **Legacy migration** — the v1 app's ``advanced_typing_history.json``
  (a plain list) is imported once, automatically.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from typingtest import config

log = logging.getLogger(__name__)

SCHEMA_VERSION = 2


# ---------------------------------------------------------------------------
# Low-level JSON helpers
# ---------------------------------------------------------------------------


def load_json(path: Path, default: Any) -> Any:
    """Load JSON from ``path``; on corruption move the file aside.

    Returns ``default`` when the file is missing or unrecoverable.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Could not read %s (%s); backing it up", path, exc)
        try:
            path.replace(path.with_suffix(path.suffix + ".corrupt"))
        except OSError:
            pass
        return default


def save_json(path: Path, data: Any) -> None:
    """Write ``data`` to ``path`` atomically (temp file + replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-",
                                    suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        os.replace(tmp_name, path)
    except OSError:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class SettingsManager:
    """Simple dict-backed key/value settings with defaults and dirty-save."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or config.app_data_dir() / config.SETTINGS_FILENAME
        self._lock = threading.Lock()
        stored = load_json(self._path, {})
        self._data: Dict[str, Any] = {**config.DEFAULT_SETTINGS,
                                      **{k: v for k, v in stored.items()
                                         if k in config.DEFAULT_SETTINGS}}

    @property
    def path(self) -> Path:
        return self._path

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any, *, save: bool = True) -> None:
        with self._lock:
            self._data[key] = value
            if save:
                self._save_locked()

    def as_dict(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._data)

    def _save_locked(self) -> None:
        try:
            save_json(self._path, self._data)
        except OSError as exc:  # never crash the app over settings
            log.error("Failed to save settings: %s", exc)

    def save(self) -> None:
        with self._lock:
            self._save_locked()


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


class HistoryManager:
    """Append-only store of test results with aggregates and export.

    On-disk format (``history.json``)::

        {
          "version": 2,
          "unlocked_achievements": {"wpm_40": "2026-01-01T10:00:00"},
          "mistakes": {"e": 12, "t": 9},
          "tests": [ { ...result dicts... } ]
        }
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path or config.app_data_dir() / config.HISTORY_FILENAME
        self._lock = threading.Lock()
        raw = load_json(self._path, {})
        self._tests: List[dict] = list(raw.get("tests", []))
        self._unlocked: Dict[str, str] = dict(raw.get("unlocked_achievements", {}))
        self._mistakes: Counter = Counter(raw.get("mistakes", {}))
        self._listeners: List[Callable[[], None]] = []

    # -- basic access -----------------------------------------------------

    @property
    def path(self) -> Path:
        return self._path

    def tests(self) -> List[dict]:
        with self._lock:
            return list(self._tests)

    def count(self) -> int:
        with self._lock:
            return len(self._tests)

    def mistakes(self) -> Counter:
        with self._lock:
            return Counter(self._mistakes)

    def unlocked_achievements(self) -> Dict[str, str]:
        with self._lock:
            return dict(self._unlocked)

    def total_chars_typed(self) -> int:
        with self._lock:
            return sum(int(t.get("total_chars", 0)) for t in self._tests)

    def on_change(self, callback: Callable[[], None]) -> None:
        """Register a callback fired after each mutation (UI refresh hook)."""
        self._listeners.append(callback)

    def _notify(self) -> None:
        for cb in self._listeners:
            try:
                cb()
            except Exception:  # a broken callback must not break storage
                log.exception("history change listener failed")

    # -- mutation ---------------------------------------------------------

    def add_result(self, result: dict,
                   mistakes: Optional[Counter] = None,
                   unlockable: Iterable[str] = ()) -> None:
        """Persist one result; merge keystroke mistakes; record unlocks."""
        from datetime import datetime

        with self._lock:
            self._tests.append(result)
            if mistakes:
                self._mistakes.update(mistakes)
            for key in unlockable:
                if key not in self._unlocked:
                    self._unlocked[key] = datetime.now().isoformat(timespec="seconds")
            self._save_locked()
        self._notify()

    def clear(self) -> None:
        with self._lock:
            self._tests.clear()
            self._mistakes.clear()
            self._save_locked()
        self._notify()

    def _save_locked(self) -> None:
        payload = {
            "version": SCHEMA_VERSION,
            "unlocked_achievements": self._unlocked,
            "mistakes": dict(self._mistakes),
            "tests": self._tests,
        }
        try:
            save_json(self._path, payload)
        except OSError as exc:
            log.error("Failed to save history: %s", exc)

    # -- aggregates ---------------------------------------------------------

    def best_wpm(self) -> float:
        with self._lock:
            return max((t.get("wpm", 0.0) for t in self._tests), default=0.0)

    def averages(self) -> Dict[str, float]:
        with self._lock:
            tests = list(self._tests)
        if not tests:
            return {"wpm": 0.0, "accuracy": 0.0, "completion": 0.0}
        n = len(tests)
        return {
            "wpm": sum(t.get("wpm", 0.0) for t in tests) / n,
            "accuracy": sum(t.get("accuracy", 0.0) for t in tests) / n,
            "completion": sum(t.get("completion", 0.0) for t in tests) / n,
        }

    def per_category(self) -> Dict[str, Dict[str, float]]:
        """Average WPM / accuracy grouped by category, with test counts."""
        buckets: Dict[str, List[dict]] = {}
        with self._lock:
            for t in self._tests:
                buckets.setdefault(t.get("category", "General"),
                                   []).append(t)
        return {
            cat: {
                "tests": len(rows),
                "wpm": sum(r.get("wpm", 0.0) for r in rows) / len(rows),
                "accuracy": sum(r.get("accuracy", 0.0) for r in rows) / len(rows),
            }
            for cat, rows in sorted(buckets.items())
        }

    # -- legacy migration ---------------------------------------------------

    def import_legacy(self, legacy_path: Path) -> int:
        """Import a v1 ``advanced_typing_history.json`` list, once.

        Returns the number of imported records (0 if nothing to import).
        The legacy file itself is left untouched.
        """
        from typingtest.core import TestResult

        data = load_json(legacy_path, [])
        if not isinstance(data, list) or not data:
            return 0
        imported = 0
        with self._lock:
            existing_dates = {t.get("date") for t in self._tests}
            for row in data:
                if not isinstance(row, dict):
                    continue
                if row.get("date") in existing_dates:
                    continue
                try:
                    self._tests.append(TestResult.from_dict(row).to_dict())
                except (TypeError, ValueError) as exc:
                    log.warning("Skipping bad legacy row: %s", exc)
                    continue
                imported += 1
            if imported:
                self._save_locked()
        if imported:
            self._notify()
        return imported

    # -- export -----------------------------------------------------------

    def export_json(self, path: Path) -> None:
        with self._lock:
            save_json(path, list(self._tests))

    def export_csv(self, path: Path) -> None:
        fields = ["date", "text_id", "category", "difficulty", "test_mode",
                  "elapsed_time", "wpm", "net_wpm", "accuracy", "errors",
                  "total_chars", "text_length", "completion", "grade"]
        with self._lock:
            rows = list(self._tests)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(",".join(fields) + "\n")
            for row in rows:
                fh.write(",".join(str(row.get(f, "")) for f in fields) + "\n")
