# How to Update an App Icon in an IMM-Integrated Project

This procedure covers replacing the application icon in a project that has
already integrated Icon_Manager_Module. It assumes the initial integration
(described in `PROCEDURE_IMM-integration.md`) has been completed and the app
is currently running with a working icon.

---

## When to use this procedure

- You have a new logo or redesigned icon and need to roll it out.
- You want to swap the source artwork (e.g., from a flat design to a rounded
  variant produced by `make_icon.py`).
- The existing icon assets are outdated or low-resolution and you have a
  better source image.

---

## Prerequisites

- **ImageMagick** installed and on PATH (same requirement as initial setup).
- A **new high-resolution source image** (256 px minimum, 512 px recommended;
  PNG with transparency preferred).
- Access to the `generate_icons.py` script from Icon_Manager_Module.

---

## Steps

### 1. Prepare the new source image

Start with the highest-resolution version of the new icon you have. If you
want rounded corners, run `make_icon.py` first to produce a polished 512x512
source PNG:

```bash
cd C:\Users\jimur\Projects\Icon_Manager_Module
python make_icon.py new_logo_raw.png new_logo.png
```

The output (`new_logo.png`) becomes the source image for step 2.

If you already have a finished source image at 256 px or larger, skip this
step.

### 2. Regenerate icon assets

Run `generate_icons.py` with the new source image, pointing `--output-dir` at
the project's icon directory. This overwrites all `app.*` and `app_NxN.png`
files in place.

**Default layout** (`resources/icons/` next to `icon_loader.py`):

```bash
python generate_icons.py new_logo.png --output-dir /path/to/yourapp/resources/icons
```

**Custom layout** (e.g., SysMon uses `icons/` at project root):

```bash
python generate_icons.py new_logo.png --output-dir /path/to/yourapp/icons
```

This regenerates all platform-specific assets:

| File | Purpose |
|------|---------|
| `app.ico` | Windows executable icon + window/taskbar icon |
| `app.icns` | macOS dock/Finder icon |
| `app_16x16.png` ... `app_256x256.png` | Multi-resolution PNGs |
| `app.png` | Default Linux icon (copy of 256 px) |

**Important:** `generate_icons.py` only writes files with the `app.*` /
`app_NxN.png` naming convention. Any other icon files in the directory
(e.g., legacy `ICON_AppName.png` files) are left untouched.

### 3. Verify — run from source

Launch the application from the Python interpreter and visually confirm:

**Windows:**
- Window title-bar icon shows the new image.
- Taskbar icon shows the new image (not the old one or the generic Python
  icon).

**macOS:**
- Dock icon shows the new image.
- Window title-bar icon shows the new image.

**Linux** (check all four — they use different lookup paths):
- Window title-bar icon (set by `setWindowIcon`).
- App launcher / menu icon (from `.desktop` `Icon=` + hicolor theme).
- Taskbar / panel icon (requires `setDesktopFileName` + hicolor theme).
- Alt+Tab window switcher icon.

No code changes are needed at this stage — `icon_loader.py` loads icons by
filename convention (`app.ico`, `app.icns`, `app_NxN.png`), so replacing the
files is sufficient.

### 4. Rebuild the packaged executable

If the project distributes a compiled executable (PyInstaller, cx_Freeze,
etc.), rebuild it. The new `app.ico` will be embedded as the `.exe` file icon,
and the new PNGs/ICO/ICNS will be bundled as data.

**PyInstaller example:**

```bash
pyinstaller YourApp.spec --noconfirm
```

The `.spec` file should already have:
- `icon=['path/to/icons/app.ico']` — embeds the icon in the `.exe` itself.
- `datas=[('path/to/icons', 'icons')]` (or `('resources/icons',
  'resources/icons')`) — bundles icon files for runtime loading.

No `.spec` changes are needed unless the icon directory has moved.

### 5. Verify — run the packaged executable

