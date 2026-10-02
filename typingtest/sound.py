"""Optional audio feedback.

Design goals
------------
* **Zero dependencies** — uses ``winsound.Beep`` on Windows and the Tk
  bell elsewhere (or nothing at all if unavailable).
* **Never blocks the UI** — every cue is rendered on a short-lived daemon
  thread; repeated keystroke clicks collapse into one pending click so
  fast typists don't spawn a thread per key.
* **Never crashes the app** — every backend failure is logged and muted.
"""
from __future__ import annotations

import logging
import sys
import threading
from typing import Callable, Optional, Sequence, Tuple

log = logging.getLogger(__name__)

try:
    import winsound  # type: ignore
    _HAVE_WINSOUND = True
except ImportError:  # non-Windows
    _HAVE_WINSOUND = False

Tone = Tuple[int, int]  # (frequency Hz, duration ms)


class SoundManager:
    """Plays short feedback cues; safe no-op when audio is unavailable."""

    def __init__(self, enabled: bool = True,
                 bell: Optional[Callable[[], None]] = None) -> None:
        #: ``bell`` lets the UI pass ``widget.bell`` as a fallback backend.
        self._enabled = enabled
        self._bell = bell
        self._click_pending = threading.Lock()
        self._click_busy = False

    # -- configuration ----------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    # -- public cues ------------------------------------------------------

    def click(self) -> None:
        """Subtle keystroke tick (coalesced: one in-flight max)."""
        if not (self._enabled and _HAVE_WINSOUND):
            return
        with self._click_pending:
            if self._click_busy:
                return
            self._click_busy = True

        def _play() -> None:
            try:
                winsound.Beep(2400, 12)
            except Exception as exc:  # pragma: no cover - hardware failure
                log.debug("click failed: %s", exc)
            finally:
                with self._click_pending:
                    self._click_busy = False

        threading.Thread(target=_play, daemon=True).start()

    def error(self) -> None:
        """Low thud on an incorrect key."""
        self._play([(300, 60)])

    def success(self) -> None:
        """Little ascending jingle when a test finishes."""
        self._play([(523, 90), (659, 90), (784, 130)])

    def new_personal_best(self) -> None:
        """Fanfare for a personal record."""
        self._play([(523, 80), (659, 80), (784, 80), (1047, 180)])

    # -- internals --------------------------------------------------------

    def _play(self, tones: Sequence[Tone]) -> None:
        if not self._enabled:
            return
        if _HAVE_WINSOUND:
            self._play_async(tones)
        elif self._bell is not None:
            try:
                self._bell()
            except Exception as exc:  # pragma: no cover - tk failure
                log.debug("bell failed: %s", exc)

    def _play_async(self, tones: Sequence[Tone]) -> None:
        def _run() -> None:
            for freq, dur in tones:
                try:
                    winsound.Beep(freq, dur)
                except Exception as exc:  # pragma: no cover
                    log.debug("beep failed: %s", exc)
                    return

        threading.Thread(target=_run, daemon=True).start()


def system_beep_supported() -> bool:
    """Whether real frequency-controlled beeps exist on this platform."""
    return sys.platform == "win32" and _HAVE_WINSOUND
