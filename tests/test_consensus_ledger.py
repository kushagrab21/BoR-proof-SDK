"""
Test suite for consensus ledger functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from bor_consensus.ledger import compute_epochs, group_by_hrich


def test_quorum_confirmation():
    """Test that consensus is confirmed when quorum (≥3) is reached."""
    entries = [
        {"user": "a", "H_RICH": "h1"},
        {"user": "b", "H_RICH": "h1"},
        {"user": "c", "H_RICH": "h1"},
        {"user": "d", "H_RICH": "h2"},
    ]
    epochs = compute_epochs(entries, min_quorum=3)
    by_hash = {e["hash"]: e for e in epochs}
    
    assert by_hash["h1"]["status"] == "CONSENSUS_CONFIRMED"
    assert by_hash["h1"]["count"] == 3
    assert by_hash["h2"]["status"] == "PENDING"
    assert by_hash["h2"]["count"] == 1


def test_pending_status():
    """Test that consensus is pending when quorum not reached."""
    entries = [
        {"user": "a", "H_RICH": "h1"},
        {"user": "b", "H_RICH": "h1"},
    ]
    epochs = compute_epochs(entries, min_quorum=3)
    
    assert len(epochs) == 1
    assert epochs[0]["status"] == "PENDING"
    assert epochs[0]["count"] == 2


def test_group_by_hrich():
    """Test grouping entries by H_RICH hash."""
    entries = [
        {"H_RICH": "hash1", "data": "a"},
        {"H_RICH": "hash1", "data": "b"},
        {"H_RICH": "hash2", "data": "c"},
    ]
    grouped = group_by_hrich(entries)
    
    assert len(grouped) == 2
    assert len(grouped["hash1"]) == 2
    assert len(grouped["hash2"]) == 1


def test_deterministic_ordering():
    """Test that epochs are ordered deterministically."""
    entries = [
        {"user": "a", "H_RICH": "h2"},
        {"user": "b", "H_RICH": "h1"},
        {"user": "c", "H_RICH": "h1"},
        {"user": "d", "H_RICH": "h1"},
    ]
    epochs = compute_epochs(entries, min_quorum=3)
    
    # Confirmed should come first
    assert epochs[0]["status"] == "CONSENSUS_CONFIRMED"
    assert epochs[0]["hash"] == "h1"
    assert epochs[1]["status"] == "PENDING"


if __name__ == "__main__":
    test_quorum_confirmation()
    test_pending_status()
    test_group_by_hrich()
    test_deterministic_ordering()
    print("✓ All consensus ledger tests passed")

