# Icon Manager Module

**v0.3.0 2026-02-01**

A cross-platform icon management module for PyQt6 applications. This project provides a centralized, reliable solution for handling application icons consistently across Windows, macOS, and Linux.

## The Problem

Application icon behavior in Qt is notoriously inconsistent across platforms. There is no single "app icon" — instead, multiple consumers (taskbar, title bar, system tray, Alt-Tab switcher, About dialog) each have different requirements, formats, and caching rules. Each operating system handles these consumers differently, and Qt only partially abstracts these differences, leading to silent failures and missing icons.

This module serves as the **single source of truth** for all icons in a PyQt6 application, solving these cross-platform issues with a unified API.

## Features

- Unified icon loading API for all parts of an application
- Automatic OS-specific format selection (`.ico`, `.icns`, `.png`)
- Qt Resource System support (`:/icons/...`)
- Multi-resolution icon handling
- Absolute path resolution for packaged apps (PyInstaller, cx_Freeze)
- Graceful fallback behavior with debug warnings
- Theme icon support with fallbacks (Linux desktop integration)

## Usage

```python
from icon_loader import icons
from PyQt6.QtWidgets import QApplication

app = QApplication([])
app.setWindowIcon(icons.app_icon())
```

### Window title bar

```python
window.setWindowIcon(icons.app_icon())
```

### System tray

```python
tray = QSystemTrayIcon()
tray.setIcon(icons.app_icon())
tray.show()
```

### Toolbar and menu actions

```python
open_action = QAction(icons.load("open.png"), "Open", parent)
```

### Theme icons with fallback

```python
save_action = QAction(icons.theme("document-save", "save.png"), "Save", parent)
```

## API Overview

### `IconLoader(base_path=None)`

Creates an icon loader instance. If no `base_path` is provided, defaults to `<project_root>/resources/icons`.

| Method | Description |
|--------|-------------|
| `app_icon()` | Returns the platform-appropriate application icon (`.ico` on Windows, `.icns` on macOS, `.png` on Linux) |
| `load(filename)` | Loads an icon from disk or Qt resources |
| `theme(name, fallback)` | Loads a system theme icon with a guaranteed fallback |
| `ensure_valid(icon, context)` | Debug helper that warns when an icon is null |

A convenience global instance is available:

```python
from icon_loader import icons
```

## Platform Requirements

| Platform | Format | Recommended Sizes | Notes |
|----------|--------|-------------------|-------|
| Windows | `.ico` | 16, 32, 48, 256 px | Embed in executable; set `AppUserModelID` for taskbar |
| macOS | `.icns` | 128, 256, 512 px | Bundle in `.app`; support dark mode templates |
| Linux | `.png` / `.svg` | 16–256 px | Desktop file integration; theme icon fallback |

## Demo

A visual demo exercises every API method in a single window:

```bash
python demo_icon_loader.py             # GUI window
python demo_icon_loader.py --headless  # text-only summary (for CI)
```

The GUI shows the app icon at 64px, a gallery of all sized PNGs at native resolution, missing-file and Qt resource path behavior, theme icon fallback, and `ensure_valid()` results. A console panel at the bottom captures all `[IconLoader]` warning output.

> **Note (Windows):** The demo sets a per-window `AppUserModelID` via COM `IPropertyStore` so the taskbar displays the app icon instead of the generic Python icon. This is required when running under the Microsoft Store Python alias.

## Project Structure

```
Icon_Manager_Module/
├── .gitattributes                           # Line ending normalization rules
├── .gitignore                               # Ignored files (bytecode, build artifacts)
├── README.md
├── CHANGELOG.md
├── icon_loader.py                           # Cross-platform icon loader module
├── demo_icon_loader.py                      # Visual demo of every API method
├── generate_icons.py                        # ImageMagick icon asset generator
├── PLAN_Qt-Icon-Manaager-Module.md          # Module blueprint and implementation spec
├── Application_Icons_in_PyQt6_Per_Bing.md   # Best practices reference
├── Guide_to_Qt_Icon_Documentation.md        # Curated Qt documentation links
├── tests/                                   # Test suite
│   ├── test_icon_loader.py                  # 17 pytest tests for icon_loader
│   └── demo_results.txt                     # Headless demo output
└── notes/                                   # Research from multiple sources
    ├── ...-per-ChatGPT.md
    ├── ...-per-Claude.md
    ├── ...-per-Gemini.md
    ├── ...-per-OCzen.md                     # Most comprehensive reference
    └── ...-per-Qwen.md
```

## Documentation

The `notes/` directory contains consolidated research on PyQt6 icon behavior from multiple sources, covering:

- **Icon consumer model** — understanding which OS component owns each icon surface
- **Platform-specific rules** — format, timing, and API differences per OS
- **Windows taskbar fix** — using `ctypes` to set `AppUserModelID`
- **Qt Resource System** — bundling icons via `.qrc` files
- **Packaging** — PyInstaller and cx_Freeze icon configuration
- **Testing methodology** — visual and automated validation across platforms and DPI scales

## Status

v0.3.0 — Icon loader module, test suite (17 pytest tests), and demo application are complete. Icon generation pipeline is in place. The demo includes a Win32 taskbar icon fix for Microsoft Store Python.

## Requirements

- Python 3.x
- PyQt6

## License

See project files for license details.
