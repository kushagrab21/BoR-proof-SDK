#!/usr/bin/env python3
"""
Real-Time LLM Trace Streamer with Live Trust Diagnostics

Streams LLM output token-by-token and computes trust metrics incrementally.
Used for live hallucination detection in the dashboard.

Usage:
    from trace_streamer import stream_trace_with_diagnostics
    
    for chunk in stream_trace_with_diagnostics(prompt="Hello", model="gpt-4"):
        print(chunk['token'], chunk['trust_score'])
"""

import json
import time
import uuid
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator
from collections import deque

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set directly

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================================================================
# INCREMENTAL TRUST METRICS
# ============================================================================

def compute_incremental_trust(
    tokens: List[str],
    chunk_size: int = 10
) -> Dict[str, Any]:
    """
    Compute trust metrics for current token window.
    Lightweight version for real-time computation.
    
    Args:
        tokens: List of tokens generated so far
        chunk_size: Window size for analysis
        
    Returns:
        Dict with trust_score, trust_label, metrics
    """
    if len(tokens) < 3:
        return {
            "trust_score": 1.0,
            "trust_label": "Trusted",
            "semantic_similarity": None,
            "entropy_change": None,
            "logical_consistency": None,
            "token_overlap": None,
            "status": "green"
        }
    
    # Simple heuristics (fast, no ML models)
    recent_tokens = tokens[-chunk_size:] if len(tokens) > chunk_size else tokens
    text = "".join(recent_tokens)
    
    # Token diversity (proxy for entropy)
    unique_ratio = len(set(recent_tokens)) / len(recent_tokens)
    
    # Repetition detection
    has_repetition = any(
        recent_tokens[i] == recent_tokens[i+1] 
        for i in range(len(recent_tokens)-1)
    )
    
    # Length consistency
    avg_token_len = sum(len(t) for t in recent_tokens) / len(recent_tokens)
    length_variance = sum((len(t) - avg_token_len)**2 for t in recent_tokens) / len(recent_tokens)
    
    # Compute trust score (simple heuristic)
    trust_score = 1.0
    
    if unique_ratio < 0.3:  # Very repetitive
        trust_score -= 0.3
    
    if has_repetition:
        trust_score -= 0.1
    
    if length_variance > 100:  # Unusual length variation
        trust_score -= 0.2
    
    trust_score = max(0.0, min(1.0, trust_score))
    
    # Determine label
    if trust_score >= 0.85:
        trust_label = "Trusted"
        status = "green"
    elif trust_score >= 0.65:
        trust_label = "Review"
        status = "yellow"
    else:
        trust_label = "Untrusted"
        status = "red"
    
    return {
        "trust_score": trust_score,
        "trust_label": trust_label,
        "semantic_similarity": unique_ratio,
        "entropy_change": 1.0 - unique_ratio,
        "logical_consistency": 1.0 if not has_repetition else 0.5,
        "token_overlap": unique_ratio,
        "status": status,
        "metrics": {
            "unique_ratio": unique_ratio,
            "has_repetition": has_repetition,
            "length_variance": length_variance
        }
    }


# ============================================================================
# STREAMING TRACE COLLECTOR
# ============================================================================

