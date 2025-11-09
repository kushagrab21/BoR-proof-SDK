#!/usr/bin/env python3
"""
Compute hallucination detection metrics for reasoning steps.

This script populates guard_state fields in visual_data.json with:
- Semantic similarity (prompt-response alignment)
- Entropy change (information drift detection)
- Logical consistency (reasoning coherence)
- Token overlap (grounding verification)
"""

from __future__ import annotations  # Enable deferred annotation evaluation

import json
import math
import argparse
from collections import Counter
from typing import Dict, List, Any, Tuple, Optional

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from sentence_transformers import SentenceTransformer, util
    import numpy as np
    MODELS_AVAILABLE = True
except ImportError as e:
    MODELS_AVAILABLE = False
    IMPORT_ERROR = str(e)


# Thresholds for guard metrics
THRESHOLDS = {
    "semantic_similarity": {"green": 0.75, "yellow": 0.50},
    "entropy_change": {"green": 0.2, "yellow": 0.5},
    "logical_consistency": {"green": 0.70, "yellow": 0.50, "contradiction": 0.40},
    "token_overlap": {"green": 0.30, "yellow": 0.15}
}

# Color codes for terminal output
COLORS = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "reset": "\033[0m"
}


def load_visual_data(filepath: str) -> Dict[str, Any]:
    """Load visual_data.json."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_visual_data(filepath: str, data: Dict[str, Any]) -> None:
    """Save updated visual_data.json."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def compute_semantic_similarity(prompt: str, response: str, model: SentenceTransformer) -> float:
    """
    Compute cosine similarity between prompt and response embeddings.
    
    Uses sentence-transformers to encode text and compute similarity.
    Returns value in [0, 1] range.
    """
    embeddings = model.encode([prompt, response], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    return max(0.0, min(1.0, similarity))


def compute_shannon_entropy(text: str, tokenizer: Any) -> float:
    """
    Compute Shannon entropy of text based on token distribution.
    
    H = -Σ p(token) * log2(p(token))
    Returns entropy in bits.
    """
    # Tokenize text
    tokens = tokenizer.tokenize(text.lower())
    if not tokens:
        return 0.0
    
    # Count token frequencies
    token_counts = Counter(tokens)
    total_tokens = len(tokens)
    
    # Compute entropy
    entropy = 0.0
    for count in token_counts.values():
        probability = count / total_tokens
        entropy -= probability * math.log2(probability)
    
    return entropy


def compute_entropy_change(
    current_text: str,
    previous_text: Optional[str],
    tokenizer: Any
) -> Tuple[float, Optional[float]]:
    """
    Compute entropy change between consecutive steps.
    
    Returns (absolute_change, current_entropy).
    If no previous text, returns (0.0, current_entropy).
    """
    current_entropy = compute_shannon_entropy(current_text, tokenizer)
    
    if previous_text is None:
        return 0.0, current_entropy
    
    previous_entropy = compute_shannon_entropy(previous_text, tokenizer)
    entropy_change = abs(current_entropy - previous_entropy)
    
    return entropy_change, current_entropy


def compute_logical_consistency(
    previous_response: str,
    current_response: str,
    nli_model: Any,
    nli_tokenizer: Any,
    device: str
) -> Dict[str, float]:
    """
    Compute logical consistency using NLI (Natural Language Inference).
    
    Treats previous response as premise, current response as hypothesis.
    Returns probabilities: {entailment, neutral, contradiction}.
    """
    if not previous_response:
        # First step has perfect consistency by default
        return {"entailment": 1.0, "neutral": 0.0, "contradiction": 0.0}
    
    # Prepare input for NLI model
    inputs = nli_tokenizer(
        previous_response,
        current_response,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    ).to(device)
    
    # Get predictions
    with torch.no_grad():
        outputs = nli_model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)[0]
    
    # BART-large-mnli outputs: [contradiction, neutral, entailment]
    return {
        "contradiction": probs[0].item(),
        "neutral": probs[1].item(),
        "entailment": probs[2].item()
    }


def compute_token_overlap(prompt: str, response: str, tokenizer: Any) -> float:
    """
    Compute Jaccard similarity between prompt and response tokens.
    
    J(A, B) = |A ∩ B| / |A ∪ B|
    Returns value in [0, 1] range.
    """
    prompt_tokens = set(tokenizer.tokenize(prompt.lower()))
    response_tokens = set(tokenizer.tokenize(response.lower()))
    
    if not prompt_tokens and not response_tokens:
        return 1.0
    if not prompt_tokens or not response_tokens:
        return 0.0
    
    intersection = len(prompt_tokens & response_tokens)
    union = len(prompt_tokens | response_tokens)
    
    return intersection / union if union > 0 else 0.0


