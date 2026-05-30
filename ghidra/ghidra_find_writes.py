from ghidra.program.model.listing import Function
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

monitor = ConsoleTaskMonitor()
di = DecompInterface()
di.openProgram(currentProgram)

print("Searching for functions that call FUN_00557d20 (which writes car setup data)...")

refs = list(currentProgram.getReferenceManager().getReferencesTo(toAddr("00557d20")))[
    :20
]
for ref in refs:
    caller = getFunctionAt(ref.getFromAddress())
    if caller:
        print("\n=== %s at %s ===" % (caller.getName(), ref.getFromAddress()))
        try:
            res = di.decompileFunction(caller, 60, monitor)
            if res.decompileCompleted():
                c = res.getDecompiledFunction().getC()
                lines = c.split("\n")[:50]
                for line in lines:
                    print(line)
        except Exception as e:
            print("Error:", e)

print("\n\nDone")
