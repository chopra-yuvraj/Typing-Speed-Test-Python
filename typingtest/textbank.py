"""Text bank: loads the bundled passage library and user custom texts.

Texts ship as ``data/texts.json`` inside the package::

    {"version": 2, "texts": [{"id", "category", "difficulty", "text"}]}

User-added practice texts live in the per-user data directory and merge
into the bank under the ``Custom`` category.
"""
from __future__ import annotations

import logging
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from typingtest import config
from typingtest.storage import load_json, save_json

log = logging.getLogger(__name__)

VALID_DIFFICULTIES = ("easy", "medium", "hard")
CUSTOM_CATEGORY = "Custom"
MIN_CUSTOM_CHARS = 30
MAX_CUSTOM_CHARS = 4000


@dataclass(frozen=True)
class TextEntry:
    """One practice passage."""

    id: str
    category: str
    difficulty: str
    text: str

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def char_count(self) -> int:
        return len(self.text)


class TextBankError(Exception):
    """Raised when the bundled data file is missing or malformed."""


class TextBank:
    """Read-mostly container over bundled + custom passages."""

    def __init__(self,
                 data_path: Optional[Path] = None,
                 custom_path: Optional[Path] = None) -> None:
        self._rng = random.Random()
        self._data_path = data_path or config.BUNDLED_TEXTS
        self._custom_path = (custom_path
                             or config.app_data_dir() / config.CUSTOM_TEXTS_FILENAME)
        self._entries: List[TextEntry] = self._load()
        self._custom: List[TextEntry] = self._load_custom()
        self._last_id: Optional[str] = None

    # -- loading ----------------------------------------------------------

    def _load(self) -> List[TextEntry]:
        payload = load_json(self._data_path, None)
        if payload is None:
            raise TextBankError(f"bundled text file not found: {self._data_path}")
        entries = []
        for raw in payload.get("texts", []):
            entry = self._coerce(raw)
            if entry:
                entries.append(entry)
        if not entries:
            raise TextBankError("bundled text file contains no usable texts")
        return entries

    def _load_custom(self) -> List[TextEntry]:
        raw = load_json(self._custom_path, [])
        out = []
        for item in raw if isinstance(raw, list) else []:
            entry = self._coerce(item)
            if entry:
                out.append(entry)
        return out

    @staticmethod
    def _coerce(raw: dict) -> Optional[TextEntry]:
        try:
            text = str(raw["text"]).strip()
            if not text:
                return None
            difficulty = str(raw.get("difficulty", "medium")).lower()
            if difficulty not in VALID_DIFFICULTIES:
                difficulty = "medium"
            return TextEntry(
                id=str(raw.get("id") or uuid.uuid4().hex[:8]),
                category=str(raw.get("category", "General")),
                difficulty=difficulty,
                text=text,
            )
        except (KeyError, TypeError) as exc:
            log.warning("Skipping malformed text entry: %s", exc)
            return None

    # -- queries ------------------------------------------------------------

    @property
    def all(self) -> List[TextEntry]:
        return [*self._entries, *self._custom]

    @property
    def categories(self) -> List[str]:
        seen: Dict[str, None] = {}
        for e in self.all:
            seen.setdefault(e.category)
        return list(seen)

    @property
    def total_texts(self) -> int:
        return len(self._entries)  # bundled only; matches README headline

    def filter(self,
               difficulty: Optional[str] = None,
               category: Optional[str] = None) -> List[TextEntry]:
        """Return entries matching optional filters ('All'/None = no filter)."""
        pool = self.all
        if difficulty and difficulty != "All":
            pool = [e for e in pool if e.difficulty == difficulty]
        if category and category != "All":
            pool = [e for e in pool if e.category == category]
        return pool

    # -- selection ----------------------------------------------------------

    def pick(self,
             difficulty: Optional[str] = None,
             category: Optional[str] = None) -> TextEntry:
        """Randomly pick a passage; never repeat the previous one if possible."""
        pool = self.filter(difficulty, category)
        if not pool:
            # graceful widening: relax difficulty, then category
            pool = self.filter(category=category) or self.all
        candidates = [e for e in pool if e.id != self._last_id]
        if not candidates:
            candidates = pool
        entry = self._rng.choice(candidates)
        self._last_id = entry.id
        return entry

    # -- custom texts ---------------------------------------------------------

    @property
    def custom_entries(self) -> List[TextEntry]:
        return list(self._custom)

    def add_custom(self, text: str, title: str = "") -> TextEntry:
        """Validate and persist a user-provided practice passage."""
        cleaned = text.strip()
        if len(cleaned) < MIN_CUSTOM_CHARS:
            raise ValueError(
                f"Text is too short (min {MIN_CUSTOM_CHARS} characters).")
        if len(cleaned) > MAX_CUSTOM_CHARS:
            raise ValueError(
                f"Text is too long (max {MAX_CUSTOM_CHARS} characters).")
        entry = TextEntry(
            id=f"custom-{uuid.uuid4().hex[:8]}",
            category=CUSTOM_CATEGORY,
            difficulty="medium",
            text=cleaned,
        )
        self._custom.append(entry)
        self._save_custom()
        return entry

    def remove_custom(self, entry_id: str) -> bool:
        before = len(self._custom)
        self._custom = [e for e in self._custom if e.id != entry_id]
        changed = len(self._custom) != before
        if changed:
            self._save_custom()
        return changed

    def _save_custom(self) -> None:
        payload = [
            {"id": e.id, "category": e.category,
             "difficulty": e.difficulty, "text": e.text}
            for e in self._custom
        ]
        try:
            save_json(self._custom_path, payload)
        except OSError as exc:
            log.error("Failed to save custom texts: %s", exc)
            raise