def evaluate_metric(value: float, metric_name: str) -> str:
    """
    Evaluate a metric value against thresholds.
    
    Returns "green", "yellow", or "red".
    """
    thresholds = THRESHOLDS[metric_name]
    
    if metric_name == "entropy_change":
        # Lower is better for entropy change
        if value <= thresholds["green"]:
            return "green"
        elif value <= thresholds["yellow"]:
            return "yellow"
        else:
            return "red"
    else:
        # Higher is better for other metrics
        if value >= thresholds["green"]:
            return "green"
        elif value >= thresholds["yellow"]:
            return "yellow"
        else:
            return "red"


def evaluate_logical_consistency_status(nli_probs: Dict[str, float]) -> str:
    """
    Evaluate logical consistency based on NLI probabilities.
    
    Returns "green", "yellow", or "red".
    """
    thresholds = THRESHOLDS["logical_consistency"]
    
    if nli_probs["entailment"] >= thresholds["green"]:
        return "green"
    elif nli_probs["contradiction"] >= thresholds["contradiction"]:
        return "red"
    elif nli_probs["neutral"] > thresholds["yellow"]:
        return "yellow"
    else:
        # Default to yellow for uncertain cases
        return "yellow"


def evaluate_guard_state(metrics: Dict[str, Any]) -> Tuple[str, List[str]]:
    """
    Evaluate overall guard status based on all metrics.
    
    Returns (status, triggered_guards).
    - "red" if any metric is red
    - "yellow" if no red but any yellow
    - "green" otherwise
    """
    metric_statuses = {
        "semantic_similarity": evaluate_metric(metrics["semantic_similarity"], "semantic_similarity"),
        "entropy_change": evaluate_metric(metrics["entropy_change"], "entropy_change"),
        "logical_consistency": metrics["logical_consistency_status"],
        "token_overlap": evaluate_metric(metrics["token_overlap"], "token_overlap")
    }
    
    triggered_guards = []
    has_red = False
    has_yellow = False
    
    for metric_name, status in metric_statuses.items():
        if status == "red":
            triggered_guards.append(f"{metric_name}_red")
            has_red = True
        elif status == "yellow":
            triggered_guards.append(f"{metric_name}_yellow")
            has_yellow = True
    
    if has_red:
        overall_status = "red"
    elif has_yellow:
        overall_status = "yellow"
    else:
        overall_status = "green"
    
    return overall_status, triggered_guards


def compute_trust_diagnostics(metrics: Dict[str, Any], status: str, triggered: List[str]) -> Dict[str, Any]:
    """
    Compute trust diagnostics with score, label, and failure reasons.
    
    Trust score = weighted mean of normalized metrics:
        - 40% semantic similarity
        - 20% logical consistency
        - 20% token overlap
        - 20% entropy stability (1 - abs(normalized_entropy))
    
    Args:
        metrics: Dict with all computed metrics
        status: Guard status (green/yellow/red)
        triggered: List of triggered guard names
    
    Returns:
        Dict with trust_score, trust_label, failure_reason
    """
    semantic_sim = metrics["semantic_similarity"]
    entropy = metrics["entropy_change"]
    logic = metrics["logical_consistency"]
    overlap = metrics["token_overlap"]
    
    # Normalize entropy to 0-1 (1 = stable, 0 = high change)
    # Entropy can range from 0 to ~1.0 bits typically
    entropy_stability = max(0, min(1, 1 - abs(entropy)))
    
    # Weighted trust score
    trust_score = (
        0.4 * semantic_sim +
        0.2 * logic +
        0.2 * overlap +
        0.2 * entropy_stability
    )
    
    # Trust label based on thresholds
    if trust_score >= 0.8:
        trust_label = "Trusted"
    elif trust_score >= 0.5:
        trust_label = "Review"
    else:
        trust_label = "Untrusted"
    
    # Build failure reason string
    failure_reasons = []
    
    # Check for specific failures based on triggered guards
    if any("semantic_similarity" in t for t in triggered):
        if semantic_sim < 0.50:
            failure_reasons.append(f"Semantic drift (similarity {semantic_sim:.2f} < 0.50)")
        else:
            failure_reasons.append(f"Semantic similarity borderline ({semantic_sim:.2f})")
    
    if any("entropy_change" in t for t in triggered):
        if abs(entropy) > 0.5:
            failure_reasons.append(f"High entropy jump ({abs(entropy):.2f} > 0.50 bits)")
        else:
            failure_reasons.append(f"Entropy change elevated ({abs(entropy):.2f} bits)")
    
    if any("logical_consistency" in t for t in triggered):
        if logic < 0.40:
            failure_reasons.append(f"Logical contradiction detected (consistency {logic:.2f} < 0.40)")
        else:
            failure_reasons.append(f"Logical consistency weak ({logic:.2f})")
    
    if any("token_overlap" in t for t in triggered):
        if overlap < 0.15:
            failure_reasons.append(f"Low token overlap ({overlap:.2f} < 0.15)")
        else:
            failure_reasons.append(f"Token overlap below threshold ({overlap:.2f})")
    
    failure_reason = "; ".join(failure_reasons) if failure_reasons else None
    
    # Compute root causes (simplified, threshold-based)
    root_causes = []
    
    if semantic_sim < 0.5:
        root_causes.append("Semantic Drift")
    
    if abs(entropy) > 0.5:
        root_causes.append("Entropy Spike")
    
    if logic < 0.4:
        root_causes.append("Logical Contradiction")
    
    if overlap < 0.15:
        root_causes.append("Low Token Overlap")
    
    return {
        "trust_score": round(trust_score, 3),
        "trust_label": trust_label,
        "failure_reason": failure_reason,
        "root_causes": root_causes
    }


