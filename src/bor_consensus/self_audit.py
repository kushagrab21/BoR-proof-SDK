"""
Self-Audit Module
Replays recent bundles to detect drift
"""

import glob
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from bor import verify


def discover_bundles(root="out", limit=10):
    """
    Discover proof bundles sorted by modification time (newest first).
    Returns list of paths.
    """
    pattern = os.path.join(root, "**", "rich_proof_bundle.json")
    paths = sorted(
        glob.glob(pattern, recursive=True),
        key=os.path.getmtime,
        reverse=True
    )
    return paths[:limit]


def replay_bundle(path):
    """
    Replay a single bundle using verify.verify_bundle_file().
    Returns dict with ok status and optional reason.
    """
    try:
        result = verify.verify_bundle_file(path)
        ok = bool(result.get("ok"))
        reason = None if ok else "verify_bundle_failed"
        return {"ok": ok, "reason": reason}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def audit_last_n(n=5, root="out"):
    """
    Audit the last N bundles.
    Returns dict with checked count, verified count, drift list, and ok status.
    """
    bundles = discover_bundles(root, n)
    drift = []
    verified = 0
    
    for b in bundles:
        r = replay_bundle(b)
        if r["ok"]:
            verified += 1
        else:
            drift.append({"bundle": b, "reason": r["reason"]})
    
    return {
        "checked": len(bundles),
        "verified": verified,
        "drift": drift,
        "ok": verified == len(bundles)
    }

