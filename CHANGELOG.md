# Changelog

All notable changes to Icon Manager Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Third integration: JSM (JAUs-Systems)
- Successfully integrated into [JSM](https://github.com/juren53/JAUs-Systems) (JAUs Systems Manager, PyQt6)
- Discovered that `gtk-update-icon-cache` fails on `~/.local/share/icons/hicolor/` unless
  `index.theme` is present — copy it first from `/usr/share/icons/hicolor/index.theme`
  before running the cache update command (not covered in v0.3.2 procedure)
- Confirmed that the installed `.desktop` file (`~/.local/share/applications/`) must be
  manually updated when redeploying; updating the project-level `jsm.desktop` alone is
  not sufficient

---

## [0.3.4] - 2026-02-07

### Fixed
- **`console=False` crash** — `icon_loader.py` now redirects `sys.stdout` and `sys.stderr` to `os.devnull` when they are `None` (PyInstaller `console=False` on Windows sets them to `None`, causing `'NoneType' object has no attribute 'write'` on any `print()` call)
  - Bug found during HPM (HSTL Photo Metadata Framework) compiled build: the 5 `[IconLoader] WARNING:` print statements could crash the application if any warning path was triggered

### Changed
- **Integration procedure** — added PyInstaller warning to Step 4 about custom `base_path` bypassing frozen-environment detection; callers must use `sys._MEIPASS` explicitly when passing a custom path
- **Lessons learned** — added HPM integration section documenting custom `base_path` frozen path resolution and `console=False` stdout issues

### Second integration: HPM
- Successfully integrated into [HPM](https://github.com/juren53/HST-Metadata) (HSTL Photo Metadata Framework)
- Icons generated from `ICON_HSTL.png` into project's `icons/` directory (non-default location)
- Discovered that custom `base_path` requires caller-side `sys._MEIPASS` handling for frozen builds
- Discovered that `console=False` + `print()` = crash — fixed in `icon_loader.py` itself
- HSTL icon now displays in window title bar, taskbar, and Alt-Tab on compiled Windows executable

---

## [0.3.3] - 2026-02-05

### Fixed
- **PyInstaller compatibility** — `IconLoader.__init__()` now detects frozen environments (`sys.frozen` / `sys._MEIPASS`) and resolves icon paths from the PyInstaller extraction directory instead of using `__file__`-relative paths, which break in onefile bundles
  - Bug found during SysMon Windows build: icons not displayed when running the `.exe` because `pathlib.Path(__file__).resolve().parent` escapes the `_MEIxxxxx` temp directory

---

## [0.3.2] - 2026-02-02

### Changed
- **Integration procedure** — rewrote Linux `.desktop` guidance (Step 12) to use XDG hicolor icon theme installation instead of fragile absolute paths
  - Step-by-step commands for installing multi-resolution PNGs into `~/.local/share/icons/hicolor/<size>/apps/`
  - `.desktop` `Icon=` now uses theme name only (no path, no extension)
  - Commands for installing `.desktop` file and updating icon/desktop caches
- **Step 5** now includes `setDesktopFileName()` — required for Linux desktop environments to associate running windows with their `.desktop` file
- **Step 13** verification checklist expanded with per-platform sections; Linux now lists all four independent icon display points (title bar, app launcher, taskbar, Alt+Tab)
- **Minimal integration example** updated with `setApplicationName()` and `setDesktopFileName()` calls
- **Lessons learned** — added Linux desktop integration subsection documenting XDG findings from LMDE/Cinnamon deployment

---

## [0.3.1] - 2026-02-01

### Added
- **Integration procedure** (`PROCEDURE_IMM-integration.md`) — step-by-step guide for adding Icon_Manager_Module to an existing PyQt6 codebase
  - 13 steps covering asset generation, code changes, build/packaging, platform launchers, and verification
  - Migrate-vs-reuse guidance for projects with pre-existing icon directories
  - PyInstaller `.spec` and `--add-data` configuration examples
  - Platform launcher updates (`.desktop`, `Info.plist`)
  - Minimal integration code example (QApplication + QMainWindow)
- **Lessons learned** section documenting findings from the first real integration into [MDviewer](https://github.com/juren53/MDviewer)

### First integration: MDviewer
- Successfully integrated into MDviewer (PyQt6 markdown viewer)
- 5 lines of code across 2 files (`main.py`, `viewer/main_window.py`)
- Windows taskbar icon fix worked on first attempt
- Identified gaps in original procedure: pre-existing icon directories, build/packaging config, platform launchers, manual verification requirement

## [0.3.0] - 2026-02-01

### Added
- **Demo application** (`demo_icon_loader.py`) — visual showcase of every IconLoader API method
  - GUI mode: PyQt6 window with grouped sections for `app_icon()`, `load()`, `theme()`, and `ensure_valid()`
  - Icon gallery displaying all `app_NxN.png` files at native resolution
  - Failure cases: missing file (null icon + warning) and Qt resource path (no warning)
  - Console output panel capturing all `[IconLoader]` messages in real-time
  - `--headless` flag for CI-friendly text-only output
- **Demo results** (`tests/demo_results.txt`) — headless output for reference
- **`set_taskbar_icon(window, app_id)`** — new public method on `IconLoader` that applies the Win32 per-window `AppUserModelID` via COM `IPropertyStore` + `WM_SETICON`; silent no-op on non-Windows
- **`_init_win32()`** — module-level helper that sets a process-level `AppUserModelID` at import time on Windows, so any app importing the module gets the taskbar fix automatically
- **3 new tests** for `set_taskbar_icon()` (test suite now 20 tests total)

### Changed
- Moved Win32 taskbar icon fix from `demo_icon_loader.py` into `icon_loader.py` as a reusable API method
- Demo app now calls `icons.set_taskbar_icon(window)` instead of inline Win32 COM code

## [0.2.0] - 2026-02-01

### Added
- **Test suite** (`tests/test_icon_loader.py`) — 17 pytest tests covering the full IconLoader API
  - `__init__`: default and custom base_path resolution
  - `load()`: existing file, missing file warning, Qt resource path bypass, return type
  - `app_icon()`: return type, multi-resolution PNG fallback, empty directory warning, `app.png` fallback
  - `theme()`: return type, fallback for unknown theme names
  - `ensure_valid()`: null icon warning, valid icon silence, identity return
  - Module-level `icons` instance type and default path

## [0.1.1] - 2026-02-01

### Added
- `.gitattributes` for consistent cross-platform line ending handling
- `.gitignore` for Python bytecode and packaging artifacts
- `Project_Rules.md` and `ICON_MDviewer.png`

### Changed
- Updated README project structure to reflect all tracked files

## [0.1.0] - 2026-02-01

### Added
- **Icon Loader Module** (`icon_loader.py`) - Cross-platform icon loading API for PyQt6
  - `IconLoader` class with configurable `base_path` (defaults to `resources/icons`)
  - `app_icon()` — platform-aware application icon selection: `.ico` on Windows, `.icns` on macOS, multi-resolution PNGs on Linux, with automatic cross-platform fallback
  - `load(filename)` — loads icons from disk with absolute path resolution, or from Qt Resource System (`:/` paths)
  - `theme(name, fallback)` — system theme icon support with guaranteed fallback
  - `ensure_valid(icon, context)` — debug helper that warns on null icons
  - Module-level `icons` convenience instance for simple imports
  - Graceful fallback chain: native format → sized PNGs (`app_NxN.png`) → `app.png` → null icon with warning

## [0.0.1] - 2026-02-01 1154 CST

### Added
- **Icon Generation Script** (`generate_icons.py`) - ImageMagick-driven asset pipeline
  - Generates all icon files needed for cross-platform PyQt6 use from a single source image
  - Individual PNGs at 7 standard sizes: 16, 24, 32, 48, 64, 128, 256px
  - Multi-resolution `.ico` for Windows (all 7 sizes embedded)
  - `.icns` for macOS via `iconutil` on macOS or ImageMagick fallback on other platforms
  - Primary `app.png` (256x256) for Linux
  - CLI interface with `--output-dir` option (default: `resources/icons`)
  - ImageMagick v7/v6 auto-detection with clear error messaging
  - Source image validation via `magick identify`
  - File summary with sizes printed on completion
- **Project Documentation**
  - README with module overview, planned API, platform requirements, and usage examples
  - Detailed module blueprint and implementation spec (`PLAN_Qt-Icon-Manaager-Module.md`)
  - Cross-platform icon best practices reference (`Application_Icons_in_PyQt6_Per_Bing.md`)
  - Curated Qt icon documentation links (`Guide_to_Qt_Icon_Documentation.md`)
  - Research notes from multiple AI sources in `notes/` directory

### Technical
- Python 3.x with no dependencies beyond the standard library
- Requires ImageMagick (v6 or v7) installed and on PATH
- Platform-aware `.icns` generation (native `iconutil` on macOS, ImageMagick fallback elsewhere)
- Output directory created automatically via `os.makedirs`
