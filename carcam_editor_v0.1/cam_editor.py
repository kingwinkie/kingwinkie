#!/usr/bin/env python3
"""
NR2003 Car Camera (.cam) File Editor
Format: "MACC" + 4-byte int + 55 4-byte floats (220 bytes)
Total file size: 228 bytes
"""

import struct
import sys
import os

CAMERA_NAMES = [
    "nose",
    "gearbox",
    "zeppelin/shoulder",
    "front suspension",
    "rear suspension",
    "roll bar",  # Camera 6 - user selectable in game
]
FIELD_NAMES = ["x", "y", "z", "yaw", "pitch", "bank", "zoom", "unknown1", "unknown2"]

CAMERA_DESCRIPTIONS = {
    "nose": "Forward-facing camera at front of car",
    "gearbox": "Rear-facing camera at transmission",
    "zeppelin/shoulder": "Overhead chase camera",
    "front suspension": "Camera focused on front wheels",
    "rear suspension": "Camera focused on rear wheels",
    "roll bar": "Interior/roll bar camera view",
}

FIELD_DESCRIPTIONS = {
    "x": "Horizontal position (left/right), in meters from car center",
    "y": "Vertical position (up/down), in meters from car center",
    "z": "Forward/back position, in meters from car center",
    "yaw": "Rotation around vertical axis (radians, 0 = forward)",
    "pitch": "Rotation around lateral axis (radians)",
    "bank": "Rotation around longitudinal axis (radians)",
    "zoom": "Field of view / zoom (higher = closer, ~1.36 = default)",
    "unknown1": "Unknown - may be FOV or distance multiplier",
    "unknown2": "Unknown - often ~-0.125, possibly a flag/indicator",
}

NR2003_NOTES = """
Camera Notes for NR2003:
- Camera positions (x, y, z) are in meters from car center
- Yaw values are often multiples of π (180°, 360°, etc.)
- Zoom values typically range from ~1.0 to 3.0+ (higher = closer)
- The 6 cameras are selected in-game via number keys or UI
- make_a.cam is the default NR2003 camera file
"""


def show_help():
    """Show comprehensive help and documentation"""
    print("=" * 70)
    print("NR2003 Car Camera (.cam) File Editor")
    print("=" * 70)
    print()
    print("FILE FORMAT:")
    print("-" * 70)
    print("  Total size: 228 bytes")
    print("  Bytes 0-3:   'MACC' header (magic number)")
    print("  Bytes 4-7:   Unknown int (always 0)")
    print("  Bytes 8-227: 55 floats (220 bytes)")
    print()
    print("  Structure: 1 header float + 6 cameras × 9 fields = 55 floats")
    print()
    print("CAMERA TYPES (6 cameras):")
    print("-" * 70)
    for i, name in enumerate(CAMERA_NAMES):
        desc = CAMERA_DESCRIPTIONS.get(name, "")
        print(f"  {i}: {name:20s} - {desc}")
    print()
    print("FIELD DESCRIPTIONS (9 fields per camera):")
    print("-" * 70)
    for i, name in enumerate(FIELD_NAMES):
        desc = FIELD_DESCRIPTIONS.get(name, "")
        print(f"  {i}: {name:10s} - {desc}")
    print()
    print("INDEX MAPPING (float index = 1 + camera_idx * 9 + field_idx):")
    print("-" * 70)
    print("           x   y   z   yaw pitch bank zoom unk1 unk2")
    for cam_idx, cam_name in enumerate(CAMERA_NAMES):
        indices = [1 + cam_idx * 9 + f for f in range(9)]
        print(
            f"  {cam_name:20s}: {indices[0]:2d}  {indices[1]:2d}  {indices[2]:2d}  {indices[3]:2d}   {indices[4]:2d}   {indices[5]:2d}  {indices[6]:2d}  {indices[7]:2d}  {indices[8]:2d}"
        )
    print()
    print(NR2003_NOTES)
    print("USAGE EXAMPLES:")
    print("-" * 70)
    print("  python3 cam_editor.py <file.cam>           # View camera settings")
    print("  python3 cam_editor.py <file.cam> dump     # Dump to file.cam.txt")
    print("  python3 cam_editor.py <file.cam> dump!    # Dump to stdout")
    print("  python3 cam_editor.py <file.cam> <idx> <val>  # Edit float by index")
    print("  python3 cam_editor.py <f1.cam> <f2.cam>  # Compare two files")
    print()
    print("EXAMPLE - Editing make_a.cam for NR2003:")
    print("-" * 70)
    print("  # First dump current values:")
    print("  python3 cam_editor.py make_a.cam dump")
    print()
    print("  # Set nose camera zoom (index 7) to 2.0:")
    print("  python3 cam_editor.py make_a.cam 7 2.0")
    print()
    print("  # Set zeppelin zoom (index 25) to 2.5:")
    print("  python3 cam_editor.py make_a.cam 25 2.5")
    print()
    print("SAMPLE VALUES FROM REFERENCE FILES:")
    print("-" * 70)
    print()

    # Show sample values
    print("SAMPLE VALUES:")
    print("-" * 70)

    if os.path.exists("make_a.cam"):
        try:
            data = read_cam("make_a.cam")
            floats = data["floats"]
            print(f"make_a.cam (NR2003 default):")
            print(
                f"  Nose:     x={floats[1]:7.3f} y={floats[2]:7.3f} z={floats[3]:7.3f} zoom={floats[7]:7.3f}"
            )
            print(
                f"  Gearbox:  x={floats[10]:7.3f} y={floats[11]:7.3f} z={floats[12]:7.3f} zoom={floats[16]:7.3f}"
            )
            print(
                f"  Zeppelin: x={floats[19]:7.3f} y={floats[20]:7.3f} z={floats[21]:7.3f} zoom={floats[25]:7.3f}"
            )
            print(
                f"  Front Susp: x={floats[28]:7.3f} z={floats[30]:7.3f} yaw={floats[31]:7.3f}"
            )
            print(
                f"  Rear Susp:  x={floats[37]:7.3f} z={floats[39]:7.3f} yaw={floats[40]:7.3f}"
            )
        except Exception as e:
            print(f"  (could not load make_a.cam: {e})")


