# 🚀 LLM Sandbox Quick Start Guide

**Step 12A Implementation** — Prompt → Trace Capture Pipeline

---

## 🎯 What is the LLM Sandbox?

The **LLM Sandbox** is a new interactive feature in the BoR-SDK dashboard that allows you to:

1. ✍️ **Enter any prompt** directly in the web interface
2. 🤖 **Run LLM models** (GPT-4, GPT-3.5, etc.)
3. 📊 **Capture detailed traces** including tokens, logprobs, and timing
4. 💾 **Save traces** for later verification and analysis

This is the foundation for **live BoR verification** of LLM reasoning (coming in Steps 12B–12D).

---

## ⚡ Quick Start (5 Minutes)

### 1. **Launch the Dashboard**

```bash
cd /Users/kaku/Desktop/bor-sdk-ap2/bor-sdk-ap-1/BoR-proof-SDK
streamlit run interactive_visual_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### 2. **Navigate to LLM Sandbox**

Click on the **"🤖 LLM Sandbox"** tab at the top of the dashboard.

### 3. **Try a Mock Trace** (No API Key Required)

1. In the text area, enter:
   ```
   What is quantum entanglement?
   ```

2. Click **"🎭 Generate Mock Trace"**

3. View the results:
   - ✅ Mock response text
   - 📊 Token count, duration, model info
   - 🔍 Trace preview table (first 10 tokens)
   - 📋 Full trace JSON (expandable)
   - 💾 Saved file paths

### 4. **Try a Real Trace** (Requires OpenAI API Key)

1. Set your API key (one-time setup):
   ```bash
   export OPENAI_API_KEY='sk-your-key-here'
   ```

2. Restart the dashboard:
   ```bash
   streamlit run interactive_visual_dashboard.py
   ```

3. Enter a prompt:
   ```
   Explain the theory of relativity in simple terms.
   ```

4. Select model: **gpt-4-turbo**

5. Adjust parameters (optional):
   - Max Tokens: 300
   - Temperature: 0.7

6. Click **"🚀 Run Trace Capture"**

7. Wait 2-5 seconds for the LLM to respond

8. View the full trace with real logprobs!

---

## 📚 View Trace History

Scroll down to the **"📚 Trace History"** section to:

- See all saved traces (last 10)
- Inspect any previous session
- View prompts, responses, and full traces

---

## 🧪 Test from Command Line

```bash
# Test the trace collector directly
cd /Users/kaku/Desktop/bor-sdk-ap2/bor-sdk-ap-1/BoR-proof-SDK

# Generate a mock trace
python trace_collector.py --mock --prompt "Hello, world!"

# List all saved traces
python trace_collector.py --list

# Run a real trace (requires API key)
export OPENAI_API_KEY='sk-...'
python trace_collector.py --prompt "Count from 1 to 10" --model gpt-3.5-turbo

