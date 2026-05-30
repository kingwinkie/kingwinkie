from ghidra.program.model.listing import Function
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import os

monitor = ConsoleTaskMonitor()
di = DecompInterface()
di.openProgram(currentProgram)

target = "00557e40"
func = getFunctionAt(toAddr(target))

if func:
    print("Function:", func.getName())
    print("Calling conventions:", func.getCallingConventionName())
    print("\nParameters:")
    for param in func.getParameters():
        print("  -", param.getName(), "=", param.getDataType())

    print("\nReferences TO this function:")
    refs = currentProgram.getReferenceManager().getReferencesTo(toAddr(target))
    ref_list = list(refs)[:15]
    for ref in ref_list:
        caller = getFunctionAt(ref.getFromAddress())
        if caller:
            print("  - %s at %s" % (caller.getName(), ref.getFromAddress()))
else:
    print("Function not found")