def get_field_index(camera_idx, field_idx):
    """Convert camera+field to float index"""
    return 1 + camera_idx * 9 + field_idx


def read_cam(filename):
    """Read a .cam file and return the raw bytes and parsed floats"""
    with open(filename, "rb") as f:
        data = f.read()

    if len(data) < 8:
        raise ValueError(f"File too small: {len(data)} bytes")

    header = data[:4]
    if header != b"MACC":
        raise ValueError(f"Invalid header: {header!r} (expected b'MACC')")

    unknown_int = struct.unpack("<I", data[4:8])[0]
    floats = struct.unpack("<55f", data[8:])

    return {
        "filename": filename,
        "header": header,
        "unknown_int": unknown_int,
        "floats": list(floats),
        "raw": data,
    }


def write_cam(filename, data):
    """Write a .cam file from the parsed data structure"""
    header = data["header"]
    unknown_int = data["unknown_int"]
    floats = data["floats"]

    raw = header + struct.pack("<I", unknown_int) + struct.pack("<55f", *floats)

    with open(filename, "wb") as f:
        f.write(raw)


def print_cam_detailed(data):
    """Print the contents of a .cam file with camera names"""
    print(f"File: {data['filename']}")
    print(f"Header: {data['header']}")
    print(f"Unknown int: {data['unknown_int']}")
    print()
    print("Cameras:")
    print("=" * 70)

    floats = data["floats"]
    for cam_idx in range(6):
        print(f"{CAMERA_NAMES[cam_idx].upper()}:")
        for field_idx in range(9):
            float_idx = 1 + cam_idx * 9 + field_idx
            val = floats[float_idx]
            print(f"  {FIELD_NAMES[field_idx]:10s} [{float_idx:2d}]: {val:12.6f}")
        print()


def compare_cam(data1, data2):
    """Compare two .cam files and show differences"""
    print(f"Comparing: {data1['filename']} vs {data2['filename']}")
    print()
    print("Index | File1         | File2         | Diff")
    print("-" * 55)

    diffs = []
    for i in range(55):
        v1, v2 = data1["floats"][i], data2["floats"][i]
        diff = v2 - v1
        if abs(diff) > 0.0001:
            diffs.append((i, v1, v2, diff))
            print(f"  {i:2d} | {v1:12.6f} | {v2:12.6f} | {diff:12.6f}")

    if not diffs:
        print("  (no significant differences)")

    return diffs


def edit_cam(filename, index, value):
    """Edit a single float value in a .cam file"""
    data = read_cam(filename)
    old_value = data["floats"][index]
    data["floats"][index] = float(value)
    write_cam(filename, data)
    print(f"Changed float[{index}] from {old_value} to {value}")
    return data


