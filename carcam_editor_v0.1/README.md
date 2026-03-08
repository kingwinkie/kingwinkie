# NR2003 Car Camera File Editor

Python tool for editing `.cam` camera files for **NASCAR Racing 2003 Season (NR2003)** by Papyrus.

The camera file `make_a.cam` is used by NR2003 for the default car camera positions.

## File Format

| Offset | Size | Description |
|--------|------|-------------|
| 0x00 | 4 bytes | "MACC" header (magic number) |
| 0x04 | 4 bytes | Unknown int (always 0) |
| 0x08 | 220 bytes | 55 floats (4 bytes each) |

### Structure

- **Float 0**: Header/unknown
- **Floats 1-9**: Camera 1 (nose)
- **Floats 10-18**: Camera 2 (gearbox)
- **Floats 19-27**: Camera 3 (zeppelin/shoulder)
- **Floats 28-36**: Camera 4 (front suspension)
- **Floats 37-45**: Camera 5 (rear suspension)
- **Floats 46-54**: Camera 6

### Camera Types

| Index | Name | Description |
|-------|------|-------------|
| 0 | nose | Forward-facing camera at front of car |
| 1 | gearbox | Rear-facing camera at transmission |
| 2 | zeppelin/shoulder | Overhead chase camera |
| 3 | front suspension | Camera focused on front wheels |
| 4 | rear suspension | Camera focused on rear wheels |
| 5 | roll bar | Interior/roll bar camera view |

### Fields (per camera)

| Index | Name | Description |
|-------|------|-------------|
| 0 | x | Horizontal position (left/right), in meters from car center |
| 1 | y | Vertical position (up/down), in meters from car center |
| 2 | z | Forward/back position, in meters from car center |
| 3 | yaw | Rotation around vertical axis (radians, 0 = forward) |
| 4 | pitch | Rotation around lateral axis (radians) |
| 5 | bank | Rotation around longitudinal axis (radians) |
| 6 | zoom | Field of view / zoom (higher = closer, ~1.36 = default) |
| 7 | unknown1 | Unknown - may be FOV or distance multiplier |
| 8 | unknown2 | Unknown - often ~-0.125, possibly a flag/indicator |

### Index Reference

```
           x   y   z   yaw pitch bank zoom unk1 unk2
nose                :  1   2   3   4    5    6   7   8   9
gearbox             : 10  11  12  13   14   15  16  17  18
zeppelin/shoulder   : 19  20  21  22   23   24  25  26  27
front suspension    : 28  29  30  31   32   33  34  35  36
rear suspension     : 37  38  39  40   41   42  43  44  45
roll bar            : 46  47  48  49   50   51  52  53  54
```

## Usage

```bash
# Show help and documentation
python3 cam_editor.py

# View a .cam file
python3 cam_editor.py make_a.cam

# Dump current values to file (for backup/starting point)
python3 cam_editor.py make_a.cam dump

# Dump to stdout
python3 cam_editor.py make_a.cam dump!

# Restore from backup file
python3 cam_editor.py make_a.cam restore

# Compare two files
python3 cam_editor.py make_a.cam make_a.camorg

# Edit a value by index
python3 cam_editor.py make_a.cam 7 2.5
# This sets float index 7 (nose camera zoom) to 2.5
```

## Editing Examples

### First: Dump Starting Values

```bash
# Always dump first to have a backup!
python3 cam_editor.py make_a.cam dump
# Creates make_a.cam.txt with all current values
```

### Common Edits for NR2003

```bash
# Set nose camera zoom (index 7)
python3 cam_editor.py make_a.cam 7 2.0

# Set nose camera position (indices 1, 2, 3 are x, y, z)
python3 cam_editor.py make_a.cam 1 1.5
python3 cam_editor.py make_a.cam 2 0.0
python3 cam_editor.py make_a.cam 3 0.3

# Set gearbox zoom (index 16)
python3 cam_editor.py make_a.cam 16 1.8

# Set zeppelin zoom (index 25)
python3 cam_editor.py make_a.cam 25 2.5
```

### Restore Original Values

```bash
# If something goes wrong, restore from backup
python3 cam_editor.py make_a.cam restore

# Or restore from original backup
cp make_a.camorg make_a.cam
```

## Files

- `make_a.cam` - NR2003 camera file (edit this)
- `make_a.camorg` - Original backup of make_a.cam
- `make_a.cam.txt` - Dumped values (created by `dump` command)

## Notes

- Values are stored as 32-bit floats (IEEE 754)
- Position values (x, y, z) are in meters relative to car center
- Rotation values (yaw, pitch, bank) are in radians
- Yaw values in NR2003 are often multiples of π (180° = 3.14159, 360° = 6.28318)
- Zoom values typically range from ~1.0 to 3.0+ (higher = closer)
