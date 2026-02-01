# Procedure: Integrating Icon_Manager_Module into a PyQt6 Application

## Prerequisites

- **Python 3.8+** with **PyQt6** installed (`pip install PyQt6`)
- **ImageMagick** installed and on PATH (for icon generation)
  - Download: <https://imagemagick.org/script/download.php>
- A **high-resolution source image** (256 px or larger, PNG recommended)

---

## Steps

### 1. Audit existing icon assets

Before generating new icons, check whether your project already has icon files
(e.g. `assets/icons/`, `images/`, or similar). Note their location and naming
convention — you will decide in step 2 whether to migrate to the standard
`resources/icons/` layout or point `IconLoader` at your existing directory.

### 2. Generate icon assets

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

### 3. Copy files into your project

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
layout differs, pass a custom path when constructing the loader (see step 4).

**If your project already has an icon directory** (e.g. `assets/icons/`), choose
one of these approaches:

- **Migrate:** Generate icons directly into a new `resources/icons/` directory and
  remove the old icon files once everything works. Update any references (build
  scripts, `.desktop` files, `.spec` files) to point to the new location.
- **Reuse in place:** Generate icons into your existing directory
  (`--output-dir assets/icons`) and point `IconLoader` at it via `base_path=`.
  This avoids duplicate icon directories but means your existing files must coexist
  with the `app.ico` / `app_NxN.png` naming convention.

Avoid leaving icons in two locations long-term — it creates confusion about which
set is authoritative.

### 4. Import the icon loader

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

### 5. Set the application icon

```python
app = QApplication(sys.argv)
app.setWindowIcon(icons.app_icon())
```

`app_icon()` automatically selects `app.ico` on Windows, `app.icns` on macOS, or
multi-resolution PNGs on Linux.

### 6. Set the window icon

```python
window = QMainWindow()
window.setWindowIcon(icons.app_icon())
```

### 7. Fix the Windows taskbar icon

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

### 8. Load additional icons

For toolbar, menu, or status-bar icons placed in `resources/icons/`:

```python
save_icon = icons.load("save.png")
open_icon = icons.load("open.png")
```

Qt Resource System paths are also supported:

```python
icon = icons.load(":/icons/save.png")
```

### 9. Use theme icons (Linux)

Load a freedesktop theme icon with a guaranteed local fallback:

```python
icon = icons.theme("document-save", "save.png")
```

On Linux desktops this returns the theme icon; on other platforms (or if the theme
icon is missing) it falls back to `save.png` from the icons directory.

### 10. Debug null icons

Wrap any icon in `ensure_valid()` to print a warning if it resolved to null:

```python
icon = icons.ensure_valid(icons.load("missing.png"), "toolbar save button")
```

Output when the icon is null:

```
[IconLoader] WARNING: Null icon encountered (toolbar save button)
```

### 11. Update build/packaging configuration

If your project uses **PyInstaller**, **cx_Freeze**, or a similar packager, add
the `resources/icons/` directory to the bundled data so icons are available in the
distributed build.

**PyInstaller `.spec` file** — add to the `datas` list:

```python
datas=[
    ('resources/icons', 'resources/icons'),
    # ... other data entries
],
```

**PyInstaller `--add-data` flag** (command-line usage):

```bash
pyinstaller --add-data "resources/icons:resources/icons" main.py
```

Also update the `.spec` file's `icon=` parameter to use the generated `app.ico`:

```python
icon='resources/icons/app.ico',
```

### 12. Update platform launchers

If your project has platform-specific launcher configurations, update them to
reference the new icon paths:

- **Linux `.desktop` file:** update the `Icon=` line to point to the new location
  (e.g. `Icon=/path/to/your_app/resources/icons/app.png`)
- **macOS `Info.plist`:** ensure `CFBundleIconFile` references `app.icns`
- **Windows shortcut:** the `.ico` embedded by PyInstaller handles this
  automatically if the `.spec` `icon=` is set correctly

### 13. Verify

Run the application and visually confirm the icons are correct. This step requires
a manual check — icon rendering depends on the OS compositor and cannot be
validated through automated tests.

Check the following:

- The window title-bar icon is correct.
- The **Windows taskbar** icon displays your image (not the generic Python icon).
- On macOS, the **dock** icon is correct.
- On Linux, the **window** icon is correct.
- If applicable, build the packaged executable and repeat the checks above to
  confirm icons are bundled correctly.

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

---

## Lessons learned (from MDviewer integration)

The first real integration into [MDviewer](https://github.com/juren53/MDviewer)
revealed the following:

**What worked well:**

- The five code-level steps (import, app icon, window icon, taskbar fix, verify)
  required only 5 new lines of code across 2 files.
- `generate_icons.py` produced all platform assets from a single source PNG in one
  command.
- `set_taskbar_icon()` resolved the Windows taskbar icon on the first attempt with
  no troubleshooting.
- The cross-platform no-op design meant no `if sys.platform` guards were needed in
  the application code.

**What the original procedure missed:**

- **Pre-existing icon directories.** MDviewer already had `assets/icons/` with
  differently-named files. The procedure had no guidance on migrating from or
  coexisting with an existing icon layout.
- **Build/packaging updates.** The PyInstaller `.spec` file needed its `datas` list
  updated to bundle `resources/icons/`, and its `icon=` parameter pointed at the
  old path. Without this step, packaged builds would have missing icons.
- **Platform launcher updates.** The Linux `.desktop` file still referenced the old
  icon path after integration.
- **Verification is manual.** Icon rendering is visual and OS-dependent. Automated
  smoke tests cannot confirm correct icon display — the procedure now states this
  explicitly.
