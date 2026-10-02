"""Application bootstrap: logging, services, legacy migration, mainloop."""
from __future__ import annotations

import argparse
import logging
import sys
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Sequence

from typingtest import __app_name__, __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="typing-speed-test",
        description=f"{__app_name__} — improve your typing speed.")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--debug", action="store_true",
                        help="enable verbose debug logging")
    return parser


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point used by the console script, ``python -m``, and the
    legacy ``typing_speed_test.py`` launcher."""
    args = build_parser().parse_args(argv)
    configure_logging(args.debug)
    log = logging.getLogger("typingtest")

    # Local imports: keep module import cheap & GUI-free for testing.
    from typingtest.main_window import MainWindow
    from typingtest.settings_bootstrap import build_services

    root = tk.Tk()
    try:
        services = build_services(root)
    except Exception as exc:  # data dir issues, missing texts.json, ...
        log.exception("Startup failed")
        messagebox.showerror(f"{__app_name__} — startup error", str(exc))
        return 2

    MainWindow(root, **services)
    log.debug("Services ready: %s", {k: type(v).__name__
                                     for k, v in services.items()})
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
