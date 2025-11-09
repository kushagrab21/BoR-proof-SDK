#!/usr/bin/env python3
"""
BoR-SDK Interactive Visual Dashboard

A modern, explorable web interface for reasoning trace verification,
hallucination detection, and cryptographic proof inspection.

Usage:
    streamlit run interactive_visual_dashboard.py
    python interactive_visual_dashboard.py --export  # Export to HTML
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
import time
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set directly

# Import trace collector
try:
    from trace_collector import collect_trace, list_traces, load_trace, generate_mock_trace
    TRACE_COLLECTOR_AVAILABLE = True
except ImportError:
    TRACE_COLLECTOR_AVAILABLE = False
    print("⚠️ Warning: trace_collector not available")

# Import trace streamer
try:
    from trace_streamer import stream_trace_with_diagnostics, stream_mock_trace
    TRACE_STREAMER_AVAILABLE = True
except ImportError:
    TRACE_STREAMER_AVAILABLE = False
    print("⚠️ Warning: trace_streamer not available")

# Streamlit and plotting
try:
    import streamlit as st
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    import networkx as nx
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("❌ Error: Required packages not installed")
    print("   Install with: pip install streamlit plotly pandas networkx")


# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_visual_data(filepath: str = "visual_data.json") -> Dict[str, Any]:
    """Load visual_data.json with caching."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"❌ Error: {filepath} not found. Run extraction first.")
        return {"steps": [], "master_certificates": [], "session_info": {}, "metadata": {}}


