#!/usr/bin/env python3
"""
BoR-SDK Visualization CLI

Command-line interface for running the visual proof pipeline.
"""

import sys
import argparse
import subprocess
from pathlib import Path


# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_colored(message: str, color: str = Colors.NC):
    """Print a colored message."""
    print(f"{color}{message}{Colors.NC}")


def run_pipeline(strict: bool = False, session_id: str = None) -> int:
    """
    Run the visual proof pipeline.
    
    Args:
        strict: If True, fail on verification warnings
        session_id: Optional session ID (for future use)
    
    Returns:
        Exit code (0 for success)
    """
    # Build command
    cmd = ["./run_visual_pipeline.sh"]
    
    if strict:
        cmd.append("--strict")
    
    if session_id:
        cmd.extend(["--session", session_id])
    
    # Check if script exists
    script_path = Path("run_visual_pipeline.sh")
    if not script_path.exists():
        print_colored("❌ Error: run_visual_pipeline.sh not found", Colors.RED)
        print_colored("   Make sure you're in the BoR-proof-SDK directory", Colors.YELLOW)
        return 1
    
    # Make sure it's executable
    if not script_path.stat().st_mode & 0o111:
        print_colored("⚠️  Making run_visual_pipeline.sh executable...", Colors.YELLOW)
        script_path.chmod(script_path.stat().st_mode | 0o111)
    
    # Run the pipeline
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Pipeline interrupted by user", Colors.YELLOW)
        return 130
    except Exception as e:
        print_colored(f"❌ Error running pipeline: {e}", Colors.RED)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BoR-SDK Visual Proof Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bor visualize                  Run pipeline (non-strict)
  bor visualize --strict         Run with strict verification
  bor visualize --session ID     Specify session ID
  bor visualize --interactive    Launch interactive dashboard

Exit Codes:
  0 - Success (all checks passed or partial with warnings in non-strict mode)
  1 - Partial verification failure (warnings in strict mode)
  2 - Complete failure (critical checks failed)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # visualize command
    visualize_parser = subparsers.add_parser(
        'visualize',
        help='Run the complete visual proof pipeline'
    )
    visualize_parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on verification warnings (strict mode)'
    )
    visualize_parser.add_argument(
        '--session',
        type=str,
        help='Specify session ID (optional)'
    )
    visualize_parser.add_argument(
        '--interactive',
        action='store_true',
        help='Launch interactive web dashboard'
    )
    
    args = parser.parse_args()
    
    # If no command specified, default to visualize
    if not args.command:
        # Check if there are any arguments that look like visualize options
        if '--strict' in sys.argv or '--session' in sys.argv or '--interactive' in sys.argv:
            args.command = 'visualize'
            # Re-parse with visualize subparser
            args = visualize_parser.parse_args(sys.argv[1:])
        else:
            parser.print_help()
            return 0
    
    if args.command == 'visualize':
        interactive = getattr(args, 'interactive', False)
        
        # Interactive mode
        if interactive:
            print_colored("🌐 Launching Interactive Dashboard...", Colors.BLUE)
            try:
                result = subprocess.run(["streamlit", "run", "interactive_visual_dashboard.py"], check=False)
                return result.returncode
            except FileNotFoundError:
                print_colored("❌ Error: Streamlit not installed", Colors.RED)
                print_colored("   Install with: pip install streamlit plotly pandas", Colors.YELLOW)
                return 1
            except KeyboardInterrupt:
                print_colored("\n\n⚠️  Dashboard interrupted by user", Colors.YELLOW)
                return 130
        
        # Standard pipeline mode
        strict = getattr(args, 'strict', False)
        session = getattr(args, 'session', None)
        return run_pipeline(strict=strict, session_id=session)
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

