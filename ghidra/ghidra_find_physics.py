from ghidra.program.model.listing import Function
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import os
from ghidra.program.model.data import StringDataType
from ghidra.program.model.data import DataUtilities
from ghidra.util.task import TaskMonitor

out_dir = os.getcwd()
monitor = ConsoleTaskMonitor()
fm = currentProgram.getFunctionManager()
listing = currentProgram.getListing()

target_keywords = [
    "xpos",
    "ypos",
    "xlen",
    "ylen",
    "fntc",
    "bgrr",
    "bgrg",
    "bgrb",
    "bgrt",
    "fntn",
    "stpn",
    "objn",
    "gener",
    "/gener",
    "/edit",
    "/list",
    "fopen",
    "fwrite",
    "fread",
    "roll",
    "couple",
    "sway",
    "spring",
    "weight",
    "bias",
    "wedge",
    "tire",
    "shock",
    "camber",
    "caster",
    "rideheight",
    "stagger",
    "toe",
    "compression",
    "rebound",
    "front",
    "rear",
    "left",
    "right",
    "lf",
    "rf",
    "lr",
    "rr",
    "bar",
    "stiffness",
    "percentage",
    "percent",
    "distribution",
    "corner",
    "lateral",
    "understeer",
    "oversteer",
    "suspension",
    "downforce",
    "grip",
    "chassis",
    "setup",
    "trackbar",
    "track bar",
]


def write_strings_and_refs():
    try:
        define_ascii_strings()
    except Exception:
        pass

    strings_file = os.path.join(out_dir, "strings_refs.txt")
    refs_file = os.path.join(out_dir, "string_references.txt")
    open(strings_file, "w").write("")
    open(refs_file, "w").write("")

    it = listing.getDefinedData(True)
    while it.hasNext():
        d = it.next()
        try:
            val = d.getValue()
            s = str(val)
            if s and len(s) >= 3:
                addr = d.getAddress()
                with open(strings_file, "a") as sf:
                    sf.write("%s\t%s\n" % (addr, s))
                refs = d.getReferenceIteratorTo()
                found = set()
                while refs.hasNext():
                    r = refs.next()
                    func = fm.getFunctionContaining(r.getFromAddress())
                    if func:
                        found.add((func.getName(), func.getEntryPoint()))
                if found:
                    with open(refs_file, "a") as rf:
                        rf.write(
                            "%s\t%s\trefs:%s\n"
                            % (addr, s, ",".join([n for (n, a) in found]))
                        )
        except Exception:
            pass


def decompile_and_search():
    di = DecompInterface()
    di.openProgram(currentProgram)
    candidates = []
    for func in fm.getFunctions(True):
        try:
            res = di.decompileFunction(func, 60, monitor)
            if res.decompileCompleted():
                c = res.getDecompiledFunction().getC()
                lower = c.lower()
                if any(k in lower for k in target_keywords):
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
                    candidates.append((func.getName(), func.getEntryPoint(), fname))
        except Exception:
            pass

    idxf = os.path.join(out_dir, "decompiled_candidates.txt")
    with open(idxf, "w") as idx:
        for n, a, f in candidates:
            idx.write("%s\t%s\t%s\n" % (n, a, f))


def main():
    write_strings_and_refs()
    decompile_and_search()
    print("Helper export complete.")


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
                if mem.getBlock(addr) is None or not mem.getBlock(addr).isInitialized():
                    addr = addr.add(1)
                    continue
                b = mem.getByte(addr) & 0xFF
            except Exception:
                addr = addr.add(1)
                continue

            if 32 <= b <= 126:
                run_start = addr
                run_len = 0
                while addr.compareTo(end) <= 0:
                    try:
                        bb = mem.getByte(addr) & 0xFF
                        if 32 <= bb <= 126:
                            run_len += 1
                            addr = addr.add(1)
                        else:
                            break
                    except Exception:
                        break
                if run_len >= min_len:
                    try:
                        DataUtilities.createData(
                            currentProgram,
                            run_start,
                            StringDataType(),
                            run_len,
                            DataUtilities.ClearDataMode.CLEAR_ALL,
                            monitor,
                        )
                    except Exception:
                        pass
            else:
                addr = addr.add(1)


if __name__ == "__main__":
    main()
