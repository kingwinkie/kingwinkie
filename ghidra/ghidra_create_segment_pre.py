# Ghidra pre-script to create a memory block covering segment 0x1000
# Run this as a -preScript in analyzeHeadless so analysis sees the full code
# range before decompilation.

from ghidra.util import Msg

try:
    mem = currentProgram.getMemory()
    start_addr = toAddr(0x10000)  # segment 0x1000 -> linear 0x1000 * 16
    size = 0x10000  # 64KB block to cover the full segment
    existing = mem.getBlock(start_addr)
    if existing:
        print('Memory block already exists: %s' % existing.getName())
    else:
        block = mem.createUninitializedBlock('CODE_SEG_1000', start_addr, size, False)
        block.setExecute(True)
        block.setRead(True)
        block.setWrite(False)
        print('Created memory block CODE_SEG_1000 at %s size 0x%x' % (start_addr, size))
except Exception as e:
    print('Failed to create memory block: %s' % e)


# Also pre-define ASCII strings found in memory so auto-analysis can create references
try:
    from ghidra.program.model.data import StringDataType
    from ghidra.program.model.data import DataUtilities
    from ghidra.util.task import TaskMonitor

    def define_ascii_strings(min_len=4):
        mem = currentProgram.getMemory()
        blocks = mem.getBlocks()
        monitor = TaskMonitor.DUMMY
        for block in blocks:
            start = block.getStart()
            end = block.getEnd()
            addr = start
            while addr.compareTo(end) <= 0:
                try:
                    b = mem.getByte(addr) & 0xff
                except Exception:
                    addr = addr.add(1)
                    continue
                if 32 <= b <= 126:
                    run_start = addr
                    run_len = 0
                    while addr.compareTo(end) <= 0:
                        try:
                            bb = mem.getByte(addr) & 0xff
                        except Exception:
                            break
                        if 32 <= bb <= 126:
                            run_len += 1
                            addr = addr.add(1)
                        else:
                            break
                    if run_len >= min_len:
                        try:
                            DataUtilities.createData(currentProgram, run_start, StringDataType(), run_len, DataUtilities.ClearDataMode.CLEAR_ALL, monitor)
                        except Exception:
                            pass
                else:
                    addr = addr.add(1)

    print('Defining ASCII strings before analysis...')
    define_ascii_strings(min_len=4)
    print('String definition complete.')
except Exception as e:
    print('Pre-string-define failed:', e)
