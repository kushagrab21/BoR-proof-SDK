"""
Test suite for self-audit functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from bor_consensus.self_audit import audit_last_n


def test_audit_shape(monkeypatch):
    """Test audit result structure with mocked bundle discovery and replay."""
    def fake_discover(root="out", limit=10):
        return ["a.json", "b.json", "c.json"]
    
    def fake_replay(path):
        # b.json fails, others succeed
        ok = path != "b.json"
        return {"ok": ok, "reason": None if ok else "verify_bundle_failed"}
    
    import bor_consensus.self_audit as sa
    monkeypatch.setattr(sa, "discover_bundles", fake_discover)
    monkeypatch.setattr(sa, "replay_bundle", fake_replay)
    
    res = audit_last_n(3)
    
    assert res["checked"] == 3
    assert res["verified"] == 2
    assert len(res["drift"]) == 1
    assert res["ok"] is False
    assert res["drift"][0]["bundle"] == "b.json"
    assert res["drift"][0]["reason"] == "verify_bundle_failed"


def test_all_verified(monkeypatch):
    """Test audit with all bundles verified successfully."""
    def fake_discover(root="out", limit=10):
        return ["x.json", "y.json"]
    
    def fake_replay(path):
        return {"ok": True, "reason": None}
    
    import bor_consensus.self_audit as sa
    monkeypatch.setattr(sa, "discover_bundles", fake_discover)
    monkeypatch.setattr(sa, "replay_bundle", fake_replay)
    
    res = audit_last_n(2)
    
    assert res["checked"] == 2
    assert res["verified"] == 2
    assert len(res["drift"]) == 0
    assert res["ok"] is True


def test_empty_discovery(monkeypatch):
    """Test audit with no bundles found."""
    def fake_discover(root="out", limit=10):
        return []
    
    import bor_consensus.self_audit as sa
    monkeypatch.setattr(sa, "discover_bundles", fake_discover)
    
    res = audit_last_n(5)
    
    assert res["checked"] == 0
    assert res["verified"] == 0
    assert len(res["drift"]) == 0
    assert res["ok"] is True  # No bundles = no drift


if __name__ == "__main__":
    # Manual testing without pytest
    print("Note: Run with pytest for monkeypatch support")
    print("$ python -m pytest tests/test_self_audit.py -v")

