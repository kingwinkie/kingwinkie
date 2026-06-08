#!/usr/bin/env python3
import argparse
import shlex
import subprocess
import sys
from pathlib import Path

def build_argument_list(proj_dir, proj_name, input_file, scripts_dir, pre, post):
    a = []
    a.append(str(proj_dir))
    a.append(proj_name)
    if input_file:
        a += ['-import', str(input_file)]
    if scripts_dir:
        a += ['-scriptPath', str(scripts_dir)]
    for s in pre or []:
        if s:
            a += ['-preScript', s]
    for s in post or []:
        if s:
            a += ['-postScript', s]
    return a

def main():
    parser = argparse.ArgumentParser(description="Run Ghidra analyzeHeadless with safe, consistent args")
    parser.add_argument('--ghidra-root', default=r'/home/pi/apps/ghidra_10.4_PUBLIC',
                        help='Path to Ghidra install root (recommended)')
    parser.add_argument('--ghidra-analyze', default=None,
                        help='Path to analyzeHeadless (optional; ghidra-root overrides)')
    parser.add_argument('--project-dir', default=r'/home/pi/apps/decompile/rts_dll/ghidra_project')
    parser.add_argument('--project-name', default='Res_dll')
    parser.add_argument('--input-file', default=r'/home/pi/apps/decompile/res_dll/PapyRes.dll')
    parser.add_argument('--scripts-dir', default=r'/home/pi/apps/decompile/res_dll/ghidra')
    parser.add_argument('--pre-scripts', nargs='*', default=['ghidra_create_segment_pre.py'])
    parser.add_argument('--post-scripts', nargs='*', default=['ghidra_export_helpers.py','ghidra_decompile_list.py'])
    parser.add_argument('--show-command', action='store_true', help='Print the full command before running')
    parser.add_argument('--dry-run', action='store_true', help='Print command and exit without running')

    args = parser.parse_args()

    ghidra_root = Path(args.ghidra_root) if args.ghidra_root else None
    if args.ghidra_analyze:
        ghidra_exe = Path(args.ghidra_analyze)
    elif ghidra_root:
        ghidra_exe = (ghidra_root / 'support' / 'analyzeHeadless').resolve()
    else:
        print('Either --ghidra-root or --ghidra-analyze must be provided', file=sys.stderr)
        return 2

    if ghidra_root and not ghidra_root.exists():
        print(f'Warning: ghidra-root does not exist: {ghidra_root}', file=sys.stderr)

    if not ghidra_exe.exists():
        print(f'ERROR: analyzeHeadless not found at {ghidra_exe}', file=sys.stderr)
        return 2

    proj_dir = Path(args.project_dir)
    proj_name = args.project_name
    input_file = Path(args.input_file) if args.input_file else None
    scripts_dir = Path(args.scripts_dir) if args.scripts_dir else None

    arg_list = build_argument_list(proj_dir, proj_name, input_file, scripts_dir, args.pre_scripts, args.post_scripts)

    cmd_list = [str(ghidra_exe)] + arg_list
    cmd_str = ' '.join(shlex.quote(x) for x in cmd_list)

    if args.show_command or args.dry_run:
        print('AnalyzeHeadless command:')
        print(cmd_str)

    print(f"Running analyzeHeadless:\n  exe: {ghidra_exe}\n  project: {proj_dir} / {proj_name}\n  input: {input_file}\n  scripts: {scripts_dir}")

    if args.dry_run:
        return 0

    # Run analyzeHeadless with working directory set to Ghidra root if available
    cwd = str(ghidra_root) if ghidra_root and ghidra_root.exists() else None

    try:
        completed = subprocess.run(cmd_list, check=True, cwd=cwd)
        print('analyzeHeadless finished')
        return completed.returncode
    except subprocess.CalledProcessError as e:
        print('analyzeHeadless exited with non-zero status:', e.returncode, file=sys.stderr)
        return e.returncode
    except FileNotFoundError as e:
        print('Failed to start analyzeHeadless:', file=sys.stderr)
        print(e, file=sys.stderr)
    except Exception as e:
        print('Failed to start analyzeHeadless:', file=sys.stderr)
        print(e, file=sys.stderr)

    # Fallback: try invoking via shell from ghidra_root (helps when wrappers are needed)
    print('Falling back to direct invocation using shell', file=sys.stderr)
    try:
        fallback_cmd = cmd_str
        completed = subprocess.run(fallback_cmd, shell=True, check=True, cwd=cwd)
        print('Fallback finished')
        return completed.returncode
    except Exception as e:
        print('Fallback also failed:', file=sys.stderr)
        print(e, file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())

