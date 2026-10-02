# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-10-02

A full production-grade rewrite.

### Added
- Modular `typingtest` package with GUI-free, unit-tested core
  (`core.py`: metrics, typing engine, grades, achievements)
- Dark & light themes with runtime toggle (`Ctrl+T`) and persistence
- Difficulty levels: easy / medium / hard filtering
- Code practice mode: Python, JavaScript, SQL and HTML snippets
- 16 new passages (49 total): easy stories, symbol/number-heavy hard texts, code
- Custom practice texts ("Practice → Practice custom text…")
- Sound feedback: keystroke clicks, error thuds, completion jingle,
  personal-best fanfare (toggleable)
- Live WPM sparkline during tests
- Statistics dashboard (`Ctrl+D`): WPM trend chart, per-category averages,
  error-prone-key analysis, history table, export, clear
- 12 unlockable achievements and personal-best detection
- Result grades (S/A/B/C/D) with copyable share summary
- Auto-start on first keystroke; keyboard shortcuts
  (`Ctrl+Enter`, `Ctrl+N`, `Esc`, `Ctrl+D`, `Ctrl+T`, `Ctrl+E`)
- Persistent settings; per-user data directory
- Atomic JSON storage with corruption recovery, schema versioning and
  automatic import of legacy `advanced_typing_history.json`
- `pyproject.toml` packaging with `typing-speed-test` console script
- CLI flags: `--version`, `--debug`
- 64 unit tests (stdlib `unittest`, pytest-compatible)
- Windows executable built automatically on every tagged release

### Changed
- App data moved to the OS user-data directory
  (`%LOCALAPPDATA%\TypingSpeedTest` on Windows)
- Legacy `typing_speed_test.py` is now a thin launcher for the package

## [1.0.0] - 2025

Initial release: single-file Tkinter app with 33 passages, timed and
complete-text modes, real-time WPM/accuracy/progress, results history
(JSON/CSV export) and per-test result windows.
