#!/usr/bin/env python3
"""
Generate reasoning chain visualization.

Creates an SVG graph showing the sequential reasoning flow with
prompt → response progression, colored by guard status.
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


def get_color_for_status(status: str) -> str:
    """Return color hex code for guard status."""
    colors = {
        "green": "#50E3C2",
        "yellow": "#F8E71C",
        "red": "#D0021B"
    }
    return colors.get(status, "#CCCCCC")


def create_reasoning_chain_graph(visual_data: Dict[str, Any]) -> Digraph:
    """
    Create a Graphviz digraph of the reasoning chain with modern styling.
    
    Returns a Digraph object ready to be rendered.
    """
    dot = Digraph(comment='BoR Reasoning Chain - Verified Cognition Trace')
    
    # Modern dark theme with subtle gradient background
    dot.attr(rankdir='TB')  # Top to bottom
    dot.attr(size='14,28')
    dot.attr(bgcolor='#0D1117:0E1520')  # Subtle dark gradient
    dot.attr(fontname='Inter, Arial', fontcolor='#C9D1D9')
    dot.attr(pad='0.5')
    dot.attr(nodesep='0.8')
    dot.attr(ranksep='1.2')
    
    # Modern node styling with rounded corners and shadows
    dot.attr('node', 
             shape='box',
             style='rounded,filled',
             fontname='Inter, Arial',
             fontsize='11',
             margin='0.3,0.2',
             penwidth='2')
    
    # Enhanced edge styling with smooth curves
    dot.attr('edge',
             fontname='Inter, Arial',
             fontsize='9',
             fontcolor='#8B949E',
             color='#30363D',
             penwidth='2',
             arrowsize='0.8')
    
    steps = visual_data.get("steps", [])
    
    # Root cause emoji mapping
    cause_emojis = {
        "Semantic Drift": "🧩",
        "Entropy Spike": "⚡",
        "Logical Contradiction": "❌",
        "Low Token Overlap": "🪶"
    }
    
    for step in steps:
        step_num = step["step_number"]
        prompt = step["prompt"]
        response = step["response"]
        chain_hash = step["chain_hash"]
        guard_status = step["guard_state"]["status"]
        
        # Get trust diagnostics
        trust_diag = step.get("trust_diagnostics", {})
        trust_score = trust_diag.get("trust_score", 0.0)
        trust_label = trust_diag.get("trust_label", "Unknown")
        root_causes = trust_diag.get("root_causes", [])
        
        # Truncate long text for display
        prompt_display = prompt[:90] + "..." if len(prompt) > 90 else prompt
        response_display = response[:90] + "..." if len(response) > 90 else response
        hash_prefix = chain_hash[:8]
        
        # Modern color scheme with glow effects based on guard status
        status_colors = {
            "green": "#2ECC71:#27AE60",   # Green gradient with glow
            "yellow": "#F39C12:#E67E22",  # Amber gradient
            "red": "#E74C3C:#C0392B"       # Red gradient with warning
        }
        node_gradient = status_colors.get(guard_status, "#7F8C8D:#95A5A6")
        
        # Status emoji for visual clarity
        status_emoji = {"green": "✓", "yellow": "⚠", "red": "✗"}[guard_status]
        
        # Build root causes tooltip text with emojis
        causes_text = ""
        if root_causes:
            causes_with_emoji = [f"{cause_emojis.get(c, '•')} {c}" for c in root_causes]
            causes_text = f"\n\n🔍 Causes: {'; '.join(causes_with_emoji)}"
        
        # Create prompt node with blue gradient
        prompt_node_id = f"prompt_{step_num}"
        dot.node(
            prompt_node_id,
            f"⚡ STEP {step_num} — PROMPT\n\n{prompt_display}",
            fillcolor="#4A90E2:#357ABD",
            fontcolor="#FFFFFF",
            style='rounded,filled',
            penwidth='0',
            tooltip=f"Step {step_num} Prompt\n{prompt[:200]}"
        )
        
        # Create response node with status-based gradient, badge, and trust info
        response_label = f"💬 RESPONSE {step_num}\n\n{response_display}\n\n"
        response_label += f"[{status_emoji} {guard_status.upper()}]"
        
        # Add trust score and causes to label
        if trust_label in ["Review", "Untrusted"]:
            response_label += f"\n\nTrust: {trust_score:.0%} ({trust_label})"
            if root_causes:
                # Show compact causes in label
                response_label += f"\n{' '.join([cause_emojis.get(c, '•') for c in root_causes])}"
        
        # Build detailed tooltip
        tooltip_text = f"{trust_label} — Trust Score: {trust_score:.0%}\n"
        tooltip_text += f"Response: {response[:150]}...\n"
        if root_causes:
            tooltip_text += f"Root Causes: {', '.join(root_causes)}"
        else:
            tooltip_text += "No issues detected"
        
        response_node_id = f"response_{step_num}"
        dot.node(
            response_node_id,
            response_label,
            fillcolor=node_gradient,
            fontcolor="#FFFFFF",
            style='rounded,filled',
            penwidth='3' if guard_status == 'red' else '0',
            tooltip=tooltip_text
        )
        
        # Connect prompt to response with hash annotation
        dot.edge(
            prompt_node_id,
            response_node_id,
            label=f"  🔒 {hash_prefix}  ",
            color="#58A6FF",
            penwidth='2.5',
            fontcolor="#79C0FF"
        )
        
        # Connect to next prompt if exists (session-aware)
        if step_num < len(steps):
            next_prompt_id = f"prompt_{step_num + 1}"
            next_step = next((s for s in steps if s["step_number"] == step_num + 1), None)
            if next_step and next_step["session_id"] == step["session_id"]:
                dot.edge(
                    response_node_id,
                    next_prompt_id,
                    style="dashed",
                    color="#484F58",
                    penwidth='1.5',
                    arrowhead='vee'
                )
    
    # Calculate guard summary
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in steps:
        status_counts[step["guard_state"]["status"]] += 1
    
    # Calculate root cause summary
    all_causes = []
    for step in steps:
        all_causes.extend(step.get("trust_diagnostics", {}).get("root_causes", []))
    
    from collections import Counter
    cause_counts = Counter(all_causes)
    
    # Build cause summary with emojis
    cause_summary = ""
    if cause_counts:
        cause_parts = []
        for cause, count in cause_counts.most_common():
            emoji = cause_emojis.get(cause, "•")
            cause_parts.append(f"{emoji} {cause}: {count}")
        cause_summary = f"\\nRoot Causes: {' | '.join(cause_parts)}\\n"
    
    # Add modern header and footer with branding
    extraction_time = visual_data["metadata"].get("extraction_timestamp", "N/A")
    chain_status = "✅ VERIFIED" if visual_data["metadata"].get("chain_valid", False) else "⚠️ PARTIAL"
    
    header = "🧠 BoR-SDK Visual Proof — Deterministic AI Reasoning Chain"
    footer = (f"\\n\\nGuard Summary: 🟢 {status_counts['green']}  🟡 {status_counts['yellow']}  "
             f"🔴 {status_counts['red']}  |  Chain Status: {chain_status}"
             f"{cause_summary}"
             f"BoR-Verified • Deterministic Replay • Hallucination-Proof\\n"
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    dot.attr(label=footer, fontsize='10', fontcolor='#8B949E')
    
    return dot


def write_sidecar_spec(visual_data: Dict[str, Any], output_dir: str = "figures", filename: str = "reasoning_chain.spec.json") -> str:
    """
    Write sidecar JSON specification for verification.
    
    Returns the full output path.
    """
    steps = visual_data.get("steps", [])
    
    spec = []
    for step in steps:
        spec.append({
            "step_number": step["step_number"],
            "hash_prompt_prefix": step["hash_prompt"][:8],
            "hash_response_prefix": step["hash_response"][:8],
            "chain_hash_prefix": step["chain_hash"][:8],
            "status": step["guard_state"]["status"]
        })
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    full_path = output_path / filename
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    return str(full_path)


def save_figure(dot: Digraph, output_dir: str = "figures", filename: str = "reasoning_chain") -> str:
    """
    Save the graph as SVG.
    
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
    
    print("📊 Generating reasoning chain visualization...")
    
    # Load data
    try:
        visual_data = load_data()
    except FileNotFoundError:
        print("❌ Error: visual_data.json not found")
        return
    
    steps = visual_data.get("steps", [])
    if not steps:
        print("⚠️  Warning: No steps found in visual_data.json")
        return
    
    # Create graph
    print(f"   Creating graph with {len(steps)} steps...")
    dot = create_reasoning_chain_graph(visual_data)
    
    # Save
    output_path = save_figure(dot)
    print(f"✅ Reasoning chain saved to: {output_path}")
    
    # Write sidecar spec
    spec_path = write_sidecar_spec(visual_data)
    print(f"   Sidecar spec: {spec_path}")
    
    # Summary
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in steps:
        status = step["guard_state"]["status"]
        status_counts[status] += 1
    
    print(f"\n📊 Visualization summary:")
    print(f"   Total steps: {len(steps)}")
    print(f"   🟢 Green:  {status_counts['green']}")
    print(f"   🟡 Yellow: {status_counts['yellow']}")
    print(f"   🔴 Red:    {status_counts['red']}")


if __name__ == "__main__":
    main()

