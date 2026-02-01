"""
demo_icon_loader.py
Visual demo of every IconLoader API method.

Usage:
    python demo_icon_loader.py             # GUI window
    python demo_icon_loader.py --headless  # text-only summary (for CI)
"""

from __future__ import annotations

import io
import pathlib
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from icon_loader import IconLoader, icons


# ------------------------------------------------------------------
# Stdout capture helper
# ------------------------------------------------------------------

class TeeStream(io.TextIOBase):
    """Duplicates writes to the original stream and a buffer."""

    def __init__(self, original: io.TextIOBase):
        super().__init__()
        self.original = original
        self.buffer = io.StringIO()

    def write(self, s: str) -> int:
        self.original.write(s)
        self.buffer.write(s)
        return len(s)

    def flush(self) -> None:
        self.original.flush()

    def getvalue(self) -> str:
        return self.buffer.getvalue()


# ------------------------------------------------------------------
# Headless mode
# ------------------------------------------------------------------

def run_headless() -> str:
    """Execute every demo and return a plain-text report."""
    lines: list[str] = []

    def heading(title: str) -> None:
        lines.append("")
        lines.append(f"=== {title} ===")

    # 1 -- app_icon()
    heading("App Icon (app_icon)")
    icon = icons.app_icon()
    if sys.platform.startswith("win"):
        path_used = "Windows: app.ico"
    elif sys.platform == "darwin":
        path_used = "macOS: app.icns"
    else:
        path_used = "Linux: multi-resolution PNGs"
    lines.append(f"  Platform path : {path_used}")
    lines.append(f"  isNull()      : {icon.isNull()}")

    # 2 -- load() gallery
    heading("Icon Gallery (load)")
    icon_dir = icons.base_path
    for png in sorted(icon_dir.glob("app_*x*.png")):
        loaded = icons.load(png.name)
        sizes = loaded.availableSizes()
        dim = f"{sizes[0].width()}x{sizes[0].height()}" if sizes else "n/a"
        lines.append(f"  {png.name:20s}  loaded={not loaded.isNull()}  size={dim}")

    # 3 -- load() missing file
    heading("Missing Icon (load failure)")
    missing = icons.load("nonexistent.png")
    lines.append(f"  load('nonexistent.png').isNull() = {missing.isNull()}")

    # 4 -- Qt resource path
    heading("Qt Resource Path (load with :/)")
    qt_icon = icons.load(":/icons/fake.png")
    lines.append(f"  load(':/icons/fake.png').isNull() = {qt_icon.isNull()}")
    lines.append("  No file-existence warning expected (resource path)")

    # 5 -- theme()
    heading("Theme Icon (theme)")
    theme_icon = icons.theme("document-open", "app.png")
    lines.append(f"  theme('document-open', 'app.png').isNull() = {theme_icon.isNull()}")
    lines.append("  Theme name attempted : document-open")
    lines.append("  Fallback file        : app.png")

    # 6 -- ensure_valid()
    heading("Validation (ensure_valid)")
    good_icon = icons.load("app.png")
    icons.ensure_valid(good_icon, "good icon")
    lines.append(f"  ensure_valid(good_icon)  -> isNull={good_icon.isNull()}  [PASS]")

    null_icon = QIcon()
    icons.ensure_valid(null_icon, "null icon")
    lines.append(f"  ensure_valid(null_icon)  -> isNull={null_icon.isNull()}  [warned]")

    heading("Done")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------
# GUI helpers
# ------------------------------------------------------------------

def _icon_to_pixmap(icon: QIcon, size: int) -> QPixmap:
    """Render a QIcon into a QPixmap at the requested size."""
    return icon.pixmap(size, size)