Launch the built executable and repeat all the visual checks from step 3.
This is a separate verification because PyInstaller bundles icons at build
time — passing step 3 does not guarantee step 5 will pass.

On Windows, you may also want to check:
- Right-click the `.exe` in Explorer → Properties → the icon on the General
  tab should show the new image.
- Pin the app to the taskbar — the pinned icon should update.

**Windows icon cache note:** Windows aggressively caches `.exe` icons. If
Explorer still shows the old icon after a rebuild, flush the cache:

```cmd
ie4uinit.exe -show
```

Or restart Explorer. In stubborn cases, delete the icon cache files in
`%LOCALAPPDATA%\Microsoft\Windows\Explorer\` and reboot.

### 6. Update Linux hicolor theme icons (Linux only)

If the project installs icons into the XDG hicolor theme (as recommended in
`PROCEDURE_IMM-integration.md` step 12), re-copy the new PNGs:

```bash
cp resources/icons/app_16x16.png   ~/.local/share/icons/hicolor/16x16/apps/yourapp.png
cp resources/icons/app_24x24.png   ~/.local/share/icons/hicolor/24x24/apps/yourapp.png
cp resources/icons/app_32x32.png   ~/.local/share/icons/hicolor/32x32/apps/yourapp.png
cp resources/icons/app_48x48.png   ~/.local/share/icons/hicolor/48x48/apps/yourapp.png
cp resources/icons/app_64x64.png   ~/.local/share/icons/hicolor/64x64/apps/yourapp.png
cp resources/icons/app_128x128.png ~/.local/share/icons/hicolor/128x128/apps/yourapp.png
cp resources/icons/app_256x256.png ~/.local/share/icons/hicolor/256x256/apps/yourapp.png

gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor/
```

A logout/login may be required for the app launcher and taskbar to pick up
the new icon.

### 7. Archive the source image

Store the new source image (and the raw pre-`make_icon.py` version if
applicable) in a known location so future icon updates start from the same
high-quality original. Suggested locations:

- In the Icon_Manager_Module project root as `ICON_AppName.png` (the existing
  convention — see `ICON_sysmon.png`, `ICON_MDviewer.png`).
- In the app project's icon directory alongside the generated assets.

### 8. Commit and push

Stage the regenerated icon assets and commit. There are no code changes — only
binary image files are updated.

```bash
git add icons/app.ico icons/app.icns icons/app.png icons/app_*x*.png
git commit -m "Update app icon to new design"
git push
```

---

## Quick reference: what changes and what doesn't

| Item | Changes? | Notes |
|------|----------|-------|
| `app.ico`, `app.icns`, `app_NxN.png`, `app.png` | **Yes** | Regenerated from new source |
| `icon_loader.py` | No | Loads by filename convention, not content |
| Application source code | No | No icon paths or references change |
| PyInstaller `.spec` file | No | Already points at `app.ico` and icon dir |
| `.desktop` file (Linux) | No | Uses theme name, not a specific file |
| Hicolor theme icons (Linux) | **Yes** | Must re-copy updated PNGs |

---

## Troubleshooting

**Old icon still appears after rebuild (Windows):**
Windows caches `.exe` icons aggressively. Run `ie4uinit.exe -show` or
restart Explorer. For pinned taskbar icons, unpin and re-pin.

**Old icon still appears in app launcher (Linux):**
Run `gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor/` and
log out / log in.

**Icon looks blurry or pixelated:**
The source image was too small. Start with at least 256x256; 512x512 is
recommended for sharp rendering at all display scales.

**`generate_icons.py` fails with "cannot read" error:**
Ensure the source image is a valid PNG. JPEG and other formats may work
but PNG with transparency is preferred.

**PyInstaller build succeeds but exe shows old icon in Explorer:**
Delete the `build/` and `dist/` directories and rebuild from scratch.
PyInstaller caches intermediate artifacts that can retain the old icon.
