Look in the dist folder for single file cmds

# NR2003 Controls.cfg Editor

Tool for reading and modifying NASCAR Racing 2003 Season control mappings.

## Quick Start

```bash
cd tools/controls_editor

# List current controls
python3 controls_editor.py controls.cfg --list

# Show joystick calibration
python3 controls_editor.py controls.cfg --cal
```

## Changing Controls

```bash
# Change Steer to W key
python3 controls_editor.py controls.cfg --set 1 keyboard w -o modified.cfg

# Change Throttle to SPACE
python3 controls_editor.py controls.cfg --set 2 keyboard space -o modified.cfg

# Change Brake to joystick button 1
python3 controls_editor.py controls.cfg --set 3 joystick 1 -o modified.cfg
```

## Function IDs

| ID | Function |
|----|----------|
| 1 | Steer |
| 2 | Throttle |
| 3 | Brake |
| 4 | Clutch |
| 5 | Shift Up |
| 6 | Shift Down |
| 7 | Look Left |
| 8 | Look Right |
| 9 | Cockpit View |
| 10 | Pause |
| 11 | Reverse |
| 12 | Raise Arm |

## Device Types

- `keyboard` (7)
- `joystick` (2)
- `mouse` (1)

## File Format

The `controls.cfg` file has a simple binary format:

- **Header** (0x00-0x3F): `CCFG` magic, version
- **Joystick Calibration** (0x40-0x1FF): `PJOY` section
- **Control Bindings** (0x250+): `CTRL` section

### Forcefeedback

Forcefeedback is stored in the header:
- Offset 0x24: Enable flag (1 = enabled)
- Offset 0x25: Strength (0-100)

```bash
# Set forcefeedback to 50%
python3 controls_editor.py controls.cfg --ff 50

# Set forcefeedback to 0% (min)
python3 controls_editor.py controls.cfg --ff 0

# Set forcefeedback to 100% (max - default)
python3 controls_editor.py controls.cfg --ff 100

# Extended range: Set forcefeedback to 150% (can go up to 255)
python3 controls_editor.py controls.cfg --ff 150
```

### Steering/Wheel Parameters

Additional wheel settings are stored in the header:

| Offset | Size | Parameter | Typical Range |
|--------|------|-----------|---------------|
| 0x12 | 2 bytes | Steering Linearity | 0-100 |
| 0x16 | 2 bytes | Input Momentum Steering | 0-100 |
| 0x1A | 2 bytes | Input Momentum Throttle | 0-100 |
| 0x1E | 2 bytes | Input Momentum Brakes | 0-100 |
| 0x22 | 1 byte | Steering Boost (0=off, 1=on) | 0-1 |
| 0x24 | 1 byte | Forcefeedback Enable | 0-1 |
| 0x25 | 1 byte | Forcefeedback Strength | 0-255 |
| 0x26 | 2 bytes | Wheel Damping | 0-100 |
| 0x28 | 2 bytes | Wheel Latency | 0-255 |

```python
# Example: Read steering linearity
with open('controls.cfg', 'rb') as f:
    f.seek(0x12)
    linearity = struct.unpack('<H', f.read(2))[0]
```

Each control entry is 0x60 bytes:
- Offset +0x04: Device type (1=mouse, 2=joystick, 7=keyboard)
- Offset +0x08: Key/button code
- Offset +0x0C: Function ID

Note: The file uses reversed 4-byte strings (`CCFG`, `PJOY`, `CTRL`) - this is how Papyrus stored them in the original game.
