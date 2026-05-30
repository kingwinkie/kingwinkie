# Running Ghidra headless to export decompiled pseudocode

This file shows how to run Ghidra headless (command-line) to execute the
`ghidra_export_decomp.py` script included in `tools/ghidra/`.

Prerequisites
- Install Ghidra and confirm the `analyzeHeadless` script is available in the
  Ghidra installation `support` directory.
- Copy or move `N2003LYT.EXE` into a local Ghidra workspace folder.

Example steps (PowerShell):

1) Create a workspace directory and copy the binary there (optional):

```powershell
mkdir C:\ghidra_workspace
copy .\N2003LYT.EXE C:\ghidra_workspace\
cd C:\ghidra_workspace
```

2) Run analyzeHeadless with the script (adjust `GhidraInstallDir`):

```powershell
$GhidraDir = 'C:\Program Files\ghidra'  # adjust to your install path
$ProjectDir = 'C:\ghidra_workspace'
$ProjectName = 'n2003lyt_project'
$Script = 'tools/ghidra/ghidra_export_decomp.py'

& "$GhidraDir\support\analyzeHeadless.bat" $ProjectDir $ProjectName -import N2003LYT.EXE -scriptPath "$PWD\tools\ghidra" -preScript ghidra_create_segment_pre.py -postScript ghidra_export_helpers.py
```

Expected output
- The script writes files `decomp_<funcname>_<addr>.c` into your current
  working directory (the workspace where `analyzeHeadless` runs). Upload
  relevant files (`decomp_readInfo_...c`, `decomp_manipuliereInfo_...c`, etc.) for me to analyze.

Notes
- If the Decompiler fails on some functions, try running the script from the
  Ghidra GUI first, run auto-analysis with additional options, then re-run
  headless. Some 16-bit binaries need manual memory block fixes in GUI before
  headless runs succeed.
