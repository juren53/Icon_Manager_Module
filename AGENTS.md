# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Icon Manager Module is a **cross-platform icon management module for PyQt6 applications**. The core problem it solves: application icon behavior in Qt is notoriously inconsistent across platforms. There is no single "app icon" — instead, multiple consumers (taskbar, title bar, system tray, Alt-Tab switcher, About dialog) each have different requirements, formats, and caching rules. This module serves as the **single source of truth** for all icons in a PyQt6 application.

**Current version:** v0.3.1 (2026-02-01)

## Core Architecture

### Three-file system
The module consists of three standalone components that work together:

1. **`icon_loader.py`** — The runtime icon loader module
   - `IconLoader` class with platform-aware icon selection
   - Module-level convenience instance: `icons = IconLoader()`
   - Windows-specific taskbar icon fix via COM/ctypes (Win32 `AppUserModelID` + `WM_SETICON`)
   - Key methods: `app_icon()`, `load(filename)`, `theme(name, fallback)`, `set_taskbar_icon(window, app_id)`, `ensure_valid(icon, context)`
   - Auto-selects `.ico` (Windows), `.icns` (macOS), or multi-resolution PNGs (Linux)
   - Graceful fallback chain: native format → sized PNGs (`app_NxN.png`) → `app.png` → null icon with warning

2. **`generate_icons.py`** — ImageMagick-driven asset generation pipeline
   - Converts a single high-resolution source image into all platform-specific formats
   - Outputs: multi-resolution `.ico` (Windows), `.icns` (macOS via `iconutil` or ImageMagick fallback), individual PNGs (16-256px), and `app.png` (Linux default)
   - Auto-detects ImageMagick v6/v7 (`convert` vs `magick` command)

3. **`demo_icon_loader.py`** — Visual demo application
   - Exercises every `IconLoader` API method in a PyQt6 GUI
   - Shows app icon, icon gallery (all sized PNGs), missing file behavior, Qt resource paths, theme icons, and `ensure_valid()` results
   - Includes console panel capturing all `[IconLoader]` warning output
   - Supports `--headless` mode for CI-friendly text output
   - Demonstrates Windows taskbar icon fix via `set_taskbar_icon()`

### Platform-specific behavior

**Windows:** Uses `app.ico` (multi-resolution). Taskbar icon requires Win32 COM manipulation (`IPropertyStore` + `WM_SETICON`) to override the default Python icon when running under Microsoft Store Python alias. This fix is built into `IconLoader.set_taskbar_icon()` and also runs at module import via `_init_win32()`.

**macOS:** Uses `app.icns`. Requires `iconutil` (macOS-only) for proper `.icns` generation. Cross-platform fallback uses ImageMagick but may produce invalid files.

**Linux:** Uses multi-resolution PNGs (`app_16x16.png`, `app_32x32.png`, etc.) loaded via `_load_multi_res_png()`. Falls back to `app.png` (256x256). Supports freedesktop theme icons via `QIcon.fromTheme()` with guaranteed fallback.

### Design patterns

- **Single source of truth:** All icon loading goes through `IconLoader`, never direct `QIcon()` calls with hardcoded paths
- **Absolute path resolution:** `icon_loader.py` resolves paths relative to its own location to avoid silent failures in packaged apps (PyInstaller, cx_Freeze)
- **Graceful degradation:** Missing icons return null `QIcon()` with console warnings, never crash
- **Platform abstraction:** Caller uses `icons.app_icon()` and the loader selects the right format internally
- **Qt Resource System support:** Paths starting with `:/` bypass file existence checks and pass directly to `QIcon()`

## Development Commands

### Running tests
```powershell
python -m pytest tests\test_icon_loader.py -v
```
The test suite contains 20 pytest tests covering all `IconLoader` methods, including platform-specific behavior, fallback chains, warning messages, and the Windows taskbar icon API.

### Running the demo
```powershell
# GUI mode (shows visual demo window)
python demo_icon_loader.py

# Headless mode (text-only output for CI)
python demo_icon_loader.py --headless
```

### Generating icons
```powershell
# Generate all icon files from a source image
python generate_icons.py path\to\source_image.png

# Custom output directory
python generate_icons.py path\to\source_image.png --output-dir custom\path
```
**Requirements:** ImageMagick v6 or v7 must be installed and on PATH. On macOS, `iconutil` is used for `.icns` generation; on other platforms ImageMagick generates it (may not produce valid files).

## Version Conventions (CRITICAL)

**Timezone:** ALL timestamps, dates, and times in this project MUST use **Central Time USA (CST/CDT)**, NEVER UTC or any other timezone. This applies to:
- Changelog entries
- Version labels
- Git commit messages
- Documentation timestamps

**Formats:**
- Changelog: `Tue 03 Dec 2025 09:20:00 PM CST`
- Version label: `v0.0.9b 2025-12-03`
- Always include timezone indicator (CST or CDT) in full timestamps

