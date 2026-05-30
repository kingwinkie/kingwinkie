from ghidra.program.model.listing import Function
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import os

out_dir = os.getcwd()
monitor = ConsoleTaskMonitor()
fm = currentProgram.getFunctionManager()

print("Decompiling all functions...")

count = 0
di = DecompInterface()
di.openProgram(currentProgram)

for func in fm.getFunctions(True):
    try:
        res = di.decompileFunction(func, 60, monitor)
        if res.decompileCompleted():
            c = res.getDecompiledFunction().getC()
            func_name = func.getName().replace(":", "_")
            entry = str(func.getEntryPoint()).replace(":", "_")
            fname = "decomp_%s_%s.c" % (func_name, entry)
            path = os.path.join(out_dir, fname)
            with open(path, "w") as f:
                f.write(
                    "/* Function: %s\n   Entry: %s\n*/\n\n"
                    % (func.getName(), func.getEntryPoint())
                )
                f.write(c)
            count += 1
            if count % 100 == 0:
                print("Decompiled %d functions..." % count)
    except Exception as e:
        pass

print("Total functions decompiled: %d" % count)
print("Done!")
