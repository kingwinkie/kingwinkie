# NR2003 FOV Patcher - Tachometer Issue

## Summary

Patching FOV min (65.0 → lower value) **breaks the tachometer**. The FOV min value is directly used in tachometer calculations.

## What Works

| Patch | FOV Range | Tachometer |
|-------|-----------|------------|
| Aspect ratio only (0.75→0.5625) | 65-78 | Works |
| Aspect + FOV max (78→97) | 65-97 | Works |
| Aspect + FOV max + FOV min (30) | 30-97 | **Broken** |

## The Fix

1. **Aspect ratio**: Patch all 0.75 → 0.5625 (199 addresses)
2. **FOV max**: Patch 78.0 → 97.0 (166 addresses)  
3. **FOV min**: DO NOT patch (keep at 65.0)

## Usage

```bash
# Normal (tach works):
python patch_nr2003_fov.py --exe original.exe --output patched.exe

# With custom FOV min (WARNING - breaks tach!):
python patch_nr2003_fov.py --exe original.exe --output patched.exe --fov-min 50 --patch-fov-min
```

## Addresses Excluded (tach-related)

- `0x00320acc` - aspect ratio (0.75)
- `0x00320b3c` - aspect ratio (0.75)
- `0x00320b9c` - aspect ratio (0.75)

## Tachometer Relationship

The tachometer reading is directly proportional to FOV min:
- FOV min 65 → tach 1000 (idle)
- FOV min 50 → tach ~500 (idle)

The game uses the FOV min value to calculate RPM/tachometer.

## Files

- `nr2003_final.exe` - Working version (FOV 65-97, aspect 16:9)
- `nr2003_fovmin_50_test.exe` - Test version (FOV 50-97, tach reads ~500)
