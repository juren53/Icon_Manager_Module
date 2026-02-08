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

> **⚠️ PyInstaller warning:** When you pass a custom `base_path`, `IconLoader`'s
> built-in frozen-environment detection is bypassed. If your app will be compiled
> with PyInstaller, you must resolve the path yourself:
>
> ```python
> import sys
> from pathlib import Path
> from icon_loader import IconLoader
>
> if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
>     icons = IconLoader(base_path=Path(sys._MEIPASS) / "icons")
> else:
>     icons = IconLoader(base_path=Path(__file__).parent / "icons")
> ```
>
> Without this, `Path(__file__).parent` resolves outside the `_MEIPASS` extraction
> directory and your icons will not be found in the compiled executable.

### 5. Set the application icon

```python
app = QApplication(sys.argv)
app.setApplicationName("YourApp")
app.setDesktopFileName("YourApp")   # must match YourApp.desktop filename
app.setWindowIcon(icons.app_icon())
```

`app_icon()` automatically selects `app.ico` on Windows, `app.icns` on macOS, or
multi-resolution PNGs on Linux.

`setDesktopFileName()` is required on Linux so the desktop environment (GNOME,
Cinnamon, KDE, etc.) can associate the running window with its `.desktop` file.
Without this call, the taskbar and Alt+Tab window switcher may show a blank or
generic icon even when the `.desktop` file itself is correct. The value must match
the `.desktop` filename without the extension (e.g. `"MyApp"` for `MyApp.desktop`).

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
reference the new icon paths.

#### Linux `.desktop` file

**Do not use absolute paths** for the `Icon=` field — they break silently whenever
the project directory is moved or restructured. Instead, install icons into the
XDG hicolor icon theme and reference them by theme name.

**a) Install icons into the hicolor theme:**

Copy each resolution PNG into the corresponding hicolor directory. Replace
`yourapp` with your application's icon name (lowercase, no spaces):

```bash
mkdir -p ~/.local/share/icons/hicolor/{16x16,24x24,32x32,48x48,64x64,128x128,256x256}/apps

cp resources/icons/app_16x16.png   ~/.local/share/icons/hicolor/16x16/apps/yourapp.png
cp resources/icons/app_24x24.png   ~/.local/share/icons/hicolor/24x24/apps/yourapp.png
cp resources/icons/app_32x32.png   ~/.local/share/icons/hicolor/32x32/apps/yourapp.png
cp resources/icons/app_48x48.png   ~/.local/share/icons/hicolor/48x48/apps/yourapp.png
cp resources/icons/app_64x64.png   ~/.local/share/icons/hicolor/64x64/apps/yourapp.png
cp resources/icons/app_128x128.png ~/.local/share/icons/hicolor/128x128/apps/yourapp.png
cp resources/icons/app_256x256.png ~/.local/share/icons/hicolor/256x256/apps/yourapp.png
```

**b) Update the `.desktop` file to use the theme name:**

```ini
Icon=yourapp
```

Use only the name — no path, no file extension. The desktop environment will
look up the correct resolution from the hicolor theme automatically.

**c) Install the `.desktop` file:**

```bash
cp YourApp.desktop ~/.local/share/applications/
```

**d) Update caches:**

```bash
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor/
update-desktop-database ~/.local/share/applications/
```

A logout/login (or restarting the desktop shell) may be needed for the app
launcher icon to refresh.

#### macOS `Info.plist`

Ensure `CFBundleIconFile` references `app.icns`.

#### Windows shortcut

The `.ico` embedded by PyInstaller handles this automatically if the `.spec`
`icon=` is set correctly.

### 13. Verify

Run the application and visually confirm the icons are correct. This step requires
a manual check — icon rendering depends on the OS compositor and cannot be
validated through automated tests.

Check the following on each platform:

**Windows:**
- The window title-bar icon is correct.
- The **taskbar** icon displays your image (not the generic Python icon).

**macOS:**
- The **dock** icon is correct.
- The window title-bar icon is correct.

**Linux** (each uses a different icon lookup path and can fail independently):
- The **window title-bar** icon is correct (set by `setWindowIcon`).
- The **app launcher / menu** icon is correct (from `.desktop` `Icon=` and the
  hicolor theme).
- The **taskbar / panel** icon is correct (requires `setDesktopFileName` +
  hicolor theme icon).
- The **Alt+Tab window switcher** icon is correct.

