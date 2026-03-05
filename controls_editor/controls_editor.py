#!/usr/bin/env python3
"""
NR2003 Controls.cfg Reader/Writer
Decodes and modifies the controls.cfg file used by NASCAR Racing 2003 Season
"""

import struct
import sys
import os

CONTROL_FUNCTIONS = {
    0: "None",
    1: "Steer",
    2: "Throttle",
    3: "Brake",
    4: "Clutch",
    5: "Shift Up",
    6: "Shift Down",
    7: "Look Left",
    8: "Look Right",
    9: "Cockpit View",
    10: "Pause",
    11: "Reverse",
    12: "Raise Arm",
    13: "Neutral",
    14: "Enter",
    15: "F11/F12",
    16: "Ctrl+C",
    17: "L Key",
    18: "Camera Up",
    19: "Camera Down",
    20: "Toggle Mirror",
}

KEYBOARD_SCAN_CODES = {
    0x01: "ESC",
    0x02: "1",
    0x03: "2",
    0x04: "3",
    0x05: "4",
    0x06: "5",
    0x07: "6",
    0x08: "7",
    0x09: "8",
    0x0A: "9",
    0x0B: "0",
    0x0C: "-",
    0x0D: "=",
    0x0E: "BKSP",
    0x0F: "TAB",
    0x10: "Q",
    0x11: "W",
    0x12: "E",
    0x13: "R",
    0x14: "T",
    0x15: "Y",
    0x16: "U",
    0x17: "I",
    0x18: "O",
    0x19: "P",
    0x1A: "[",
    0x1B: "]",
    0x1C: "ENTER",
    0x1D: "LCTRL",
    0x1E: "A",
    0x1F: "S",
    0x20: "D",
    0x21: "F",
    0x22: "G",
    0x23: "H",
    0x24: "J",
    0x25: "K",
    0x26: "L",
    0x27: ";",
    0x28: "'",
    0x29: "`",
    0x2A: "LSHIFT",
    0x2B: "\\",
    0x2C: "Z",
    0x2D: "X",
    0x2E: "C",
    0x2F: "V",
    0x30: "B",
    0x31: "N",
    0x32: "M",
    0x33: ",",
    0x34: ".",
    0x35: "/",
    0x36: "RSHIFT",
    0x37: "NUMPAD*",
    0x38: "LALT",
    0x39: "SPACE",
    0x3A: "CAPS",
    0x3B: "F1",
    0x3C: "F2",
    0x3D: "F3",
    0x3E: "F4",
    0x3F: "F5",
    0x40: "F6",
    0x41: "F7",
    0x42: "F8",
    0x43: "F9",
    0x44: "F10",
    0x45: "NUMLOCK",
    0x46: "SCROLL",
    0x47: "NUMPAD7",
    0x48: "NUMPAD8",
    0x49: "NUMPAD9",
    0x4A: "NUMPAD-",
    0x4B: "NUMPAD4",
    0x4C: "NUMPAD5",
    0x4D: "NUMPAD6",
    0x4E: "NUMPAD+",
    0x4F: "NUMPAD1",
    0x50: "NUMPAD2",
    0x51: "NUMPAD3",
    0x52: "NUMPAD0",
    0x53: "NUMPAD.",
    0x54: "F11",
    0x55: "F12",
}

KEYBOARD_SCAN_CODES_REVERSE = {v: k for k, v in KEYBOARD_SCAN_CODES.items()}

DEVICE_TYPES = {
    1: "Mouse",
    2: "Joystick",
    3: "Wheel",
    4: "Pedals",
    5: "Gamepad",
    6: "Wheel Axis",
    7: "Keyboard",
}

DEVICE_TYPES_REVERSE = {v: k for k, v in DEVICE_TYPES.items()}


class ControlsFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None
        self.controls = []

    def load(self):
        """Load the controls.cfg file"""
        with open(self.filepath, "rb") as f:
            self.data = bytearray(f.read())

        self._parse_controls()
        return self

    def _parse_controls(self):
        """Parse control bindings from the file"""
        self.controls = []

        for offset in range(0x240, len(self.data) - 20, 4):
            try:
                dev_type = self.data[offset + 4]
                if dev_type in [1, 2, 3, 4, 5, 6, 7]:
                    key_code = self.data[offset + 8]
                    func_id = struct.unpack("<I", self.data[offset + 12 : offset + 16])[
                        0
                    ]

                    if key_code < 128 and func_id < 50:
                        self.controls.append(
                            {
                                "offset": offset,
                                "device_type": dev_type,
                                "key_code": key_code,
                                "function_id": func_id,
                            }
                        )
            except:
                pass

    def save(self, filepath=None):
        """Save the controls.cfg file"""
        if filepath is None:
            filepath = self.filepath

        with open(filepath, "wb") as f:
            f.write(self.data)

    def get_device_name(self, dev_type):
        """Get device name from type"""
        return DEVICE_TYPES.get(dev_type, f"Unknown({dev_type})")

    def get_key_name(self, dev_type, key_code):
        """Get key/button name"""
        if dev_type == 7:
            return KEYBOARD_SCAN_CODES.get(key_code, f"0x{key_code:02X}")
        elif dev_type in [2, 3, 4, 5, 6]:
            return f"Axis/Button {key_code}"
        else:
            return f"Button {key_code}"

    def get_function_name(self, func_id):
        """Get function name from ID"""
        return CONTROL_FUNCTIONS.get(func_id, f"Function {func_id}")

    def print_controls(self):
        """Print all controls in human-readable format"""
        print("\n" + "=" * 75)
        print("CONTROLS.CFG CONTENTS")
        print("=" * 75)

        # Header info
        magic = self.data[0:4][::-1].decode()
        version = struct.unpack("<I", self.data[8:12])[0]
        print(f"\nFile: {self.filepath}")
        print(f"Magic: {magic}")
        print(f"Version: {version}")
        print(f"Total control bindings: {len(self.controls)}")

        # Group by function
        print("\n" + "-" * 75)
        print("CONTROLS BY FUNCTION")
        print("-" * 75)
        print(f"{'Function':<20} {'Device':<12} {'Input':<15} {'Offset':<10}")
        print("-" * 75)

        # Remove duplicates based on key+function
        seen = set()
        unique = []
        for c in self.controls:
            key = (c["key_code"], c["function_id"])
            if key not in seen:
                seen.add(key)
                unique.append(c)

        # Sort by function
        unique.sort(key=lambda x: x["function_id"])

        for c in unique:
            func_name = self.get_function_name(c["function_id"])
            dev_name = self.get_device_name(c["device_type"])
            key_name = self.get_key_name(c["device_type"], c["key_code"])
            print(f"{func_name:<20} {dev_name:<12} {key_name:<15} 0x{c['offset']:04X}")

    def set_control(self, function_id, device_type, key_code):
        """
        Set a control binding
        function_id: Control function to bind (1-20)
        device_type: 7=Keyboard, 2=Joystick, 1=Mouse
        key_code: Key code (keyboard scan code) or button number
        """
        # Find existing entry for this function or create new
        # For simplicity, we'll update the first matching function

        for c in self.controls:
            if c["function_id"] == function_id and c["device_type"] == device_type:
                # Update existing
                c["key_code"] = key_code
                self.data[c["offset"] + 8] = key_code
                return True

        # If not found, add to first available slot for this device type
        for offset in range(0x250, len(self.data) - 20, 4):
            try:
                current_dev = self.data[offset + 4]
                current_key = self.data[offset + 8]
                current_func = struct.unpack(
                    "<I", self.data[offset + 12 : offset + 16]
                )[0]

                # Find empty slot or slot with same device type
                if current_dev == device_type and current_func == 0:
                    self.data[offset + 4] = device_type
                    self.data[offset + 8] = key_code
                    struct.pack_into("<I", self.data, offset + 12, function_id)
                    self.controls.append(
                        {
                            "offset": offset,
                            "device_type": device_type,
                            "key_code": key_code,
                            "function_id": function_id,
                        }
                    )
                    return True
            except:
                pass

        return False

    def set_keyboard_control(self, function_id, key_name):
        """Set a keyboard control by key name"""
        key_code = KEYBOARD_SCAN_CODES_REVERSE.get(key_name.upper())
        if key_code is None:
            print(f"Unknown key: {key_name}")
            print(
                f"Available keys: {', '.join(sorted(KEYBOARD_SCAN_CODES_REVERSE.keys())[:20])}..."
            )
            return False

        return self.set_control(function_id, 7, key_code)

    def get_forcefeedback(self):
        """Get forcefeedback settings"""
        enabled = self.data[0x24]
        strength = self.data[0x25]
        return {"enabled": enabled, "strength": strength}

    def set_forcefeedback(self, strength):
        """
        Set forcefeedback strength (0-255, default range 0-100)

        NOTE: Extended range (0-255) added to allow testing values above 100%.
        Original game typically uses 0-100, but the field can hold 0-255.
        To revert to original 0-100 limit, change 255 to 100 below.
        """
        if strength < 0 or strength > 255:
            print("Forcefeedback strength must be 0-255")
            return False

        self.data[0x24] = 1
        self.data[0x25] = strength
        return True

    def print_forcefeedback(self):
        """Print forcefeedback settings"""
        ff = self.get_forcefeedback()
        print("\n" + "=" * 50)
        print("FORCEFEEDBACK SETTINGS")
        print("=" * 50)
        print(f"Enabled: {'Yes' if ff['enabled'] else 'No'}")
        print(f"Strength: {ff['strength']}%")

    def get_joystick_calibration(self):
        """Get joystick calibration data"""
        cal = []
        for i in range(5):
            base = 0x40 + (i * 0x40)
            vals = struct.unpack("<IIIIIIII", self.data[base : base + 0x20])
            cal.append(
                {
                    "joystick": i,
                    "center_x": vals[0],
                    "max_x": vals[1],
                    "min_x": vals[2],
                    "center_y": vals[3],
                    "max_y": vals[4],
                    "min_y": vals[5],
                }
            )
        return cal

    def print_joystick_calibration(self):
        """Print joystick calibration data"""
        print("\n" + "=" * 50)
        print("JOYSTICK CALIBRATION")
        print("=" * 50)

        cal = self.get_joystick_calibration()
        for c in cal:
            if c["max_x"] > 0 or c["max_y"] > 0:
                print(f"\nJoystick {c['joystick']}:")
                print(
                    f"  X axis: center={c['center_x']}, min={c['min_x']}, max={c['max_x']}"
                )
                print(
                    f"  Y axis: center={c['center_y']}, min={c['min_y']}, max={c['max_y']}"
                )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="NR2003 Controls.cfg Editor")
    parser.add_argument("file", nargs="?", help="Path to controls.cfg file")
    parser.add_argument(
        "--set",
        nargs=3,
        metavar=("FUNCTION", "DEVICE", "KEY"),
        help="Set a control binding",
    )
    parser.add_argument("--list", action="store_true", help="List all controls")
    parser.add_argument("--cal", action="store_true", help="Show joystick calibration")
    parser.add_argument(
        "--ff",
        "--forcefeedback",
        dest="forcefeedback",
        metavar="N",
        help="Set forcefeedback strength (0-100)",
    )
    parser.add_argument("--output", "-o", help="Output file (default: overwrite input)")

    args = parser.parse_args()

    if not args.file:
        # Try default location
        default_path = os.path.join(
            os.getcwd(), "players", "Player__The", "controls.cfg"
        )
        if os.path.exists(default_path):
            args.file = default_path
        else:
            print(
                "Usage: controls_editor.py <controls.cfg> [--list] [--set FUNCTION DEVICE KEY]"
            )
            print("\nFUNCTION IDs:")
            for k, v in CONTROL_FUNCTIONS.items():
                print(f"  {k}: {v}")
            print("\nDEVICE types:")
            print("  7: Keyboard")
            print("  2: Joystick")
            print("  1: Mouse")
            print("\nExamples:")
            print("  controls_editor.py controls.cfg --list")
            print("  controls_editor.py controls.cfg --set 1 keyboard w")
            print("  controls_editor.py controls.cfg --set 2 keyboard 3")
            return

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        return

    cf = ControlsFile(args.file).load()

    if args.list:
        cf.print_controls()

    if args.cal:
        cf.print_joystick_calibration()

    if args.forcefeedback is not None:
        try:
            strength = int(args.forcefeedback)
            if cf.set_forcefeedback(strength):
                output_file = args.output or args.file
                cf.save(output_file)
                print(f"Forcefeedback strength set to {strength}%")
                print(f"Saved to: {output_file}")
        except ValueError:
            print(f"Invalid forcefeedback value: {args.forcefeedback}")

    if args.set:
        func_name = args.set[0].lower()
        device_name = args.set[1].lower()
        key_name = args.set[2]

        # Parse function ID
        func_id = None
        for k, v in CONTROL_FUNCTIONS.items():
            if v.lower().replace(" ", "") == func_name.replace(" ", ""):
                func_id = k
                break
        if func_id is None:
            try:
                func_id = int(func_name)
            except:
                print(f"Unknown function: {func_name}")
                return

        # Parse device type - case insensitive lookup
        device_type = None
        for name, dtype in DEVICE_TYPES_REVERSE.items():
            if name.lower() == device_name.lower():
                device_type = dtype
                break
        if device_type is None:
            try:
                device_type = int(device_name)
            except:
                print(f"Unknown device: {device_name}")
                return

        # Set the control
        if device_type == 7:
            success = cf.set_keyboard_control(func_id, key_name)
        else:
            try:
                key_code = int(key_name)
                success = cf.set_control(func_id, device_type, key_code)
            except:
                print(f"Invalid key code: {key_name}")
                return

        if success:
            output_file = args.output or args.file
            cf.save(output_file)
            print(
                f"Control updated: Function {func_id} ({CONTROL_FUNCTIONS.get(func_id)}) -> {device_name} {key_name}"
            )
            print(f"Saved to: {output_file}")
        else:
            print("Failed to set control - no available slot found")

    # If no arguments, show help
    if not args.list and not args.set and not args.cal and args.forcefeedback is None:
        cf.print_controls()
        cf.print_forcefeedback()
        print("\nUse --help for usage information")


if __name__ == "__main__":
    main()
