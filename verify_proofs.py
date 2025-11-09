#!/usr/bin/env python3
"""
Custom proof verifier for BoR-Application
Validates proof structure and integrity
"""
import json
import glob
import os
from pathlib import Path

def verify_proofs(session_name="Cursor-Integrated-LLM"):
    """Verify all proofs for a given session."""
    proofs_dir = Path("proofs")
    
    if not proofs_dir.exists():
        print("❌ No proofs directory found")
        return False
    
    proof_files = sorted(proofs_dir.glob("*.json"))
    
    if not proof_files:
        print("❌ No proof files found")
        return False
    
    print(f"🔍 Verifying {len(proof_files)} proof(s)...")
    
    session_proofs = []
    master_certs = []
    manifests = []
    
    # Required fields for different certificate types
    step_cert_fields = {"session", "prompt", "response", "timestamp", "chain"}
    master_cert_fields = {"certificate_type", "session", "chain", "steps"}
    manifest_fields = {"session_name", "session_id", "environment"}
    
    for proof_file in proof_files:
        try:
            with open(proof_file) as f:
                data = json.load(f)
            
            # Identify certificate type
            if "certificate_type" in data and data["certificate_type"] == "MASTER_REASONING_CERTIFICATE":
                # Master certificate
                if not master_cert_fields.issubset(data.keys()):
                    print(f"❌ {proof_file.name}: Invalid master certificate structure")
                    return False
                master_certs.append(data)
                
            elif "session_name" in data and "environment" in data:
                # Session manifest
                if not manifest_fields.issubset(data.keys()):
                    print(f"❌ {proof_file.name}: Invalid manifest structure")
                    return False
                manifests.append(data)
                
            elif "session" in data and "prompt" in data:
                # Step certificate
                if not step_cert_fields.issubset(data.keys()):
                    print(f"❌ {proof_file.name}: Invalid step certificate structure")
                    return False
                
                # Check session match
                if isinstance(data["session"], dict):
                    if data["session"].get("name") == session_name:
                        session_proofs.append(data)
                elif data["session"] == session_name:
                    session_proofs.append(data)
            
        except json.JSONDecodeError:
            print(f"❌ {proof_file.name}: Invalid JSON")
            return False
        except Exception as e:
            print(f"❌ {proof_file.name}: Error - {e}")
            return False
    
    print(f"✅ All proofs structurally valid")
    print(f"✅ Found {len(session_proofs)} step certificate(s) for session '{session_name}'")
    print(f"✅ Found {len(master_certs)} master certificate(s)")
    print(f"✅ Found {len(manifests)} session manifest(s)")
    
    # Verify hash integrity for step certificates
    import hashlib
    for proof in session_proofs:
        if "prompt" in proof and "hash_sha256" in proof["prompt"]:
            computed_hash = hashlib.sha256(proof["prompt"]["content"].encode()).hexdigest()
            if computed_hash != proof["prompt"]["hash_sha256"]:
                print(f"⚠️  Hash mismatch for prompt: {proof['prompt']['content'][:50]}...")
                return False
    
    print(f"✅ Hash integrity verified")
    return True

if __name__ == "__main__":
    import sys
    session = sys.argv[1] if len(sys.argv) > 1 else "Cursor-Integrated-LLM"
    success = verify_proofs(session)
    sys.exit(0 if success else 1)

