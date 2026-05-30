from ghidra.program.model.listing import Function
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import os

monitor = ConsoleTaskMonitor()
di = DecompInterface()
di.openProgram(currentProgram)

target_addr = "0050ee70"
func = getFunctionAt(toAddr(target_addr))

if func:
    res = di.decompileFunction(func, 60, monitor)
    if res.decompileCompleted():
        c = res.getDecompiledFunction().getC()
        print("Function:", func.getName())
        print("Entry:", func.getEntryPoint())
        print("\nDecompiled code:")
        print(c)
else:
    print("Function not found at", target_addr)
