#!/usr/bin/env python3
"""
Generate master certificate tree visualization with modern styling.

Creates an SVG showing hierarchical aggregation of step certificates
into master certificates and session manifests.
"""

from __future__ import annotations  # Enable deferred annotation evaluation

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


def load_data(filepath: str = "visual_data.json") -> Dict[str, Any]:
    """Load visual_data.json."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_certificate_tree(visual_data: Dict[str, Any]) -> Digraph:
    """
    Create a Graphviz tree showing certificate hierarchy with modern styling.
    
    Returns a Digraph object.
    """
    dot = Digraph(comment='BoR Proof-of-Cognition Certificate Hierarchy')
    
    # Modern light theme for better readability
    dot.attr(rankdir='TB')  # Top to bottom
    dot.attr(size='24,20')
    dot.attr(bgcolor='#F9FAFB:FFFFFF')  # Subtle light gradient
    dot.attr(fontname='Inter, Arial', fontcolor='#1F2937')
    dot.attr(pad='0.6')
    dot.attr(nodesep='1.0')
    dot.attr(ranksep='1.8')
    
    # Enhanced node styling
    dot.attr('node',
             shape='box',
             style='rounded,filled',
             fontname='Inter, Arial',
             fontsize='11',
             margin='0.5,0.3',
             penwidth='2')
    
    # Enhanced edge styling
    dot.attr('edge',
             fontname='Inter, Arial',
             fontsize='9',
             fontcolor='#6B7280',
             penwidth='2.5',
             arrowsize='1.0')
    
    steps = visual_data.get("steps", [])
    master_certs = visual_data.get("master_certificates", [])
    session_info = visual_data.get("session_info", {})
    
    # Root: Session Manifest with metallic silver gradient
    session_id = session_info.get("session_id", "unknown")
    session_id_short = session_id[:16] + "..."
    total_steps = session_info.get("total_steps", len(steps))
    
    dot.node(
        "session",
        f"🎯 SESSION ROOT\n{session_id_short}\n\nTotal Steps: {total_steps}",
        fillcolor="#94A3B8:#64748B",  # Silver metallic gradient
        fontcolor="#FFFFFF",
        fontsize="14",
        style="rounded,filled",
        penwidth='4',
        peripheries='2'
    )
    
    # Middle: Master Certificates with blue gradients
    for i, master in enumerate(master_certs):
        master_id = f"master_{i}"
        cert_id = master["cert_id"]
        agg_hash = master["aggregated_hash"][:12] + "..."
        step_count = master["step_count"]
        status = master["verification_status"]
        
        # Status emoji
        status_icon = "✅" if status == "verified" else ("⚠️" if status == "partial" else "❌")
        
        # Color gradient based on verification status
        if status == "verified":
            master_gradient = "#3B82F6:#2563EB"  # Blue gradient
        elif status == "partial":
            master_gradient = "#F59E0B:#D97706"  # Amber gradient
        else:
            master_gradient = "#EF4444:#DC2626"  # Red gradient
        
        dot.node(
            master_id,
            f"🏆 MASTER CERTIFICATE\n{cert_id}\n\n🔒 {agg_hash}\n📊 {step_count} aggregated steps\n{status_icon} {status.upper()}",
            fillcolor=master_gradient,
            fontcolor="#FFFFFF",
            fontsize="11",
            style="rounded,filled",
            penwidth='3'
        )
        
        # Connect to session with gradient edge
        dot.edge("session", master_id,
                color="#6366F1",
                penwidth='3.5',
                label="aggregates")
    
    # Bottom: Step Certificates (circular nodes with guard-based gradients)
    for step in steps:
        step_num = step["step_number"]
        step_id = f"step_{step_num}"
        chain_hash = step["chain_hash"][:10] + "..."
        guard_status = step["guard_state"]["status"]
        
        # Status-based emoji and gradient
        status_emoji = {"green": "✓", "yellow": "⚠", "red": "✗"}[guard_status]
        step_gradients = {
            "green": "#10B981:#059669",
            "yellow": "#F59E0B:#D97706",
            "red": "#EF4444:#DC2626"
        }
        step_gradient = step_gradients.get(guard_status, "#94A3B8:#64748B")
        
        prompt_short = step["prompt"][:35] + "..." if len(step["prompt"]) > 35 else step["prompt"]
        
        dot.node(
            step_id,
            f"{status_emoji}\nS{step_num}\n{prompt_short}\n🔒 {chain_hash}",
            fillcolor=step_gradient,
            fontcolor="#FFFFFF",
            fontsize="9",
            shape='circle',
            style='filled',
            penwidth='3' if guard_status == 'red' else '2'
        )
        
        # Find which master cert this step belongs to
        step_timestamp = step["timestamp"]
        
        # Connect to appropriate master cert
        best_master_idx = 0
        for i, master in enumerate(master_certs):
            if master["timestamp"] <= step_timestamp:
                best_master_idx = i
        
        master_id = f"master_{best_master_idx}"
        dot.edge(master_id, step_id,
                color="#9CA3AF",
                style="dashed",
                penwidth='2')
    
    # Calculate verification summary
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in steps:
        status_counts[step["guard_state"]["status"]] += 1
    
    verified_masters = sum(1 for m in master_certs if m.get("verification_status", "").lower() == "verified")
    
    # Add modern footer with branding
    footer = (f"\\n\\n🔐 Proof-of-Cognition Certificate Tree — Cryptographically Linked Hierarchy\\n"
             f"Guard Summary: 🟢 {status_counts['green']}  🟡 {status_counts['yellow']}  "
             f"🔴 {status_counts['red']}  |  Masters: {verified_masters}/{len(master_certs)} verified\\n"
             f"BoR-SDK • Deterministic AI • Hallucination-Proof Reasoning\\n"
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    dot.attr(label=footer, fontsize='11', fontcolor='#6B7280')
    
    return dot


def write_sidecar_spec(visual_data: Dict[str, Any], output_dir: str = "figures", filename: str = "master_certificate_tree.spec.json") -> str:
    """
    Write sidecar JSON specification for verification.
    
    Returns the full output path.
    """
    steps = visual_data.get("steps", [])
    master_certs = visual_data.get("master_certificates", [])
    session_info = visual_data.get("session_info", {})
    
    # Build master cert specs with their associated steps
    masters = []
    for master in master_certs:
        # Find steps that belong to this master cert (by timestamp)
        master_timestamp = master["timestamp"]
        
        # Get steps that are at or before this master cert's timestamp
        associated_steps = []
        for step in steps:
            if step["timestamp"] <= master_timestamp + 100:  # Allow small time window
                associated_steps.append(step["chain_hash"][:8])
        
        masters.append({
            "cert_id": master["cert_id"],
            "aggregated_hash_prefix": master["aggregated_hash"][:8],
            "step_count": master["step_count"],
            "verification_status": master["verification_status"].upper(),
            "steps": associated_steps[:master["step_count"]]  # Limit to actual count
        })
    
    spec = {
        "session_id": session_info.get("session_id", "unknown")[:16] + "...",
        "masters": masters
    }
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    full_path = output_path / filename
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    return str(full_path)


def save_figure(dot: Digraph, output_dir: str = "figures", filename: str = "master_certificate_tree") -> str:
    """
    Save the tree as SVG.
    
    Returns the full output path.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    full_path = output_path / filename
    dot.render(str(full_path), format='svg', cleanup=True)
    
    return str(full_path) + ".svg"


