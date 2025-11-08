#!/usr/bin/env python
"""
Consensus Tools CLI
Convenience wrapper for consensus ledger and self-audit operations
"""

import argparse
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bor_consensus.ledger import load_registry, compute_epochs, write_ledger
from bor_consensus.self_audit import audit_last_n


def main():
    parser = argparse.ArgumentParser(
        description="BoR Consensus Tools - Ledger and Self-Audit CLI"
    )
    parser.add_argument("--ledger", action="store_true",
                       help="Build consensus ledger from proof registry")
    parser.add_argument("--audit", type=int, default=0, metavar="N",
                       help="Audit last N bundles for drift")
    
    args = parser.parse_args()
    
    if not args.ledger and args.audit == 0:
        parser.print_help()
        sys.exit(1)
    
    if args.ledger:
        print("Building consensus ledger...")
        entries = load_registry()
        epochs = compute_epochs(entries, min_quorum=3)
        write_ledger(epochs)
        confirmed = [e for e in epochs if e["status"] == "CONSENSUS_CONFIRMED"]
        
        print(f"\n[BoR-Consensus] {'CONFIRMED' if confirmed else 'PENDING'}")
        print(f"  Epochs: {len(epochs)}")
        print(f"  Confirmed: {len(confirmed)}")
        print(f"  Pending: {len(epochs) - len(confirmed)}")
        print(f"\nLedger written to: consensus_ledger.json")
    
    if args.audit > 0:
        print(f"\nAuditing last {args.audit} bundles...")
        res = audit_last_n(args.audit)
        status = "OK" if res["ok"] else "DRIFT"
        
        print(f"\n[BoR-SelfAudit] {status}")
        print(f"  Checked: {res['checked']}")
        print(f"  Verified: {res['verified']}")
        print(f"  Drift: {len(res['drift'])}")
        
        if res["drift"]:
            print("\nDrift detected in:")
            for d in res["drift"]:
                print(f"  ✗ {d['bundle']}")
                print(f"    Reason: {d['reason']}")
        else:
            print("\n✓ All bundles verified successfully")


if __name__ == "__main__":
    main()

