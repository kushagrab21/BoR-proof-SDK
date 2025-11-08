"""
Consensus Ledger Management
Computes distributed consensus over proof_registry.json
"""

import json
import os
import datetime
from collections import defaultdict


def _dump_json(path, obj):
    """Write JSON with deterministic formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_registry(path="proof_registry.json"):
    """Load proof registry from disk."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def group_by_hrich(entries):
    """Group registry entries by H_RICH hash."""
    by = defaultdict(list)
    for e in entries:
        h = e.get("H_RICH") or e.get("hash")
        if h:
            by[h].append(e)
    return by


def compute_epochs(entries, min_quorum=3):
    """
    Compute consensus epochs from registry entries.
    Returns list of epoch dicts with status CONSENSUS_CONFIRMED or PENDING.
    """
    today = datetime.date.today().isoformat()
    by = group_by_hrich(entries)
    epochs = []
    
    for h, vlist in by.items():
        users = sorted({v.get("user", "unknown") for v in vlist})
        status = "CONSENSUS_CONFIRMED" if len(users) >= min_quorum else "PENDING"
        epochs.append({
            "epoch": today,
            "hash": h,
            "verifiers": users,
            "count": len(users),
            "status": status
        })
    
    # deterministic order: confirmed first, then by hash
    epochs.sort(key=lambda x: (x["status"] != "CONSENSUS_CONFIRMED", x["hash"]))
    return epochs


def write_ledger(epochs, path="consensus_ledger.json"):
    """Write consensus ledger to disk."""
    _dump_json(path, epochs)

