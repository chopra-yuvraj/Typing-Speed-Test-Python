"""Allows ``python -m typingtest`` to launch the application."""
import sys

from typingtest.app import main

if __name__ == "__main__":
    sys.exit(main())
