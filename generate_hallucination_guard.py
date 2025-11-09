#!/usr/bin/env python3
"""
Generate hallucination guard visualization.

Creates a PNG timeline plot showing guard metrics across reasoning steps
with color-coded threshold zones.
"""

from __future__ import annotations  # Enable deferred annotation evaluation

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns
    import numpy as np
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False


def load_data(filepath: str = "visual_data.json") -> Dict[str, Any]:
    """Load visual_data.json."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_entropy(entropy_values: List[float], max_entropy: float = 1.0) -> List[float]:
    """
    Normalize entropy change values to [0, 1] scale for plotting.
    
    Uses max_entropy as the scaling factor (default 1.0 bits).
    """
    return [min(abs(e) / max_entropy, 1.0) for e in entropy_values]


def create_guard_plot(visual_data: Dict[str, Any]) -> plt.Figure:
    """
    Create matplotlib figure with guard metrics timeline (Mission Control aesthetic).
    Now includes root-cause frequency subplot.
    
    Returns a Figure object.
    """
    # Modern dark dashboard theme
    plt.style.use('dark_background')
    sns.set_style("darkgrid")
    
    # Create figure with 2 subplots (metrics + root causes)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 14), dpi=300, facecolor='#0E1117',
                                     gridspec_kw={'height_ratios': [3, 1]})
    ax1.set_facecolor('#121212')
    ax2.set_facecolor('#121212')
    
    steps = visual_data.get("steps", [])
    
    # Extract data
    step_numbers = [s["step_number"] for s in steps]
    semantic_sim = [s["guard_state"]["semantic_similarity"] for s in steps]
    entropy_change = [s["guard_state"]["entropy_change"] for s in steps]
    logical_consistency = [s["guard_state"]["logical_consistency"] for s in steps]
    token_overlap = [s["guard_state"]["token_overlap"] for s in steps]
    statuses = [s["guard_state"]["status"] for s in steps]
    
    # Normalize entropy for visualization (scale to 0-1)
    entropy_normalized = normalize_entropy(entropy_change, max_entropy=1.0)
    
    # === SUBPLOT 1: Metrics Timeline ===
    # Plot threshold zones with gradient transparency
    ax1.axhspan(0.75, 1.0, alpha=0.15, color='#2ECC71', label='🟢 Safe Zone', zorder=0)
    ax1.axhspan(0.50, 0.75, alpha=0.12, color='#F39C12', label='🟡 Caution Zone', zorder=0)
    ax1.axhspan(0.0, 0.50, alpha=0.18, color='#E74C3C', label='🔴 Alert Zone', zorder=0)
    
    # Plot metrics with neon glow effects (thick lines)
    ax1.plot(step_numbers, semantic_sim, 'o-', linewidth=3.5, markersize=10,
            color='#00D9FF', label='💎 Semantic Similarity', alpha=0.95, markeredgecolor='white', markeredgewidth=1.5)
    
    ax1.plot(step_numbers, entropy_normalized, 's-', linewidth=3.5, markersize=10,
            color='#FF6B35', label='🌊 Entropy Change', alpha=0.95, markeredgecolor='white', markeredgewidth=1.5)
    
    ax1.plot(step_numbers, logical_consistency, '^-', linewidth=3.5, markersize=10,
            color='#7FFF00', label='🧠 Logical Consistency', alpha=0.95, markeredgecolor='white', markeredgewidth=1.5)
    
    ax1.plot(step_numbers, token_overlap, 'd-', linewidth=3.5, markersize=10,
            color='#FF1493', label='🔗 Token Overlap', alpha=0.95, markeredgecolor='white', markeredgewidth=1.5)
    
    # Mark red status steps with prominent alert markers
    red_steps = [step_numbers[i] for i, s in enumerate(statuses) if s == "red"]
    if red_steps:
        red_semantic = [semantic_sim[i] for i, s in enumerate(statuses) if s == "red"]
        ax1.scatter(red_steps, red_semantic, s=500, c='#FF0000', marker='X',
                  edgecolors='#FFFFFF', linewidths=3, alpha=0.9, zorder=15,
                  label='🚨 Hallucination Alert')
        
        # Annotate red steps with modern callouts
        for i, step_num in enumerate(red_steps):
            idx = step_numbers.index(step_num)
            prompt = steps[idx]["prompt"][:25] + "..."
            ax1.annotate(
                f'⚠️ Step {step_num}\n{prompt}',
                xy=(step_num, semantic_sim[idx]),
                xytext=(15, 25), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.7', fc='#E74C3C', ec='#FFFFFF', alpha=0.95, linewidth=2),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', 
                              color='#FFFFFF', lw=2),
                fontsize=9,
                color='white',
                fontweight='bold'
            )
    
    # Modern labels with enhanced visibility
    ax1.set_xlabel('Reasoning Step Number', fontsize=14, fontweight='bold', color='#C9D1D9')
    ax1.set_ylabel('Metric Value (0 = worst, 1 = best)', fontsize=14, fontweight='bold', color='#C9D1D9')
    ax1.set_title(
        '🧠 BoR Hallucination Guard Trace — Real-Time Confidence Monitor',
        fontsize=20, fontweight='bold', pad=25, color='#FFFFFF'
    )
    
    # Enhanced grid and limits
    ax1.set_ylim(-0.05, 1.08)
    ax1.set_xlim(min(step_numbers) - 0.5, max(step_numbers) + 0.5)
    ax1.grid(True, alpha=0.2, color='#30363D', linestyle='--', linewidth=0.8)
    ax1.tick_params(colors='#8B949E', labelsize=11)
    
    # Modern legend with dashboard styling
    legend = ax1.legend(loc='upper left', fontsize=11, frameon=True, fancybox=True, 
                      shadow=True, facecolor='#161B22', edgecolor='#30363D', framealpha=0.95)
    legend.get_frame().set_linewidth(2)
    for text in legend.get_texts():
        text.set_color('#C9D1D9')
    
    # Guard summary statistics panel
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for status in statuses:
        status_counts[status] += 1
    
    summary_text = (f"Guard Summary: 🟢 {status_counts['green']}  🟡 {status_counts['yellow']}  "
                   f"🔴 {status_counts['red']}  |  "
                   f"Alert Rate: {status_counts['red']/len(steps)*100:.0f}%")
    
    # Add summary badge in top-right
    ax1.text(0.98, 0.97, summary_text,
           transform=ax1.transAxes,
           fontsize=12,
           bbox=dict(boxstyle='round,pad=0.8', facecolor='#161B22', 
                    edgecolor='#30363D', alpha=0.95, linewidth=2),
           verticalalignment='top',
           horizontalalignment='right',
           color='#C9D1D9',
           fontweight='bold')
    
    # === SUBPLOT 2: Root-Cause Frequency ===
    # Collect all root causes
    from collections import Counter
    all_causes = []
    for step in steps:
        all_causes.extend(step.get("trust_diagnostics", {}).get("root_causes", []))
    
    if all_causes:
        cause_counts = Counter(all_causes)
        
        # Define cause colors
        cause_colors_map = {
            "Semantic Drift": "#00BFFF",
            "Entropy Spike": "#FF8C00",
            "Logical Contradiction": "#E74C3C",
            "Low Token Overlap": "#9B59B6"
        }
        
        causes = list(cause_counts.keys())
        counts = [cause_counts[c] for c in causes]
        colors = [cause_colors_map.get(c, "#7F8C8D") for c in causes]
        
        # Create bar chart
        bars = ax2.bar(causes, counts, color=colors, alpha=0.9, edgecolor='white', linewidth=2)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', color='#C9D1D9',
                    fontsize=12, fontweight='bold')
        
        ax2.set_xlabel('Root Cause Type', fontsize=12, fontweight='bold', color='#C9D1D9')
        ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold', color='#C9D1D9')
        ax2.set_title('🧩 Root-Cause Frequency Analysis', fontsize=16, fontweight='bold', color='#FFFFFF', pad=15)
        ax2.tick_params(colors='#8B949E', labelsize=10)
        ax2.grid(True, alpha=0.2, color='#30363D', linestyle='--', linewidth=0.8, axis='y')
    else:
        ax2.text(0.5, 0.5, '✅ No Root Causes Detected\nAll Steps Trusted',
                ha='center', va='center', transform=ax2.transAxes,
                fontsize=16, color='#2ECC71', fontweight='bold')
    
    # Footer with branding
    footer_text = (f"BoR-SDK • Deterministic AI • Hallucination-Proof Reasoning\n"
                  f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                  f"Thresholds: 🟢 ≥0.75  🟡 0.50-0.74  🔴 <0.50")
    
    fig.text(
        0.5, 0.01,
        footer_text,
        ha='center', fontsize=10, style='italic', color='#8B949E'
    )
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.98])
    
    return fig


def write_sidecar_spec(visual_data: Dict[str, Any], output_dir: str = "figures", filename: str = "hallucination_guard.spec.json") -> str:
    """
    Write sidecar JSON specification for verification.
    
    Returns the full output path.
    """
    steps = visual_data.get("steps", [])
    
    spec_steps = []
    for step in steps:
        gs = step["guard_state"]
        spec_steps.append({
            "step_number": step["step_number"],
            "semantic_similarity": gs["semantic_similarity"],
            "entropy_change": gs["entropy_change"],
            "logical_consistency": gs["logical_consistency"],
            "token_overlap": gs["token_overlap"],
            "status": gs["status"]
        })
    
    # Include thresholds for reference
    thresholds = {
        "semantic_similarity": {"green": 0.75, "yellow": 0.50},
        "entropy_change": {"green": 0.2, "yellow": 0.5},
        "logical_consistency": {"green": 0.70, "yellow": 0.50},
        "token_overlap": {"green": 0.30, "yellow": 0.15}
    }
    
    spec = {
        "steps": spec_steps,
        "thresholds": thresholds
    }
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    full_path = output_path / filename
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    return str(full_path)


def save_figure(fig: plt.Figure, output_dir: str = "figures", filename: str = "hallucination_guard.png") -> str:
    """
    Save the figure as PNG.
    
    Returns the full output path.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    full_path = output_path / filename
    fig.savefig(str(full_path), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    
    return str(full_path)


def main():
    """Main execution."""
    if not LIBS_AVAILABLE:
        print("❌ Error: Required libraries not installed")
        print("   Install with: pip install matplotlib seaborn numpy")
        return
    
    print("🚨 Generating hallucination guard visualization...")
    
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
    
    # Check if guards computed
    if not visual_data["metadata"].get("guards_computed", False):
        print("⚠️  Warning: Guard metrics not computed yet")
        print("   Run compute_hallucination_guards.py first")
        return
    
    # Create plot
    print(f"   Plotting guard metrics for {len(steps)} steps...")
    fig = create_guard_plot(visual_data)
    
    # Save
    output_path = save_figure(fig)
    print(f"✅ Hallucination guard plot saved to: {output_path}")
    
    # Write sidecar spec
    spec_path = write_sidecar_spec(visual_data)
    print(f"   Sidecar spec: {spec_path}")
    
    # Alert summary
    red_count = sum(1 for s in steps if s["guard_state"]["status"] == "red")
    yellow_count = sum(1 for s in steps if s["guard_state"]["status"] == "yellow")
    
    print(f"\n🚨 Alert summary:")
    print(f"   🔴 Red alerts (hallucinations): {red_count}")
    print(f"   🟡 Yellow warnings: {yellow_count}")
    
    if red_count > 0:
        print(f"\n⚠️  WARNING: {red_count} step(s) flagged as potential hallucinations!")


if __name__ == "__main__":
    main()