def dump_cam(filename, output_file=None):
    """Dump camera values to a file with labels"""
    data = read_cam(filename)
    floats = data["floats"]

    lines = []
    lines.append(f"# Camera file: {filename}")
    lines.append(f"# Header: {data['header']}")
    lines.append(f"# Generated by cam_editor.py")
    lines.append("")
    lines.append(f"# Header float (index 0)")
    lines.append(f"_header={floats[0]}")
    lines.append("")

    for cam_idx in range(6):
        cam_name = CAMERA_NAMES[cam_idx]
        lines.append(f"# Camera {cam_idx}: {cam_name}")
        for field_idx in range(9):
            float_idx = 1 + cam_idx * 9 + field_idx
            val = floats[float_idx]
            field_name = FIELD_NAMES[field_idx]
            lines.append(f"{cam_name}.{field_name}={val}")
        lines.append("")

    output = "\n".join(lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
        print(f"Dumped to {output_file}")
    else:
        print(output)
    return data


def load_cam(dump_file, output_cam):
    """Load camera values from a dump file"""
    floats = [0.0] * 55  # Initialize with defaults

    with open(dump_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, val = line.split("=", 1)
            float_val = float(val)

            if key == "_header":
                floats[0] = float_val
                continue

            # Parse key like "nose.x" or "gearbox.zoom"
            parts = key.split(".")
            if len(parts) != 2:
                continue

            cam_name = parts[0]
            field_name = parts[1]

            try:
                cam_idx = CAMERA_NAMES.index(cam_name)
                field_idx = FIELD_NAMES.index(field_name)
                float_idx = 1 + cam_idx * 9 + field_idx
                floats[float_idx] = float_val
            except ValueError:
                pass  # Unknown camera or field

    # Write the cam file
    header = b"MACC"
    unknown_int = 0
    raw = header + struct.pack("<I", unknown_int) + struct.pack("<55f", *floats)

    with open(output_cam, "wb") as f:
        f.write(raw)

    print(f"Loaded values from {dump_file} to {output_cam}")
    return read_cam(output_cam)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    if len(sys.argv) == 2:
        # View file
        data = read_cam(sys.argv[1])
        print_cam_detailed(data)

    elif len(sys.argv) == 3:
        arg2 = sys.argv[2]
        if arg2 == "dump":
            # Dump to file with same name + .txt
            dump_cam(sys.argv[1], sys.argv[1] + ".txt")
        elif arg2 == "dump!":
            # Dump to stdout
            dump_cam(sys.argv[1])
        elif arg2 == "restore":
            # Restore from backup
            backup_file = sys.argv[1] + ".txt"
            if os.path.exists(backup_file):
                load_cam(backup_file, sys.argv[1])
            else:
                print(f"Backup file not found: {backup_file}")
                print("Run 'dump' first to create a backup")
        else:
            # Compare files
            data1 = read_cam(sys.argv[1])
            data2 = read_cam(sys.argv[2])
            compare_cam(data1, data2)

    elif len(sys.argv) == 4:
        arg2 = sys.argv[2]
        if arg2 == "dump":
            dump_cam(sys.argv[1], sys.argv[3])
        elif arg2 == "load":
            load_cam(sys.argv[1], sys.argv[3])
        else:
            filename = sys.argv[1]
            index = int(sys.argv[2])
            value = float(sys.argv[3])
            edit_cam(filename, index, value)

    elif len(sys.argv) == 5:
        if sys.argv[3] == "dump":
            # Dump to specific file
            dump_cam(sys.argv[1], sys.argv[4])
        elif sys.argv[3] == "load":
            # Load from dump file
            load_cam(sys.argv[2], sys.argv[4])
        else:
            print("Unknown command")
            sys.exit(1)

    else:
        print("Unknown command")
        print("Usage:")
        print("  python3 cam_editor.py <file.cam>           # View")
        print("  python3 cam_editor.py <file.cam> dump     # Dump to file.cam.txt")
        print("  python3 cam_editor.py <file.cam> dump!    # Dump to stdout")
        print("  python3 cam_editor.py <file.cam> restore  # Restore from file.cam.txt")
        print("  python3 cam_editor.py <file.cam> <idx> <val>  # Edit")
        print("  python3 cam_editor.py <f1> <f2>           # Compare")
        sys.exit(1)
