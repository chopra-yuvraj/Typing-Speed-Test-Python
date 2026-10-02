#!/usr/bin/env python3
"""Backward-compatible launcher for Typing Speed Test.

The application code lives in the :mod:`typingtest` package; this script
exists so existing workflows (``python typing_speed_test.py``) keep working.

Equivalent ways to start the app::

    python typing_speed_test.py
    python -m typingtest
    typing-speed-test            # after ``pip install .``
"""
import sys

from typingtest.app import main

if __name__ == "__main__":
    sys.exit(main())
