# Changelog

All notable changes to Icon Manager Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
