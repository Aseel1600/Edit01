#!/usr/bin/env python3
"""C5-REAL Execution Bypass.

Provides deterministic shell execution bypassing zsh fork/exec issues
by running the command via python's subprocess.run(shell=True).
"""
import sys
import subprocess
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: c5_exec.py <command>")
        sys.exit(1)
    
    # The command is passed as a single string argument
    cmd = sys.argv[1]
    
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            check=False,
            cwd=os.getcwd(),
            env=os.environ
        )
        sys.exit(proc.returncode)
    except Exception as e:
        print(f"c5_exec execution failed: {e}", file=sys.stderr)
        sys.exit(127)

if __name__ == "__main__":
    main()
