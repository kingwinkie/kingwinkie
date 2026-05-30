from ghidra.program.model.listing import Function
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import re

monitor = ConsoleTaskMonitor()
di = DecompInterface()
di.openProgram(currentProgram)

print("Searching for functions that might calculate roll couple...")
print("Looking for functions that access parameter index 1 (roll couple)")

count = 0
for func in currentProgram.getFunctionManager().getFunctions(True):
    try:
        res = di.decompileFunction(func, 60, monitor)
        if res.decompileCompleted():
            c = res.getDecompiledFunction().getC()
            # Look for functions that might be doing calculation with springs/sways
            if "0x4" in c and ("+" in c or "-" in c):
                # This is a heuristic - look for array accesses with index arithmetic
                if "0x4" in c:
                    print("\n--- %s at %s ---" % (func.getName(), func.getEntryPoint()))
                    # Print just a snippet
                    lines = c.split("\n")[:30]
                    for line in lines:
                        print(line)
                    count += 1
                    if count >= 3:
                        break
    except:
        pass

print("\nDone")
