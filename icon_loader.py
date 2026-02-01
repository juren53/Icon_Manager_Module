"""
icon_loader.py
A robust, cross-platform icon loader for PyQt6 applications.

Features:
- Unified icon loading for all parts of the app
- Automatic OS-specific icon selection (.ico, .icns, .png)
- Optional Qt Resource System support (":/icons/...")
- Multi-resolution icon handling
- Absolute path resolution for packaged apps (PyInstaller, cx_Freeze)
- Graceful fallback behavior
"""

from __future__ import annotations

import sys
import pathlib
from typing import Optional

from PyQt6.QtGui import QIcon


class IconLoader:
    """
    A centralized icon loader that ensures consistent icon behavior across
    Windows, macOS, and Linux.
    """

    def __init__(self, base_path: Optional[pathlib.Path] = None):
        """
        base_path:
            Directory containing your icon files.
            If None, defaults to: <project_root>/resources/icons
        """
        if base_path is None:
            base_path = pathlib.Path(__file__).resolve().parent / "resources" / "icons"

        self.base_path = base_path.resolve()

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def app_icon(self) -> QIcon:
        """
        Returns the best icon for the application window, dock, and taskbar.
        Automatically selects .ico (Windows), .icns (macOS), or multi-resolution
        PNGs (Linux), with cross-platform fallback.
        """
        if sys.platform.startswith("win"):
            ico_path = self.base_path / "app.ico"
            if ico_path.exists():
                return QIcon(str(ico_path))
            print(f"[IconLoader] WARNING: app.ico not found, falling back to PNGs")

        elif sys.platform == "darwin":
            icns_path = self.base_path / "app.icns"
            if icns_path.exists():
                return QIcon(str(icns_path))
            print(f"[IconLoader] WARNING: app.icns not found, falling back to PNGs")

        # Linux primary path, or fallback for Windows/macOS when native format missing
        return self._load_multi_res_png()

    def load(self, filename: str) -> QIcon:
        """
        Loads an icon from disk or Qt resources.
        """
        # Qt Resource System path
        if filename.startswith(":/"):
            return QIcon(filename)

        # Absolute path resolution
        path = self.base_path / filename

        if not path.exists():
            print(f"[IconLoader] WARNING: Icon not found: {path}")
            return QIcon()  # Null icon

        return QIcon(str(path))

    def theme(self, name: str, fallback: str) -> QIcon:
        """
        Loads a theme icon (Linux) with a guaranteed fallback.
        """
        return QIcon.fromTheme(name, self.load(fallback))

    # ------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------

    def ensure_valid(self, icon: QIcon, context: str = "") -> QIcon:
        """
        Debug helper: warn if icon is null.
        """
        if icon.isNull():
            print(f"[IconLoader] WARNING: Null icon encountered ({context})")
        return icon

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _load_multi_res_png(self) -> QIcon:
        """
        Build a QIcon from all app_NxN.png files found in base_path,
        giving Qt every available resolution. Falls back to app.png.
        """
        icon = QIcon()
        found = False

        for png in sorted(self.base_path.glob("app_*x*.png")):
            icon.addFile(str(png))
            found = True

        if found:
            return icon

        # Final fallback: plain app.png
        app_png = self.base_path / "app.png"
        if app_png.exists():
            return QIcon(str(app_png))

        print("[IconLoader] WARNING: No app icon files found")
        return QIcon()


# ------------------------------------------------------------
# Convenience global instance
# ------------------------------------------------------------

# Typical usage:
#   from icon_loader import icons
#   window.setWindowIcon(icons.app_icon())
icons = IconLoader()
