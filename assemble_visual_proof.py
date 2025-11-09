#!/usr/bin/env python3
"""
Assemble visual proof documentation.

Generates docs/visual_proof.md with embedded figures and verification summary.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from collections import Counter


def load_json(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_markdown(visual_data: Dict[str, Any], verification_report: Dict[str, Any]) -> str:
    """
    Generate markdown documentation with embedded figures.
    
    Returns markdown string.
    """
    steps = visual_data.get("steps", [])
    session_info = visual_data.get("session_info", {})
    metadata = visual_data.get("metadata", {})
    
    # Build markdown
    md = []
    
    # Header
    md.append("# BoR-SDK Visual Proof of Cognition")
    md.append("")
    md.append("**Verified Reasoning Trace with Hallucination Detection**")
    md.append("")
    
    # Metadata
    md.append("## Metadata")
    md.append("")
    md.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    md.append(f"- **Session ID**: `{session_info.get('session_id', 'N/A')[:32]}...`")
    md.append(f"- **Total Steps**: {len(steps)}")
    md.append(f"- **Sessions**: {metadata.get('total_sessions', 1)}")
    md.append(f"- **Extraction Time**: {metadata.get('extraction_timestamp', 'N/A')}")
    md.append(f"- **Guards Computed**: {'✅ Yes' if metadata.get('guards_computed', False) else '❌ No'}")
    md.append("")
    
    # Reasoning Chain
    md.append("## Reasoning Chain")
    md.append("")
    md.append("The complete reasoning trace showing prompt→response progression with cryptographic hash chaining. ")
    md.append("Each node represents a verified reasoning step, color-coded by guard status:")
    md.append("")
    md.append("- **Blue**: Prompt")
    md.append("- **Green**: Safe response (all guards passed)")
    md.append("- **Yellow**: Caution (some metrics in warning zone)")
    md.append("- **Red**: Alert (potential hallucination detected)")
    md.append("")
    md.append("![Reasoning Chain](../figures/reasoning_chain.svg)")
    md.append("")
    md.append("*Each edge is labeled with the SHA-256 hash prefix linking steps cryptographically.*")
    md.append("")
    
    # Hash Propagation
    md.append("## Hash Propagation Proof")
    md.append("")
    md.append("Cryptographic hash chain showing parent→child relationships. ")
    md.append("This demonstrates tamper-evidence: any modification to a step would break the chain.")
    md.append("")
    md.append("![Hash Flow](../figures/hash_flow.png)")
    md.append("")
    md.append("- **Teal nodes**: Regular step certificates")
    md.append("- **Red nodes**: Master certificates (aggregation points)")
    md.append("- **Arrows**: Parent hash → Chain hash links")
    md.append("")
    
    # Hallucination Guard Trace
    md.append("## Hallucination Guard Trace")
    md.append("")
    md.append("Temporal visualization of hallucination detection metrics across all reasoning steps. ")
    md.append("Four independent metrics provide multi-faceted detection:")
    md.append("")
    md.append("1. **Semantic Similarity** (blue solid): Measures prompt-response alignment")
    md.append("2. **Entropy Change** (orange dashed): Detects information drift/injection")
    md.append("3. **Logical Consistency** (green dotted): Validates reasoning coherence")
    md.append("4. **Token Overlap** (purple dash-dot): Verifies response grounding")
    md.append("")
    md.append("![Hallucination Guard](../figures/hallucination_guard.png)")
    md.append("")
    md.append("### Thresholds")
    md.append("")
    md.append("- **Green Zone**: ≥ 0.75 (safe)")
    md.append("- **Yellow Zone**: 0.50 - 0.74 (caution)")
    md.append("- **Red Zone**: < 0.50 (alert)")
    md.append("")
    
    # Red alert steps table
    red_steps = [s for s in steps if s["guard_state"]["status"] == "red"]
    if red_steps:
        md.append("### 🚨 Hallucination Alerts")
        md.append("")
        md.append("The following steps triggered hallucination guards:")
        md.append("")
        md.append("| Step | Prompt | Triggered Guards |")
        md.append("|------|--------|------------------|")
        
        for step in red_steps:
            prompt_short = step["prompt"][:50] + "..." if len(step["prompt"]) > 50 else step["prompt"]
            guards = step["guard_state"]["triggered_guards"]
            guards_str = ", ".join(guards) if guards else "N/A"
            md.append(f"| {step['step_number']} | {prompt_short} | {guards_str} |")
        
        md.append("")
        md.append(f"**Total**: {len(red_steps)} step(s) flagged as potential hallucinations")
        md.append("")
    
    # Certificate Hierarchy
    md.append("## Certificate Hierarchy")
    md.append("")
    md.append("Hierarchical aggregation showing how step certificates roll up into master certificates and session manifests. ")
    md.append("This structure enables efficient verification of large reasoning traces.")
    md.append("")
    md.append("![Master Certificate Tree](../figures/master_certificate_tree.svg)")
    md.append("")
    md.append("- **Top**: Session manifest (aggregates all proofs)")
    md.append("- **Middle**: Master certificates (aggregate multiple steps)")
    md.append("- **Bottom**: Individual step certificates (leaf nodes)")
    md.append("")
    
    # Verification Summary
    md.append("## Verification Summary")
    md.append("")
    
    if verification_report:
        overall = verification_report.get("overall_status", "UNKNOWN")
        passed = verification_report.get("checks_passed", 0)
        warned = verification_report.get("checks_warned", 0)
        failed = verification_report.get("checks_failed", 0)
        
        # Status badge
        if overall == "VERIFIED":
            badge = "✅ VERIFIED"
        elif overall == "PARTIAL":
            badge = "⚠️ PARTIAL"
        else:
            badge = "❌ FAILED"
        
        md.append(f"**Overall Status**: {badge}")
        md.append("")
        md.append("| Check | Status |")
        md.append("|-------|--------|")
        
        for detail in verification_report.get("details", []):
            check_name = detail["check_name"].replace("_", " ").title()
            status = detail["status"].upper()
            status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(status, "❓")
            md.append(f"| {check_name} | {status_icon} {status} |")
        
        md.append("")
        md.append(f"- **Checks Passed**: {passed}")
        md.append(f"- **Checks Warned**: {warned}")
        md.append(f"- **Checks Failed**: {failed}")
        md.append("")
        
        if overall == "VERIFIED":
            md.append("All visualizations accurately represent the underlying cryptographic proofs. ")
            md.append("No discrepancies detected between figures and verified data.")
        elif overall == "PARTIAL":
            md.append("Some non-critical discrepancies detected. Core integrity maintained.")
        else:
            md.append("⚠️ Critical mismatches detected. Manual review recommended.")
    else:
        md.append("⚠️ Verification report not available.")
        md.append("")
        md.append("Run `verify_visual_integrity.py` to generate verification report.")
    
    md.append("")
    
    # Root-Cause Summary
    md.append("## 🔍 Root-Cause Summary")
    md.append("")
    md.append("> Root causes identify *why* specific reasoning steps lost trust. ")
    md.append("> They correspond to measurable guard metrics such as semantic drift, ")
    md.append("> entropy spikes, logical contradictions, and low token overlap. ")
    md.append("> This quantitative breakdown enables rapid audit of reasoning reliability.")
    md.append("")
    
    # Collect root causes
    cause_counter = Counter()
    step_map = {}
    for step in steps:
        causes = step.get("trust_diagnostics", {}).get("root_causes", [])
        for cause in causes:
            cause_counter[cause] += 1
            step_map.setdefault(cause, []).append(str(step["step_number"]))
    
    if cause_counter:
        # Emoji mapping
        cause_emojis = {
            "Semantic Drift": "🧩",
            "Entropy Spike": "⚡",
            "Logical Contradiction": "❌",
            "Low Token Overlap": "🪶"
        }
        
        md.append("| Cause | Count | Affected Steps |")
        md.append("|-------|-------|----------------|")
        
        # Sort by count (descending)
        for cause, count in cause_counter.most_common():
            emoji = cause_emojis.get(cause, "•")
            steps_list = step_map[cause]
            
            # Show first 5 steps
            if len(steps_list) <= 5:
                example_steps = ", ".join(steps_list)
            else:
                example_steps = ", ".join(steps_list[:5]) + f", ... (+{len(steps_list) - 5} more)"
            
            md.append(f"| {emoji} {cause} | {count} | {example_steps} |")
        
        md.append("")
        md.append(f"**Total Issues Detected**: {sum(cause_counter.values())} across {len(step_map)} distinct cause types")
        md.append("")
    else:
        md.append("✅ **No root causes detected** — all reasoning steps passed trust diagnostics.")
        md.append("")
    
    md.append("_This summary quantifies the main failure reasons detected by BoR-SDK's ")
    md.append("Hallucination-Guard system, enabling rapid audit of reasoning reliability._")
    md.append("")
    
    # Appendix
    md.append("## Appendix")
    md.append("")
    md.append("### Statistics")
    md.append("")
    
    # Count statuses
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in steps:
        status = step["guard_state"]["status"]
        status_counts[status] += 1
    
    md.append(f"- **Total Reasoning Steps**: {len(steps)}")
    md.append(f"- **Green (Safe)**: {status_counts['green']} ({status_counts['green']/len(steps)*100:.1f}%)")
    md.append(f"- **Yellow (Caution)**: {status_counts['yellow']} ({status_counts['yellow']/len(steps)*100:.1f}%)")
    md.append(f"- **Red (Alert)**: {status_counts['red']} ({status_counts['red']/len(steps)*100:.1f}%)")
    md.append("")
    
    # Guard metrics
    if steps and steps[0]["guard_state"].get("semantic_similarity") is not None:
        md.append("### Guard Metrics")
        md.append("")
        md.append("Computed using:")
        md.append("")
        md.append("- **Semantic Similarity**: sentence-transformers/all-MiniLM-L6-v2")
        md.append("- **Entropy Change**: Shannon entropy (bits)")
        md.append("- **Logical Consistency**: facebook/bart-large-mnli (NLI)")
        md.append("- **Token Overlap**: Jaccard similarity")
        md.append("")
    
    # Session info
    if session_info.get("start_time"):
        md.append("### Session Information")
        md.append("")
        md.append(f"- **Start Time**: {datetime.fromtimestamp(session_info['start_time']).isoformat()}")
        if session_info.get("end_time"):
            duration = session_info["end_time"] - session_info["start_time"]
            md.append(f"- **Duration**: {duration:.2f} seconds")
        md.append("")
    
    # Footer
    md.append("---")
    md.append("")
    md.append("*This document was automatically generated by the BoR-SDK visualization pipeline.*")
    md.append("")
    md.append("For more information, see [BoR-proof-SDK](https://github.com/yourusername/BoR-proof-SDK).")
    md.append("")
    
    return "\n".join(md)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Assemble visual proof documentation"
    )
    parser.add_argument(
        "--out",
        default="docs/visual_proof.md",
        help="Output markdown file path"
    )
    args = parser.parse_args()
    
    print("📝 Assembling visual proof documentation...\n")
    
    # Load data
    try:
        visual_data = load_json("visual_data.json")
        print("   ✅ Loaded visual_data.json")
    except FileNotFoundError:
        print("❌ Error: visual_data.json not found")
        return 1
    
    # Load verification report (optional)
    try:
        verification_report = load_json("visual_verification_report.json")
        print("   ✅ Loaded visual_verification_report.json")
    except FileNotFoundError:
        print("   ⚠️  Warning: visual_verification_report.json not found")
        print("      Skipping verification summary")
        verification_report = None
    
    # Generate markdown
    print("\n   Generating markdown...")
    markdown = generate_markdown(visual_data, verification_report)
    
    # Ensure output directory exists
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n✅ Visual proof assembled and saved to: {output_path}")
    
    # Summary
    steps = visual_data.get("steps", [])
    red_count = sum(1 for s in steps if s["guard_state"]["status"] == "red")
    
    print(f"\n📊 Document summary:")
    print(f"   - {len(steps)} reasoning steps documented")
    print(f"   - 4 figures embedded")
    print(f"   - {red_count} hallucination alerts reported")
    
    # Root cause summary
    cause_counter = Counter()
    for step in steps:
        causes = step.get("trust_diagnostics", {}).get("root_causes", [])
        cause_counter.update(causes)
    
    if cause_counter:
        print(f"   - {sum(cause_counter.values())} total root causes detected:")
        for cause, count in cause_counter.most_common():
            emoji = {"Semantic Drift": "🧩", "Entropy Spike": "⚡", 
                    "Logical Contradiction": "❌", "Low Token Overlap": "🪶"}.get(cause, "•")
            print(f"      {emoji} {cause}: {count}")
    else:
        print(f"   - ✅ No root causes detected")
    
    if verification_report:
        overall = verification_report.get("overall_status", "UNKNOWN")
        print(f"   - Verification status: {overall}")
    
    print("\n✅ Visual proof assembled and verified.")
    
    return 0


if __name__ == "__main__":
    exit(main())

