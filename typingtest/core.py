"""Core typing-test logic.

This module is deliberately free of any GUI dependency so it can be
unit-tested in headless CI. The UI feeds it whole strings of typed input
and pulls immutable snapshots of stats back out.
"""
from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

#: Standard typing-test convention: one "word" is five characters.
CHARS_PER_WORD = 5


class CharStatus(Enum):
    """Per-character render state in the target text."""

    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    CURRENT = "current"  # the next character to type


class Grade(Enum):
    """Letter grade awarded for a finished test."""

    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"

    @property
    def commentary(self) -> str:
        return {
            Grade.S: "Legendary. Keyboard ninja status unlocked.",
            Grade.A: "Excellent! Fast and precise.",
            Grade.B: "Great job — solid, reliable speed.",
            Grade.C: "Good progress. Keep practicing smoothness.",
            Grade.D: "Warm-up round. Accuracy first, speed follows.",
        }[self]


# ---------------------------------------------------------------------------
# Pure metric functions
# ---------------------------------------------------------------------------


def gross_wpm(correct_chars: int, elapsed_seconds: float) -> float:
    """Words per minute: (correct chars / 5) / minutes."""
    if elapsed_seconds <= 0:
        return 0.0
    return (correct_chars / CHARS_PER_WORD) / (elapsed_seconds / 60.0)


def net_wpm(correct_chars: int, errors: int, elapsed_seconds: float) -> float:
    """WPM penalized by one word per error minute."""
    if elapsed_seconds <= 0:
        return 0.0
    penalty = errors / (elapsed_seconds / 60.0)
    return max(0.0, gross_wpm(correct_chars, elapsed_seconds) - penalty)


def accuracy(correct_chars: int, total_typed: int, floor: float = 100.0) -> float:
    """Accuracy percentage; ``floor`` is returned when nothing is typed."""
    if total_typed <= 0:
        return floor
    return max(0.0, min(100.0, (correct_chars / total_typed) * 100.0))


def grade_for(wpm: float, acc: float) -> Grade:
    """Map performance to a letter grade."""
    if wpm >= 90 and acc >= 98:
        return Grade.S
    if wpm >= 70 and acc >= 95:
        return Grade.A
    if wpm >= 50 and acc >= 92:
        return Grade.B
    if wpm >= 30 and acc >= 85:
        return Grade.C
    return Grade.D


# ---------------------------------------------------------------------------
# Snapshots
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LiveStats:
    """Point-in-time view of an in-progress test."""

    elapsed: float
    gross_wpm: float
    net_wpm: float
    accuracy: float
    correct: int
    incorrect: int
    total_typed: int
    progress: float  # 0..100
    remaining: Optional[float]  # seconds left in timed modes, else None