def _icon_label(icon: QIcon, size: int, text: str) -> QWidget:
    """Small widget: icon pixmap on top, caption below."""
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(4, 4, 4, 4)

    img = QLabel()
    pm = _icon_to_pixmap(icon, size)
    if pm.isNull():
        img.setText("(null)")
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setFixedSize(size, size)
    else:
        img.setPixmap(pm)
        img.setFixedSize(pm.width(), pm.height())

    caption = QLabel(text)
    caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
    caption.setStyleSheet("font-size: 10px;")

    layout.addWidget(img, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(caption, alignment=Qt.AlignmentFlag.AlignCenter)
    return box


def _section(title: str) -> tuple[QGroupBox, QVBoxLayout]:
    group = QGroupBox(title)
    layout = QVBoxLayout(group)
    return group, layout


# ------------------------------------------------------------------
# GUI window
# ------------------------------------------------------------------

class DemoWindow(QWidget):
    def __init__(self, captured_output: str):
        super().__init__()
        self.setWindowTitle("IconLoader Demo")
        self.setWindowIcon(icons.app_icon())
        self.setMinimumWidth(700)

        root = QVBoxLayout(self)

        # Wrap sections in a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        body = QVBoxLayout(container)

        self._build_app_icon_section(body)
        self._build_gallery_section(body)
        self._build_missing_section(body)
        self._build_qt_resource_section(body)
        self._build_theme_section(body)
        self._build_validation_section(body)

        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

        # Console output section (not scrolled with the rest)
        console_group, console_layout = _section("Console Output ([IconLoader] messages)")
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlainText(captured_output)
        self.console.setMinimumHeight(120)
        console_layout.addWidget(self.console)
        root.addWidget(console_group)

    # -- individual sections --

    def _build_app_icon_section(self, parent: QVBoxLayout) -> None:
        group, layout = _section("1. App Icon  (app_icon())")
        row = QHBoxLayout()

        icon = icons.app_icon()
        row.addWidget(_icon_label(icon, 64, "app icon @ 64px"))

        if sys.platform.startswith("win"):
            path_used = "Windows: app.ico"
        elif sys.platform == "darwin":
            path_used = "macOS: app.icns"
        else:
            path_used = "Linux: multi-resolution PNGs"

        info = QLabel(f"Platform path: {path_used}\nisNull: {icon.isNull()}")
        row.addWidget(info)
        row.addStretch()

        layout.addLayout(row)
        parent.addWidget(group)

    def _build_gallery_section(self, parent: QVBoxLayout) -> None:
        group, layout = _section("2. Icon Gallery  (load())")
        grid = QGridLayout()
        col = 0
        for png in sorted(icons.base_path.glob("app_*x*.png")):
            loaded = icons.load(png.name)
            sizes = loaded.availableSizes()
            if sizes:
                native = sizes[0].width()
            else:
                native = 32  # fallback display size
            dim = f"{sizes[0].width()}x{sizes[0].height()}" if sizes else "n/a"
            caption = f"{png.name}\n{dim}"
            grid.addWidget(_icon_label(loaded, native, caption), 0, col)
            col += 1
        layout.addLayout(grid)
        parent.addWidget(group)

    def _build_missing_section(self, parent: QVBoxLayout) -> None:
        group, layout = _section("3. Missing Icon  (load() failure)")
        row = QHBoxLayout()

        missing = icons.load("nonexistent.png")
        row.addWidget(_icon_label(missing, 32, "nonexistent.png"))

        info = QLabel(
            f"load('nonexistent.png')\nisNull: {missing.isNull()}\n"
            "Warning printed to console"
        )
        row.addWidget(info)
        row.addStretch()
        layout.addLayout(row)
        parent.addWidget(group)

    def _build_qt_resource_section(self, parent: QVBoxLayout) -> None:
        group, layout = _section("4. Qt Resource Path  (load() with :/)")
        row = QHBoxLayout()

        qt_icon = icons.load(":/icons/fake.png")
        row.addWidget(_icon_label(qt_icon, 32, ":/icons/fake.png"))

        info = QLabel(
            f"load(':/icons/fake.png')\nisNull: {qt_icon.isNull()}\n"
            "No file-existence warning (resource path)"
        )
        row.addWidget(info)
        row.addStretch()
        layout.addLayout(row)
        parent.addWidget(group)

    def _build_theme_section(self, parent: QVBoxLayout) -> None:
        group, layout = _section("5. Theme Icon  (theme())")
        row = QHBoxLayout()

        theme_icon = icons.theme("document-open", "app.png")
        row.addWidget(_icon_label(theme_icon, 32, "document-open"))

        info = QLabel(
            f"theme('document-open', 'app.png')\n"
            f"isNull: {theme_icon.isNull()}\n"
            "Theme attempted: document-open\n"
            "Fallback: app.png"
        )
        row.addWidget(info)
        row.addStretch()
        layout.addLayout(row)
        parent.addWidget(group)

    def _build_validation_section(self, parent: QVBoxLayout) -> None:
        group, layout = _section("6. Validation  (ensure_valid())")

        # Good icon
        good = icons.load("app.png")
        icons.ensure_valid(good, "good icon")
        good_status = "PASS" if not good.isNull() else "FAIL"
        layout.addWidget(QLabel(
            f"ensure_valid( load('app.png'), 'good icon' ) -> "
            f"isNull={good.isNull()}  [{good_status}]"
        ))

        # Null icon
        null_icon = QIcon()
        icons.ensure_valid(null_icon, "null icon")
        null_status = "warned" if null_icon.isNull() else "unexpected"
        layout.addWidget(QLabel(
            f"ensure_valid( QIcon(), 'null icon' ) -> "
            f"isNull={null_icon.isNull()}  [{null_status}]"
        ))

        parent.addWidget(group)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setWindowIcon(icons.app_icon())

    headless = "--headless" in sys.argv

    # Capture stdout to collect [IconLoader] messages
    tee = TeeStream(sys.stdout)
    sys.stdout = tee

    if headless:
        report = run_headless()
        sys.stdout = tee.original  # restore before final print
        print(report, end="")
        return

    # GUI mode -- run headless logic first to collect console text,
    # then build the window (which also exercises the APIs visually).
    _ = run_headless()
    captured = tee.getvalue()

    window = DemoWindow(captured)
    window.resize(750, 800)
    window.show()

    icons.set_taskbar_icon(window)

    sys.stdout = tee.original  # restore for normal operation
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
