"""
# Decompile functions from the current program.

This script decompiles functions from the loaded program and writes
`decomp_<name>_<addr>.c` files for each function. By default it will decompile
all discovered functions. This is helpful to export helper routines that are
not referenced directly by string tables.

Run from Ghidra Script Manager or headless as a postScript.
"""
import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

cwd = os.getcwd()
refs_file = os.path.join(cwd, 'string_references.txt')
if not os.path.exists(refs_file):
    print('string_references.txt not found in', cwd)
    print('This script must be run from within Ghidra (Script Manager) or as a -postScript via analyzeHeadless after the program is opened.')
else:
    # Defensive check: ensure currentProgram is available
    try:
        prog = currentProgram
    except NameError:
        prog = None
    if prog is None:
        print('No program context (currentProgram is None).')
        print('Run this script from Ghidra Script Manager with the program open, or run it as a -postScript in analyzeHeadless after import/analysis.')
    else:
        fm = prog.getFunctionManager()
        di = DecompInterface()
        di.openProgram(prog)
        monitor = ConsoleTaskMonitor()

        # Iterate all functions discovered in the program and decompile each one.
        count = 0
        for func in fm.getFunctions(True):
            try:
                fname = func.getName()
            except Exception:
                fname = 'func'
            try:
                res = di.decompileFunction(func, 60, monitor)
                outname = 'decomp_%s_%s.c' % (fname, str(func.getEntryPoint()).replace(':', '_'))
                with open(os.path.join(cwd, outname), 'w') as outf:
                    outf.write('/* Function: %s\n   Entry: %s\n*/\n\n' % (func.getName(), func.getEntryPoint()))
                    if res.decompileCompleted():
                        outf.write(res.getDecompiledFunction().getC())
                    else:
                        outf.write('// Decompilation failed\n')
                print('Wrote', outname)
                count += 1
            except Exception as e:
                print('Failed to decompile', func.getEntryPoint(), e)
        print('Decompiled %d functions' % count)
