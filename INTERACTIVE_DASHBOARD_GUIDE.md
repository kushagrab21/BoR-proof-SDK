# 🌐 BoR-SDK Interactive Dashboard — User Guide

## Overview

The **BoR-SDK Interactive Proof Explorer** is a modern web dashboard that transforms static visualizations into an explorable, real-time experience. Built with Streamlit and Plotly, it provides:

- 🧠 **Interactive Reasoning Chain** — Explore step-by-step AI reasoning with hover tooltips
- 🚨 **Real-Time Hallucination Monitor** — Live metrics tracking semantic drift and logical consistency
- 🔐 **Cryptographic Chain Inspector** — Tamper-evident hash verification
- ✅ **Verification Dashboard** — Automated integrity checks with detailed reports

---

## 🚀 Quick Start

### Installation

```bash
# Install interactive dashboard dependencies
pip install streamlit plotly pandas

# Or install all visualization dependencies
pip install -r requirements-viz.txt
```

### Launch Dashboard

**Option 1: Using Make**
```bash
make dashboard
```

**Option 2: Using CLI**
```bash
bor visualize --interactive
```

**Option 3: Direct Streamlit**
```bash
streamlit run interactive_visual_dashboard.py
```

The dashboard will automatically open in your default browser at `http://localhost:8501`.

---

## 📊 Dashboard Features

### 1️⃣ Reasoning Flow Tab

**What it shows:**
- Interactive graph of reasoning steps
- Prompt → Response → Hash progression
- Color-coded nodes based on guard status

**Interactions:**
- **Hover** over nodes to see:
  - Step number
  - Prompt/Response preview
  - Hash prefix
  - Guard status
- **Select** a step from dropdown to view:
  - Full prompt text
  - Full response text
  - Cryptographic metadata
  - Session information

**Visual Legend:**
- 🟢 **Green nodes** — Safe, verified reasoning
- 🟡 **Yellow nodes** — Caution, borderline metrics
- 🔴 **Red nodes** — Alert, potential hallucination
- **Square nodes** — Prompts
- **Circle nodes** — Responses

---

### 2️⃣ Hallucination Monitor Tab

**What it shows:**
- Real-time line charts of 4 key metrics:
  - 💎 **Semantic Similarity** (cyan) — Prompt-response coherence
  - 🌊 **Entropy Change** (orange) — Token distribution stability
  - 🧠 **Logical Consistency** (lime) — NLI-based reasoning validity
  - 🔗 **Token Overlap** (magenta) — Lexical similarity
- Threshold zones:
  - 🟢 **Safe Zone** (0.75-1.0)
  - 🟡 **Caution Zone** (0.50-0.75)
  - 🔴 **Alert Zone** (0.0-0.50)

**Interactions:**
- **Hover** over data points to see exact metric values
- **Zoom** and **pan** using Plotly controls
- **Toggle** metrics on/off by clicking legend items

**Alert Feed:**
- Expandable cards for each red-flagged step
- Shows triggered guards and metric breakdown
- Full prompt/response for context

---

### 3️⃣ Cryptographic Chain Tab

**What it shows:**
- Tabular view of hash chain progression
- Parent → Child linkage for tamper detection
- Color-coded status indicators
- Timestamp tracking

**Interactions:**
- **Scroll** through complete chain history
- **Sort** by any column
- **Expand** master certificates to see:
  - Aggregated hash
  - Step count
  - Verification status

**Master Certificates:**
- Hierarchical roll-up of step certificates
- Verification status badges
- Aggregated hash prefixes

---

### 4️⃣ Verification Tab

**What it shows:**
- Overall verification status (VERIFIED / PARTIAL / FAILED)
- Detailed check results:
  - ✅ Hash correspondence
  - ✅ Node count match
  - ✅ Chain integrity
  - ✅ Guard status accuracy
  - ✅ Determinism verification
- Session metadata
- Extraction timestamps

