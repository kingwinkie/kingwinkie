from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

monitor = ConsoleTaskMonitor()
di = DecompInterface()
di.openProgram(currentProgram)

print("Looking at parameter table entries for roll couple (index 1)...")

base = toAddr("00c05152")
index = 1
offset = index * 6

entry_addr = base.add(offset)
print("Entry for index %d at %s" % (index, entry_addr))

mem = currentProgram.getMemory()
print("\nReading parameter table entries:")

for i in range(20):
    addr = base.add(i * 6)
    try:
        data = mem.getBytes(addr, 6)
        print("Index %d at %s: %s" % (i, addr, " ".join("%02x" % b for b in data)))
    except:
        break

print("\n\nNow finding function pointers in the table...")

# The entry structure seems to be:
# +0: short - type/flag
# +2: pointer to function or value
# Look for function pointer at offset 0xb from base

for i in range(50):
    try:
        func_ptr_addr = toAddr(0xC05152 + i * 6 + 0xB)
        if func_ptr_addr.getOffset() > 0xC06000:
            break
        ptr_val = mem.getInt(func_ptr_addr)
        if ptr_val != 0 and ptr_val != -1:
            print(
                "Index %d: function pointer at %s = 0x%x" % (i, func_ptr_addr, ptr_val)
            )
            func = getFunctionAt(toAddr(ptr_val))
            if func:
                print("  -> %s" % func.getName())
    except:
        pass
