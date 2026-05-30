#!/usr/bin/env python3
"""
NR2003 FOV Max Patcher Only
Patches only the max FOV value (78.0 -> higher), no aspect ratio changes.
"""

import struct
import os
import sys
import argparse

DEFAULT_EXE = "nr2003.exe"
OUTPUT_EXE = "nr2003_patched.exe"


def get_float_bytes(value):
    return struct.pack("<f", float(value))


def patch_fov_max_only(exe_path, output_path, fov_max):
    """Patch only FOV max (78.0 -> new value)."""

    with open(exe_path, "rb") as f:
        data = bytearray(f.read())

    original_data = bytes(data)

    print(f"Patching FOV max: 78.0 -> {fov_max}")

    # Patch FOV max only
    old_max = get_float_bytes(78.0)
    new_max = get_float_bytes(float(fov_max))

    max_count = 0
    for i in range(len(data) - 3):
        if data[i : i + 4] == old_max:
            data[i : i + 4] = new_max
            max_count += 1

    print(f"Patched {max_count} max FOV values")

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


def main():
    parser = argparse.ArgumentParser(description="NR2003 FOV Max Patcher")
    parser.add_argument("--exe", default=DEFAULT_EXE, help="Path to nr2003.exe")
    parser.add_argument(
        "--output", default=OUTPUT_EXE, help="Output path for patched exe"
    )
    parser.add_argument(
        "--fov-max", type=float, default=97, help="Maximum FOV (default: 97)"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("NR2003 FOV Max Patcher (No Aspect Ratio)")
    print("=" * 50)

    exe_path = args.exe

    if not os.path.exists(exe_path):
        print(f"Error: File not found: {exe_path}")
        sys.exit(1)

    fov_max = args.fov_max
    output_path = args.output

    if fov_max > 97.1:
        print("\n*** WARNING: Values > 97.10 break the rearview mirror! ***\n")

    print(f"\nSettings:")
    print(f"  Exe: {exe_path}")
    print(f"  Output: {output_path}")
    print(f"  FOV Max: {fov_max} (min stays at 65)")

    # Do the patch
    print("\n" + "=" * 50)
    patch_fov_max_only(exe_path, output_path, fov_max)
    print("=" * 50)


if __name__ == "__main__":
    main()