@st.cache_data
def load_verification_report(filepath: str = "visual_verification_report.json") -> Dict[str, Any]:
    """Load verification report with caching."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"checks_passed": 0, "checks_failed": 0, "overall_status": "UNKNOWN", "details": []}


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def build_reasoning_graph(steps: List[Dict[str, Any]]) -> Tuple[nx.DiGraph, Dict]:
    """
    Build NetworkX graph from reasoning steps.
    
    Returns:
        (graph, pos) - NetworkX DiGraph and node positions
    """
    G = nx.DiGraph()
    
    for step in steps:
        step_num = step["step_number"]
        prompt = step["prompt"]
        response = step["response"]
        chain_hash = step["chain_hash"][:8]
        guard_status = step["guard_state"]["status"]
        
        # Add nodes for prompt and response
        prompt_id = f"P{step_num}"
        response_id = f"R{step_num}"
        
        G.add_node(prompt_id, 
                  type="prompt",
                  step=step_num,
                  text=prompt[:100],
                  full_text=prompt,
                  hash=chain_hash,
                  status=guard_status)
        
        G.add_node(response_id,
                  type="response",
                  step=step_num,
                  text=response[:100],
                  full_text=response,
                  hash=chain_hash,
                  status=guard_status)
        
        # Connect prompt to response
        G.add_edge(prompt_id, response_id, label=chain_hash)
        
        # Connect to next prompt
        if step_num < len(steps):
            next_step = next((s for s in steps if s["step_number"] == step_num + 1), None)
            if next_step and next_step.get("session_id") == step.get("session_id"):
                G.add_edge(response_id, f"P{step_num + 1}", label="→", style="dashed")
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    return G, pos


def create_interactive_reasoning_graph(steps: List[Dict[str, Any]]) -> go.Figure:
    """Create Plotly interactive reasoning graph."""
    G, pos = build_reasoning_graph(steps)
    
    # Edge traces
    edge_trace = go.Scatter(
        x=[], y=[],
        line=dict(width=2, color='#58A6FF'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    )
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    # Node traces (separate by type and status)
    node_traces = []
    
    for node in G.nodes():
        node_data = G.nodes[node]
        x, y = pos[node]
        
        # Color based on status
        status_colors = {
            "green": "#2ECC71",
            "yellow": "#F39C12",
            "red": "#E74C3C"
        }
        color = status_colors.get(node_data.get("status", "green"), "#4A90E2")
        
        # Different marker for prompt vs response
        symbol = "square" if node_data["type"] == "prompt" else "circle"
        
        hover_text = (f"<b>Step {node_data['step']}</b><br>"
                     f"Type: {node_data['type'].title()}<br>"
                     f"Hash: {node_data['hash']}<br>"
                     f"Status: {node_data['status'].upper()}<br>"
                     f"Text: {node_data['text']}...")
        
        node_trace = go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=20 if node_data["type"] == "response" else 15,
                color=color,
                line=dict(width=2, color='white')
            ),
            text=node,
            textposition="top center",
            hovertext=hover_text,
            hoverinfo='text',
            name=f"{node_data['type'].title()} - {node_data['status']}",
            showlegend=False
        )
        node_traces.append(node_trace)
    
    # Create figure
    fig = go.Figure(data=[edge_trace] + node_traces)
    
    fig.update_layout(
        title="🧠 Interactive Reasoning Chain",
        titlefont_size=20,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#0D1117',
        paper_bgcolor='#0D1117',
        font=dict(color='#C9D1D9')
    )
    
    return fig


# ============================================================================
# HALLUCINATION METRICS
# ============================================================================

def create_hallucination_dashboard(steps: List[Dict[str, Any]]) -> go.Figure:
    """Create interactive hallucination metrics dashboard."""
    step_numbers = [s["step_number"] for s in steps]
    
    # Extract metrics
    semantic_sim = [s["guard_state"]["semantic_similarity"] or 0 for s in steps]
    entropy = [s["guard_state"]["entropy_change"] or 0 for s in steps]
    logic = [s["guard_state"]["logical_consistency"] or 0 for s in steps]
    token_overlap = [s["guard_state"]["token_overlap"] or 0 for s in steps]
    
    fig = go.Figure()
    
    # Add threshold zones
    fig.add_hrect(y0=0.75, y1=1.0, fillcolor="#2ECC71", opacity=0.1, 
                  annotation_text="🟢 Safe Zone", annotation_position="top left")
    fig.add_hrect(y0=0.50, y1=0.75, fillcolor="#F39C12", opacity=0.1,
                  annotation_text="🟡 Caution Zone", annotation_position="top left")
    fig.add_hrect(y0=0.0, y1=0.50, fillcolor="#E74C3C", opacity=0.1,
                  annotation_text="🔴 Alert Zone", annotation_position="top left")
    
    # Add metric traces
    fig.add_trace(go.Scatter(
        x=step_numbers, y=semantic_sim,
        mode='lines+markers',
        name='💎 Semantic Similarity',
        line=dict(color='#00D9FF', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=step_numbers, y=entropy,
        mode='lines+markers',
        name='🌊 Entropy Change',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=step_numbers, y=logic,
        mode='lines+markers',
        name='🧠 Logical Consistency',
        line=dict(color='#7FFF00', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=step_numbers, y=token_overlap,
        mode='lines+markers',
        name='🔗 Token Overlap',
        line=dict(color='#FF1493', width=3),
        marker=dict(size=10)
    ))
    
    # Highlight red steps
    red_steps = [i for i, s in enumerate(steps) if s["guard_state"]["status"] == "red"]
    if red_steps:
        fig.add_trace(go.Scatter(
            x=[step_numbers[i] for i in red_steps],
            y=[semantic_sim[i] for i in red_steps],
            mode='markers',
            name='🚨 Hallucination Alert',
            marker=dict(size=20, color='#FF0000', symbol='x', line=dict(width=2, color='white'))
        ))
    
    fig.update_layout(
        title="🚨 Real-Time Hallucination Monitor",
        xaxis_title="Reasoning Step",
        yaxis_title="Metric Value (0 = worst, 1 = best)",
        hovermode='x unified',
        plot_bgcolor='#121212',
        paper_bgcolor='#0E1117',
        font=dict(color='#C9D1D9', size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


# ============================================================================
# VERIFICATION PANEL
# ============================================================================

def create_verification_panel(report: Dict[str, Any]) -> None:
    """Create verification summary panel."""
    status = report.get("overall_status", "UNKNOWN")
    passed = report.get("checks_passed", 0)
    failed = report.get("checks_failed", 0)
    
    # Status badge
    if status == "VERIFIED":
        st.success(f"✅ **VERIFIED** — All {passed} integrity checks passed")
    elif status == "PARTIAL":
        st.warning(f"⚠️ **PARTIAL** — {passed} passed, {failed} failed")
    else:
        st.error(f"❌ **FAILED** — {failed} checks failed")
    
    # Detailed checks
    with st.expander("🔍 Detailed Verification Checks"):
        for detail in report.get("details", []):
            check_status = detail.get("status", "unknown")
            check_name = detail.get("check_name", "Unknown")
            message = detail.get("message", "No details")
            
            if check_status == "pass":
                st.markdown(f"✅ **{check_name}**: {message}")
            elif check_status == "warn":
                st.markdown(f"⚠️ **{check_name}**: {message}")
            else:
                st.markdown(f"❌ **{check_name}**: {message}")


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    """Main Streamlit dashboard."""
    if not STREAMLIT_AVAILABLE:
        print("❌ Streamlit not available. Install with: pip install streamlit plotly pandas")
        return
    
    # pandas is imported at module level
    
    # Page config
    st.set_page_config(
        page_title="BoR-SDK Interactive Proof Explorer",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state for cross-tab synchronization
    if "latest_trace_session" not in st.session_state:
        st.session_state["latest_trace_session"] = None
    if "latest_verification_time" not in st.session_state:
        st.session_state["latest_verification_time"] = None
    if "data_source" not in st.session_state:
        st.session_state["data_source"] = "visual_data.json"
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        background-color: #0D1117;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #161B22;
        border-radius: 8px;
        padding: 0 24px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #238636;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <h1 style='text-align: center; color: #58A6FF; font-size: 48px;'>
        🔐 BoR-SDK Interactive Proof Explorer
    </h1>
    <p style='text-align: center; color: #8B949E; font-size: 16px;'>
        Deterministic AI • Hallucination-Proof Reasoning • Cryptographic Verification
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check for data source updates from session state
    data_file = st.session_state.get("data_source", "visual_data.json")
    
    # Show notification if new data was just captured
    if st.session_state.get("latest_trace_session"):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info(f"📊 **New data captured!** Session: `{st.session_state['latest_trace_session']}` — "
                    f"Switch to 'Latest Trace' in sidebar to view verified data across all tabs.")
        with col2:
            if st.button("✕ Dismiss", key="dismiss_notification"):
                st.session_state["latest_trace_session"] = None
                st.rerun()
    
    # Load data
    try:
        visual_data = load_visual_data(data_file)
        if data_file != "visual_data.json":
            st.sidebar.success(f"📊 Viewing: Latest Trace")
    except FileNotFoundError:
        # Fallback to default
        st.warning(f"⚠️ Could not load {data_file}, using default data")
        visual_data = load_visual_data("visual_data.json")
    
    verification_report = load_verification_report()
    
    steps = visual_data.get("steps", [])
    masters = visual_data.get("master_certificates", [])
    session_info = visual_data.get("session_info", {})
    
    # Data source indicator
    data_source = visual_data.get("metadata", {}).get("source_trace", None)
    if data_source:
        st.info(f"📊 **Viewing Data From**: `{data_source}`\n\n"
                f"This is a converted LLM trace. To view multi-step reasoning chains, capture longer conversations in the **🤖 LLM Sandbox** tab.")
    elif visual_data.get("metadata", {}).get("source_directory") == "proofs":
        st.info("📊 **Viewing Data From**: Existing BoR proof files (`proofs/` directory)")
    
    if not steps:
        st.error("❌ No reasoning steps found. Please run extraction first: `make extract`")
        return
    
    # Sidebar - Summary Stats
    with st.sidebar:
        st.markdown("## 📊 Summary Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Steps", len(steps))
            st.metric("Sessions", len(set(s.get("session_id", "unknown") for s in steps)))
        with col2:
            st.metric("Masters", len(masters))
            st.metric("Verified", len([m for m in masters if m.get("verification_status") == "verified"]))
        
        # Guard status breakdown
        status_counts = {"green": 0, "yellow": 0, "red": 0}
        for step in steps:
            status_counts[step["guard_state"]["status"]] += 1
        
        st.markdown("### 🛡️ Guard Status")
        st.markdown(f"🟢 **Green**: {status_counts['green']} steps")
        st.markdown(f"🟡 **Yellow**: {status_counts['yellow']} steps")
        st.markdown(f"🔴 **Red**: {status_counts['red']} steps")
        
        if status_counts['red'] > 0:
            alert_rate = (status_counts['red'] / len(steps)) * 100
            st.error(f"🚨 Alert Rate: {alert_rate:.1f}%")
        
        st.markdown("---")
        
        # Root-Cause Distribution
        st.markdown("### 🧩 Root-Cause Distribution")
        
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
            fig_causes = go.Figure(data=[
                go.Bar(x=causes, y=counts, marker_color=colors, text=counts, textposition='auto')
            ])
            
            fig_causes.update_layout(
                title="Frequency",
                height=250,
                margin=dict(l=0, r=0, t=30, b=0),
                plot_bgcolor='#0D1117',
                paper_bgcolor='#0D1117',
                font=dict(color='#C9D1D9', size=10),
                showlegend=False,
                xaxis=dict(tickangle=-45)
            )
            
            st.plotly_chart(fig_causes, use_container_width=True)
        else:
            st.success("✅ No root causes detected")
        
        st.markdown("---")
        
        # Theme toggle (placeholder for now)
        theme = st.selectbox("🎨 Theme", ["Dark (Default)", "Light"], index=0)
        
        st.markdown("---")
        st.markdown("### 🔄 Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("♻️ Reload Data", use_container_width=True):
                st.cache_data.clear()
                st.session_state["latest_trace_session"] = None
                st.rerun()
        with col2:
            if st.button("🔄 Sync Tabs", use_container_width=True, help="Synchronize all tabs with latest data"):
                st.cache_data.clear()
                st.rerun()
        
        # Data source selector
        st.markdown("### 📂 Data Source")
        current_source = st.session_state.get("data_source", "visual_data.json")
        data_source_option = st.radio(
            "Select data source:",
            ["Main Proofs", "Latest Trace"],
            index=0 if current_source == "visual_data.json" else 1,
            label_visibility="collapsed"
        )
        
        # Update and trigger rerun if changed
        new_source = "bor_inputs/visual_data_trace.json" if data_source_option == "Latest Trace" else "visual_data.json"
        if new_source != current_source:
            st.session_state["data_source"] = new_source
            st.cache_data.clear()
            st.rerun()
    
    # Main content - Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧠 Reasoning Flow",
        "🚨 Hallucination Monitor",
        "🔐 Cryptographic Chain",
        "✅ Verification",
        "🤖 LLM Sandbox"
    ])
    
    # Tab 1: Reasoning Flow
    with tab1:
        st.markdown("### Interactive Reasoning Chain Explorer")
        
        if len(steps) == 0:
            st.warning("📭 No reasoning steps found. Please run extraction first: `make extract`")
        elif len(steps) == 1:
            st.info("💡 **Single Step Detected**: Graph visualization works best with multiple steps. The current data shows 1 reasoning step.\n\n"
                   "To see a connected reasoning chain:\n"
                   "- Use the **🤖 LLM Sandbox** tab to capture multi-step traces\n"
                   "- Or run verification on existing multi-step proofs")
        else:
            st.markdown("**Hover** over nodes to see prompts/responses. **Click** to select.")
        
        try:
            fig = create_interactive_reasoning_graph(steps)
            st.plotly_chart(fig, use_container_width=True, key="reasoning_flow_graph")
        except Exception as e:
            st.error(f"❌ Error creating graph: {e}")
            with st.expander("Show error details"):
                import traceback
                st.code(traceback.format_exc())
        
        # Step details
        st.markdown("---")
        st.markdown("### 📝 Step Details")
        
        selected_step = st.selectbox(
            "Select a step to inspect:",
            options=range(1, len(steps) + 1),
            format_func=lambda x: f"Step {x} — {steps[x-1]['guard_state']['status'].upper()}"
        )
        
        if selected_step:
            step_data = steps[selected_step - 1]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📥 Prompt:**")
                st.text_area("Prompt", step_data["prompt"], height=150, key=f"prompt_{selected_step}", label_visibility="collapsed")
            with col2:
                st.markdown("**📤 Response:**")
                st.text_area("Response", step_data["response"], height=150, key=f"response_{selected_step}", label_visibility="collapsed")
            
            # Trust Diagnostics Panel
            st.markdown("**🧩 Trust Diagnostics:**")
            trust_diag = step_data.get("trust_diagnostics", {})
            trust_score = trust_diag.get("trust_score", 0)
            trust_label = trust_diag.get("trust_label", "Unknown")
            root_causes = trust_diag.get("root_causes", [])
            
            # Trust gauge
            gauge_color = "#16A34A" if trust_label == "Trusted" else "#FACC15" if trust_label == "Review" else "#DC2626"
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Trust Score", f"{trust_score:.0%}")
                st.markdown(f"**Label:** {trust_label}")
            with col2:
                if root_causes:
                    cause_emojis = {"Semantic Drift": "🧩", "Entropy Spike": "⚡", 
                                  "Logical Contradiction": "❌", "Low Token Overlap": "🪶"}
                    causes_with_emoji = [f"{cause_emojis.get(c, '•')} {c}" for c in root_causes]
                    st.error(f"**Root Causes:**\n" + "\n".join([f"- {c}" for c in causes_with_emoji]))
                else:
                    st.success("✅ No issues detected")
            
            # Metadata
            st.markdown("**🔐 Cryptographic Metadata:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.code(f"Hash: {step_data['chain_hash'][:16]}...")
            with col2:
                st.code(f"Status: {step_data['guard_state']['status'].upper()}")
            with col3:
                st.code(f"Session: {step_data.get('session_id', 'N/A')[:8]}...")
    
    # Tab 2: Hallucination Monitor
    with tab2:
        st.markdown("### Real-Time Hallucination Detection Dashboard")
        st.markdown("📊 **Purpose**: Track hallucination detection metrics across reasoning steps")
        st.markdown("Live metrics tracking semantic drift, entropy spikes, and logical consistency.")
        
        if len(steps) == 1:
            st.info("💡 **Single Step**: Hallucination detection works best with multiple steps to compare. Metrics are computed relative to context.")
        
        # Root-Cause Filter UI
        st.markdown("#### 🔍 Filter by Root Cause")
        cause_emojis = {
            "Semantic Drift": "🧩",
            "Entropy Spike": "⚡",
            "Logical Contradiction": "❌",
            "Low Token Overlap": "🪶"
        }
        
        available_causes = ["Semantic Drift", "Entropy Spike", "Logical Contradiction", "Low Token Overlap"]
        cause_options = [f"{cause_emojis[c]} {c}" for c in available_causes]
        
        selected_cause_labels = st.multiselect(
            "Select causes to filter (empty = show all)",
            cause_options,
            default=[]
        )
        
        # Map back to cause names
        selected_causes = [c.split(" ", 1)[1] for c in selected_cause_labels]
        
        # Filter steps if causes selected
        filtered_steps = steps
        if selected_causes:
            filtered_steps = [
                s for s in steps 
                if any(c in s.get("trust_diagnostics", {}).get("root_causes", []) for c in selected_causes)
            ]
            st.info(f"Showing {len(filtered_steps)} of {len(steps)} steps matching selected causes")
        
        try:
            fig = create_hallucination_dashboard(filtered_steps if filtered_steps else steps)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating dashboard: {e}")
        
        # Alert feed
        st.markdown("---")
        st.markdown("### 🚨 Alert Feed")
        
        red_steps = [s for s in steps if s["guard_state"]["status"] == "red"]
        if red_steps:
            st.error(f"⚠️ **{len(red_steps)} hallucination alerts detected**")
            
            for step in red_steps:
                trust_diag = step.get("trust_diagnostics", {})
                root_causes = trust_diag.get("root_causes", [])
                trust_score = trust_diag.get("trust_score", 0)
                trust_label = trust_diag.get("trust_label", "Unknown")
                
                with st.expander(f"🔴 Step {step['step_number']} — {step['prompt'][:50]}..."):
                    # Trust Diagnostics
                    st.markdown(f"**Trust Score:** {trust_score:.0%} ({trust_label})")
                    
                    # Root Causes with emojis
                    if root_causes:
                        causes_with_emoji = [f"{cause_emojis.get(c, '•')} {c}" for c in root_causes]
                        st.error(f"**Root Causes:** {', '.join(causes_with_emoji)}")
                    
                    st.markdown(f"**Triggered Guards:** {', '.join(step['guard_state']['triggered_guards'])}")
                    
                    # Metrics
                    metrics = step['guard_state']
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Semantic", f"{metrics['semantic_similarity']:.2f}" if metrics['semantic_similarity'] else "N/A")
                    with col2:
                        st.metric("Entropy", f"{metrics['entropy_change']:.2f}" if metrics['entropy_change'] else "N/A")
                    with col3:
                        st.metric("Logic", f"{metrics['logical_consistency']:.2f}" if metrics['logical_consistency'] else "N/A")
                    with col4:
                        st.metric("Overlap", f"{metrics['token_overlap']:.2f}" if metrics['token_overlap'] else "N/A")
                    
                    st.markdown(f"**Prompt:** {step['prompt']}")
                    st.markdown(f"**Response:** {step['response']}")
        else:
            st.success("✅ No hallucination alerts. All steps passed guard checks.")
    
    # Tab 3: Cryptographic Chain
    with tab3:
        st.markdown("### Cryptographic Hash Chain Visualization")
        st.markdown("🔐 **Purpose**: Verify cryptographic integrity and hash chain linkage")
        st.markdown("Tamper-evident proof-of-cognition chain with parent→child linkage.")
        
        # Create hash chain dataframe
        chain_data = []
        for step in steps:
            chain_data.append({
                "Step": step["step_number"],
                "Chain Hash": step["chain_hash"][:16] + "...",
                "Parent Hash": step["parent_hash"][:16] + "..." if step["parent_hash"] else "null",
                "Status": step["guard_state"]["status"].upper(),
                "Timestamp": datetime.fromtimestamp(step["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        df = pd.DataFrame(chain_data)
        
        # Color-code by status
        def highlight_status(row):
            colors = {
                "GREEN": "background-color: #2ECC71; color: white",
                "YELLOW": "background-color: #F39C12; color: white",
                "RED": "background-color: #E74C3C; color: white"
            }
            return [colors.get(row["Status"], "")] * len(row)
        
        st.dataframe(
            df.style.apply(highlight_status, axis=1),
            use_container_width=True,
            height=400
        )
        
        # Master certificates
        st.markdown("---")
        st.markdown("### 🏆 Master Certificates")
        
        if masters:
            for master in masters:
                status = master.get("verification_status", "unknown")
                icon = "✅" if status == "verified" else "⚠️"
                
                with st.expander(f"{icon} {master['cert_id']} — {master['step_count']} steps"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.code(f"Aggregated Hash:\n{master['aggregated_hash']}")
                    with col2:
                        st.metric("Verification", status.upper())
                        st.metric("Steps Aggregated", master['step_count'])
        else:
            st.info("No master certificates found.")
    
    # Tab 4: Verification
    with tab4:
        st.markdown("### Verification & Integrity Report")
        st.markdown("✅ **Purpose**: View verification results and trust diagnostics summary")
        st.markdown("Automated cross-checks between visual artifacts and cryptographic proofs.")
        
        create_verification_panel(verification_report)
        
        # Session info
        st.markdown("---")
        st.markdown("### 📋 Session Information")
        
        if session_info:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Session ID", session_info.get("session_id", "N/A")[:16] + "...")
            with col2:
                st.metric("Total Steps", session_info.get("total_steps", 0))
            with col3:
                st.metric("Duration", f"{session_info.get('end_time', 0) - session_info.get('start_time', 0):.2f}s")
        
        # Root-Cause Summary
        st.markdown("---")
        st.markdown("### 🧩 Root-Cause Analysis")
        
        # Collect all root causes with their steps
        from collections import defaultdict
        cause_steps = defaultdict(list)
        for step in steps:
            for cause in step.get("trust_diagnostics", {}).get("root_causes", []):
                cause_steps[cause].append(step["step_number"])
        
        if cause_steps:
            # Create summary table
            cause_emojis = {"Semantic Drift": "🧩", "Entropy Spike": "⚡", 
                          "Logical Contradiction": "❌", "Low Token Overlap": "🪶"}
            
            summary_data = []
            for cause, step_nums in cause_steps.items():
                emoji = cause_emojis.get(cause, "•")
                example_steps = ", ".join(map(str, sorted(step_nums)[:5]))
                if len(step_nums) > 5:
                    example_steps += f" (+{len(step_nums) - 5} more)"
                
                summary_data.append({
                    "Cause": f"{emoji} {cause}",
                    "Count": len(step_nums),
                    "Affected Steps": example_steps
                })
            
            df_causes = pd.DataFrame(summary_data).sort_values("Count", ascending=False)
            st.dataframe(df_causes, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No root causes detected across all steps")
        
        # Metadata
        st.markdown("---")
        st.markdown("### 🔧 Extraction Metadata")
        
        metadata = visual_data.get("metadata", {})
        if metadata:
            col1, col2 = st.columns(2)
            with col1:
                st.code(f"Extraction Time: {metadata.get('extraction_timestamp', 'N/A')}")
                st.code(f"Chain Valid: {metadata.get('chain_valid', False)}")
            with col2:
                st.code(f"Total Sessions: {metadata.get('total_sessions', 0)}")
                st.code(f"Generation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Tab 5: LLM Sandbox
    with tab5:
        st.markdown("### 🤖 LLM Sandbox — Prompt → Trace Capture")
        st.markdown("🎯 **Purpose**: Capture new LLM traces with optional live trust diagnostics")
        st.markdown("Enter any prompt, run an LLM, and capture detailed reasoning traces for BoR verification.")
        
        # Check model compatibility
        env_model = os.getenv("OPENAI_MODEL", "")
        if "gpt-5" in env_model.lower() or "o1" in env_model.lower():
            st.warning(f"⚠️ **Model Compatibility Issue**: Your configured model `{env_model}` uses hidden reasoning tokens "
                      "and is not compatible with BoR trace verification.\n\n"
                      "**Recommendation**: Use **Mock Traces** instead (click '🎭 Stream Mock' or '🎭 Generate Mock Trace' buttons). "
                      "These provide full functionality without requiring API access.\n\n"
                      "For real API traces, you'll need access to `gpt-4-turbo`, `gpt-3.5-turbo`, or `gpt-4o`. "
                      "See `MODEL_COMPATIBILITY.txt` for details.")
        
        if not TRACE_COLLECTOR_AVAILABLE:
            st.error("❌ Trace collector not available. Make sure `trace_collector.py` is in the same directory.")
        else:
            # Mode Selection
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                live_mode = st.checkbox(
                    "🔴 Live Trust Diagnostics",
                    value=False,
                    help="Stream output with real-time hallucination detection",
                    key="live_mode_toggle"
                )
            with col2:
                if live_mode:
                    chunk_size_live = st.slider(
                        "🔄 Chunk Size",
                        min_value=5,
                        max_value=50,
                        value=10,
                        step=5,
                        key="chunk_size_live"
                    )
            with col3:
                auto_verify = st.checkbox(
                    "⚙️ Auto-Verify after Capture",
                    value=False,
                    help="Automatically run BoR verification when streaming completes",
                    key="auto_verify_toggle"
                )
            
            st.markdown("---")
            
            # Live Streaming Section
            if live_mode and TRACE_STREAMER_AVAILABLE:
                st.markdown("### 🔴 Live Monitoring")
                st.info("💡 Enter a prompt below and click 'Stream with Live Diagnostics' to see real-time trust metrics")
                
                # Prompt input for streaming
                stream_prompt = st.text_area(
                    "Enter your prompt",
                    height=100,
                    placeholder="Type any prompt... (e.g., 'Explain the theory of relativity')",
                    key="stream_prompt_input"
                )
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    stream_btn = st.button("🔴 Stream with Live Diagnostics", type="primary", use_container_width=True)
                with col2:
                    stream_mock_btn = st.button("🎭 Stream Mock", use_container_width=True)
                with col3:
                    # Get default model from environment
                    default_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
                    available_models = ["gpt-4-turbo", "gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-5-nano-2025-08-07"]
                    
                    # Add environment model if not in list
                    if default_model not in available_models:
                        available_models.insert(0, default_model)
                    
                    # Set default index
                    try:
                        default_idx = available_models.index(default_model)
                    except ValueError:
                        default_idx = 0
                    
                    stream_model = st.selectbox(
                        "Model",
                        available_models,
                        index=default_idx,
                        key="stream_model_select",
                        help=f"Environment default: {default_model}"
                    )
                
                # Run streaming
                if (stream_btn or stream_mock_btn) and stream_prompt.strip():
                    api_key_set = os.getenv("OPENAI_API_KEY") is not None
                    
                    if stream_btn and not api_key_set:
                        st.error("❌ OPENAI_API_KEY not set. Use Mock Stream instead.")
                    else:
                        # Create placeholders for live updates
                        st.markdown("---")
                        st.markdown("#### 📊 Live Trust Timeline")
                        
                        trust_chart_placeholder = st.empty()
                        status_placeholder = st.empty()
                        
                        st.markdown("#### 🚨 Real-Time Alerts")
                        alerts_placeholder = st.empty()
                        
                        st.markdown("#### 🔄 Stream Console")
                        console_placeholder = st.empty()
                        
                        # Data collectors
                        trust_scores = []
                        token_indices = []
                        status_counts = {"green": 0, "yellow": 0, "red": 0}
                        recent_tokens = []
                        alerts = []
                        
                        # Stream
                        try:
                            if stream_mock_btn:
                                stream_fn = stream_mock_trace
                                stream_kwargs = {"prompt": stream_prompt, "delay": 0.05}
                            else:
                                stream_fn = stream_trace_with_diagnostics
                                stream_kwargs = {"prompt": stream_prompt, "model": stream_model}
                            
                            final_result = None
                            
                            for chunk in stream_fn(**stream_kwargs, chunk_size=chunk_size_live):
                                if chunk.get("complete"):
                                    final_result = chunk
                                    break
                                
                                if chunk.get("error"):
                                    st.error(f"❌ Error: {chunk['error']}")
                                    break
                                
                                # Update data
                                trust_scores.append(chunk["trust_score"])
                                token_indices.append(chunk["index"])
                                status_counts[chunk["status"]] += 1
                                recent_tokens.append({
                                    "token": chunk["token"],
                                    "status": chunk["status"],
                                    "trust": chunk["trust_score"]
                                })
                                
                                # Track alerts
                                if chunk["status"] == "red":
                                    alerts.append({
                                        "index": chunk["index"],
                                        "token": chunk["token"],
                                        "trust_score": chunk["trust_score"],
                                        "label": chunk["trust_label"]
                                    })
                                
                                # Update trust timeline
                                if len(trust_scores) > 1:
                                    fig_trust = go.Figure()
                                    fig_trust.add_trace(go.Scatter(
                                        x=token_indices,
                                        y=trust_scores,
                                        mode='lines+markers',
                                        name='Trust Score',
                                        line=dict(color='#00D9FF', width=3),
                                        marker=dict(size=6)
                                    ))
                                    
                                    # Add threshold lines
                                    fig_trust.add_hline(y=0.85, line_dash="dash", line_color="green", annotation_text="Trusted")
                                    fig_trust.add_hline(y=0.65, line_dash="dash", line_color="yellow", annotation_text="Review")
                                    
                                    fig_trust.update_layout(
                                        height=300,
                                        xaxis_title="Token Index",
                                        yaxis_title="Trust Score",
                                        yaxis_range=[0, 1.1],
                                        plot_bgcolor='#0D1117',
                                        paper_bgcolor='#0D1117',
                                        font=dict(color='#C9D1D9')
                                    )
                                    
                                    trust_chart_placeholder.plotly_chart(fig_trust, use_container_width=True)
                                
                                # Update status metrics
                                with status_placeholder.container():
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Tokens", chunk["token_count"])
                                    with col2:
                                        st.metric("🟢 Trusted", status_counts["green"])
                                    with col3:
                                        st.metric("🟡 Review", status_counts["yellow"])
                                    with col4:
                                        st.metric("🔴 Alerts", status_counts["red"])
                                
                                # Update alerts
                                if alerts:
                                    with alerts_placeholder.container():
                                        for alert in alerts[-5:]:  # Last 5 alerts
                                            st.error(f"🔴 Token [{alert['index']}] **{alert['token']}** — Trust: {alert['trust_score']:.2f}")
                                
                                # Update console (last 10 tokens)
                                with console_placeholder.container():
                                    console_df = pd.DataFrame([
                                        {
                                            "Status": {"green": "🟢", "yellow": "🟡", "red": "🔴"}[t["status"]],
                                            "Token": t["token"],
                                            "Trust": f"{t['trust']:.2f}"
                                        }
                                        for t in recent_tokens[-10:]
                                    ])
                                    st.dataframe(console_df, use_container_width=True, hide_index=True)
                            
                            # Completion
                            if final_result and not final_result.get("error"):
                                st.markdown("---")
                                st.success(f"✅ Streaming complete! Session: `{final_result['session_id']}`")
                                
                                # Update session state for cross-tab sync
                                st.session_state["latest_trace_session"] = final_result['session_id']
                                st.session_state["latest_verification_time"] = time.time()
                                
                                # Show full response
                                st.markdown("#### 📤 Complete Response")
                                st.markdown(f"```\n{final_result['response_text']}\n```")
                                
                                # Final metrics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Tokens", final_result['token_count'])
                                with col2:
                                    st.metric("Duration", f"{final_result['duration']:.2f}s")
                                with col3:
                                    if status_counts["red"] > 0:
                                        alert_rate = (status_counts["red"] / final_result['token_count']) * 100
                                        st.metric("Alert Rate", f"{alert_rate:.1f}%")
                                    else:
                                        st.metric("Alert Rate", "0%")
                                
                                # Files
                                st.code(f"Trace: {final_result['trace_file']}")
                                st.code(f"Manifest: {final_result['manifest_file']}")
                                
                                # Auto-verify
                                if auto_verify:
                                    st.markdown("---")
                                    st.markdown("#### 🔐 Auto-Verification")
                                    
                                    with st.spinner("Running BoR verification..."):
                                        import subprocess
                                        result = subprocess.run(
                                            ["python", "extract_trace_for_bor.py", "--session", final_result['session_id']],
                                            capture_output=True,
                                            text=True
                                        )
                                        
                                        if result.returncode == 0:
                                            st.success("✅ Verification complete!")
                                            # Update session state and trigger reload
                                            st.session_state["data_source"] = "bor_inputs/visual_data_trace.json"
                                            st.session_state["latest_verification_time"] = time.time()
                                            st.info("💡 Click '🔄 Sync Tabs' in sidebar or switch to 'Latest Trace' to view verified data")
                                            if st.button("🔄 View Verified Data Now", key="view_verified"):
                                                st.cache_data.clear()
                                                st.rerun()
                                        else:
                                            st.warning(f"⚠️ Verification had issues: {result.stderr[:100]}")
                                
                        except Exception as e:
                            st.error(f"❌ Streaming error: {e}")
                            import traceback
                            st.code(traceback.format_exc())
                
                elif stream_btn or stream_mock_btn:
                    st.warning("⚠️ Please enter a prompt before streaming")
                
                st.markdown("---")
            
            elif live_mode and not TRACE_STREAMER_AVAILABLE:
                st.error("❌ Trace streamer not available. Install required dependencies.")
            
            # Standard Capture Section
            st.markdown("### 📸 Standard Capture")
            st.markdown("#### 📝 Prompt Input")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                user_prompt = st.text_area(
                    "Enter your prompt",
                    height=150,
                    placeholder="Type any prompt here... (e.g., 'Explain quantum teleportation simply')",
                    key="llm_sandbox_prompt"
                )
            with col2:
                # Get default model from environment
                default_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
                available_models = ["gpt-4-turbo", "gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-5-nano-2025-08-07"]
                
                # Add environment model if not in list
                if default_model not in available_models:
                    available_models.insert(0, default_model)
                
                # Set default index
                try:
                    default_idx = available_models.index(default_model)
                except ValueError:
                    default_idx = 0
                
                model_choice = st.selectbox(
                    "Select Model",
                    available_models,
                    index=default_idx,
                    key="llm_sandbox_model",
                    help=f"Environment default: {default_model}"
                )
                
                max_tokens = st.slider(
                    "Max Tokens",
                    min_value=50,
                    max_value=2000,
                    value=300,
                    step=50,
                    key="llm_sandbox_max_tokens"
                )
                
                # Get default temperature from environment
                default_temp = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
                
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=default_temp,
                    step=0.1,
                    key="llm_sandbox_temperature",
                    help=f"Environment default: {default_temp}"
                )
            
            # Action Buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                run_btn = st.button("🚀 Run Trace Capture", type="primary", use_container_width=True)
            with col2:
                mock_btn = st.button("🎭 Generate Mock Trace", use_container_width=True)
            with col3:
                st.markdown("")  # Spacer
            
            # Check for API key
            api_key_set = os.getenv("OPENAI_API_KEY") is not None
            if not api_key_set and not mock_btn:
                st.warning("⚠️ OPENAI_API_KEY not found in environment. Set it to use real LLM traces, or use Mock Trace for testing.")
            
            # Run Trace Capture
            if run_btn and user_prompt.strip():
                if not api_key_set:
                    st.error("❌ Cannot run trace capture: OPENAI_API_KEY not set. Use Mock Trace instead or set your API key.")
                else:
                    with st.spinner(f"🧠 Running {model_choice} and capturing trace..."):
                        try:
                            result = collect_trace(
                                prompt=user_prompt,
                                model=model_choice,
                                max_tokens=max_tokens,
                                temperature=temperature
                            )
                            
                            st.success(f"✅ Trace captured successfully! Session ID: `{result['session_id']}`")
                            
                            # Update session state for cross-tab sync
                            st.session_state["latest_trace_session"] = result['session_id']
                            st.session_state["latest_verification_time"] = time.time()
                            
                            # Display response
                            st.markdown("#### 📤 Model Response")
                            st.markdown(f"```\n{result['response_text']}\n```")
                            
                            # Display trace summary
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Tokens Generated", result['token_count'])
                            with col2:
                                st.metric("Duration", f"{result['duration']:.2f}s")
                            with col3:
                                st.metric("Model", model_choice)
                            
                            # Display trace preview
                            st.markdown("#### 🔍 Trace Preview (First 10 Tokens)")
                            trace_preview = result['trace'][:10]
                            
                            # Create trace dataframe
                            trace_df = pd.DataFrame([
                                {
                                    "Index": t["index"],
                                    "Token": t["token"],
                                    "LogProb": f"{t['logprob']:.4f}",
                                    "Probability": f"{100 * (2 ** t['logprob']):.2f}%"
                                }
                                for t in trace_preview
                            ])
                            
                            st.dataframe(trace_df, use_container_width=True, hide_index=True)
                            
                            # Expandable full trace
                            with st.expander("📋 View Full Trace JSON"):
                                st.json(result['trace'])
                            
                            # Expandable manifest
                            with st.expander("📄 View Manifest JSON"):
                                st.json(result['manifest'])
                            
                            # File paths
                            st.markdown("#### 💾 Saved Files")
                            st.code(f"Trace: {result['trace_file']}")
                            st.code(f"Manifest: {result['manifest_file']}")
                            
                            # BoR Verification Section
                            st.markdown("---")
                            st.markdown("#### 🔐 BoR Verification")
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                verify_btn = st.button(
                                    "🔐 Verify with BoR",
                                    key=f"verify_{result['session_id']}",
                                    type="secondary",
                                    use_container_width=True
                                )
                            with col2:
                                st.info("Apply cryptographic verification and trust diagnostics to this trace")
                            
                            if verify_btn:
                                with st.spinner("🔐 Running BoR verification pipeline..."):
                                    try:
                                        import subprocess
                                        
                                        # Step 1: Extract trace to BoR format
                                        st.write("⚙️ Step 1/3: Converting trace to BoR format...")
                                        extract_result = subprocess.run(
                                            ["python", "extract_trace_for_bor.py", "--session", result['session_id']],
                                            capture_output=True,
                                            text=True
                                        )
                                        
                                        if extract_result.returncode != 0:
                                            st.error(f"❌ Extraction failed: {extract_result.stderr}")
                                        else:
                                            st.success("✅ Trace converted to BoR format")
                                            
                                            # Step 2: Compute hallucination guards
                                            st.write("⚙️ Step 2/3: Computing hallucination guards...")
                                            guards_result = subprocess.run(
                                                ["python", "compute_hallucination_guards.py", "--input", "bor_inputs/visual_data_trace.json"],
                                                capture_output=True,
                                                text=True
                                            )
                                            
                                            if guards_result.returncode != 0:
                                                st.warning(f"⚠️ Guard computation: {guards_result.stderr[:200]}")
                                            else:
                                                st.success("✅ Hallucination guards computed")
                                            
                                            # Step 3: Generate visualizations
                                            st.write("⚙️ Step 3/3: Generating proof visualizations...")
                                            viz_result = subprocess.run(
                                                ["python", "generate_all_visualizations.py", "--visual-data", "bor_inputs/visual_data_trace.json"],
                                                capture_output=True,
                                                text=True
                                            )
                                            
                                            if viz_result.returncode == 0:
                                                st.success("✅ Visualizations generated")
                                            
                                            # Display results
                                            st.markdown("---")
                                            st.markdown("#### ✅ Verification Complete")
                                            
                                            # Try to load verification results
                                            try:
                                                verified_data = load_visual_data("bor_inputs/visual_data_trace.json")
                                                
                                                # Compute summary stats
                                                verified_steps = verified_data.get("steps", [])
                                                status_counts = {"green": 0, "yellow": 0, "red": 0}
                                                for step in verified_steps:
                                                    status = step.get("guard_state", {}).get("status", "green")
                                                    status_counts[status] += 1
                                                
                                                # Display metrics
                                                col1, col2, col3, col4 = st.columns(4)
                                                with col1:
                                                    st.metric("Total Steps", len(verified_steps))
                                                with col2:
                                                    st.metric("🟢 Trusted", status_counts['green'])
                                                with col3:
                                                    st.metric("🟡 Review", status_counts['yellow'])
                                                with col4:
                                                    st.metric("🔴 Untrusted", status_counts['red'])
                                                
                                                # Display trust summary
                                                if status_counts['red'] > 0:
                                                    alert_rate = (status_counts['red'] / len(verified_steps)) * 100
                                                    st.error(f"🚨 Alert Rate: {alert_rate:.1f}% — {status_counts['red']} steps flagged")
                                                elif status_counts['yellow'] > 0:
                                                    st.warning(f"⚠️ {status_counts['yellow']} steps need review")
                                                else:
                                                    st.success("✅ All steps passed verification")
                                                
                                                # Link to visualizations
                                                st.markdown("**📊 Generated Visualizations:**")
                                                st.markdown("- View in dashboard tabs or check `figures/` directory")
                                                st.markdown("- Reasoning chain, hash flow, and hallucination guard charts")
                                                
                                            except Exception as e:
                                                st.warning(f"Could not load verification results: {e}")
                                    
                                    except Exception as e:
                                        st.error(f"❌ Verification failed: {e}")
                                        import traceback
                                        st.code(traceback.format_exc())
                            
                        except Exception as e:
                            st.error(f"❌ Error during trace collection: {e}")
                            import traceback
                            st.code(traceback.format_exc())
            
            # Generate Mock Trace
            elif mock_btn and user_prompt.strip():
                with st.spinner("🎭 Generating mock trace..."):
                    try:
                        result = generate_mock_trace(
                            prompt=user_prompt,
                            response="This is a simulated LLM response for testing purposes. It demonstrates the trace capture pipeline without making actual API calls. The trace includes token-level information with logprobs."
                        )
                        
                        st.success(f"✅ Mock trace generated! Session ID: `{result['session_id']}`")
                        
                        # Update session state for cross-tab sync
                        st.session_state["latest_trace_session"] = result['session_id']
                        st.session_state["latest_verification_time"] = time.time()
                        
                        # Display response
                        st.markdown("#### 📤 Mock Response")
                        st.markdown(f"```\n{result['response_text']}\n```")
                        
                        # Display trace summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Tokens Generated", result['token_count'])
                        with col2:
                            st.metric("Duration", f"{result['duration']:.2f}s")
                        with col3:
                            st.metric("Model", "mock-model")
                        
                        # Display trace preview
                        st.markdown("#### 🔍 Trace Preview")
                        trace_df = pd.DataFrame([
                            {
                                "Index": t["index"],
                                "Token": t["token"],
                                "LogProb": f"{t['logprob']:.4f}"
                            }
                            for t in result['trace'][:10]
                        ])
                        
                        st.dataframe(trace_df, use_container_width=True, hide_index=True)
                        
                        # File paths
                        st.markdown("#### 💾 Saved Files")
                        st.code(f"Trace: {result['trace_file']}")
                        st.code(f"Manifest: {result['manifest_file']}")
                        
                        # BoR Verification Section for Mock Traces
                        st.markdown("---")
                        st.markdown("#### 🔐 BoR Verification")
                        
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            verify_mock_btn = st.button(
                                "🔐 Verify with BoR",
                                key=f"verify_mock_{result['session_id']}",
                                type="secondary",
                                use_container_width=True
                            )
                        with col2:
                            st.info("Apply cryptographic verification and trust diagnostics to this trace")
                        
                        if verify_mock_btn:
                            with st.spinner("🔐 Running BoR verification pipeline..."):
                                try:
                                    import subprocess
                                    
                                    # Step 1: Extract trace to BoR format
                                    st.write("⚙️ Step 1/3: Converting trace to BoR format...")
                                    extract_result = subprocess.run(
                                        ["python", "extract_trace_for_bor.py", "--session", result['session_id']],
                                        capture_output=True,
                                        text=True
                                    )
                                    
                                    if extract_result.returncode != 0:
                                        st.error(f"❌ Extraction failed: {extract_result.stderr}")
                                    else:
                                        st.success("✅ Trace converted to BoR format")
                                        st.code(extract_result.stdout)
                                
                                except Exception as e:
                                    st.error(f"❌ Verification failed: {e}")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating mock trace: {e}")
            
            elif run_btn or mock_btn:
                st.warning("⚠️ Please enter a prompt before running trace capture.")
            
            # Trace History Section
            st.markdown("---")
            st.markdown("#### 📚 Trace History")
            
            try:
                traces = list_traces()
                
                if traces:
                    st.info(f"Found {len(traces)} saved trace(s)")
                    
                    # Create history table
                    history_df = pd.DataFrame([
                        {
                            "Session ID": t["session_id"],
                            "Model": t["model"],
                            "Prompt": t["prompt"][:60] + "...",
                            "Tokens": t["token_count"],
                            "Duration": f"{t['duration']:.2f}s",
                            "Timestamp": t["timestamp"]
                        }
                        for t in traces[-10:]  # Show last 10
                    ])
                    
                    st.dataframe(history_df, use_container_width=True, hide_index=True)
                    
                    # Session selector
                    st.markdown("##### 🔍 Inspect Saved Trace")
                    selected_session = st.selectbox(
                        "Select a session to view:",
                        options=[t["session_id"] for t in traces],
                        format_func=lambda sid: f"{sid} — {next(t['prompt'][:50] for t in traces if t['session_id'] == sid)}..."
                    )
                    
                    if selected_session:
                        try:
                            loaded = load_trace(selected_session)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Prompt:**")
                                st.text_area("Prompt", loaded["manifest"]["prompt"], height=100, key=f"loaded_prompt_{selected_session}", disabled=True, label_visibility="collapsed")
                            with col2:
                                st.markdown("**Response:**")
                                st.text_area("Response", loaded["manifest"]["response"], height=100, key=f"loaded_response_{selected_session}", disabled=True, label_visibility="collapsed")
                            
                            with st.expander("📋 View Full Trace"):
                                st.json(loaded["trace"])
                            
                            # BoR Verification for Historical Traces
                            st.markdown("---")
                            verify_hist_btn = st.button(
                                "🔐 Verify This Trace with BoR",
                                key=f"verify_hist_{selected_session}",
                                type="primary"
                            )
                            
                            if verify_hist_btn:
                                with st.spinner("🔐 Running BoR verification..."):
                                    try:
                                        import subprocess
                                        
                                        # Extract and verify
                                        st.write("⚙️ Converting to BoR format...")
                                        extract_result = subprocess.run(
                                            ["python", "extract_trace_for_bor.py", "--session", selected_session],
                                            capture_output=True,
                                            text=True
                                        )
                                        
                                        if extract_result.returncode == 0:
                                            st.success("✅ Trace extracted")
                                            
                                            # Compute guards
                                            st.write("⚙️ Computing hallucination guards...")
                                            subprocess.run(
                                                ["python", "compute_hallucination_guards.py", 
                                                 "--input", "bor_inputs/visual_data_trace.json"],
                                                capture_output=True,
                                                text=True
                                            )
                                            st.success("✅ Verification complete! Check bor_inputs/visual_data_trace.json")
                                        else:
                                            st.error(f"Extraction failed: {extract_result.stderr}")
                                    
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                            
                        except Exception as e:
                            st.error(f"❌ Error loading trace: {e}")
                    
                else:
                    st.info("📭 No traces saved yet. Run a trace capture to get started!")
                    
            except Exception as e:
                st.warning(f"⚠️ Could not load trace history: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; color: #6B7280; font-size: 12px;'>
        BoR-SDK Interactive Proof Explorer v1.0 • 
        <a href='https://github.com/yourusername/bor-sdk' style='color: #58A6FF;'>GitHub</a> • 
        Powered by Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


# ============================================================================
# EXPORT MODE
# ============================================================================

def export_to_html(output_path: str = "docs/interactive_proof.html"):
    """Export dashboard as static HTML (requires additional setup)."""
    print("📦 Export mode not yet implemented.")
    print("   For now, use: streamlit run interactive_visual_dashboard.py")
    print("   Then: File → Save As → HTML in browser")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BoR-SDK Interactive Visual Dashboard")
    parser.add_argument("--export", action="store_true", help="Export to static HTML")
    parser.add_argument("--output", default="docs/interactive_proof.html", help="Output path for HTML export")
    
    args = parser.parse_args()
    
    if args.export:
        export_to_html(args.output)
    else:
        main()

