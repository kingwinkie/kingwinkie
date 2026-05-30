Ghidra import checklist for `N2003LYT.EXE`

1) Install Ghidra (https://ghidra-sre.org/) and ensure Java 11+ is available.
2) Start Ghidra and create a new project (Non-Shared Project is fine).
3) Import `N2003LYT.EXE` from this repo (copy into a local analysis folder first).
   - When prompted, confirm the format detection. The file is a 16-bit DOS MZ format; set the language to 8086:LE:16:real if needed.
4) Run the auto-analysis with default options. Allow it to finish (may take a few minutes).
5) Use the Strings window to locate the string `xpos=%d`, `*    objn %s`, `/edit`, `/list`, `/gener` and double-click to jump to cross-references.
6) Run the supplied auto-label script `ghidra_autolabel.py` (copy it into Ghidra's `Scripts` folder or run from the Script Manager). The script attempts to rename functions that reference the known format strings.
7) Manually inspect functions named `_main`, `_readInfo`, `_printGener`, `_manipuliereInfo`. Look for calls to file IO routines and parsing loops.
8) Export function pseudocode (Decompile window) for `_readInfo` and `_manipuliereInfo` and save to disk — they will be the main source for recovering the `.gener` parsing and `.lyt` writing logic.

Notes
- Ghidra's analysis of 16-bit real-mode binaries may need manual segment/base fixing. If code/data boundaries look off, try adjusting memory block boundaries and re-running analysis on the affected area.
- Save incremental project snapshots after major discoveries.
