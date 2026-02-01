# Procedure: Integrating Icon_Manager_Module into a PyQt6 Application

## Prerequisites

- **Python 3.8+** with **PyQt6** installed (`pip install PyQt6`)
- **ImageMagick** installed and on PATH (for icon generation)
  - Download: <https://imagemagick.org/script/download.php>
- A **high-resolution source image** (256 px or larger, PNG recommended)

---

## Steps

### 1. Generate icon assets

Run `generate_icons.py` against your source image to produce all platform-specific
icon files:

```bash
python generate_icons.py your_logo.png
```

This creates `resources/icons/` containing:

| File | Purpose |
|------|---------|
| `app.ico` | Windows taskbar / window icon |
| `app.icns` | macOS dock icon (macOS only) |
| `app_16x16.png` … `app_256x256.png` | Individual resolution PNGs |
| `app.png` | Default Linux icon (copy of 256 px) |

To specify a different output directory:

```bash
python generate_icons.py your_logo.png --output-dir path/to/icons
```

### 2. Copy files into your project

Place these into your application tree:

```
your_app/
├── icon_loader.py
└── resources/
    └── icons/
        ├── app.ico
        ├── app.icns
        ├── app.png
        ├── app_16x16.png
        ├── app_32x32.png
        ├── ...
        └── (any additional toolbar/menu icons)
```

`icon_loader.py` expects `resources/icons/` to sit next to it by default. If your
layout differs, pass a custom path when constructing the loader (see step 3).

### 3. Import the icon loader

```python
from icon_loader import icons
```

`icons` is a module-level `IconLoader` instance that points to `resources/icons/`
relative to `icon_loader.py`.

If your icons live elsewhere, create your own instance instead:

```python
from icon_loader import IconLoader
icons = IconLoader(base_path=pathlib.Path("path/to/icons"))
```

### 4. Set the application icon

```python
app = QApplication(sys.argv)
app.setWindowIcon(icons.app_icon())
```

`app_icon()` automatically selects `app.ico` on Windows, `app.icns` on macOS, or
multi-resolution PNGs on Linux.

### 5. Set the window icon

```python
window = QMainWindow()
window.setWindowIcon(icons.app_icon())
```

### 6. Fix the Windows taskbar icon

After showing the window, call `set_taskbar_icon()` to force Windows to display
your icon on the taskbar (instead of the default Python icon):

```python
window.show()
icons.set_taskbar_icon(window)
```

This sets a per-window `AppUserModelID` and sends `WM_SETICON` via ctypes. On
non-Windows platforms it is a silent no-op, so the call is safe to leave in
cross-platform code.

To supply a custom AppUserModelID:

```python
icons.set_taskbar_icon(window, app_id="com.yourcompany.yourapp")
```

### 7. Load additional icons

For toolbar, menu, or status-bar icons placed in `resources/icons/`:

```python
save_icon = icons.load("save.png")
open_icon = icons.load("open.png")
```

Qt Resource System paths are also supported:

```python
icon = icons.load(":/icons/save.png")
```

### 8. Use theme icons (Linux)

Load a freedesktop theme icon with a guaranteed local fallback:

```python
icon = icons.theme("document-save", "save.png")
```

On Linux desktops this returns the theme icon; on other platforms (or if the theme
icon is missing) it falls back to `save.png` from the icons directory.

### 9. Debug null icons

Wrap any icon in `ensure_valid()` to print a warning if it resolved to null:

```python
icon = icons.ensure_valid(icons.load("missing.png"), "toolbar save button")
```

Output when the icon is null:

```
[IconLoader] WARNING: Null icon encountered (toolbar save button)
```

### 10. Verify

Run the application on Windows and confirm:

- The window title-bar icon is correct.
- The taskbar icon displays your image (not the generic Python icon).
- On macOS, the dock icon is correct.
- On Linux, the window icon is correct.

---

## Minimal integration example

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from icon_loader import icons


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setWindowIcon(icons.app_icon())


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(icons.app_icon())

    window = MainWindow()
    window.show()

    # Fix Windows taskbar icon (no-op on other platforms)
    icons.set_taskbar_icon(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```
