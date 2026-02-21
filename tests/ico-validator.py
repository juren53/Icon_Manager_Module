#!/usr/bin/env python3
"""
Inspect the contents of a Windows .ico file using Pillow.

- Confirms the file format
- Lists all embedded icon sizes
- Shows color mode for each image
- Optionally extracts a selected icon size to PNG

Usage:
    python inspect_ico.py icon.ico
"""

import sys
from PIL import Image


def inspect_ico(path: str, extract_index: int | None = None) -> None:
    ico = Image.open(path)

    # Sanity check
    if ico.format != "ICO":
        raise ValueError(f"{path} is not an ICO file (detected format: {ico.format})")

    print(f"File:   {path}")
    print(f"Format: {ico.format}")
    print("Images contained:")

    i = 0
    try:
        while True:
            ico.seek(i)
            print(f"  [{i}] size={ico.size}, mode={ico.mode}")
            i += 1
    except EOFError:
        pass

    print(f"Total images: {i}")

    # Optional extraction
    if extract_index is not None:
        if extract_index < 0 or extract_index >= i:
            raise IndexError(f"Invalid extract index {extract_index}")

        ico.seek(extract_index)
        out_name = f"icon_{ico.size[0]}x{ico.size[1]}.png"
        ico.save(out_name)
        print(f"Extracted image [{extract_index}] -> {out_name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_ico.py <icon.ico> [extract_index]")
        sys.exit(1)

    ico_path = sys.argv[1]
    extract_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None

    inspect_ico(ico_path, extract_idx)