@dataclass(frozen=True)
class TestResult:
    """Immutable record of one finished test — serialized into history."""

    timestamp: str
    text_id: str
    category: str
    difficulty: str
    mode: str
    duration_seconds: float
    gross_wpm: float
    net_wpm: float
    accuracy: float
    errors: int
    correct_chars: int
    total_chars_typed: int
    text_length: int
    completion: float  # 0..100
    grade: str

    def to_dict(self) -> dict:
        return {
            "date": self.timestamp,
            "text_id": self.text_id,
            "category": self.category,
            "difficulty": self.difficulty,
            "test_mode": self.mode,
            "elapsed_time": round(self.duration_seconds, 1),
            "wpm": round(self.gross_wpm, 1),
            "net_wpm": round(self.net_wpm, 1),
            "accuracy": round(self.accuracy, 1),
            "errors": self.errors,
            "correct_chars": self.correct_chars,
            "total_chars": self.total_chars_typed,
            "text_length": self.text_length,
            "completion": round(self.completion, 1),
            "grade": self.grade,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TestResult":
        """Rebuild from persisted/legacy JSON (legacy rows lack grades)."""
        return cls(
            timestamp=data.get("date", ""),
            text_id=str(data.get("text_id", data.get("text_number", ""))),
            category=data.get("category", "General"),
            difficulty=data.get("difficulty", "medium"),
            mode=data.get("test_mode", MODE_COMPLETE_DEFAULT),
            duration_seconds=float(data.get("elapsed_time", 0.0)),
            gross_wpm=float(data.get("wpm", 0.0)),
            net_wpm=float(data.get("net_wpm", 0.0)),
            accuracy=float(data.get("accuracy", 100.0)),
            errors=int(data.get("errors", 0)),
            correct_chars=int(data.get("correct_chars", data.get("total_chars", 0))),
            total_chars_typed=int(data.get("total_chars", 0)),
            text_length=int(data.get("text_length", 0)),
            completion=float(data.get("completion", 0.0)),
            grade=data.get("grade") or grade_for(
                float(data.get("wpm", 0.0)), float(data.get("accuracy", 100.0))
            ).value,
        )


MODE_COMPLETE_DEFAULT = "Complete Text"


@dataclass(frozen=True)
class Achievement:
    """A milestone unlocked (or tracked) from history."""

    key: str
    title: str
    description: str
    icon: str
    unlocked: bool = False


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class TypingEngine:
    """Deterministic typing-test engine.

    The UI pushes the full typed string in (same diff-approach the legacy
    app used, which also plays nicely with pastes and IMEs), and pulls
    char statuses and stats back out. ``clock`` is injectable for tests.

    Lifecycle::

        engine = TypingEngine("hello", time_limit=60)
        engine.begin()
        engine.update("hel")
        engine.record_mistake("l", "o")   # optional, for error analytics
        stats = engine.stats()
        result = engine.finish(meta=...)   # when done
    """

    def __init__(
        self,
        target: str,
        time_limit: Optional[float] = None,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not target:
            raise ValueError("target text must not be empty")
        if time_limit is not None and time_limit <= 0:
            raise ValueError("time_limit must be positive or None")
        self._target = target
        self._time_limit = time_limit
        self._clock = clock
        self._start: Optional[float] = None
        self._typed: str = ""
        self._statuses: List[CharStatus] = [CharStatus.PENDING] * len(target)
        self.mistakes: Counter = Counter()  # expected char -> times mistyped

    # -- lifecycle -------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._start is not None

    def begin(self) -> None:
        """Start the clock. Idempotent."""
        if self._start is None:
            self._start = self._clock()

    def reset(self) -> None:
        """Clear all input but keep the same target text."""
        self._start = None
        self._typed = ""
        self._statuses = [CharStatus.PENDING] * len(self._target)
        self.mistakes.clear()

    # -- text access ------------------------------------------------------

    @property
    def target(self) -> str:
        return self._target

    @property
    def typed(self) -> str:
        return self._typed

    @property
    def statuses(self) -> List[CharStatus]:
        """Per-character statuses; the next char to type is CURRENT."""
        result = list(self._statuses)
        if len(self._typed) < len(self._target):
            result[len(self._typed)] = CharStatus.CURRENT
        return result

    # -- input ------------------------------------------------------------

    def update(self, typed: str) -> None:
        """Replace the engine's view of user input (clamped to target length)."""
        self._typed = typed[: len(self._target)]
        n = len(self._typed)
        self._statuses = [
            CharStatus.CORRECT
            if self._typed[i] == self._target[i]
            else CharStatus.INCORRECT
            for i in range(n)
        ] + [CharStatus.PENDING] * (len(self._target) - n)

    def record_mistake(self, expected: str, typed: str) -> None:
        """Track that ``typed`` was pressed where ``expected`` belonged."""
        if expected:
            self.mistakes[expected] += 1

    # -- timing -----------------------------------------------------------

    def elapsed(self) -> float:
        if self._start is None:
            return 0.0
        raw = self._clock() - self._start
        if self._time_limit is not None:
            return min(raw, self._time_limit)
        return raw

    def remaining(self) -> Optional[float]:
        if self._time_limit is None or self._start is None:
            return self._time_limit
        return max(0.0, self._time_limit - (self._clock() - self._start))

    # -- stats ------------------------------------------------------------

    def stats(self) -> LiveStats:
        correct = sum(1 for s in self._statuses if s is CharStatus.CORRECT)
        incorrect = sum(1 for s in self._statuses if s is CharStatus.INCORRECT)
        typed = len(self._typed)
        elapsed = self.elapsed()
        return LiveStats(
            elapsed=elapsed,
            gross_wpm=gross_wpm(correct, elapsed),
            net_wpm=net_wpm(correct, incorrect, elapsed),
            accuracy=accuracy(correct, incorrect + correct) if typed else 100.0,
            correct=correct,
            incorrect=incorrect,
            total_typed=typed,
            progress=min(100.0, (typed / len(self._target)) * 100.0),
            remaining=self.remaining(),
        )

    def is_finished(self) -> bool:
        """Complete mode: perfect full transcription. Timed: clock expired."""
        if self._start is None:
            return False
        if self._time_limit is None:
            return self._typed == self._target
        return self.remaining() == 0.0 or self._typed == self._target

    def finish(self, *, text_id: str, category: str, difficulty: str,
               mode: str, timestamp: str) -> TestResult:
        """Freeze current stats into a :class:`TestResult`."""
        s = self.stats()
        g = grade_for(s.gross_wpm, s.accuracy)
        return TestResult(
            timestamp=timestamp,
            text_id=text_id,
            category=category,
            difficulty=difficulty,
            mode=mode,
            duration_seconds=s.elapsed,
            gross_wpm=s.gross_wpm,
            net_wpm=s.net_wpm,
            accuracy=s.accuracy,
            errors=s.incorrect,
            correct_chars=s.correct,
            total_chars_typed=s.total_typed,
            text_length=len(self._target),
            completion=s.progress,
            grade=g.value,
        )


# ---------------------------------------------------------------------------
# Achievements (pure — evaluated against a list of persisted result dicts)
# ---------------------------------------------------------------------------


def evaluate_achievements(history: List[dict],
                          total_chars: int,
                          unlocked_keys: Dict[str, str],
                          ) -> List[Achievement]:
    """Compute the full achievement list with unlock flags.

    ``history`` is a list of result dicts (as produced by
    :meth:`TestResult.to_dict`), ``total_chars`` the lifetime character
    count, and ``unlocked_keys`` maps already-unlocked achievement keys to
    ISO timestamps (persisted so unlocks never regress).
    """
    def seen(key: str) -> bool:
        return key in unlocked_keys

    wpms = [h.get("wpm", 0.0) for h in history]
    accs = [h.get("accuracy", 0.0) for h in history]
    completions = [h.get("completion", 0.0) for h in history]
    n = len(history)

    # streak of 5 consecutive tests at >=95% accuracy
    streak = 0
    best_streak = 0
    for a in accs:
        streak = streak + 1 if a >= 95.0 else 0
        best_streak = max(best_streak, streak)

    defs = [
        ("first_test", "First Steps", "Complete your very first test", "🎯",
         n >= 1),
        ("ten_tests", "Getting Serious", "Finish 10 tests", "🔟", n >= 10),
        ("fifty_tests", "Dedicated", "Finish 50 tests", "🏅", n >= 50),
        ("wpm_40", "Cruising", "Reach 40 WPM", "🚗", any(w >= 40 for w in wpms)),
        ("wpm_60", "Fast Hands", "Reach 60 WPM", "⚡", any(w >= 60 for w in wpms)),
        ("wpm_80", "Speed Demon", "Reach 80 WPM", "🔥", any(w >= 80 for w in wpms)),
        ("wpm_100", "Century Club", "Reach 100 WPM", "🚀", any(w >= 100 for w in wpms)),
        ("sharp", "Sharpshooter", "98%+ accuracy on a test", "🎯",
         any(a >= 98.0 and c >= 50.0 for a, c in zip(accs, completions))),
        ("flawless", "Flawless Victory", "100% accuracy, full completion", "💎",
         any(a >= 100.0 and c >= 100.0 for a, c in zip(accs, completions))),
        ("consistent", "Metronome", "5 tests in a row at 95%+ accuracy", "🎵",
         best_streak >= 5),
        ("marathon", "Marathoner", "Type 50,000 characters lifetime", "🏃",
         total_chars >= 50_000),
        ("scholar", "Bookworm", "Type 250,000 characters lifetime", "📚",
         total_chars >= 250_000),
    ]
    return [
        Achievement(key=k, title=t, description=d, icon=i,
                    unlocked=seen(k) or flag)
        for k, t, d, i, flag in defs
    ]