**Interactions:**
- **Expand** detailed checks to see:
  - Check name
  - Status (pass/warn/fail)
  - Evidence and messages
- View session information:
  - Session ID
  - Total steps
  - Duration

---

## 🎨 Sidebar Features

### Summary Statistics

- **Total Steps** — Number of reasoning steps
- **Sessions** — Count of unique sessions
- **Masters** — Master certificates generated
- **Verified** — Successfully verified certificates

### Guard Status Breakdown

- 🟢 **Green** — Safe steps count
- 🟡 **Yellow** — Caution steps count
- 🔴 **Red** — Alert steps count
- **Alert Rate** — Percentage of flagged steps

### Actions

- **♻️ Reload Data** — Refresh from `visual_data.json`
- **🎨 Theme** — Toggle dark/light mode (coming soon)

---

## 🔧 Technical Details

### Data Sources

The dashboard reads from:
- `visual_data.json` — Reasoning trace with guard metrics
- `visual_verification_report.json` — Integrity check results
- `figures/*.spec.json` — Sidecar specifications (optional)

### Auto-Reload

Streamlit automatically detects file changes. To manually reload:
1. Click **♻️ Reload Data** in sidebar
2. Or press `R` in the browser

### Performance

- **Caching** — Data is cached for fast re-renders
- **Lazy Loading** — Graphs render on-demand per tab
- **Responsive** — Works on desktop and tablet (mobile experimental)

---

## 🎯 Use Cases

### 1. Research & Development

**Scenario:** Debugging hallucination detection thresholds

**Workflow:**
1. Run pipeline: `make visualize`
2. Launch dashboard: `make dashboard`
3. Navigate to **Hallucination Monitor**
4. Identify steps near threshold boundaries
5. Adjust guard parameters in `compute_hallucination_guards.py`
6. Re-run pipeline and reload dashboard

### 2. Demo & Presentation

**Scenario:** Showing BoR-SDK capabilities to stakeholders

**Workflow:**
1. Generate proofs with diverse prompts
2. Launch dashboard in presentation mode
3. Walk through **Reasoning Flow** tab
4. Highlight **Verification** status
5. Show **Alert Feed** for transparency

### 3. Audit & Compliance

**Scenario:** Proving deterministic AI for regulatory review

**Workflow:**
1. Run strict verification: `make visualize-strict`
2. Launch dashboard: `make dashboard`
3. Navigate to **Verification** tab
4. Export detailed check results
5. Show **Cryptographic Chain** for tamper-evidence

### 4. Education & Training

**Scenario:** Teaching explainable AI concepts

**Workflow:**
1. Use dashboard to visualize reasoning steps
2. Show how guards detect hallucinations
3. Explain cryptographic chaining
4. Interactive exploration by students

---

## 📦 Export & Sharing

### Screenshot Export

1. Navigate to desired tab
2. Use browser's screenshot tool (Cmd+Shift+4 on macOS)
3. Or use Streamlit's built-in screenshot (coming soon)

### HTML Export (Experimental)

```bash
python interactive_visual_dashboard.py --export
```

Generates `docs/interactive_proof.html` (requires additional setup).

### Embedding

The dashboard can be embedded in:
- Jupyter notebooks (using `streamlit run` in background)
- Documentation sites (iframe)
- Internal portals (reverse proxy)

---

## 🎨 Customization

### Theme Colors

Edit `interactive_visual_dashboard.py` to customize:

```python
# Status colors
status_colors = {
    "green": "#2ECC71",  # Change to your brand green
    "yellow": "#F39C12", # Change to your brand yellow
    "red": "#E74C3C"     # Change to your brand red
}
```

### Layout

Modify Streamlit layout options:

```python
st.set_page_config(
    page_title="Your Custom Title",
    page_icon="🔐",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)
```

### Custom CSS

Add custom styling in the `st.markdown()` block:

```python
st.markdown("""
<style>
.main {
    background-color: #YOUR_COLOR;
}
</style>
""", unsafe_allow_html=True)
```

