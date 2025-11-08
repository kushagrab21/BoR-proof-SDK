"""
Test suite for invariant hooks
Validates that the hook system maintains determinism.
"""

import os
import sys

# Add src to path for bor_core imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from bor_core.init_hooks import transform_hook, pre_run_hook, post_run_hook


@transform_hook
def add(x, y):
    """Simple addition function for testing."""
    return x + y


def test_determinism():
    """Test that identical operations produce identical results."""
    pre_run_hook(7, {"offset": 4}, "v1.0")
    a1 = add(2, 3)
    a2 = add(2, 3)
    assert a1 == a2, f"Determinism violated: {a1} != {a2}"


def test_pre_run_hook():
    """Test pre_run_hook returns hashes."""
    h_env, h_input = pre_run_hook(10, {"test": True}, "v1.0")
    assert isinstance(h_env, str) and len(h_env) == 64, "Invalid env hash"
    assert isinstance(h_input, str) and len(h_input) == 64, "Invalid input hash"


def test_post_run_hook():
    """Test post_run_hook returns result hash."""
    h_out = post_run_hook("test_step", {"result": 42})
    assert isinstance(h_out, str) and len(h_out) == 64, "Invalid output hash"


if __name__ == "__main__":
    test_determinism()
    test_pre_run_hook()
    test_post_run_hook()
    print("✓ All invariant hook tests passed")

