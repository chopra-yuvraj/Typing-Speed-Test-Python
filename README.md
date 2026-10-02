# Advanced Typing Speed Test

[![CI](https://github.com/chopra-yuvraj/Typing-Speed-Test-Python/actions/workflows/python-package.yml/badge.svg)](https://github.com/chopra-yuvraj/Typing-Speed-Test-Python/actions/workflows/python-package.yml)
[![Release](https://img.shields.io/github/v/release/chopra-yuvraj/Typing-Speed-Test-Python?style=for-the-badge&logo=github)](https://github.com/chopra-yuvraj/Typing-Speed-Test-Python/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Tests](https://img.shields.io/badge/tests-64%20passing-brightgreen?style=for-the-badge)](tests/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/mit/)

A production-grade typing practice suite built with **pure Python + Tkinter** —
no runtime dependencies, fully tested core logic, and a growing feature set
I use to compete with my friends on typing speed.

---

## Why Advanced Typing Speed Test?

As a B.Tech CSE student at VIT and a B.S Data Science student at IIT Madras,
I spend countless hours typing code, reports, and assignments.
Also, my friends and I compete with each other in our typing speeds.

## Key Features

### Practice
- **49 curated passages** across 14 categories — technology, science, history, literature, business, health, travel, environment and more
- **Difficulty levels** — beginner-friendly *easy*, standard *medium*, and symbol/number-packed *hard*
- **Code mode** — practice real Python, JavaScript, SQL and HTML snippets with indentation and symbols
- **Custom texts** — paste any text and practice on it instantly
- **Flexible modes** — complete the full text, or timed sprints of 60s / 120s / 300s
- **Auto-start** — just start typing, the test begins on your first keystroke

### Feedback while you type
- **Live stats cards** — WPM, accuracy, progress, errors and countdown
- **Live WPM sparkline** — watch your speed evolve in real time
- **Per-character highlighting** — correct / incorrect / current-position colouring
- **Sound feedback** — subtle keystroke clicks, error thuds and a completion jingle (toggleable)

### Analytics & progression
- **Statistics dashboard** — lifetime WPM trend chart, per-category averages, error-prone-key analysis
- **Achievements** — 12 unlockable badges, from *First Steps* to the *Century Club*
- **Grades** (S/A/B/C/D) with a shareable, copy-to-clipboard result summary
- **Personal-best detection** with celebration fanfare
- **Typed history** — every test persisted with atomic writes and automatic corruption recovery
- **Export** — JSON or CSV, for your own analysis

### Production-grade engineering
- **Theming** — hand-tuned dark & light palettes, switchable at runtime (persists across restarts)
- **Modular package layout** — GUI-free core, dependency-injected services, reusable canvas widgets
- **64 unit tests** covering metrics, the typing engine, storage and the text bank
- **Safe persistence** — atomic JSON writes, schema versioning, legacy v1 data auto-import
- **CI** — flake8 lint + test matrix (Python 3.9–3.11) via GitHub Actions
- **Structured logging** with a `--debug` flag

---

## Getting started

### Option A — Download the Windows app (no Python needed)

Grab **`TypingSpeedTest.exe`** from the
[**latest release**](https://github.com/chopra-yuvraj/Typing-Speed-Test-Python/releases/latest) —
it is built automatically by GitHub Actions on every tagged release.
Optionally verify the download against the attached
`TypingSpeedTest.exe.sha256.txt` checksum, then just double-click to run.

### Option B — Run from source

Prerequisites: **Python 3.9+** ([download](https://python.org/downloads/)) —
Tkinter ships with it, and the app has **zero third-party dependencies**.

```bash
git clone https://github.com/chopra-yuvraj/Typing-Speed-Test-Python.git
cd Typing-Speed-Test-Python

python typing_speed_test.py     # classic entry point
python -m typingtest            # package entry point
```

Or install it as a real package:

```bash
pip install .
typing-speed-test               # console command
```

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| *any key* | auto-starts the test |
| `Ctrl`+`Enter` | start / stop |
| `Ctrl`+`N` | new text |
| `Esc` | restart current text |
| `Ctrl`+`D` | open dashboard |
| `Ctrl`+`T` | toggle dark / light theme |
| `Ctrl`+`E` | export results (JSON) |

### Test modes

| Mode | Description | Best for |
|------|-------------|----------|
| **Complete Text** | Type the entire passage | accuracy & completion practice |
| **60 seconds** | Type as much as possible in 1 minute | speed bursts |
| **120 seconds** | 2-minute challenge | sustained performance |
| **300 seconds** | 5-minute endurance | long-form typing practice |

---

## Project structure

```
├── typing_speed_test.py      # backward-compatible launcher
├── pyproject.toml            # packaging metadata + tool config
├── typingtest/               # the application package
│   ├── app.py                # CLI bootstrap + logging
│   ├── settings_bootstrap.py # service wiring + legacy migration
│   ├── config.py             # modes, defaults, data paths
│   ├── core.py               # metrics, engine, grades, achievements (GUI-free)
│   ├── textbank.py           # passage loading, filtering, custom texts
│   ├── storage.py            # atomic JSON history/settings persistence
│   ├── sound.py              # audio feedback (winsound / bell fallback)
│   ├── themes.py             # dark & light palettes
│   ├── widgets.py            # StatCard, Sparkline, LineChart, BarChart
│   ├── main_window.py        # main UI
│   ├── results.py            # post-test results dialog
│   ├── dashboard.py          # statistics dashboard
│   ├── custom_text.py        # add-your-own-text dialog
│   └── data/texts.json       # 49 practice passages
└── tests/                    # 64 unit tests (stdlib unittest, pytest-compatible)
```

Your data lives in a per-user directory (`%LOCALAPPDATA%\TypingSpeedTest` on
Windows, `~/.local/share/typing-speed-test` on Linux) — history, settings,
unlocked achievements, mistake statistics and custom texts.

## Run the tests

```bash
python -m unittest discover -s tests    # no dependencies
pytest                                  # if you have it
```

---

## Roadmap

- [x] Dark / light themes
- [x] Difficulty levels
- [x] Audio feedback for errors and completion
- [x] Statistics dashboard with charts
- [x] Achievements & personal bests
- [x] Code-snippet practice mode
- [x] Auto-built Windows `.exe` release pipeline
- [ ] Multi-language passages
- [ ] Online score sharing / friend comparisons
- [ ] Mobile version

## Releasing a new version (maintainers)

Everything is automated — a tag push produces a GitHub Release with a
ready-to-run Windows executable:

```bash
# 1. bump __version__ in typingtest/__init__.py and update CHANGELOG.md
git add -A && git commit -m "Release v2.0.0"
git push

# 2. tag it — this kicks off the release build
git tag v2.0.0
git push origin v2.0.0
```

The [release workflow](.github/workflows/release.yml) then:
1. ✅ re-runs lint + the full test matrix,
2. ✅ verifies the tag matches `__version__` (fails the build on mismatch),
3. 🛠️ builds `TypingSpeedTest.exe` with PyInstaller on a Windows runner
   and smoke-tests that it launches,
4. 🔐 attaches a SHA-256 checksum,
5. 📦 publishes the GitHub Release with auto-generated notes
   (`vX.Y.Z-beta`-style tags become pre-releases automatically).

To build the executable locally:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name TypingSpeedTest ^
    --add-data "typingtest/data;typingtest/data" typing_speed_test.py
# → dist/TypingSpeedTest.exe
```

## GitHub features enabled

- 🤖 **CI** — lint + tests on Ubuntu across Python 3.9–3.13 (`.github/workflows/python-package.yml`)
- 📦 **Release automation** — tag → tested → compiled `.exe` → published release (`.github/workflows/release.yml`)
- 🔍 **CodeQL** — weekly + per-PR static security analysis of the Python code
- 🤖 **Dependabot** — weekly dependency & GitHub Actions updates
- 🐛 **Issue forms** — structured bug reports & feature requests (`.github/ISSUE_TEMPLATE/`)
- 🔀 **PR template & CODEOWNERS** — consistent, reviewed contributions
- 📜 **Changelog, Contributing guide & Code of Conduct**

---

## License

Licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

## Acknowledgments

- **My professors at VIT Vellore** for emphasizing practical software development
- **IIT Madras faculty** for inspiring interdisciplinary learning approaches
- **My classmates** who tested early versions and provided valuable feedback
- **The Python community** for creating such accessible and powerful tools

---

## About the Developer

**Yuvraj Chopra**
B.Tech Computer Science Engineering — VIT Vellore
B.S. Data Science — IIT Madras
Vellore, Tamil Nadu, India

*Passionate about building simple, effective solutions to everyday problems.
Currently exploring the intersection of software engineering and data science.*

### Connect with me

[![GitHub](https://img.shields.io/badge/GitHub-chopra--yuvraj-181717?style=for-the-badge&logo=github)](https://github.com/chopra-yuvraj)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-chopra--yuvraj-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/chopra-yuvraj)
[![Email](https://img.shields.io/badge/Email-yuvrajchopra19%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:yuvrajchopra19@gmail.com)

---

<div align="center">

**Made with ❤️ and ☕ by Yuvraj Chopra**

[ **View on GitHub**](https://github.com/chopra-yuvraj/Typing-Speed-Test-Python)

</div>
