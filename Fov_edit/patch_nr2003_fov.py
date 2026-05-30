#!/usr/bin/env python3
"""
NR2003 FOV and Widescreen Patcher
Patches nr2003.exe to extend FOV range and enable widescreen support.
"""

import struct
import os
import sys
import argparse

DEFAULT_EXE = "nr2003.exe"
OUTPUT_EXE = "nr2003_patched.exe"
DEFAULT_DLL = "rend_ogl.dll"

TACH_EXCLUDE_ADDRESSES = [0x00320ACC, 0x00320B3C, 0x00320B9C]

PATCH_FOV_MIN = False  # WARNING: Patching FOV min breaks tachometer!


def get_float_bytes(value):
    return struct.pack("<f", float(value))


def patch_exe(
    exe_path, output_path, fov_min, fov_max, aspect_ratio="16:9", patch_fov_min=False
):
    """Patch the exe with new FOV range and aspect ratio."""

    with open(exe_path, "rb") as f:
        data = bytearray(f.read())

    original_data = bytes(data)

    # Calculate aspect ratio inverse
    aspect_map = {
        "4:3": (1.3333, 0.75),
        "16:9": (1.7778, 0.5625),
        "16:10": (1.6, 0.625),
    }

    if aspect_ratio not in aspect_map:
        print(f"Unknown aspect ratio: {aspect_ratio}")
        print(f"Using 16:9")
        aspect_ratio = "16:9"

    aspect_val = aspect_map[aspect_ratio][1]
    print(f"Using aspect ratio: {aspect_ratio} (inverse: {aspect_val})")

    # Patch aspect ratio (0.75 -> new value)
    old_aspect = get_float_bytes(0.75)
    new_aspect = get_float_bytes(aspect_val)

    aspect_count = 0
    for i in range(len(data) - 3):
        if data[i : i + 4] == old_aspect:
            if i not in TACH_EXCLUDE_ADDRESSES:
                data[i : i + 4] = new_aspect
                aspect_count += 1

    print(f"Patched {aspect_count} aspect ratio values")

    # Patch FOV min (disabled by default - breaks tachometer)
    if patch_fov_min:
        old_min = get_float_bytes(65.0)
        new_min = get_float_bytes(float(fov_min))

        min_count = 0
        for i in range(len(data) - 3):
            if data[i : i + 4] == old_min:
                data[i : i + 4] = new_min
                min_count += 1

        print(f"Patched {min_count} min FOV values (65 -> {fov_min})")
    else:
        print("Skipped FOV min patching (PATCH_FOV_MIN = False)")

    # Patch FOV max
    old_max = get_float_bytes(78.0)
    new_max = get_float_bytes(float(fov_max))

    max_count = 0
    for i in range(len(data) - 3):
        if data[i : i + 4] == old_max:
            data[i : i + 4] = new_max
            max_count += 1

    print(f"Patched {max_count} max FOV values (78 -> {fov_max})")

    # Check if anything changed
    if data == original_data:
        print(
            "Warning: No changes made - exe may already be patched or values not found"
        )

    # Save output
    with open(output_path, "wb") as f:
        f.write(data)

    print(f"\nSaved patched exe to: {output_path}")
    return True


def patch_dll(dll_path, aspect_ratio):
    """Patch the rend_ogl.dll with new aspect ratio."""

    if not os.path.exists(dll_path):
        print(f"Warning: DLL not found: {dll_path}")
        return False

    with open(dll_path, "rb") as f:
        data = bytearray(f.read())

    original_data = bytes(data)

    # Calculate aspect ratio inverse
    aspect_map = {
        "4:3": (1.3333, 0.75),
        "16:9": (1.7778, 0.5625),
        "16:10": (1.6, 0.625),
    }

    aspect_val = aspect_map[aspect_ratio][1]
    print(
        f"\nPatching rend_ogl.dll with aspect ratio: {aspect_ratio} (inverse: {aspect_val})"
    )

    # Patch aspect ratio (0.75 -> new value)
    old_aspect = get_float_bytes(0.75)
    new_aspect = get_float_bytes(aspect_val)

    aspect_count = 0
    for i in range(len(data) - 3):
        if data[i : i + 4] == old_aspect:
            data[i : i + 4] = new_aspect
            aspect_count += 1

    print(f"Patched {aspect_count} aspect ratio values in DLL")

    # Check if anything changed
    if data == original_data:
        print("Warning: No changes made to DLL - values not found or already patched")
        return False

    # Save output
    with open(dll_path, "wb") as f:
        f.write(data)

    print(f"Patched DLL saved to: {dll_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="NR2003 FOV and Widescreen Patcher")
    parser.add_argument("--exe", default=DEFAULT_EXE, help="Path to nr2003.exe")
    parser.add_argument(
        "--output", default=OUTPUT_EXE, help="Output path for patched exe"
    )
    parser.add_argument(
        "--fov-min", type=float, default=30, help="Minimum FOV (default: 30)"
    )
    parser.add_argument(
        "--fov-max", type=float, default=97, help="Maximum FOV (default: 97)"
    )
    parser.add_argument(
        "--aspect",
        choices=["16:9", "16:10", "4:3"],
        default="16:9",
        help="Aspect ratio (default: 16:9)",
    )
    parser.add_argument(
        "--no-dll", action="store_true", help="Skip patching rend_ogl.dll"
    )
    parser.add_argument(
        "--patch-fov-min",
        action="store_true",
        default=False,
        help="Patch FOV min (WARNING: breaks tachometer!)",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("NR2003 FOV and Widescreen Patcher")
    print("=" * 50)

    exe_path = args.exe

    if not os.path.exists(exe_path):
        print(f"Error: File not found: {exe_path}")
        sys.exit(1)

    fov_min = args.fov_min
    fov_max = args.fov_max
    aspect_ratio = args.aspect
    output_path = args.output
    patch_fov_min = args.patch_fov_min

    if fov_min >= fov_max:
        print("Error: Min FOV must be less than Max FOV")
        sys.exit(1)

    if fov_max > 97.1:
        print("\n*** WARNING: Values > 97.10 break the rearview mirror! ***\n")

    print(f"\nSettings:")
    print(f"  Exe: {exe_path}")
    print(f"  Output: {output_path}")
    print(f"  FOV Range: {fov_min} - {fov_max}")
    print(f"  Aspect Ratio: {aspect_ratio}")

    # Do the patch
    print("\n" + "=" * 50)
    patch_exe(exe_path, output_path, fov_min, fov_max, aspect_ratio, patch_fov_min)
    print("=" * 50)

    # Also patch the rendering DLL
    if not args.no_dll:
        dll_path = os.path.join(os.path.dirname(exe_path), "rend_ogl.dll")
        patch_dll(dll_path, aspect_ratio)

    print("=" * 50)

    # Update player.ini
    ini_path = os.path.join(
        os.path.dirname(exe_path), "players", "Player__The", "player.ini"
    )
    if os.path.exists(ini_path):
        with open(ini_path, "r") as f:
            ini_content = f.read()

        # Update field_of_view if found
        if "field_of_view=" in ini_content:
            import re

            ini_content = re.sub(
                r"field_of_view=[\d.]+", f"field_of_view={fov_max}", ini_content
            )
            with open(ini_path, "w") as f:
                f.write(ini_content)
            print(f"Updated player.ini field_of_view to {fov_max}")


if __name__ == "__main__":
    main()
