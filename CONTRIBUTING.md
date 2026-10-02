# Contributing

Thanks for your interest in improving the Typing Speed Test!

## Development setup

```bash
git clone https://github.com/chopra-yuvraj/Typing-Speed-Test-Python.git
cd Typing-Speed-Test-Python
pip install -r requirements-dev.txt   # just pytest + flake8
```

Run the app:

```bash
python -m typingtest            # or: python typing_speed_test.py
python -m typingtest --debug    # verbose logging
```

Run the tests:

```bash
python -m pytest          # or: python -m unittest discover -s tests
```

## Project layout

| Path | Responsibility |
|------|----------------|
| `typingtest/core.py` | Metrics, engine, grades, achievements — **no GUI imports** |
| `typingtest/storage.py` | Atomic JSON persistence, history, settings |
| `typingtest/textbank.py` | Passage loading & custom texts |
| `typingtest/sound.py` | Audio feedback |
| `typingtest/themes.py` / `widgets.py` | Palettes & reusable UI widgets |
| `typingtest/main_window.py` … | UI layer |
| `typingtest/data/texts.json` | Bundled passages |
| `tests/` | Unit tests (GUI-free) |

## Ground rules

- Keep `core.py`, `storage.py` and `textbank.py` free of `tkinter` imports —
  they must stay unit-testable headlessly (CI enforces this).
- Add tests for anything in those modules.
- Keep the runtime dependency-free (standard library only).
- Max line length 100; `flake8` must report no `E9,F63,F7,F82` errors.
- Small, focused pull requests are easier to review than big ones.

## Releasing (maintainers)

1. Bump `__version__` in `typingtest/__init__.py` and update `CHANGELOG.md`.
2. `git tag vX.Y.Z && git push origin vX.Y.Z`
3. The Release workflow builds the Windows `.exe` and publishes the GitHub
   Release automatically (it fails if tag ≠ `__version__`).
