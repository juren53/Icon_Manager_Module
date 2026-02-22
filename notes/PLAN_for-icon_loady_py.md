## PLAN_for-icon_loady_py.md


● Here's the plan. The key points:

  - Single file: icon_loader.py at the project root
  - 4 methods on the IconLoader class: app_icon(), load(), theme(), ensure_valid()
  - app_icon() picks the right format per OS (.ico on Windows, .icns on macOS, multi-resolution PNGs on Linux), with
   fallback chains if the preferred format is missing
  - load() supports both filesystem paths and Qt resource paths (:/...)
  - theme() wraps QIcon.fromTheme() with a guaranteed fallback
  - ensure_valid() is a debug helper that warns on null icons
  - A module-level icons = IconLoader() convenience instance for simple imports