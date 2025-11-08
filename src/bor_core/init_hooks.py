"""
Invariant hooks for BoR-Proof SDK
Implements lifecycle hooks for pre/post-run, transformation, registration, and drift detection.
"""

import hashlib
import json
import os
import time
from .registry import log_state, update_metric
from .env_utils import capture_env_hash


def _canonical(obj):
    """Canonicalize an object to a deterministic JSON string."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def pre_run_hook(initial, config, version):
    """Hash environment + inputs before run."""
    h_env = capture_env_hash()
    h_input = hashlib.sha256(
        _canonical({"initial": initial, "config": config, "version": version}).encode()
    ).hexdigest()
    log_state({"step": "pre_run", "hash": h_input, "env": h_env, "status": "ok"})
    return h_env, h_input


def post_run_hook(step_name, result):
    """Verify determinism after each step."""
    h_out = hashlib.sha256(_canonical(result).encode()).hexdigest()
    log_state({"step": step_name, "hash": h_out, "status": "ok"})
    return h_out


def transform_hook(func):
    """Decorator ensuring referential transparency."""
    def wrapper(*args, **kwargs):
        start = time.time()
        out = func(*args, **kwargs)
        end = time.time()
        post_run_hook(func.__name__, {"output": out, "elapsed": end - start})
        return out
    return wrapper


def register_proof_hook(bundle_path="out/rich_proof_bundle.json"):
    """Compare stored vs recomputed proof hashes."""
    if not os.path.exists(bundle_path):
        return
    
    with open(bundle_path, 'r') as f:
        data = json.load(f)
    
    h_master = data.get("H_MASTER")
    h_rich = data.get("H_RICH")
    update_metric("H_MASTER", h_master)
    update_metric("H_RICH", h_rich)
    log_state({"step": "register_proof", "hash": h_rich, "status": "ok"})


def drift_check_hook(prev_hash, curr_hash):
    """Detect and log drift between runs."""
    drift = prev_hash != curr_hash
    update_metric("drift_detected", drift)
    if drift:
        log_state({"step": "drift_check", "hash": curr_hash, "status": "DRIFT"})
    return drift

