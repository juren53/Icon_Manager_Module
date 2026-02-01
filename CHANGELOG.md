# Changelog

All notable changes to Icon Manager Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-01

### Added
- `.gitattributes` for consistent cross-platform line ending handling
- `.gitignore` for Python bytecode and packaging artifacts
- `Project_Rules.md` and `ICON_MDviewer.png`

### Changed
- Updated README project structure to reflect all tracked files

## [0.1.0] - 2026-02-01

### Added
- **Icon Loader Module** (`icon_loader.py`) - Cross-platform icon loading API for PyQt6
  - `IconLoader` class with configurable `base_path` (defaults to `resources/icons`)
  - `app_icon()` — platform-aware application icon selection: `.ico` on Windows, `.icns` on macOS, multi-resolution PNGs on Linux, with automatic cross-platform fallback
  - `load(filename)` — loads icons from disk with absolute path resolution, or from Qt Resource System (`:/` paths)
  - `theme(name, fallback)` — system theme icon support with guaranteed fallback
  - `ensure_valid(icon, context)` — debug helper that warns on null icons
  - Module-level `icons` convenience instance for simple imports
  - Graceful fallback chain: native format → sized PNGs (`app_NxN.png`) → `app.png` → null icon with warning

## [0.0.1] - 2026-02-01 1154 CST

### Added
- **Icon Generation Script** (`generate_icons.py`) - ImageMagick-driven asset pipeline
  - Generates all icon files needed for cross-platform PyQt6 use from a single source image
  - Individual PNGs at 7 standard sizes: 16, 24, 32, 48, 64, 128, 256px
  - Multi-resolution `.ico` for Windows (all 7 sizes embedded)
  - `.icns` for macOS via `iconutil` on macOS or ImageMagick fallback on other platforms
  - Primary `app.png` (256x256) for Linux
  - CLI interface with `--output-dir` option (default: `resources/icons`)
  - ImageMagick v7/v6 auto-detection with clear error messaging
  - Source image validation via `magick identify`
  - File summary with sizes printed on completion
- **Project Documentation**
  - README with module overview, planned API, platform requirements, and usage examples
  - Detailed module blueprint and implementation spec (`PLAN_Qt-Icon-Manaager-Module.md`)
  - Cross-platform icon best practices reference (`Application_Icons_in_PyQt6_Per_Bing.md`)
  - Curated Qt icon documentation links (`Guide_to_Qt_Icon_Documentation.md`)
  - Research notes from multiple AI sources in `notes/` directory

### Technical
- Python 3.x with no dependencies beyond the standard library
- Requires ImageMagick (v6 or v7) installed and on PATH
- Platform-aware `.icns` generation (native `iconutil` on macOS, ImageMagick fallback elsewhere)
- Output directory created automatically via `os.makedirs`