# Run the test suite
python test_llm_sandbox.py
```

---

## 📊 Example Output

### Trace Preview Table

When you run a trace, you'll see a table like this:

| Index | Token    | LogProb  | Probability |
|-------|----------|----------|-------------|
| 0     | Quantum  | -0.0823  | 92.11%      |
| 1     | entangle | -0.1456  | 86.45%      |
| 2     | ment     | -0.0234  | 97.69%      |
| 3     | is       | -0.0567  | 94.48%      |
| 4     | a        | -0.0912  | 91.28%      |

**Interpretation:**
- **LogProb**: Log probability of the token (higher = more confident)
- **Probability**: Converted to percentage (2^logprob × 100%)

### Saved Files

Each trace generates two files:

```
llm_traces/
├── trace_a12f9bcd.json      # Token-level data
└── manifest_a12f9bcd.json   # Session metadata
```

**Trace File Example:**
```json
[
  {
    "index": 0,
    "token": "Quantum",
    "logprob": -0.0823,
    "bytes": [81, 117, 97, 110, 116, 117, 109],
    "timestamp": 1699989123.10,
    "top_alternatives": [
      {"token": "The", "logprob": -2.5, "bytes": [84, 104, 101]}
    ]
  }
]
```

**Manifest File Example:**
```json
{
  "session_id": "a12f9bcd",
  "model": "gpt-4-turbo",
  "prompt": "What is quantum entanglement?",
  "response": "Quantum entanglement is...",
  "timestamp": "2025-11-09T05:12:00Z",
  "duration_seconds": 2.134,
  "token_count": 47,
  "temperature": 0.7,
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 47,
    "total_tokens": 52
  }
}
```

---

## 🎛️ Parameter Guide

### Model Selection

| Model | Description | Speed | Cost |
|-------|-------------|-------|------|
| `gpt-4-turbo` | Latest GPT-4 (recommended) | Medium | $$ |
| `gpt-3.5-turbo` | Fast and cheap | Fast | $ |
| `gpt-4` | Original GPT-4 | Slow | $$$ |
| `gpt-4o` | GPT-4 optimized | Fast | $$ |

### Temperature

- **0.0** → Deterministic, same output every time
- **0.7** → Balanced (default)
- **1.0** → Creative, varied outputs
- **2.0** → Very random

### Max Tokens

- **50** → Very short responses
- **300** → Medium responses (default)
- **2000** → Long responses

---

## 🛠️ Troubleshooting

### Problem: "OPENAI_API_KEY not found"

**Solution:** Use mock traces or set your API key:
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

### Problem: "trace_collector not available"

**Solution:** Make sure you're in the correct directory:
```bash
cd /Users/kaku/Desktop/bor-sdk-ap2/bor-sdk-ap-1/BoR-proof-SDK
ls trace_collector.py  # Should exist
```

### Problem: API call fails

**Solution:** Check:
1. API key is valid: `echo $OPENAI_API_KEY`
2. You have OpenAI credits
3. Internet connection is working
4. Try a shorter prompt with lower max_tokens

### Problem: Traces not showing in history

**Solution:** Check the `llm_traces/` directory:
```bash
ls -la llm_traces/
```

If empty, traces weren't saved. Check console for errors.

---

## 🔐 Security Note

**Your API key is never stored in trace files.** Only the model, prompt, response, and timing data are saved.

However, be careful not to commit `llm_traces/` to version control if your prompts contain sensitive information. The `.gitignore` already excludes this directory.

---

## 🚀 Next Steps

### After Step 12A (Current)

You can:
- ✅ Capture LLM traces interactively
- ✅ View token-level details
- ✅ Save traces for later analysis

### Coming in Step 12B

- 🔐 **BoR verification** applied to captured traces
- ✅ **Cryptographic chain** generation
- 🔍 **Verification status** displayed in UI

### Coming in Step 12C

- 🚨 **Hallucination detection** on live traces
- 📊 **Trust scores** and root-cause analysis
- 🟢🟡🔴 **Guard status** indicators

### Coming in Step 12D

- 🎬 **Live visualization** of reasoning
- ⏯️ **Playback controls** for token-by-token review
- 🌈 **BoR overlays** showing verification state

---

## 📝 Example Use Cases

### 1. **Debugging Model Behavior**

Capture traces to see exactly what tokens the model generated and with what confidence:

```
Prompt: "2 + 2 = ?"
Trace: ["2", " +", " ", "2", " =", " ", "4"] (with logprobs)
```

### 2. **Testing Prompt Engineering**

Compare traces from different prompts to see which produces better results:

```
Prompt A: "Explain quantum physics"
Prompt B: "Explain quantum physics in simple terms for a 10-year-old"
```

### 3. **Reproducibility Testing**

Set temperature = 0.0 and run the same prompt multiple times to verify determinism.

### 4. **API Cost Analysis**

Check the `usage` field in manifests to track token consumption and estimate costs.

---

## 🎉 You're Ready!

You now have a fully functional **LLM Sandbox** for capturing reasoning traces.

Try it out, experiment with different prompts and models, and get ready for **BoR verification** in Step 12B!

---

## 📞 Need Help?

1. Run the test suite: `python test_llm_sandbox.py`
2. Check the status doc: `STEP12A_LLM_SANDBOX_STATUS.md`
3. View saved traces: `ls llm_traces/`
4. Try mock traces first (no API key needed)

---

**Happy Tracing! 🧠🚀**