If applicable, build the packaged executable and repeat the checks above to
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
    app.setApplicationName("MyApp")
    app.setDesktopFileName("MyApp")  # matches MyApp.desktop
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
- **`resources/icons` must be in PyInstaller `datas`.** Icons that displayed
  correctly when running via the Python interpreter were missing in the compiled
  executable. The root cause was that the `.spec` file bundled `assets/` but not
  `resources/icons/`, which is where `icon_loader.py` resolves its paths at
  runtime. Adding `('resources/icons', 'resources/icons')` to the `datas` list
  fixed the issue. Step 11 already documents this, but it is easy to overlook
  when the project has a separate legacy icon directory that *is* bundled.
- **Platform launcher updates.** The Linux `.desktop` file still referenced the old
  icon path after integration.
- **Verification is manual.** Icon rendering is visual and OS-dependent. Automated
  smoke tests cannot confirm correct icon display — the procedure now states this
  explicitly. Always verify icons in both the Python interpreter *and* the
  compiled executable — passing one does not guarantee the other.

**Linux desktop integration (discovered on LMDE / Cinnamon):**

- **Absolute paths in `.desktop` `Icon=` are fragile.** The original procedure
  recommended `Icon=/path/to/resources/icons/app.png`. After the Icon_Manager_Module
  integration moved icons from `assets/icons/` to `resources/icons/`, the installed
  `.desktop` file still pointed to the old path, resulting in blank icons everywhere
  (app launcher, taskbar, window switcher). The fix was to install icons into the
  XDG hicolor theme (`~/.local/share/icons/hicolor/<size>/apps/`) and use
  `Icon=appname` (theme name only) in the `.desktop` file.
- **`setDesktopFileName()` is required.** Without this PyQt6 call, Linux desktop
  environments cannot associate the running window with its `.desktop` file. This
  caused blank taskbar and Alt+Tab icons even when the `.desktop` file itself was
  correctly configured.
- **Linux has four independent icon display points** (title bar, app launcher,
  taskbar, Alt+Tab) that each use different lookup mechanisms and can fail
  independently. The verification checklist now covers all four.

---

## Lessons learned (from HPM integration)

The second integration into [HPM](https://github.com/juren53/HST-Metadata)
(HSTL Photo Metadata Framework) revealed two additional issues, both specific to
PyInstaller `console=False` GUI applications.

**Custom `base_path` breaks frozen path resolution:**

- HPM stores icons in `icons/` (not `resources/icons/`), so it constructs
  `IconLoader(base_path=framework_dir / "icons")` with a custom path.
- In source mode, `framework_dir = Path(__file__).parent.parent` resolves correctly.
- In a frozen PyInstaller `.exe`, `Path(__file__).parent.parent` resolves to a path
  **outside** the `_MEIPASS` temp extraction directory, so the bundled icons cannot
  be found — the app launches but shows a generic icon.
- **Fix (caller side):** The caller must handle `sys._MEIPASS` when computing a
  custom `base_path`:

  ```python
  if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
      _icons_path = Path(sys._MEIPASS) / "icons"
  else:
      _icons_path = framework_dir / "icons"
  icons = IconLoader(base_path=_icons_path)
  ```

- **Root cause:** `IconLoader.__init__()` has frozen-environment detection for its
  *default* path (`resources/icons`), but when the caller passes a custom
  `base_path`, that logic is bypassed. This is by design — the caller knows their
  own directory layout — but Step 4 of the procedure should warn about it.

**`console=False` makes `sys.stdout` `None`:**

- PyInstaller's `console=False` option (standard for GUI apps — suppresses the
  console window) sets `sys.stdout` and `sys.stderr` to `None` on Windows.
- `icon_loader.py` contains 5 `print()` calls (all `[IconLoader] WARNING:` messages).
  Any of these will crash the app with `'NoneType' object has no attribute 'write'`.
- This does not surface during development (Python always has a console) or in
  `console=True` builds. It only manifests in production `console=False` executables,
  and only when a warning path is hit (e.g., a missing icon file).
- **Fix (in icon_loader.py):** Added a module-level guard that redirects
  `sys.stdout` / `sys.stderr` to `os.devnull` when they are `None`. This protects
  all `print()` calls throughout the module and any downstream code that imports it.

  ```python
  if sys.stdout is None:
      sys.stdout = open(os.devnull, "w")
  if sys.stderr is None:
      sys.stderr = open(os.devnull, "w")
  ```

- HPM also needed this guard in its own entry point and worker threads, since
  `g2c.py` (CSV converter) uses `print()` extensively and runs in a `QThread`.
