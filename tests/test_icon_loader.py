"""
Tests for icon_loader.py

Requires PyQt6 and pytest. Run with:
    python -m pytest tests/test_icon_loader.py -v
"""

import pathlib
import sys

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Ensure a QApplication exists before any QIcon work
app = QApplication.instance() or QApplication([])

from icon_loader import IconLoader, icons


# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------

@pytest.fixture
def tmp_icons(tmp_path):
    """Create a temporary icon directory with a minimal valid PNG."""
    # 1x1 red pixel PNG (smallest valid PNG file)
    minimal_png = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx"
        b"\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    (tmp_path / "app.png").write_bytes(minimal_png)
    (tmp_path / "open.png").write_bytes(minimal_png)
    (tmp_path / "app_16x16.png").write_bytes(minimal_png)
    (tmp_path / "app_32x32.png").write_bytes(minimal_png)
    (tmp_path / "app_256x256.png").write_bytes(minimal_png)
    return tmp_path


@pytest.fixture
def loader(tmp_icons):
    """IconLoader pointed at the temp icon directory."""
    return IconLoader(base_path=tmp_icons)


@pytest.fixture
def empty_loader(tmp_path):
    """IconLoader pointed at an empty directory."""
    return IconLoader(base_path=tmp_path)


# ------------------------------------------------------------
# __init__
# ------------------------------------------------------------

class TestInit:
    def test_default_base_path(self):
        """Default base_path resolves to <module_dir>/resources/icons."""
        loader = IconLoader()
        expected = pathlib.Path(__file__).resolve().parent.parent / "resources" / "icons"
        assert loader.base_path == expected.resolve()

    def test_custom_base_path(self, tmp_path):
        """Custom base_path is stored as an absolute resolved path."""
        loader = IconLoader(base_path=tmp_path)
        assert loader.base_path == tmp_path.resolve()
        assert loader.base_path.is_absolute()


# ------------------------------------------------------------
# load()
# ------------------------------------------------------------

class TestLoad:
    def test_existing_file(self, loader, tmp_icons):
        """Loading an existing file returns a non-null QIcon."""
        icon = loader.load("open.png")
        assert not icon.isNull()

    def test_missing_file_returns_null(self, loader, capsys):
        """Loading a missing file returns a null QIcon and prints a warning."""
        icon = loader.load("nonexistent.png")
        assert icon.isNull()
        captured = capsys.readouterr()
        assert "[IconLoader] WARNING: Icon not found:" in captured.out
        assert "nonexistent.png" in captured.out

    def test_qt_resource_path_no_existence_check(self, loader, capsys):
        """A :/ resource path is passed directly to QIcon without file check."""
        icon = loader.load(":/icons/app.png")
        assert isinstance(icon, QIcon)
        captured = capsys.readouterr()
        assert "WARNING" not in captured.out

    def test_returns_qicon_type(self, loader):
        """load() always returns a QIcon instance."""
        assert isinstance(loader.load("open.png"), QIcon)
        assert isinstance(loader.load("missing.png"), QIcon)
        assert isinstance(loader.load(":/fake"), QIcon)


# ------------------------------------------------------------
# app_icon()
# ------------------------------------------------------------

class TestAppIcon:
    def test_returns_qicon(self, loader):
        """app_icon() returns a QIcon instance."""
        assert isinstance(loader.app_icon(), QIcon)

    def test_fallback_to_multi_res_pngs(self, loader, capsys):
        """When native format missing, falls back to sized PNGs."""
        icon = loader.app_icon()
        # On Windows/macOS the native format won't exist in tmp dir,
        # so it should fall back to the app_NxN.png files
        if sys.platform.startswith("win") or sys.platform == "darwin":
            captured = capsys.readouterr()
            assert "falling back to PNGs" in captured.out
        assert not icon.isNull()

    def test_empty_dir_returns_null_with_warning(self, empty_loader, capsys):
        """With no icon files at all, returns null QIcon and warns."""
        icon = empty_loader.app_icon()
        assert icon.isNull()
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_app_png_fallback(self, tmp_path):
        """When only app.png exists (no sized PNGs), it is used."""
        minimal_png = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx"
            b"\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        (tmp_path / "app.png").write_bytes(minimal_png)
        loader = IconLoader(base_path=tmp_path)
        icon = loader.app_icon()
        if sys.platform.startswith("win") or sys.platform == "darwin":
            pass  # will fall back through native format warning
        assert not icon.isNull()


# ------------------------------------------------------------
# theme()
# ------------------------------------------------------------

class TestTheme:
    def test_returns_qicon(self, loader):
        """theme() returns a QIcon instance."""
        icon = loader.theme("document-open", "open.png")
        assert isinstance(icon, QIcon)

    def test_fallback_used_for_unknown_theme(self, loader):
        """An unknown theme name falls back to the provided file."""
        icon = loader.theme("nonexistent-theme-icon-xyz", "open.png")
        assert not icon.isNull()


# ------------------------------------------------------------
# ensure_valid()
# ------------------------------------------------------------

class TestEnsureValid:
    def test_null_icon_prints_warning(self, loader, capsys):
        """ensure_valid() warns when given a null icon."""
        null_icon = QIcon()
        result = loader.ensure_valid(null_icon, "test context")
        captured = capsys.readouterr()
        assert "[IconLoader] WARNING: Null icon encountered (test context)" in captured.out
        assert result is null_icon

    def test_valid_icon_no_warning(self, loader, capsys):
        """ensure_valid() is silent for a valid icon."""
        icon = loader.load("open.png")
        result = loader.ensure_valid(icon, "should not warn")
        captured = capsys.readouterr()
        assert "WARNING" not in captured.out
        assert result is icon

    def test_returns_same_icon(self, loader):
        """ensure_valid() returns the exact same icon object."""
        icon = QIcon()
        assert loader.ensure_valid(icon) is icon


# ------------------------------------------------------------
# Module-level convenience instance
# ------------------------------------------------------------

class TestModuleInstance:
    def test_icons_is_icon_loader(self):
        """The module-level `icons` is an IconLoader instance."""
        assert isinstance(icons, IconLoader)

    def test_icons_default_path(self):
        """The module-level instance uses the default base_path."""
        expected = pathlib.Path(icons.__class__.__module__).resolve()
        # Just verify it ends with the expected suffix
        assert str(icons.base_path).endswith("resources\\icons") or \
               str(icons.base_path).endswith("resources/icons")
