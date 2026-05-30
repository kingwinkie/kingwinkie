from ghidra.program.model.listing import Function
from ghidra.program.model.symbol import Reference
from ghidra.app.script import GhidraScript
from ghidra.util.task import ConsoleTaskMonitor

target_addr = "00485070"
target_func = getFunctionAt(toAddr(target_addr))

if target_func:
    print("Function:", target_func.getName())
    print("Entry:", target_func.getEntryPoint())
    print("\nFunctions that call this:")

    refMgr = currentProgram.getReferenceManager()
    refs = refMgr.getReferencesTo(toAddr(target_addr))

    for ref in refs:
        caller_addr = ref.getFromAddress()
        func = getFunctionAt(caller_addr)
        if func:
            print("  - %s at %s" % (func.getName(), caller_addr))
else:
    print("Function not found at", target_addr)
