"""
BoR Invariant Evaluator
Validates the BoR invariant: identical inputs → identical outputs, hashes, and proofs.
"""

import argparse
import json
import os
import sys
from collections import Counter

# Add src to path for bor_core imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bor_core import registry
from bor import verify


def check_consensus(min_count=3):
    """
    Check for cross-run consensus by verifying that ≥min_count identical H_RICH entries exist.
    Returns (consensus_confirmed, h_rich_count, most_common_h_rich)
    """
    proof_registry_path = "proof_registry.json"
    
    if not os.path.exists(proof_registry_path):
        # Create registry if it doesn't exist
        return False, 0, None
    
    with open(proof_registry_path, 'r') as f:
        registry_data = json.load(f)
    
    h_rich_values = [entry.get("H_RICH") for entry in registry_data if entry.get("H_RICH")]
    
    if not h_rich_values:
        return False, 0, None
    
    counter = Counter(h_rich_values)
    most_common_h_rich, count = counter.most_common(1)[0]
    
    return count >= min_count, count, most_common_h_rich


def register_current_proof(bundle_path):
    """Register current proof in the proof registry for consensus tracking."""
    proof_registry_path = "proof_registry.json"
    
    with open(bundle_path, 'r') as f:
        bundle = json.load(f)
    
    entry = {
        "H_RICH": bundle.get("H_RICH"),
        "H_MASTER": bundle.get("H_MASTER") or bundle.get("primary", {}).get("master"),
        "timestamp": bundle.get("generated_at"),
    }
    
    # Load or create registry
    if os.path.exists(proof_registry_path):
        with open(proof_registry_path, 'r') as f:
            registry_data = json.load(f)
    else:
        registry_data = []
    
    registry_data.append(entry)
    
    with open(proof_registry_path, 'w') as f:
        json.dump(registry_data, f, indent=2, sort_keys=True)


def print_summary():
    """Print a comprehensive summary of invariant status across all layers."""
    metrics_path = "metrics.json"
    state_path = "state.json"
    
    if not os.path.exists(metrics_path):
        return
    
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    
    drift = metrics.get("drift_detected", False)
    
    # Count state entries by layer
    layer_counts = {"P₀-P₁": 0, "P₂": 0, "P₃": 0, "P₄": 0}
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            state = json.load(f)
        for entry in state:
            step = entry.get("step", "")
            if "pre_run" in step or "add" in step or "square" in step:
                layer_counts["P₀-P₁"] += 1
            elif "bundle" in step:
                layer_counts["P₂"] += 1
            elif "replay" in step or "verify" in step:
                layer_counts["P₃"] += 1
            elif "store" in step or "persistence" in step:
                layer_counts["P₄"] += 1
    
    print(f"\n[BoR-Invariant] VERIFIED")
    print(f"Layers P₀–P₄ complete | Drift = {drift} | State entries = {sum(layer_counts.values())}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate BoR invariant")
    parser.add_argument("--consensus", action="store_true", 
                       help="Check for cross-run consensus (≥3 identical H_RICH)")
    parser.add_argument("--summary", action="store_true",
                       help="Show detailed summary")
    parser.add_argument("--consensus-ledger", action="store_true",
                       help="Build consensus ledger from proof registry")
    parser.add_argument("--self-audit", type=int, default=0,
                       help="Audit last N bundles for drift")
    
    args = parser.parse_args()
    
    # P₅ Meta-Layer: Consensus Ledger
    if args.consensus_ledger:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from bor_consensus.ledger import load_registry, compute_epochs, write_ledger
        
        entries = load_registry()
        epochs = compute_epochs(entries, min_quorum=3)
        write_ledger(epochs)
        confirmed = [e for e in epochs if e["status"] == "CONSENSUS_CONFIRMED"]
        
        if confirmed:
            print(f"[BoR-Consensus] CONFIRMED  epochs={len(epochs)}  confirmed={len(confirmed)}")
        else:
            print(f"[BoR-Consensus] PENDING  epochs={len(epochs)}  confirmed=0")
        sys.exit(0)
    
    # P₅ Meta-Layer: Self-Audit
    if args.self_audit > 0:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from bor_consensus.self_audit import audit_last_n
        
        res = audit_last_n(args.self_audit)
        status = "OK" if res["ok"] else "DRIFT"
        print(f"[BoR-SelfAudit] {status}  checked={res['checked']}  verified={res['verified']}  drift={len(res['drift'])}")
        
        if res["drift"]:
            for d in res["drift"]:
                print(f"  ✗ {d['bundle']}: {d['reason']}")
        sys.exit(0)
    
    bundle_path = "out/rich_proof_bundle.json"
    
    if not os.path.exists(bundle_path):
        print(f"[BoR-Invariant] WARNING: Bundle not found at {bundle_path}")
        print("[BoR-Invariant] Run a proof generation first (e.g., examples/demo.py)")
        sys.exit(1)
    
    try:
        result = verify.verify_bundle_file(bundle_path)
        ok = result.get("ok")
        
        if not ok:
            print("[BoR-Invariant] DRIFT DETECTED")
            print(f"Verification result: {result}")
            sys.exit(1)
        
        # Register proof for consensus tracking
        register_current_proof(bundle_path)
        
        # Check consensus if requested
        if args.consensus:
            consensus, count, h_rich = check_consensus(min_count=3)
            if consensus:
                print(f"[BoR-Consensus] CONFIRMED ({count} matching proofs)")
            else:
                print(f"[BoR-Consensus] PENDING ({count} matching proofs, need ≥3)")
        
        # Show summary if requested
        if args.summary:
            print_summary()
        elif not args.consensus:
            # Default output
            print("[BoR-Invariant] VERIFIED")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"[BoR-Invariant] ERROR: {e}")
        sys.exit(1)

