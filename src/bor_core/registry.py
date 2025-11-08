"""
Registry utilities for state and metrics management
Provides deterministic logging and comparison utilities.
"""

import json
import os

STATE_FILE = "state.json"
METRICS_FILE = "metrics.json"


def _read_json(path):
    """Read JSON file or return empty structure."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []


def _write_json(path, data):
    """Write JSON file with deterministic formatting."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def log_state(entry):
    """Append state entry to state log."""
    data = _read_json(STATE_FILE)
    if not isinstance(data, list):
        data = []
    data.append(entry)
    _write_json(STATE_FILE, data)


def update_metric(key, value):
    """Update a metric in the metrics store."""
    m = _read_json(METRICS_FILE)
    if not isinstance(m, dict):
        m = {}
    m[key] = value
    _write_json(METRICS_FILE, m)


def compare_hashes(h1, h2):
    """Compare two hashes for equality."""
    return h1 == h2

