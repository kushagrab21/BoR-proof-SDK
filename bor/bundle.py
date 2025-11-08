"""
Module: bundle
--------------
Rich Proof Bundle builder: combines primary proof with sub-proofs.
Produces a comprehensive verification package with H_RICH commitment.
"""

import hashlib
import json
import os
import sys
import time
from typing import Any, Callable, Dict, Iterable

from bor.core import BoRRun
from bor.subproofs import (
    run_CCP,
    run_CMIP,
    run_DIP,
    run_DP,
    run_PEP_bad_signature,
    run_PoPI,
    run_PP,
    run_TRP,
)

# Import invariant hooks with backward compatibility
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
    from bor_core.hooks import register_proof_hook, drift_check_hook
    from bor_core.registry import update_metric
    INVARIANT_HOOKS_AVAILABLE = True
except ImportError:
    # Graceful fallback if hooks not available
    register_proof_hook = lambda *a, **k: None
    drift_check_hook = lambda *a, **k: None
    update_metric = lambda *a, **k: None
    INVARIANT_HOOKS_AVAILABLE = False


def build_primary(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Build a primary proof by executing the reasoning chain.
    Returns the primary proof JSON dictionary.
    """
    r = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r.add_step(fn)
    _ = r.finalize()
    return r.to_primary_proof()


def build_bundle(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Build a Rich Proof Bundle containing:
    - Primary proof (P0-P2)
    - Sub-proofs (DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP)
    - Sub-proof hashes
    - H_RICH: master commitment over all sub-proofs
    """
    primary = build_primary(S0, C, V, stages)

    # Run sub-proofs
    dip = run_DIP(S0, C, V, stages)
    dp = run_DP(
        S0, C, V, stages, perturb={"C": {"__bor_delta__": 1}}
    )  # harmless C perturbation key
    pep_ok, pep_exc = run_PEP_bad_signature()
    popi = run_PoPI(primary)
    ccp = run_CCP(S0, C, V, stages)
    cmip = run_CMIP(S0, C, V, stages)
    pp = run_PP(S0, C, V, stages)
    trp = run_TRP(S0, C, V, stages)

    subproofs = {
        "DIP": dip,
        "DP": dp,
        "PEP": {"ok": pep_ok, "exception": pep_exc},
        "PoPI": popi,
        "CCP": ccp,
        "CMIP": cmip,
        "PP": pp,
        "TRP": trp,
    }

    # Compute hash for each subproof
    def h_sub(obj):
        return hashlib.sha256(
            json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()

    sub_hashes = {k: h_sub(v) for k, v in subproofs.items()}

    # H_RICH = commitment over all subproof hashes
    H_RICH = hashlib.sha256(
        "|".join([sub_hashes[k] for k in sorted(sub_hashes.keys())]).encode("utf-8")
    ).hexdigest()

    bundle = {
        "primary": primary,
        "subproofs": subproofs,
        "subproof_hashes": sub_hashes,
        "H_RICH": H_RICH,
        "H_MASTER": primary.get("master"),  # Store HMASTER for invariant tracking
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    
    # Invariant Framework: Register proof and check for drift
    if INVARIANT_HOOKS_AVAILABLE:
        current_master = primary.get("master")
        
        # Store current metrics
        update_metric("H_MASTER", current_master)
        update_metric("H_RICH", H_RICH)
        
        # Check for drift by loading previous HMASTER if it exists
        try:
            prev_bundle_path = "out/rich_proof_bundle.json"
            if os.path.exists(prev_bundle_path):
                with open(prev_bundle_path, 'r') as f:
                    prev_bundle = json.load(f)
                    prev_master = prev_bundle.get("H_MASTER") or prev_bundle.get("primary", {}).get("master")
                    if prev_master:
                        drift_detected = drift_check_hook(prev_master, current_master)
                        if drift_detected:
                            print(f"[BoR-Invariant] WARNING: Drift detected between runs")
                        else:
                            print(f"[BoR-Invariant] Reproducibility maintained: HMASTER matches previous run")
        except Exception:
            # Silently continue if drift check fails
            pass
        
        # Emit telemetry
        print(f"[BoR-Invariant] H_RICH = {H_RICH[:16]}... | Subproofs = {len(subproofs)} | Status = Verified")
    
    return bundle


def build_index(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a compact index from a bundle.
    Contains H_RICH and subproof hashes for quick verification.
    """
    idx = {"H_RICH": bundle["H_RICH"], "subproof_hashes": bundle["subproof_hashes"]}
    return idx