**Version numbering:**
- Format: `v0.0.X` for releases
- Format: `v0.0.Xa`, `v0.0.Xb`, `v0.0.Xc` for point releases/patches
- Update version info in README.md, UI labels, About dialogs, and header comments when making releases
- Version info consists of: Version Number + Date + Time (in CST/CDT)

## Python Environment

**Preferred Python instance:** `C:\Users\jimur\AppData\Local\Microsoft\WindowsApps\python.exe`
- This instance has PyQt6 and other required dependencies installed
- Use this path when suggesting Python commands or debugging environment issues

## Integration Workflow

When helping users integrate this module into their PyQt6 applications, follow the procedure in **`PROCEDURE_IMM-integration.md`**. Key steps:

1. **Audit existing icon assets** — check for pre-existing icon directories
2. **Generate icon assets** — run `generate_icons.py` on source image
3. **Resolve layout conflicts** — decide whether to migrate to `resources/icons/` or reuse existing directory
4. **Code changes** — typically 5 lines across 2 files: `from icon_loader import icons`, `app.setWindowIcon(icons.app_icon())`, `window.setWindowIcon(icons.app_icon())`, `window.show()`, `icons.set_taskbar_icon(window)`
5. **Update packaging** — add `resources/icons/` to PyInstaller/cx_Freeze data files
6. **Update platform launchers** — modify `.desktop` (Linux) or `Info.plist` (macOS) to reference new icon paths
7. **Manual verification** — test on target platforms

The first real integration was into [MDviewer](https://github.com/juren53/MDviewer) and worked on first attempt (see CHANGELOG v0.3.1 for lessons learned).

## Testing Methodology

- **Unit tests:** 20 pytest tests in `tests/test_icon_loader.py` using temporary icon directories and minimal valid PNG fixtures
- **Visual demo:** `demo_icon_loader.py` exercises every API method with real UI and captures console output
- **Headless demo:** Same demo logic, text-only output for CI/automated validation
- **Platform-specific testing:** Tests verify fallback behavior across Windows/macOS/Linux using `sys.platform` monkeypatching

When adding tests for new features, follow the existing pattern: use `tmp_path` fixtures, minimal PNG fixtures (embedded as bytes), `capsys` for output verification, and `monkeypatch` for platform mocking.

## Known Issues and Gotchas

- **Windows taskbar icon:** The icon won't appear on the taskbar when running under Microsoft Store Python alias unless `set_taskbar_icon()` is called AFTER `window.show()`. This is a Windows-specific quirk, not a Qt bug.
- **macOS .icns generation:** Only works properly on macOS via `iconutil`. Cross-platform builds must generate `.icns` on a Mac or accept that the fallback file may not work.
- **Qt Resource System paths:** Paths starting with `:/` bypass all file existence checks. The loader assumes these are valid and passes them directly to `QIcon()`.
- **Multi-resolution PNG loading:** The loader scans for `app_*x*.png` files using glob patterns. File naming MUST match this pattern (`app_16x16.png`, `app_32x32.png`, etc.) or icons won't be found.

## Documentation Structure

- **README.md** — User-facing project overview, API reference, usage examples
- **CHANGELOG.md** — Version history following Keep a Changelog format
- **PLAN_Qt-Icon-Manaager-Module.md** — Original module blueprint and implementation spec
- **PROCEDURE_IMM-integration.md** — Step-by-step integration guide for users
- **Application_Icons_in_PyQt6_Per_Bing.md** — Cross-platform icon best practices reference
- **Guide_to_Qt_Icon_Documentation.md** — Curated Qt documentation links
- **notes/** — Research from multiple AI sources on PyQt6 icon behavior (most comprehensive: `notes/Application_Icon_Behavior_in_Python_PyQt6_apps-per-OCzen.md`)
- **SESSION_SUMMARY_2026-02-01.md** — Integration procedure development and MDviewer deployment notes

## Code Style and Patterns

- **Import order:** `from __future__ import annotations` at top, then stdlib, then PyQt6
- **Type hints:** Use where beneficial but not dogmatic (this is a single-file module, not a library)
- **Error handling:** Graceful degradation with console warnings, never crashes
- **Platform detection:** Use `sys.platform.startswith("win")`, `sys.platform == "darwin"`, else assume Linux
- **Pathlib usage:** All file paths use `pathlib.Path`, not string manipulation
- **Console output:** All warnings use consistent `[IconLoader]` prefix for greppability

## When making changes

- Update version number and timestamp in README.md (CST/CDT)
- Add entry to CHANGELOG.md with CST/CDT timestamp
- Run full test suite: `python -m pytest tests\test_icon_loader.py -v`
- Run demo in both GUI and headless modes to verify visual behavior
- Update PROCEDURE_IMM-integration.md if integration steps change
- Test on Windows at minimum (cross-platform testing on macOS/Linux is ideal but not always feasible)
