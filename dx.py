#!/usr/bin/env python
"""
Developer Experience (DX) CLI
Convenient wrapper for common BoR operations
"""

import argparse
import subprocess
import sys


def run(cmd):
    """Execute shell command and return exit code."""
    return subprocess.call(cmd, shell=True)


def main():
    parser = argparse.ArgumentParser(
        description="BoR-Proof SDK - Developer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dx.py prove              Generate proof bundle
  python dx.py verify             Verify bundle
  python dx.py audit --n 10       Audit last 10 bundles
  python dx.py consensus          Build consensus ledger
        """
    )
    
    parser.add_argument(
        "cmd",
        choices=["prove", "verify", "persist", "audit", "consensus"],
        help="Command to execute"
    )
    parser.add_argument(
        "--n", type=int, default=5,
        help="Number of bundles to audit (for audit command)"
    )
    
    args = parser.parse_args()
    
    if args.cmd == "prove":
        sys.exit(run("make prove"))
    elif args.cmd == "verify":
        sys.exit(run("make verify"))
    elif args.cmd == "persist":
        sys.exit(run("make persist"))
    elif args.cmd == "audit":
        sys.exit(run(f"python evaluate_invariant.py --self-audit {args.n}"))
    elif args.cmd == "consensus":
        sys.exit(run("python evaluate_invariant.py --consensus-ledger"))


if __name__ == "__main__":
    main()

