# A small Ghidra Jython script to label functions that reference known strings.
# Install: copy this file into Ghidra's Scripts folder and run it from Script Manager.

from ghidra.program.model.symbol import SourceType
from ghidra.util.task import ConsoleTaskMonitor

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
strings = currentProgram.getListing().getDefinedData(True)

def find_string_refs(target):
    results = []
    for d in strings:
        try:
            val = d.getValue()
            if val and target in str(val):
                refs = d.getReferenceIteratorTo()
                while refs.hasNext():
                    r = refs.next()
                    ref_addr = r.getFromAddress()
                    func = fm.getFunctionContaining(ref_addr)
                    if func:
                        results.append((func, ref_addr))
        except Exception as e:
            pass
    return results

for s in strings_to_search:
    refs = find_string_refs(s)
    for (func, addr) in refs:
        name = func.getName()
        if "sub_" in name or name.startswith("FUN_") or name.startswith("unk"):
            newname = None
            if "xpos" in s:
                newname = "read_field_xpos"
            elif "/edit" in s:
                newname = "entry_edit_mode"
            elif "/gener" in s:
                newname = "entry_gener"
            elif "objn" in s:
                newname = "read_object_header"
            if newname:
                try:
                    func.setName(newname, SourceType.USER_DEFINED)
                    print("Renamed function at %s to %s (string '%s')" % (func.getEntryPoint(), newname, s))
                except Exception as e:
                    print("Failed to rename %s: %s" % (func.getEntryPoint(), e))

print("Auto-label script finished. Review renamed functions and refine as needed.")
