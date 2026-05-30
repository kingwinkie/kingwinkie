"""
Ghidra script to export decompiled pseudocode for functions that reference
known format strings (/gener, /list, /edit, xpos, ypos, etc.).

Usage in Ghidra GUI:
  - Copy this script to Ghidra's Scripts folder and run from Script Manager.

Usage headless (recommended for reproducible output): see `GHIDRA_HEADLESS.md`.

The script writes one file per matched function into the current working
directory named `decomp_<funcname>_<addr>.c` containing the decompiler output
and a small header with cross-reference info.
"""
from ghidra.program.model.symbol import SourceType
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.decompiler import DecompInterface
from ghidra.program.model.listing import Function
import re

strings_to_search = [
    "xpos=%d",
    "ypos=%d",
    "xlen=%d",
    "fntc=%s",
    "*    objn %s",
    "/edit",
    "/list",
    "/gener",
]

monitor = ConsoleTaskMonitor()
fm = currentProgram.getFunctionManager()
listing = currentProgram.getListing()
data_iter = listing.getDefinedData(True)

def find_string_refs(target):
    results = set()
    it = listing.getDefinedData(True)
    while it.hasNext():
        d = it.next()
        try:
            val = d.getValue()
            if val and target in str(val):
                refs = d.getReferenceIteratorTo()
                while refs.hasNext():
                    r = refs.next()
                    ref_addr = r.getFromAddress()
                    func = fm.getFunctionContaining(ref_addr)
                    if func:
                        results.add(func)
        except Exception:
            pass
    return list(results)

def decompile_and_write(func):
    di = DecompInterface()
    di.openProgram(currentProgram)
    res = di.decompileFunction(func, 60, monitor)
    outname = "decomp_%s_%s.c" % (func.getName(), func.getEntryPoint())
    with open(outname, 'w', encoding='utf-8', errors='ignore') as f:
        f.write("/* Function: %s\n   Entry: %s\n*/\n\n" % (func.getName(), func.getEntryPoint()))
        if res.decompileCompleted():
            f.write(res.getDecompiledFunction().getC())
        else:
            f.write("// Decompilation failed or incomplete\n")
    print("Wrote", outname)

matched_funcs = set()
for s in strings_to_search:
    funcs = find_string_refs(s)
    for f in funcs:
        matched_funcs.add(f)

if not matched_funcs:
    print("No functions matched. Check the strings list or try running auto-analysis.")
else:
    for func in matched_funcs:
        try:
            decompile_and_write(func)
        except Exception as e:
            print('Failed for', func.getName(), e)

print('Export complete.')