---

## 🐛 Troubleshooting

### Dashboard won't launch

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit plotly pandas
```

---

### Data not loading

**Error:** `❌ Error: visual_data.json not found`

**Solution:**
```bash
# Run extraction first
make extract
make guards
make viz

# Then launch dashboard
make dashboard
```

---

### Graphs not rendering

**Error:** Blank graphs or "Error creating graph"

**Solution:**
1. Check browser console for JavaScript errors
2. Try clearing Streamlit cache: Click **♻️ Reload Data**
3. Ensure `visual_data.json` has valid JSON syntax
4. Restart dashboard: `Ctrl+C` then `make dashboard`

---

### Port already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or specify different port
streamlit run interactive_visual_dashboard.py --server.port 8502
```

---

## 🚀 Advanced Features (Coming Soon)

### 1. Replay Animation

Step-by-step reasoning reconstruction with 1-2s per step animation.

**Usage:**
```python
# In Reasoning Flow tab
st.button("▶️ Replay Run")
```

### 2. LLM Re-Explanation

Mini panel to explain why a step was flagged.

**Usage:**
```python
# In Alert Feed
st.button("🤖 Explain Alert")
```

### 3. Comparison Mode

Compare two reasoning traces side-by-side.

**Usage:**
```python
# In sidebar
st.file_uploader("Upload second trace for comparison")
```

### 4. Export to PDF

Generate publication-ready PDF report.

**Usage:**
```python
# In Verification tab
st.button("📄 Export PDF Report")
```

---

## 📚 Related Documentation

- **`VISUAL_AESTHETIC_UPGRADES.md`** — Static visualization design guide
- **`AESTHETIC_UPGRADE_SUMMARY.md`** — Executive summary of visual improvements
- **`README.md`** — Main project documentation
- **`docs/visual_proof.md`** — Assembled static proof document

---

## 🎯 Best Practices

### 1. Data Freshness

Always run the pipeline before launching the dashboard:

```bash
make visualize && make dashboard
```

### 2. Performance

For large traces (>100 steps), consider:
- Filtering by session
- Paginating results
- Using summary views

### 3. Sharing

When sharing the dashboard:
- Include `visual_data.json` and `visual_verification_report.json`
- Ensure recipients have dependencies installed
- Consider exporting to HTML for non-technical users

### 4. Security

For production deployments:
- Use authentication (Streamlit supports OAuth)
- Restrict file access to trusted directories
- Sanitize user inputs (if adding custom queries)

---

## 🏆 Key Advantages

| Feature | Static Visualizations | Interactive Dashboard |
|---------|----------------------|----------------------|
| **Exploration** | Limited | ✅ Full hover/click |
| **Real-Time** | No | ✅ Auto-reload |
| **Filtering** | No | ✅ Dynamic |
| **Drill-Down** | No | ✅ Multi-level |
| **Sharing** | Easy (PNG/SVG) | Medium (requires setup) |
| **Accessibility** | High | Medium (requires browser) |

**Recommendation:** Use static visualizations for papers/reports, interactive dashboard for demos/debugging.

---

## 📧 Support

For issues or questions:
- Check troubleshooting section above
- Review Streamlit docs: https://docs.streamlit.io
- Open GitHub issue: https://github.com/yourusername/bor-sdk/issues

---

**Status:** ✅ **Production Ready**  
**Version:** v1.0 (Interactive Dashboard)  
**Last Updated:** 2025-11-09  

---

## 🎊 Conclusion

The **BoR-SDK Interactive Proof Explorer** transforms your static visualizations into a living, explorable experience. It's perfect for:

- **Researchers** — Debugging and analyzing reasoning traces
- **Engineers** — Real-time monitoring and verification
- **Executives** — High-level status dashboards
- **Educators** — Interactive teaching tools

**Launch it now:**

```bash
make dashboard
```

🌐 **Experience verifiable AI in real-time!** 🎯

