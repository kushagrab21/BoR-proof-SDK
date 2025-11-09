#!/usr/bin/env python3
"""
Extract canonical reasoning trace from BoR-SDK proof certificates.

This script transforms cryptographic proof artifacts into a structured
visual_data.json file for downstream visualization pipeline.
"""

import json
import os
import hashlib
import glob
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from collections import defaultdict


def load_json(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_sha256(text: str) -> str:
    """Compute SHA-256 hash of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def extract_steps(proofs_dir: str) -> List[Dict[str, Any]]:
    """
    Extract reasoning steps from certificate files.
    
    Returns list of step dictionaries sorted chronologically.
    Groups by session and numbers steps globally.
    """
    pattern = os.path.join(proofs_dir, "reasoning_cert_step_*.json")
    step_files = glob.glob(pattern)
    
    # Group by session
    sessions = defaultdict(list)
    for filepath in step_files:
        cert = load_json(filepath)
        session_id = cert["session"]["id"]
        sessions[session_id].append((filepath, cert))
    
    # Process each session independently
    all_steps = []
    global_step_num = 1
    
    for session_id in sorted(sessions.keys()):
        session_steps = sessions[session_id]
        # Sort by timestamp within session
        session_steps.sort(key=lambda x: x[1]["timestamp"]["unix"])
        
        for filepath, cert in session_steps:
            step = {
                "step_number": global_step_num,
                "session_step_number": cert["session"]["step_number"],
                "session_id": session_id,
                "timestamp": cert["timestamp"]["unix"],
                "prompt": cert["prompt"]["content"],
                "response": cert["response"]["content"],
                "hash_prompt": cert["prompt"]["hash_sha256"],
                "hash_response": cert["response"]["hash_sha256"],
                "chain_hash": cert["chain"]["deterministic_chain_hash"],
                "parent_hash": cert["chain"]["prior_step_hashes"][-1] if cert["chain"]["prior_step_hashes"] else None,
                "guard_state": {
                    "semantic_similarity": None,
                    "entropy_change": None,
                    "logical_consistency": None,
                    "status": "green",
                    "triggered_guards": []
                },
                "metadata": {
                    "execution_time_ms": cert["response"]["elapsed_seconds"] * 1000,
                    "model": cert["model"]["name"],
                    "deterministic": cert["verification"]["deterministic"]
                }
            }
            all_steps.append(step)
            global_step_num += 1
    
    return all_steps


def extract_master_certificates(proofs_dir: str) -> List[Dict[str, Any]]:
    """
    Extract master certificate metadata.
    
    Returns list of master certificate summaries.
    """
    pattern = os.path.join(proofs_dir, "MASTER_CERTIFICATE_*.json")
    master_files = glob.glob(pattern)
    
    masters = []
    for filepath in master_files:
        cert = load_json(filepath)
        
        # Extract timestamp from filename
        basename = os.path.basename(filepath)
        timestamp_str = basename.replace("MASTER_CERTIFICATE_", "").replace(".json", "")
        
        master = {
            "cert_id": basename.replace(".json", ""),
            "timestamp": float(timestamp_str),
            "aggregated_hash": cert["chain"]["master_hash"],
            "step_count": cert["session"]["total_steps"],
            "verification_status": "verified" if cert["chain"]["integrity_verified"] else "failed"
        }
        masters.append(master)
    
    # Sort by timestamp
    masters.sort(key=lambda x: x["timestamp"])
    
    return masters


def extract_session_info(proofs_dir: str) -> Dict[str, Any]:
    """
    Extract session manifest metadata.
    
    Returns combined session information from all manifests.
    """
    pattern = os.path.join(proofs_dir, "session_*_manifest.json")
    manifest_files = glob.glob(pattern)
    
    if not manifest_files:
        return {
            "session_id": "unknown",
            "total_steps": 0,
            "start_time": None,
            "end_time": None
        }
    
    # Use the most recent manifest
    manifest_files.sort()
    latest_manifest = load_json(manifest_files[-1])
    
    session_info = {
        "session_id": latest_manifest["session_id"],
        "total_steps": len(glob.glob(os.path.join(proofs_dir, "reasoning_cert_step_*.json"))),
        "start_time": latest_manifest["start_time"],
        "end_time": None  # Will be populated if available from master cert
    }
    
    # Try to get end time from master certificate
    master_pattern = os.path.join(proofs_dir, "MASTER_CERTIFICATE_*.json")
    master_files = glob.glob(master_pattern)
    if master_files:
        master_files.sort()
        latest_master = load_json(master_files[-1])
        if "session" in latest_master and "end_time" in latest_master["session"]:
            session_info["end_time"] = latest_master["session"]["end_time"]
    
    return session_info


def validate_chain(steps: List[Dict[str, Any]]) -> bool:
    """
    Validate hash chain integrity across steps.
    
    Validates chains within each session separately.
    Returns True if all chains are valid, False otherwise.
    """
    if not steps:
        return True
    
    # Group by session
    sessions = defaultdict(list)
    for step in steps:
        sessions[step["session_id"]].append(step)
    
    all_valid = True
    
    for session_id, session_steps in sessions.items():
        # Sort by session step number
        session_steps.sort(key=lambda x: x["session_step_number"])
        
        # Check first step in session has no parent
        if session_steps[0]["parent_hash"] is not None:
            print(f"⚠️  WARNING: Session {session_id[:16]}... step 1 has non-null parent_hash")
            all_valid = False
        
        # Check subsequent steps link correctly within session
        for i in range(1, len(session_steps)):
            expected_parent = session_steps[i-1]["chain_hash"]
            actual_parent = session_steps[i]["parent_hash"]
            
            if expected_parent != actual_parent:
                print(f"⚠️  WARNING: Session {session_id[:16]}... step {session_steps[i]['session_step_number']} parent_hash mismatch")
                print(f"    Expected: {expected_parent}")
                print(f"    Actual:   {actual_parent}")
                all_valid = False
    
    return all_valid


def validate_hashes(steps: List[Dict[str, Any]]) -> bool:
    """
    Validate that stored hashes match computed hashes.
    
    Returns True if all hashes are valid, False otherwise.
    """
    valid = True
    
    for step in steps:
        # Validate prompt hash
        computed_prompt_hash = compute_sha256(step["prompt"])
        if computed_prompt_hash != step["hash_prompt"]:
            print(f"⚠️  WARNING: Step {step['step_number']} prompt hash mismatch")
            valid = False
        
        # Validate response hash
        computed_response_hash = compute_sha256(step["response"])
        if computed_response_hash != step["hash_response"]:
            print(f"⚠️  WARNING: Step {step['step_number']} response hash mismatch")
            valid = False
    
    return valid


def main():
    """Main extraction pipeline."""
    proofs_dir = "proofs"
    output_file = "visual_data.json"
    
    print("🔍 Extracting trace data from proof certificates...")
    
    # Extract data
    steps = extract_steps(proofs_dir)
    master_certificates = extract_master_certificates(proofs_dir)
    session_info = extract_session_info(proofs_dir)
    
    # Validate
    print(f"📊 Extracted {len(steps)} steps, {len(master_certificates)} master certificates")
    
    chain_valid = validate_chain(steps)
    hashes_valid = validate_hashes(steps)
    
    if chain_valid and hashes_valid:
        print("✅ Verified chain integrity")
    else:
        print("❌ Chain validation failed")
    
    # Build output structure
    visual_data = {
        "metadata": {
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_directory": proofs_dir,
            "chain_valid": chain_valid,
            "hashes_valid": hashes_valid,
            "total_sessions": len(set(s["session_id"] for s in steps))
        },
        "steps": steps,
        "master_certificates": master_certificates,
        "session_info": session_info
    }
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(visual_data, f, indent=2, ensure_ascii=False)
    
    num_sessions = len(set(s["session_id"] for s in steps))
    print(f"✅ Extracted {len(steps)} steps from {num_sessions} session(s), {len(master_certificates)} master certificates")
    print(f"📁 Output written to: {output_file}")
    
    # Summary statistics
    if steps:
        total_time_ms = sum(s["metadata"]["execution_time_ms"] for s in steps)
        print(f"⏱️  Total execution time: {total_time_ms/1000:.2f}s")
        print(f"📊 Average time per step: {total_time_ms/len(steps):.2f}ms")


if __name__ == "__main__":
    main()

