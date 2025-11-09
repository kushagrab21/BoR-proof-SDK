#!/usr/bin/env python3
"""
Generate hash flow visualization.

Creates a PNG showing cryptographic chain propagation across reasoning steps.
"""

from __future__ import annotations  # Enable deferred annotation evaluation

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False


def load_data(filepath: str = "visual_data.json") -> Dict[str, Any]:
    """Load visual_data.json."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_hash_flow_graph(visual_data: Dict[str, Any]) -> nx.DiGraph:
    """
    Create a NetworkX directed graph of hash propagation.
    
    Returns a DiGraph with nodes as hashes and edges as parent→child links.
    """
    G = nx.DiGraph()
    
    steps = visual_data.get("steps", [])
    master_certs = visual_data.get("master_certificates", [])
    
    # Track which hashes are in master certificates
    master_hashes = {cert["aggregated_hash"] for cert in master_certs}
    
    for step in steps:
        chain_hash = step["chain_hash"]
        parent_hash = step["parent_hash"]
        step_num = step["step_number"]
        
        # Add node for chain_hash
        G.add_node(
            chain_hash,
            step=step_num,
            type="step",
            is_master=chain_hash in master_hashes
        )
        
        # Add edge from parent if exists
        if parent_hash:
            if not G.has_node(parent_hash):
                G.add_node(parent_hash, type="step", is_master=False)
            G.add_edge(parent_hash, chain_hash)
    
    return G


def visualize_hash_flow(G: nx.DiGraph, visual_data: Dict[str, Any]) -> plt.Figure:
    """
    Create matplotlib visualization of hash flow graph with modern styling.
    
    Returns a matplotlib Figure object.
    """
    # Modern dark theme
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(18, 14), dpi=300, facecolor='#0A0A0A')
    ax.set_facecolor('#0D1117')
    
    # Better layout algorithm
    try:
        pos = nx.spring_layout(G, k=2.5, iterations=100, seed=42)
    except:
        pos = nx.shell_layout(G)
    
    # Enhanced node styling with gradients and glow
    node_colors = []
    node_sizes = []
    edge_colors = []
    for node in G.nodes():
        node_data = G.nodes[node]
        if node_data.get("is_master", False):
            node_colors.append("#FFD700")  # Gold for master certs
            node_sizes.append(3000)
        else:
            node_colors.append("#58A6FF")  # Bright blue for steps
            node_sizes.append(1800)
    
    # Draw nodes with glow effect (multiple layers)
    for alpha, size_mult in [(0.1, 1.5), (0.3, 1.2), (1.0, 1.0)]:
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=[s * size_mult for s in node_sizes],
            alpha=alpha,
            node_shape='H',  # Hexagonal nodes
            ax=ax,
            edgecolors='#FFFFFF' if alpha == 1.0 else 'none',
            linewidths=2 if alpha == 1.0 else 0
        )
    
    # Draw edges with gradient effect
    nx.draw_networkx_edges(
        G, pos,
        edge_color='#58A6FF',
        width=3,
        arrows=True,
        arrowsize=25,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        alpha=0.7,
        ax=ax
    )
    
    # Enhanced labels with better visibility
    labels = {}
    for node in G.nodes():
        node_data = G.nodes[node]
        step = node_data.get("step", "?")
        hash_prefix = node[:8]
        is_master = node_data.get("is_master", False)
        icon = "🏆" if is_master else "🔐"
        labels[node] = f"{icon} S{step}\n{hash_prefix}"
    
    nx.draw_networkx_labels(
        G, pos, labels,
        font_size=9,
        font_weight="bold",
        font_color='#0D1117',
        ax=ax
    )
    
    # Modern title with emoji
    ax.text(
        0.5, 0.98,
        "🔗 BoR Cryptographic Hash Flow — Tamper-Evident Chain Propagation",
        transform=ax.transAxes,
        fontsize=18,
        fontweight='bold',
        color='#C9D1D9',
        ha='center',
        va='top'
    )
    
    # Enhanced legend with modern styling
    legend_elements = [
        mpatches.Patch(facecolor='#58A6FF', edgecolor='white', linewidth=2,
                      label='Step Certificate (SHA-256)'),
        mpatches.Patch(facecolor='#FFD700', edgecolor='white', linewidth=2,
                      label='Master Certificate (Aggregated)')
    ]
    legend = ax.legend(
        handles=legend_elements,
        loc='upper right',
        fontsize=11,
        frameon=True,
        fancybox=True,
        shadow=True,
        facecolor='#161B22',
        edgecolor='#30363D'
    )
    
    # Guard summary badge
    steps = visual_data.get("steps", [])
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in steps:
        status_counts[step["guard_state"]["status"]] += 1
    
    chain_status = "✅ VERIFIED" if visual_data["metadata"].get("chain_valid", False) else "⚠️ PARTIAL"
    
    # Bottom info panel
    info_text = (f"Guard Summary: 🟢 {status_counts['green']}  🟡 {status_counts['yellow']}  "
                f"🔴 {status_counts['red']}  |  Chain Integrity: {chain_status}\n"
                f"BoR-SDK • Deterministic Hash Chain • {G.number_of_nodes()} Nodes, {G.number_of_edges()} Edges")
    
    fig.text(
        0.5, 0.02,
        info_text,
        ha='center',
        fontsize=10,
        color='#8B949E',
        style='italic'
    )
    
    ax.axis('off')
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    return fig


def write_sidecar_spec(G: nx.DiGraph, visual_data: Dict[str, Any], output_dir: str = "figures", filename: str = "hash_flow.spec.json") -> str:
    """
    Write sidecar JSON specification for verification.
    
    Returns the full output path.
    """
    steps = visual_data.get("steps", [])
    master_certs = visual_data.get("master_certificates", [])
    master_hashes = {cert["aggregated_hash"] for cert in master_certs}
    
    # Separate step nodes from master/other nodes
    step_chain_hashes = {s["chain_hash"] for s in steps}
    
    nodes_from_steps = [node[:8] for node in G.nodes() if node in step_chain_hashes]
    nodes_from_masters = [h[:8] for h in master_hashes if h in G.nodes()]
    all_nodes = [node[:8] for node in G.nodes()]
    
    # Extract edges
    edges = []
    for parent, child in G.edges():
        edges.append({
            "parent": parent[:8],
            "child": child[:8]
        })
    
    spec = {
        "nodes_from_steps": nodes_from_steps,
        "nodes_from_masters": nodes_from_masters,
        "all_nodes": all_nodes,
        "edges": edges,
        "edges_filtered_by_session": True,  # Indicates session-scoped edges
        "master_nodes": nodes_from_masters  # Kept for backwards compatibility
    }
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    full_path = output_path / filename
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    return str(full_path)


def save_figure(fig: plt.Figure, output_dir: str = "figures", filename: str = "hash_flow.png") -> str:
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
        print("   Install with: pip install networkx matplotlib")
        return
    
    print("🔗 Generating hash flow visualization...")
    
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
    print(f"   Building hash chain graph with {len(steps)} steps...")
    G = create_hash_flow_graph(visual_data)
    
    print(f"   Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Visualize
    print("   Rendering visualization...")
    fig = visualize_hash_flow(G, visual_data)
    
    # Save
    output_path = save_figure(fig)
    print(f"✅ Hash flow saved to: {output_path}")
    
    # Write sidecar spec
    spec_path = write_sidecar_spec(G, visual_data)
    print(f"   Sidecar spec: {spec_path}")
    
    # Chain integrity summary
    chain_valid = visual_data["metadata"].get("chain_valid", False)
    print(f"\n🔐 Chain integrity: {'✅ VALID' if chain_valid else '❌ INVALID'}")


if __name__ == "__main__":
    main()