def main():
    """Main execution."""
    if not GRAPHVIZ_AVAILABLE:
        print("❌ Error: graphviz not installed")
        print("   Install with: pip install graphviz")
        print("   Also ensure graphviz system package is installed:")
        print("   - macOS: brew install graphviz")
        print("   - Linux: apt-get install graphviz")
        return
    
    print("🌳 Generating modern master certificate tree...")
    
    # Load data
    try:
        visual_data = load_data()
    except FileNotFoundError:
        print("❌ Error: visual_data.json not found")
        return
    
    steps = visual_data.get("steps", [])
    masters = visual_data.get("master_certificates", [])
    
    if not steps:
        print("⚠️  Warning: No steps found in visual_data.json")
        return
    
    # Create tree with modern styling
    print(f"   Building hierarchical proof tree: {len(masters)} masters, {len(steps)} steps...")
    dot = create_certificate_tree(visual_data)
    
    # Save
    output_path = save_figure(dot)
    print(f"✅ Certificate tree saved to: {output_path}")
    
    # Write sidecar spec
    spec_path = write_sidecar_spec(visual_data)
    print(f"   Sidecar spec: {spec_path}")
    
    # Summary with enhanced stats
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in steps:
        status_counts[step["guard_state"]["status"]] += 1
    
    print(f"\n📊 Certificate hierarchy summary:")
    print(f"   Session manifests: 1")
    print(f"   Master certificates: {len(masters)}")
    print(f"   Step certificates: {len(steps)}")
    print(f"   Guard status: 🟢 {status_counts['green']}  🟡 {status_counts['yellow']}  🔴 {status_counts['red']}")
    
    # Verification status
    all_verified = all(m["verification_status"] == "verified" for m in masters)
    print(f"   Verification: {'✅ All verified' if all_verified else '⚠️  Some unverified'}")


if __name__ == "__main__":
    main()
