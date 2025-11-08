"""
Environment capture utilities
Captures and hashes the execution environment for determinism verification.
"""

import platform
import hashlib
import json
import sys
import time

try:
    from bor import __version__ as bor_version
except ImportError:
    bor_version = "unknown"


def capture_env_hash():
    """
    Capture current environment state and return its hash.
    Includes Python version, OS, timestamp, and BoR SDK version.
    """
    env = {
        "python": sys.version,
        "os": platform.platform(),
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bor_sdk": bor_version,
    }
    s = json.dumps(env, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

