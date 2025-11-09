#!/usr/bin/env python3
"""
BoR-SDK LLM Trace Collector

Captures LLM reasoning traces including tokens, logprobs, and timing information.
Prepares traces for downstream BoR verification and trust diagnostics.

Usage:
    from trace_collector import collect_trace
    
    trace_path = collect_trace(
        prompt="Explain quantum entanglement",
        model="gpt-4-turbo"
    )
"""

import json
import time
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set directly

# Try importing OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ Warning: OpenAI not available. Install with: pip install openai")


# ============================================================================
# TRACE COLLECTION
# ============================================================================

def collect_trace(
    prompt: str,
    model: str = None,
    max_tokens: int = 300,
    temperature: float = None,
    output_dir: str = "llm_traces"
) -> Dict[str, Any]:
    """
    Run LLM and capture detailed reasoning trace.
    
    Args:
        prompt: User prompt to send to the model
        model: Model identifier (gpt-4-turbo, gpt-3.5-turbo, etc.)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        output_dir: Directory to save trace files
        
    Returns:
        Dictionary with:
            - session_id: Unique identifier for this trace
            - trace_file: Path to saved trace JSON
            - manifest_file: Path to saved manifest JSON
            - response_text: Full text response
            - token_count: Number of tokens generated
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI library not available. Install with: pip install openai>=1.12.0")
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment. Set it in .env or export it.")
    
    # Use environment variables for model and temperature if not specified
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    if temperature is None:
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    client = OpenAI(api_key=api_key)
    
    # Generate session ID
    session_id = str(uuid.uuid4())[:8]
    timestamp_iso = datetime.utcnow().isoformat() + "Z"
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Capture start time
    t_start = time.time()
    
    print(f"🧠 Running {model} with prompt: {prompt[:50]}...")
    
    try:
        # Prepare API parameters
        api_params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Handle max_tokens vs max_completion_tokens (newer models)
        if "gpt-5" in model.lower() or "o1" in model.lower():
            api_params["max_completion_tokens"] = max_tokens
            # gpt-5-nano only supports temperature=1, don't include if default
            if temperature != 1.0:
                print(f"⚠️  Model {model} only supports temperature=1, ignoring requested {temperature}")
        else:
            api_params["max_tokens"] = max_tokens
            api_params["temperature"] = temperature
        
        # Try with logprobs first, fall back to without if not supported
        try:
            response = client.chat.completions.create(
                **api_params,
                logprobs=True,
                top_logprobs=3  # Get top 3 alternative tokens
            )
            has_logprobs = True
        except Exception as e:
            if "logprobs" in str(e).lower() or "not allowed" in str(e).lower():
                # Model doesn't support logprobs, try without
                print(f"⚠️  Model {model} doesn't support logprobs, continuing without them...")
                response = client.chat.completions.create(**api_params)
                has_logprobs = False
            else:
                raise
        
        # Extract response data
        choice = response.choices[0]
        response_text = choice.message.content
        finish_reason = choice.finish_reason
        
        # Extract token-level trace
        trace = []
        if has_logprobs and choice.logprobs and choice.logprobs.content:
            for i, token_obj in enumerate(choice.logprobs.content):
                token_data = {
                    "index": i,
                    "token": token_obj.token,
                    "logprob": token_obj.logprob,
                    "bytes": token_obj.bytes,
                    "timestamp": t_start + i * 0.01,  # Simulated timing
                }
                
                # Add top alternatives if available
                if token_obj.top_logprobs:
                    token_data["top_alternatives"] = [
                        {
                            "token": alt.token,
                            "logprob": alt.logprob,
                            "bytes": alt.bytes
                        }
                        for alt in token_obj.top_logprobs
                    ]
                
                trace.append(token_data)
        else:
            # No logprobs available, create simple trace from response text
            # Estimate tokens by splitting on spaces and punctuation
            tokens = response_text.split()
            for i, token in enumerate(tokens):
                trace.append({
                    "index": i,
                    "token": token,
                    "logprob": None,
                    "bytes": list(token.encode('utf-8')),
                    "timestamp": t_start + i * 0.01
                })
        
        t_end = time.time()
        duration = t_end - t_start
        
        # Build manifest
        manifest = {
            "session_id": session_id,
            "model": model,
            "prompt": prompt,
            "response": response_text,
            "timestamp": timestamp_iso,
            "duration_seconds": round(duration, 3),
            "token_count": len(trace),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "finish_reason": finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        # Save trace file
        trace_file = output_path / f"trace_{session_id}.json"
        with open(trace_file, 'w', encoding='utf-8') as f:
            json.dump(trace, f, indent=2, ensure_ascii=False)
        
        # Save manifest file
        manifest_file = output_path / f"manifest_{session_id}.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Trace captured: {len(trace)} tokens in {duration:.2f}s")
        print(f"   Trace saved: {trace_file}")
        print(f"   Manifest saved: {manifest_file}")
        
        return {
            "session_id": session_id,
            "trace_file": str(trace_file),
            "manifest_file": str(manifest_file),
            "response_text": response_text,
            "token_count": len(trace),
            "duration": duration,
            "manifest": manifest,
            "trace": trace
        }
        
    except Exception as e:
        print(f"❌ Error during trace collection: {e}")
        raise


def load_trace(session_id: str, trace_dir: str = "llm_traces") -> Dict[str, Any]:
    """
    Load a previously saved trace and manifest.
    
    Args:
        session_id: Session ID to load
        trace_dir: Directory containing trace files
        
    Returns:
        Dictionary with trace and manifest data
    """
    trace_path = Path(trace_dir)
    
    trace_file = trace_path / f"trace_{session_id}.json"
    manifest_file = trace_path / f"manifest_{session_id}.json"
    
    if not trace_file.exists():
        raise FileNotFoundError(f"Trace file not found: {trace_file}")
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_file}")
    
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace = json.load(f)
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    return {
        "session_id": session_id,
        "trace": trace,
        "manifest": manifest,
        "trace_file": str(trace_file),
        "manifest_file": str(manifest_file)
    }


def list_traces(trace_dir: str = "llm_traces") -> List[Dict[str, Any]]:
    """
    List all available traces in the trace directory.
    
    Args:
        trace_dir: Directory containing trace files
        
    Returns:
        List of manifest summaries
    """
    trace_path = Path(trace_dir)
    
    if not trace_path.exists():
        return []
    
    manifests = []
    for manifest_file in sorted(trace_path.glob("manifest_*.json")):
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                manifests.append({
                    "session_id": manifest["session_id"],
                    "model": manifest["model"],
                    "prompt": manifest["prompt"][:100],  # Truncate for display
                    "timestamp": manifest["timestamp"],
                    "token_count": manifest["token_count"],
                    "duration": manifest["duration_seconds"]
                })
        except Exception as e:
            print(f"⚠️ Warning: Could not load {manifest_file}: {e}")
    
    return manifests


# ============================================================================
# MOCK TRACE GENERATOR (for testing without API)
# ============================================================================

def generate_mock_trace(
    prompt: str,
    response: str = "This is a mock response for testing.",
    output_dir: str = "llm_traces"
) -> Dict[str, Any]:
    """
    Generate a mock trace without calling the API (for testing).
    
    Args:
        prompt: User prompt
        response: Mock response text
        output_dir: Directory to save trace files
        
    Returns:
        Same format as collect_trace()
    """
    session_id = str(uuid.uuid4())[:8]
    timestamp_iso = datetime.utcnow().isoformat() + "Z"
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate mock trace
    tokens = response.split()
    trace = []
    for i, token in enumerate(tokens):
        trace.append({
            "index": i,
            "token": token,
            "logprob": -0.1 - (i * 0.01),  # Simulated logprob
            "bytes": list(token.encode('utf-8')),
            "timestamp": time.time() + i * 0.01,
            "top_alternatives": [
                {"token": f"alt_{token}", "logprob": -0.5, "bytes": list(f"alt_{token}".encode('utf-8'))}
            ]
        })
    
    manifest = {
        "session_id": session_id,
        "model": "mock-model",
        "prompt": prompt,
        "response": response,
        "timestamp": timestamp_iso,
        "duration_seconds": 0.5,
        "token_count": len(trace),
        "max_tokens": 300,
        "temperature": 0.7,
        "finish_reason": "stop",
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(tokens),
            "total_tokens": len(prompt.split()) + len(tokens)
        }
    }
    
    # Save files
    trace_file = output_path / f"trace_{session_id}.json"
    manifest_file = output_path / f"manifest_{session_id}.json"
    
    with open(trace_file, 'w', encoding='utf-8') as f:
        json.dump(trace, f, indent=2)
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Mock trace generated: {session_id}")
    
    return {
        "session_id": session_id,
        "trace_file": str(trace_file),
        "manifest_file": str(manifest_file),
        "response_text": response,
        "token_count": len(trace),
        "duration": 0.5,
        "manifest": manifest,
        "trace": trace
    }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="BoR-SDK LLM Trace Collector")
    parser.add_argument("--prompt", type=str, help="Prompt to send to the model")
    parser.add_argument("--model", type=str, default="gpt-4-turbo", help="Model to use")
    parser.add_argument("--max-tokens", type=int, default=300, help="Max tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--list", action="store_true", help="List all saved traces")
    parser.add_argument("--mock", action="store_true", help="Generate mock trace for testing")
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Saved Traces:")
        traces = list_traces()
        if traces:
            for trace in traces:
                print(f"  • {trace['session_id']} — {trace['model']} — {trace['prompt'][:50]}...")
        else:
            print("   (none)")
    elif args.mock:
        prompt = args.prompt or "Explain quantum entanglement simply."
        result = generate_mock_trace(prompt)
        print(f"🎭 Mock trace created: {result['session_id']}")
    elif args.prompt:
        result = collect_trace(
            prompt=args.prompt,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
        print(f"✅ Trace collected: {result['session_id']}")
        print(f"   Response: {result['response_text'][:100]}...")
    else:
        parser.print_help()

