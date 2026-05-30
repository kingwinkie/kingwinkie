from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

monitor = ConsoleTaskMonitor()
di = DecompInterface()
di.openProgram(currentProgram)

# Look at addresses in the garage CSV
# 0x2EDF7B = brake bias min
# 0x2EE11F = grille tape min

print("Looking for functions that access brake bias/grille tape addresses...")

# Search for references to these addresses
search_addrs = [
    0x2EDF7B,
    0x2EDF7F,
    0x2EDF83,
    0x2EDF87,
    0x2EE11F,
    0x2EE123,
    0x2EE127,
    0x2EE12B,
]

for addr in search_addrs:
    try:
        refs = list(
            currentProgram.getReferenceManager().getReferencesTo(toAddr(hex(addr)))
        )
        if refs:
            print("\n=== References to 0x%x ===" % addr)
            for ref in refs[:5]:
                func = getFunctionAt(ref.getFromAddress())
                if func:
                    print("  %s at %s" % (func.getName(), ref.getFromAddress()))
    except Exception as e:
        pass

print("\nDone")
