## Application_Icon_Behavior_in_Python_PyQt6_apps-per-Claude.md

Icon management in PyQt6 cross-platform apps is notoriously finicky. Here's what actually works reliably:

## Core Approach: Qt Resource System

The single most important practice is using Qt's resource system (`.qrc` files) rather than file paths. This bundles icons into your Python module and eliminates path resolution issues across platforms.

```python
# icons.qrc
<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource>
        <file>app_icon.png</file>
        <file alias="icon_16.png">icons/16x16.png</file>
        <file alias="icon_32.png">icons/32x32.png</file>
        <file alias="icon_256.png">icons/256x256.png</file>
    </qresource>
</RCC>
```

Compile with: `pyside6-rcc icons.qrc -o icons_rc.py` (or `pyrcc6` if available), then import it once: `import icons_rc` at your app's entry point.

## Platform-Specific Reality

**Windows** wants `.ico` files with multiple sizes embedded (16, 32, 48, 256px). The title bar and taskbar pull from `setWindowIcon()`, but Windows Defender/UAC sometimes blocks icons unless the executable is signed.

**Linux** is most forgiving - PNG works everywhere. System tray behavior varies by desktop environment (GNOME, KDE, XFCE handle them differently).

**macOS** requires special handling - the dock icon comes from the `.app` bundle, not your Python code.

## Reliable Icon Setting Pattern

```python
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import icons_rc  # Compiled resources

app = QApplication(sys.argv)

# Create icon from resource with fallback sizes
icon = QIcon()
icon.addFile(":/icon_16.png")
icon.addFile(":/icon_32.png")
icon.addFile(":/icon_256.png")

# Set at application level FIRST
app.setWindowIcon(icon)

# Then set on each window explicitly
window = MainWindow()
window.setWindowIcon(icon)

# System tray requires separate handling
tray = QSystemTrayIcon(icon, parent=window)
```

## Critical Timing Issue

Icons must be set **after** `QApplication` instantiation but **before** showing windows. Setting `app.setWindowIcon()` provides a default for all windows, but you still need to set it explicitly on dialog boxes and secondary windows.

## System Tray Gotcha

System tray icons on Windows often need to be 16x16 or 32x32 specifically. Create a separate icon object for tray icons:

```python
tray_icon = QIcon(":/icon_16.png")
tray = QSystemTrayIcon(tray_icon)
```

## About Dialog Pattern

```python
about_dialog = QDialog(parent=main_window)
about_dialog.setWindowIcon(main_window.windowIcon())  # Inherit parent's icon
```

## The Windows .ico Solution

For Windows specifically, convert your PNG to a multi-resolution `.ico` file (use Pillow or online tools). Windows pulls different resolutions for taskbar vs title bar vs alt-tab.

```python
if sys.platform == 'win32':
    icon = QIcon(":/app_icon.ico")
else:
    icon = QIcon(":/app_icon.png")
```

## Testing Checklist

Test each scenario explicitly:
- Application window title bar
- Taskbar (Windows) / Dock (macOS) / Panel (Linux)
- Alt+Tab switcher
- System tray
- All dialog boxes (About, Preferences, etc.)
- After minimize/restore cycles

The unpredictability you're experiencing is usually from: (1) mixing resource paths and file paths, (2) wrong initialization order, (3) not setting icons explicitly on child windows, or (4) platform-specific format mismatches. The resource system + explicit setting on every window/dialog solves most of these.

What specific icon disappearance patterns are you seeing? That would help narrow down which of these issues you're hitting.