def format_colored_status(status: str) -> str:
    """Format status with terminal color codes."""
    color = COLORS.get(status, COLORS["reset"])
    return f"{color}[{status}]{COLORS['reset']}"


def compute_guards_for_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compute hallucination guard metrics for all steps.
    
    Returns updated steps with populated guard_state fields.
    """
    if not MODELS_AVAILABLE:
        print(f"❌ Error: Required ML libraries not available: {IMPORT_ERROR}")
        print("\n📦 Install dependencies:")
        print("   pip install torch transformers sentence-transformers numpy")
        return steps
    
    # Detect device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔧 Using device: {device}")
    
    # Load models
    print("📥 Loading models...")
    try:
        semantic_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        semantic_model.to(device)
        print("  ✓ Semantic similarity model loaded")
        
        nli_tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-mnli')
        nli_model = AutoModelForSequenceClassification.from_pretrained('facebook/bart-large-mnli')
        nli_model.to(device)
        nli_model.eval()
        print("  ✓ NLI model loaded")
        
        # Use semantic model's tokenizer for entropy and overlap
        basic_tokenizer = semantic_model.tokenizer
        print("  ✓ Tokenizer ready")
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        print("\n💡 Try running: pip install --upgrade torch transformers sentence-transformers")
        return steps
    
    # Group steps by session
    from collections import defaultdict
    sessions = defaultdict(list)
    for step in steps:
        sessions[step["session_id"]].append(step)
    
    # Sort each session by session_step_number
    for session_id in sessions:
        sessions[session_id].sort(key=lambda x: x["session_step_number"])
    
    # Process each step
    print(f"\n🧮 Computing guard metrics for {len(steps)} steps...\n")
    
    updated_steps = []
    step_entropies = {}  # Track entropies by session
    
    for step in steps:
        session_id = step["session_id"]
        session_step_num = step["session_step_number"]
        global_step_num = step["step_number"]
        
        prompt = step["prompt"]
        response = step["response"]
        
        # Get previous response in same session
        previous_response = None
        for s in sessions[session_id]:
            if s["session_step_number"] == session_step_num - 1:
                previous_response = s["response"]
                break
        
        # Compute semantic similarity
        semantic_sim = compute_semantic_similarity(prompt, response, semantic_model)
        
        # Compute entropy change
        entropy_change, current_entropy = compute_entropy_change(
            response, previous_response, basic_tokenizer
        )
        step_entropies[(session_id, session_step_num)] = current_entropy
        
        # Compute logical consistency
        nli_probs = compute_logical_consistency(
            previous_response or "",
            response,
            nli_model,
            nli_tokenizer,
            device
        )
        logic_status = evaluate_logical_consistency_status(nli_probs)
        logic_score = nli_probs["entailment"]
        
        # Compute token overlap
        token_overlap = compute_token_overlap(prompt, response, basic_tokenizer)
        
        # Collect metrics
        metrics = {
            "semantic_similarity": semantic_sim,
            "entropy_change": entropy_change,
            "logical_consistency": logic_score,
            "logical_consistency_status": logic_status,
            "token_overlap": token_overlap
        }
        
        # Evaluate overall guard state
        status, triggered_guards = evaluate_guard_state(metrics)
        
        # Compute trust diagnostics
        trust_diagnostics = compute_trust_diagnostics(metrics, status, triggered_guards)
        
        # Update step
        step["guard_state"] = {
            "semantic_similarity": round(semantic_sim, 3),
            "entropy_change": round(entropy_change, 3),
            "logical_consistency": round(logic_score, 3),
            "token_overlap": round(token_overlap, 3),
            "status": status,
            "triggered_guards": triggered_guards
        }
        
        # Add trust diagnostics
        step["trust_diagnostics"] = trust_diagnostics
        
        updated_steps.append(step)
        
        # Print progress with trust diagnostics
        status_colored = format_colored_status(status)
        trust_label = trust_diagnostics["trust_label"]
        trust_score = trust_diagnostics["trust_score"]
        root_causes = trust_diagnostics["root_causes"]
        
        print(f"Step {global_step_num} {status_colored} — "
              f"sim={semantic_sim:.2f}, entropy={entropy_change:.2f}, "
              f"logic={logic_score:.2f}, overlap={token_overlap:.2f}")
        print(f"         Trust: {trust_score:.2f} ({trust_label})", end="")
        
        # Show root causes
        if root_causes:
            print(f" — causes: {', '.join(root_causes)}")
        elif trust_diagnostics["failure_reason"]:
            print(f" → {trust_diagnostics['failure_reason']}")
        else:
            print()
    
    return updated_steps


def main():
    """Main execution pipeline."""
    parser = argparse.ArgumentParser(
        description="Compute hallucination guard metrics for reasoning trace"
    )
    parser.add_argument(
        "--input",
        default="visual_data.json",
        help="Input visual_data.json file (default: visual_data.json)"
    )
    parser.add_argument(
        "--output",
        default="visual_data.json",
        help="Output file path (default: overwrite input)"
    )
    args = parser.parse_args()
    
    print("🔍 Computing hallucination guard metrics...\n")
    
    # Load data
    try:
        visual_data = load_visual_data(args.input)
    except FileNotFoundError:
        print(f"❌ Error: {args.input} not found")
        print("   Run extract_trace_data.py first to generate visual_data.json")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {args.input}: {e}")
        return
    
    steps = visual_data.get("steps", [])
    if not steps:
        print("⚠️  Warning: No steps found in visual_data.json")
        return
    
    # Compute guards
    updated_steps = compute_guards_for_steps(steps)
    
    # Update visual data
    visual_data["steps"] = updated_steps
    visual_data["metadata"]["guards_computed"] = True
    
    # Save
    save_visual_data(args.output, visual_data)
    
    print(f"\n✅ Guard metrics computed and saved to: {args.output}")
    
    # Summary statistics
    status_counts = {"green": 0, "yellow": 0, "red": 0}
    for step in updated_steps:
        status = step["guard_state"]["status"]
        status_counts[status] += 1
    
    print(f"\n📊 Status distribution:")
    print(f"   🟢 Green:  {status_counts['green']}")
    print(f"   🟡 Yellow: {status_counts['yellow']}")
    print(f"   🔴 Red:    {status_counts['red']}")
    
    # Trust diagnostics summary
    trust_counts = {"Trusted": 0, "Review": 0, "Untrusted": 0}
    for step in updated_steps:
        trust_label = step.get("trust_diagnostics", {}).get("trust_label", "Unknown")
        if trust_label in trust_counts:
            trust_counts[trust_label] += 1
    
    print(f"\n🧩 Trust Diagnostics:")
    print(f"   🟢 Trusted:   {trust_counts['Trusted']}")
    print(f"   🟡 Review:    {trust_counts['Review']}")
    print(f"   🔴 Untrusted: {trust_counts['Untrusted']}")
    
    # List untrusted steps with reasons and root causes
    untrusted_steps = [s for s in updated_steps if s.get("trust_diagnostics", {}).get("trust_label") == "Untrusted"]
    if untrusted_steps:
        print(f"\n⚠️  Untrusted steps:")
        for step in untrusted_steps:
            step_num = step["step_number"]
            causes = step["trust_diagnostics"].get("root_causes", [])
            if causes:
                print(f"   Step {step_num}: {', '.join(causes)}")
            else:
                reason = step["trust_diagnostics"].get("failure_reason", "Unknown")
                print(f"   Step {step_num}: {reason}")
    
    # Root causes frequency analysis
    all_causes = []
    for step in updated_steps:
        all_causes.extend(step.get("trust_diagnostics", {}).get("root_causes", []))
    
    if all_causes:
        from collections import Counter
        cause_counts = Counter(all_causes)
        print(f"\n🔍 Root Cause Analysis:")
        for cause, count in cause_counts.most_common():
            print(f"   {cause}: {count} occurrence(s)")


if __name__ == "__main__":
    main()

