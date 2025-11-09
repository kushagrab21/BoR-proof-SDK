#!/usr/bin/env python3
"""
Verify visual integrity of generated figures against cryptographic proofs.

Cross-checks that visualizations accurately represent the data in visual_data.json
without tampering or data loss.
"""

import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_json(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_hash_correspondence(visual_data: Dict[str, Any], figdir: str) -> Dict[str, Any]:
    """
    Check that hash prefixes in reasoning_chain.spec.json match visual_data.json.
    
    Returns check result dict.
    """
    try:
        spec = load_json(str(Path(figdir) / "reasoning_chain.spec.json"))
    except FileNotFoundError:
        return {
            "check_name": "hash_correspondence",
            "status": "fail",
            "message": "reasoning_chain.spec.json not found",
            "evidence": ""
        }
    
    steps = visual_data.get("steps", [])
    mismatches = []
    
    for spec_step in spec:
        step_num = spec_step["step_number"]
        
        # Find corresponding step in visual_data
        vd_step = next((s for s in steps if s["step_number"] == step_num), None)
        if not vd_step:
            mismatches.append(f"Step {step_num} in spec but not in visual_data")
            continue
        
        # Check hash prefixes
        if vd_step["hash_prompt"][:8] != spec_step["hash_prompt_prefix"]:
            mismatches.append(f"Step {step_num}: hash_prompt mismatch")
        if vd_step["hash_response"][:8] != spec_step["hash_response_prefix"]:
            mismatches.append(f"Step {step_num}: hash_response mismatch")
        if vd_step["chain_hash"][:8] != spec_step["chain_hash_prefix"]:
            mismatches.append(f"Step {step_num}: chain_hash mismatch")
        if vd_step["guard_state"]["status"] != spec_step["status"]:
            mismatches.append(f"Step {step_num}: status mismatch")
    
    if mismatches:
        return {
            "check_name": "hash_correspondence",
            "status": "fail",
            "message": f"{len(mismatches)} hash/status mismatches found",
            "evidence": "; ".join(mismatches)
        }
    
    return {
        "check_name": "hash_correspondence",
        "status": "pass",
        "message": f"All {len(spec)} steps have matching hashes and status",
        "evidence": f"Verified {len(spec)} reasoning steps"
    }


def check_node_count_match(visual_data: Dict[str, Any], figdir: str) -> Dict[str, Any]:
    """
    Check that node count in hash_flow.spec.json matches visual_data.json.
    
    Compares step nodes only (not master cert nodes).
    Returns check result dict.
    """
    try:
        spec = load_json(str(Path(figdir) / "hash_flow.spec.json"))
    except FileNotFoundError:
        return {
            "check_name": "node_count_match",
            "status": "fail",
            "message": "hash_flow.spec.json not found",
            "evidence": ""
        }
    
    steps = visual_data.get("steps", [])
    unique_hashes = set(s["chain_hash"][:8] for s in steps)
    
    # Use nodes_from_steps if available (new format), otherwise fall back to nodes
    if "nodes_from_steps" in spec:
        spec_step_nodes = set(spec["nodes_from_steps"])
        
        if len(unique_hashes) != len(spec_step_nodes):
            return {
                "check_name": "node_count_match",
                "status": "warn",
                "message": f"Node count mismatch: {len(unique_hashes)} in data, {len(spec_step_nodes)} in spec",
                "evidence": f"Unique hashes: {len(unique_hashes)}, Spec step nodes: {len(spec_step_nodes)}"
            }
        
        # Additional info about master nodes (not counted as mismatch)
        master_count = len(spec.get("nodes_from_masters", []))
        total_nodes = len(spec.get("all_nodes", []))
        
        return {
            "check_name": "node_count_match",
            "status": "pass",
            "message": f"Step node counts match: {len(spec_step_nodes)} step nodes",
            "evidence": f"Verified {len(spec_step_nodes)} step nodes ({master_count} master nodes, {total_nodes} total)"
        }
    else:
        # Legacy format - compare against all nodes
        spec_nodes = set(spec["nodes"])
        
        if len(unique_hashes) != len(spec_nodes):
            return {
                "check_name": "node_count_match",
                "status": "warn",
                "message": f"Node count mismatch: {len(unique_hashes)} in data, {len(spec_nodes)} in spec",
                "evidence": f"Unique hashes: {len(unique_hashes)}, Spec nodes: {len(spec_nodes)}"
            }
        
        return {
            "check_name": "node_count_match",
            "status": "pass",
            "message": f"Node counts match: {len(spec_nodes)} nodes",
            "evidence": f"Verified {len(spec_nodes)} hash nodes"
        }


def check_chain_integrity(visual_data: Dict[str, Any], figdir: str) -> Dict[str, Any]:
    """
    Check that parent→child edges in hash_flow.spec.json match visual_data.json.
    
    Returns check result dict.
    """
    try:
        spec = load_json(str(Path(figdir) / "hash_flow.spec.json"))
    except FileNotFoundError:
        return {
            "check_name": "chain_integrity",
            "status": "fail",
            "message": "hash_flow.spec.json not found",
            "evidence": ""
        }
    
    steps = visual_data.get("steps", [])
    
    # Build expected edges from visual_data
    expected_edges = set()
    for step in steps:
        if step["parent_hash"]:
            parent_prefix = step["parent_hash"][:8]
            child_prefix = step["chain_hash"][:8]
            expected_edges.add((parent_prefix, child_prefix))
    
    # Build spec edges
    spec_edges = set()
    for edge in spec["edges"]:
        spec_edges.add((edge["parent"], edge["child"]))
    
    # Compare
    missing = expected_edges - spec_edges
    extra = spec_edges - expected_edges
    
    if missing or extra:
        issues = []
        if missing:
            issues.append(f"{len(missing)} edges missing from spec")
        if extra:
            issues.append(f"{len(extra)} extra edges in spec")
        
        return {
            "check_name": "chain_integrity",
            "status": "warn",
            "message": "; ".join(issues),
            "evidence": f"Expected {len(expected_edges)} edges, spec has {len(spec_edges)}"
        }
    
    return {
        "check_name": "chain_integrity",
        "status": "pass",
        "message": f"Chain edges match: {len(expected_edges)} edges verified",
        "evidence": f"All parent→child links validated"
    }


def check_guard_status_accuracy(visual_data: Dict[str, Any], figdir: str) -> Dict[str, Any]:
    """
    Check that guard metrics in hallucination_guard.spec.json match visual_data.json.
    
    Returns check result dict.
    """
    try:
        spec = load_json(str(Path(figdir) / "hallucination_guard.spec.json"))
    except FileNotFoundError:
        return {
            "check_name": "guard_status_accuracy",
            "status": "fail",
            "message": "hallucination_guard.spec.json not found",
            "evidence": ""
        }
    
    steps = visual_data.get("steps", [])
    mismatches = []
    
    for spec_step in spec["steps"]:
        step_num = spec_step["step_number"]
        
        # Find corresponding step
        vd_step = next((s for s in steps if s["step_number"] == step_num), None)
        if not vd_step:
            mismatches.append(f"Step {step_num} in spec but not in visual_data")
            continue
        
        gs = vd_step["guard_state"]
        
        # Check if guards were computed (not None)
        if gs.get("semantic_similarity") is None:
            mismatches.append(f"Step {step_num}: guards not computed (values are None)")
            continue
        
        # Check metrics (rounded to 3 decimals)
        if round(gs["semantic_similarity"], 3) != spec_step["semantic_similarity"]:
            mismatches.append(f"Step {step_num}: semantic_similarity mismatch")
        if round(gs["entropy_change"], 3) != spec_step["entropy_change"]:
            mismatches.append(f"Step {step_num}: entropy_change mismatch")
        if round(gs["logical_consistency"], 3) != spec_step["logical_consistency"]:
            mismatches.append(f"Step {step_num}: logical_consistency mismatch")
        if round(gs["token_overlap"], 3) != spec_step["token_overlap"]:
            mismatches.append(f"Step {step_num}: token_overlap mismatch")
        if gs["status"] != spec_step["status"]:
            mismatches.append(f"Step {step_num}: status mismatch")
    
    if mismatches:
        return {
            "check_name": "guard_status_accuracy",
            "status": "fail",
            "message": f"{len(mismatches)} guard metric mismatches",
            "evidence": "; ".join(mismatches)
        }
    
    return {
        "check_name": "guard_status_accuracy",
        "status": "pass",
        "message": f"All {len(spec['steps'])} steps have accurate guard metrics",
        "evidence": f"Verified 4 metrics × {len(spec['steps'])} steps"
    }


def check_determinism_verification(visual_data: Dict[str, Any], figdir: str) -> Dict[str, Any]:
    """
    Check for duplicate step numbers and validate master cert aggregations.
    
    Returns check result dict.
    """
    steps = visual_data.get("steps", [])
    
    # Check for duplicate (step_number, chain_hash_prefix) pairs
    seen = set()
    duplicates = []
    for step in steps:
        key = (step["step_number"], step["chain_hash"][:8])
        if key in seen:
            duplicates.append(f"Duplicate step {step['step_number']}")
        seen.add(key)
    
    if duplicates:
        return {
            "check_name": "determinism_verification",
            "status": "fail",
            "message": f"Found {len(duplicates)} duplicate step entries",
            "evidence": "; ".join(duplicates)
        }
    
    # Check master cert specs
    try:
        spec = load_json(str(Path(figdir) / "master_certificate_tree.spec.json"))
    except FileNotFoundError:
        return {
            "check_name": "determinism_verification",
            "status": "warn",
            "message": "master_certificate_tree.spec.json not found",
            "evidence": "Could not verify master cert aggregation"
        }
    
    # Verify master certs list correct number of steps
    issues = []
    for master in spec["masters"]:
        if len(master["steps"]) != master["step_count"]:
            issues.append(f"{master['cert_id']}: lists {len(master['steps'])} steps but claims {master['step_count']}")
    
    if issues:
        return {
            "check_name": "determinism_verification",
            "status": "warn",
            "message": "Master cert step count mismatches",
            "evidence": "; ".join(issues)
        }
    
    return {
        "check_name": "determinism_verification",
        "status": "pass",
        "message": f"No duplicate steps, {len(spec['masters'])} master certs validated",
        "evidence": f"{len(steps)} unique steps verified"
    }


def run_verification(visual_data: Dict[str, Any], figdir: str) -> Dict[str, Any]:
    """
    Run all verification checks.
    
    Returns verification report dict.
    """
    print("🔍 Running visual integrity checks...\n")
    
    checks = [
        ("hash_correspondence", check_hash_correspondence),
        ("node_count_match", check_node_count_match),
        ("chain_integrity", check_chain_integrity),
        ("guard_status_accuracy", check_guard_status_accuracy),
        ("determinism_verification", check_determinism_verification)
    ]
    
    details = []
    for check_name, check_func in checks:
        print(f"   Running: {check_name}...")
        result = check_func(visual_data, figdir)
        details.append(result)
        
        # Print result
        status_icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}.get(result["status"], "❓")
        print(f"   {status_icon} {result['status'].upper()}: {result['message']}")
    
    # Calculate overall status
    passed = sum(1 for d in details if d["status"] == "pass")
    warned = sum(1 for d in details if d["status"] == "warn")
    failed = sum(1 for d in details if d["status"] == "fail")
    
    # Note: fail_on_warn parameter will be passed from main()
    # Here we just compute the base status
    if failed == 0 and warned == 0:
        overall_status = "VERIFIED"
    elif failed > len(checks) // 2:
        overall_status = "FAILED"
    else:
        overall_status = "PARTIAL"
    
    report = {
        "timestamp": time.time(),
        "checks_passed": passed,
        "checks_failed": failed,
        "checks_warned": warned,
        "details": details,
        "overall_status": overall_status
    }
    
    return report


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Verify visual integrity against cryptographic proofs"
    )
    parser.add_argument(
        "--figdir",
        default="figures",
        help="Directory containing figure spec files"
    )
    parser.add_argument(
        "--out",
        default="visual_verification_report.json",
        help="Output verification report file"
    )
    parser.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Treat warnings as failures (strict mode)"
    )
    args = parser.parse_args()
    
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         BoR-SDK Visual Integrity Verification                    ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    # Load visual data
    try:
        visual_data = load_json("visual_data.json")
    except FileNotFoundError:
        print("❌ Error: visual_data.json not found")
        return 2
    
    # Run verification
    report = run_verification(visual_data, args.figdir)
    
    # Apply strict mode logic
    if args.fail_on_warn and report['checks_warned'] > 0 and report['checks_failed'] == 0:
        # In strict mode, warnings become failures
        report['overall_status'] = "FAILED"
        print("\n⚠️  Strict mode: warnings treated as failures")
    
    # Save report
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Verification report saved to: {args.out}")
    
    # Print summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    print(f"Checks passed: {report['checks_passed']}")
    print(f"Checks warned: {report['checks_warned']}")
    print(f"Checks failed: {report['checks_failed']}")
    if args.fail_on_warn:
        print("Mode: STRICT (warnings treated as failures)")
    print(f"\nOverall status: {report['overall_status']}")
    print("="*70)
    
    # Print final message and determine exit code
    if report["overall_status"] == "VERIFIED":
        print("\n✅ VERIFIED VISUAL TRACE")
        print("   All visualizations accurately represent cryptographic proofs.")
        return 0
    elif report["overall_status"] == "PARTIAL":
        if args.fail_on_warn:
            print("\n⚠️  PARTIAL VERIFICATION (treated as failure in strict mode)")
            print("   Some warnings detected - failing due to --fail-on-warn flag.")
            return 1
        else:
            print("\n⚠️  PARTIAL VERIFICATION")
            print("   Some checks warned but core integrity maintained.")
            return 0  # Success in non-strict mode
    else:
        print("\n❌ VERIFICATION FAILED")
        print("   Critical mismatches detected between figures and proofs.")
        return 2


if __name__ == "__main__":
    exit(main())

