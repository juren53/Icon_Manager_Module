#!/usr/bin/env python3
"""Generate all icon files needed for cross-platform PyQt6 use.

Drives ImageMagick to produce .ico, .icns, and individual PNGs
from a single high-resolution source image.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile

# Sizes for individual PNGs and the multi-resolution .ico
ICON_SIZES = [16, 24, 32, 48, 64, 128, 256]

# Sizes required for macOS .icns (via iconutil)
ICNS_SIZES = [16, 32, 128, 256, 512]


def find_magick():
    """Detect ImageMagick and return the command prefix to use.

    Returns a list like ["magick"] (v7) or ["convert"] (v6 fallback).
    Exits with an error if ImageMagick is not found.
    """
    # Try ImageMagick v7 first
    try:
        subprocess.run(
            ["magick", "--version"],
            capture_output=True,
            check=True,
        )
        return ["magick"]
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Fall back to ImageMagick v6
    try:
        result = subprocess.run(
            ["convert", "--version"],
            capture_output=True,
            check=True,
            text=True,
        )
        # Make sure it's actually ImageMagick, not some other `convert`
        if "ImageMagick" in result.stdout:
            return ["convert"]
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    print("Error: ImageMagick is not installed or not on PATH.", file=sys.stderr)
    print("Install it from https://imagemagick.org/script/download.php", file=sys.stderr)
    sys.exit(1)


def identify_image(magick_cmd, source):
    """Validate that ImageMagick can read the source image."""
    identify_cmd = magick_cmd + ["identify", source] if magick_cmd[0] == "magick" else ["identify", source]
    try:
        subprocess.run(identify_cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Error: ImageMagick cannot read '{source}'.", file=sys.stderr)
        print("Ensure it is a valid image file (PNG recommended).", file=sys.stderr)
        sys.exit(1)


def generate_pngs(magick_cmd, source, output_dir):
    """Generate individual sized PNGs from the source image."""
    generated = []
    for size in ICON_SIZES:
        out_path = os.path.join(output_dir, f"app_{size}x{size}.png")
        cmd = magick_cmd + [source, "-resize", f"{size}x{size}", out_path]
        subprocess.run(cmd, check=True)
        generated.append(out_path)
        print(f"  Created {out_path}")
    return generated


def copy_primary_png(output_dir):
    """Copy app_256x256.png as app.png (the default Linux icon)."""
    src = os.path.join(output_dir, "app_256x256.png")
    dst = os.path.join(output_dir, "app.png")
    shutil.copy2(src, dst)
    print(f"  Created {dst}")
    return dst


def generate_ico(magick_cmd, output_dir):
    """Combine individual PNGs into a multi-resolution .ico file."""
    ico_path = os.path.join(output_dir, "app.ico")
    png_inputs = [os.path.join(output_dir, f"app_{s}x{s}.png") for s in ICON_SIZES]
    cmd = magick_cmd + png_inputs + [ico_path]
    subprocess.run(cmd, check=True)
    print(f"  Created {ico_path}")
    return ico_path


def generate_icns_macos(magick_cmd, source, output_dir):
    """Generate .icns on macOS using iconutil.

    Creates an .iconset folder with Apple-named PNGs, then runs
    `iconutil -c icns` to produce the final .icns file.
    """
    icns_path = os.path.join(output_dir, "app.icns")
    iconset_dir = tempfile.mkdtemp(suffix=".iconset")

    # Apple naming convention: icon_NxN.png and icon_NxN@2x.png
    # We generate 1x variants for each size and 2x where applicable.
    apple_entries = [
        (16, 1),    # icon_16x16.png
        (16, 2),    # icon_16x16@2x.png  (32px)
        (32, 1),    # icon_32x32.png
        (32, 2),    # icon_32x32@2x.png  (64px)
        (128, 1),   # icon_128x128.png
        (128, 2),   # icon_128x128@2x.png (256px)
        (256, 1),   # icon_256x256.png
        (256, 2),   # icon_256x256@2x.png (512px)
        (512, 1),   # icon_512x512.png
        (512, 2),   # icon_512x512@2x.png (1024px)
    ]

    try:
        for base_size, scale in apple_entries:
            pixel_size = base_size * scale
            if scale == 1:
                name = f"icon_{base_size}x{base_size}.png"
            else:
                name = f"icon_{base_size}x{base_size}@2x.png"
            out_path = os.path.join(iconset_dir, name)
            cmd = magick_cmd + [source, "-resize", f"{pixel_size}x{pixel_size}", out_path]
            subprocess.run(cmd, check=True)

        subprocess.run(
            ["iconutil", "-c", "icns", iconset_dir, "-o", icns_path],
            check=True,
        )
        print(f"  Created {icns_path}")
        return icns_path
    except subprocess.CalledProcessError as e:
        print(f"  Warning: Failed to create .icns via iconutil: {e}", file=sys.stderr)
        return None
    finally:
        shutil.rmtree(iconset_dir, ignore_errors=True)


def generate_icns_fallback(magick_cmd, output_dir):
    """Attempt to generate .icns using ImageMagick (non-macOS fallback).

    ImageMagick may or may not support .icns writing depending on the build.
    """
    icns_path = os.path.join(output_dir, "app.icns")
    # Use a subset of sizes that .icns typically contains
    png_inputs = [
        os.path.join(output_dir, f"app_{s}x{s}.png")
        for s in ICNS_SIZES
        if os.path.exists(os.path.join(output_dir, f"app_{s}x{s}.png"))
    ]

    # For sizes we have PNGs for, use them; for 512 we need to generate one
    png_512 = os.path.join(output_dir, "app_512x512.png")
    if not os.path.exists(png_512) and png_inputs:
        # We don't have a 512px PNG in our standard set; skip it
        pass

    if not png_inputs:
        print("  Warning: No PNGs available for .icns generation.", file=sys.stderr)
        return None

    cmd = magick_cmd + png_inputs + [icns_path]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"  Created {icns_path}")
        return icns_path
    except subprocess.CalledProcessError:
        print(
            "  Warning: ImageMagick cannot write .icns on this platform.",
            file=sys.stderr,
        )
        print(
            "  To generate .icns, run this script on macOS or use a dedicated tool.",
            file=sys.stderr,
        )
        return None


def generate_icns(magick_cmd, source, output_dir):
    """Generate .icns, choosing the best method for the current platform."""
    if platform.system() == "Darwin":
        return generate_icns_macos(magick_cmd, source, output_dir)
    else:
        return generate_icns_fallback(magick_cmd, output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Generate cross-platform icon files from a source image.",
    )
    parser.add_argument(
        "source",
        help="Path to the high-resolution source image (PNG recommended).",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join("resources", "icons"),
        help="Output directory (default: resources/icons).",
    )
    args = parser.parse_args()

    source = os.path.abspath(args.source)
    output_dir = os.path.abspath(args.output_dir)

    # Validate source file exists
    if not os.path.isfile(source):
        print(f"Error: Source file not found: {source}", file=sys.stderr)
        sys.exit(1)

    # Detect ImageMagick
    print("Detecting ImageMagick...")
    magick_cmd = find_magick()
    print(f"  Using: {' '.join(magick_cmd)}")

    # Validate source image
    print("Validating source image...")
    identify_image(magick_cmd, source)
    print(f"  Source: {source}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate individual PNGs
    print("Generating individual PNGs...")
    generate_pngs(magick_cmd, source, output_dir)

    # Copy primary PNG (Linux default)
    print("Creating primary Linux icon...")
    copy_primary_png(output_dir)

    # Generate .ico (Windows)
    print("Generating .ico (Windows)...")
    generate_ico(magick_cmd, output_dir)

    # Generate .icns (macOS)
    print("Generating .icns (macOS)...")
    generate_icns(magick_cmd, source, output_dir)

    # Summary
    print("\nDone. Generated files:")
    for f in sorted(os.listdir(output_dir)):
        full = os.path.join(output_dir, f)
        size_kb = os.path.getsize(full) / 1024
        print(f"  {f:24s} {size_kb:>8.1f} KB")


if __name__ == "__main__":
    main()