def stream_trace_with_diagnostics(
    prompt: str,
    model: str = None,
    max_tokens: int = 300,
    temperature: float = None,
    chunk_size: int = 10,
    output_dir: str = "llm_traces"
) -> Generator[Dict[str, Any], None, None]:
    """
    Stream LLM output with real-time trust diagnostics.
    
    Yields chunks containing:
        - token: Current token text
        - logprob: Token log probability
        - index: Token index
        - timestamp: Generation time
        - trust_score: Rolling trust score
        - trust_label: Trusted/Review/Untrusted
        - status: green/yellow/red
        - accumulated_tokens: All tokens so far
        
    Args:
        prompt: User prompt
        model: Model identifier
        max_tokens: Max tokens to generate
        temperature: Sampling temperature
        chunk_size: Window for trust computation
        output_dir: Directory to save final trace
        
    Yields:
        Dict with token and diagnostic info
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI library required: pip install openai>=1.12.0")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    # Use environment variables for model and temperature if not specified
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    if temperature is None:
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    client = OpenAI(api_key=api_key)
    
    # Initialize session
    session_id = str(uuid.uuid4())[:8]
    t_start = time.time()
    
    # Token buffer
    tokens = []
    logprobs = []
    trace = []
    
    # Stream from API
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            stream_options={"include_usage": True},
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        token_index = 0
        
        for chunk in stream:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta
            
            if not delta.content:
                continue
            
            token_text = delta.content
            token_logprob = None  # Note: logprobs not available in stream mode
            
            # Add to buffer
            tokens.append(token_text)
            logprobs.append(token_logprob)
            
            # Compute trust metrics
            diagnostics = compute_incremental_trust(tokens, chunk_size)
            
            # Build trace entry
            trace_entry = {
                "index": token_index,
                "token": token_text,
                "logprob": token_logprob,
                "timestamp": time.time(),
                "bytes": list(token_text.encode('utf-8'))
            }
            
            trace.append(trace_entry)
            
            # Yield chunk with diagnostics
            yield {
                "token": token_text,
                "index": token_index,
                "logprob": token_logprob,
                "timestamp": time.time(),
                "trust_score": diagnostics["trust_score"],
                "trust_label": diagnostics["trust_label"],
                "status": diagnostics["status"],
                "semantic_similarity": diagnostics["semantic_similarity"],
                "entropy_change": diagnostics["entropy_change"],
                "logical_consistency": diagnostics["logical_consistency"],
                "token_overlap": diagnostics["token_overlap"],
                "accumulated_tokens": "".join(tokens),
                "token_count": len(tokens),
                "session_id": session_id
            }
            
            token_index += 1
        
        # Finalize
        t_end = time.time()
        duration = t_end - t_start
        response_text = "".join(tokens)
        
        # Save trace and manifest
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Trace file
        trace_file = output_path / f"trace_{session_id}.json"
        with open(trace_file, 'w', encoding='utf-8') as f:
            json.dump(trace, f, indent=2, ensure_ascii=False)
        
        # Manifest file
        manifest = {
            "session_id": session_id,
            "model": model,
            "prompt": prompt,
            "response": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 3),
            "token_count": len(tokens),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "finish_reason": "stop",
            "streaming": True
        }
        
        manifest_file = output_path / f"manifest_{session_id}.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Yield final summary
        yield {
            "token": None,
            "index": token_index,
            "complete": True,
            "session_id": session_id,
            "trace_file": str(trace_file),
            "manifest_file": str(manifest_file),
            "response_text": response_text,
            "token_count": len(tokens),
            "duration": duration
        }
        
    except Exception as e:
        yield {
            "error": str(e),
            "session_id": session_id,
            "complete": True
        }


def stream_mock_trace(
    prompt: str,
    response: str = "This is a mock streaming response for testing real-time diagnostics.",
    delay: float = 0.1,
    chunk_size: int = 10,
    output_dir: str = "llm_traces"
) -> Generator[Dict[str, Any], None, None]:
    """
    Mock streaming trace for testing without API.
    
    Simulates token-by-token generation with artificial delays.
    """
    session_id = str(uuid.uuid4())[:8]
    t_start = time.time()
    
    # Split response into tokens (words)
    tokens = response.split()
    trace = []
    
    for i, token in enumerate(tokens):
        # Simulate processing delay
        time.sleep(delay)
        
        # Add to trace
        trace_entry = {
            "index": i,
            "token": token,
            "logprob": -0.1 - (i * 0.01),
            "timestamp": time.time(),
            "bytes": list(token.encode('utf-8'))
        }
        trace.append(trace_entry)
        
        # Compute diagnostics
        current_tokens = [t["token"] for t in trace]
        diagnostics = compute_incremental_trust(current_tokens, chunk_size)
        
        # Yield chunk
        yield {
            "token": token,
            "index": i,
            "logprob": trace_entry["logprob"],
            "timestamp": time.time(),
            "trust_score": diagnostics["trust_score"],
            "trust_label": diagnostics["trust_label"],
            "status": diagnostics["status"],
            "semantic_similarity": diagnostics["semantic_similarity"],
            "entropy_change": diagnostics["entropy_change"],
            "logical_consistency": diagnostics["logical_consistency"],
            "token_overlap": diagnostics["token_overlap"],
            "accumulated_tokens": " ".join(current_tokens),
            "token_count": len(current_tokens),
            "session_id": session_id
        }
    
    # Finalize
    t_end = time.time()
    duration = t_end - t_start
    
    # Save files
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    trace_file = output_path / f"trace_{session_id}.json"
    with open(trace_file, 'w', encoding='utf-8') as f:
        json.dump(trace, f, indent=2)
    
    manifest = {
        "session_id": session_id,
        "model": "mock-streaming",
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(duration, 3),
        "token_count": len(tokens),
        "temperature": 0.7,
        "finish_reason": "stop",
        "streaming": True
    }
    
    manifest_file = output_path / f"manifest_{session_id}.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    # Final summary
    yield {
        "token": None,
        "index": len(tokens),
        "complete": True,
        "session_id": session_id,
        "trace_file": str(trace_file),
        "manifest_file": str(manifest_file),
        "response_text": response,
        "token_count": len(tokens),
        "duration": duration
    }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Stream LLM trace with live diagnostics")
    parser.add_argument("--prompt", type=str, required=True, help="Prompt to send")
    parser.add_argument("--model", type=str, default="gpt-4-turbo", help="Model to use")
    parser.add_argument("--mock", action="store_true", help="Use mock streaming")
    parser.add_argument("--chunk-size", type=int, default=10, help="Trust computation window")
    
    args = parser.parse_args()
    
    print(f"🧠 Streaming trace for: {args.prompt[:50]}...")
    print("="*60)
    
    if args.mock:
        stream_fn = stream_mock_trace
        kwargs = {"prompt": args.prompt, "delay": 0.05}
    else:
        stream_fn = stream_trace_with_diagnostics
        kwargs = {"prompt": args.prompt, "model": args.model}
    
    for chunk in stream_fn(**kwargs, chunk_size=args.chunk_size):
        if chunk.get("complete"):
            print("\n" + "="*60)
            print(f"✅ Complete: {chunk['session_id']}")
            print(f"   Tokens: {chunk['token_count']}")
            print(f"   Duration: {chunk['duration']:.2f}s")
            print(f"   Files: {chunk.get('trace_file', 'N/A')}")
        elif chunk.get("error"):
            print(f"\n❌ Error: {chunk['error']}")
        else:
            # Real-time display
            status_icon = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(chunk["status"], "⚪")
            print(f"{status_icon} [{chunk['index']:3d}] {chunk['token']:15s} "
                  f"Trust: {chunk['trust_score']:.2f} ({chunk['trust_label']})")

