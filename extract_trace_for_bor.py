#!/usr/bin/env python3
"""
Extract LLM Trace → BoR visual_data.json Converter

Converts captured LLM traces from the sandbox into the canonical
visual_data.json schema used by BoR verification pipeline.

Usage:
    python extract_trace_for_bor.py --trace llm_traces/trace_<id>.json
    python extract_trace_for_bor.py --session <session_id>
"""

import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def compute_chain_hash(prompt_hash: str, response_hash: str, parent_hash: Optional[str]) -> str:
    """
    Compute chain hash from prompt, response, and parent.
    Matches BoR SDK chaining logic.
    """
    if parent_hash:
        combined = f"{parent_hash}{prompt_hash}{response_hash}"
    else:
        combined = f"{prompt_hash}{response_hash}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()


def chunk_tokens_to_steps(
    trace: List[Dict[str, Any]],
    manifest: Dict[str, Any],
    chunk_size: int = 10
) -> List[Dict[str, Any]]:
    """
    Convert token-level trace into reasoning steps.
    Groups tokens into chunks to create meaningful reasoning steps.
    
    Args:
        trace: Token-level trace from trace_collector
        manifest: Session manifest with metadata
        chunk_size: Number of tokens per step
        
    Returns:
        List of reasoning steps in BoR format
    """
    steps = []
    session_id = manifest['session_id']
    model = manifest['model']
    full_prompt = manifest['prompt']
    full_response = manifest['response']
    base_timestamp = manifest.get('timestamp', datetime.now(timezone.utc).isoformat())
    
    # Parse base timestamp
    try:
        from dateutil import parser
        base_dt = parser.parse(base_timestamp)
        base_ts = base_dt.timestamp()
    except:
        import time
        base_ts = time.time()
    
    # Create step 1: Full prompt → response
    # This gives us a complete reasoning step
    step = {
        "step_number": 1,
        "session_step_number": 1,
        "session_id": session_id,
        "timestamp": base_ts,
        "prompt": full_prompt,
        "response": full_response,
        "hash_prompt": compute_hash(full_prompt),
        "hash_response": compute_hash(full_response),
        "chain_hash": "",  # Will compute after
        "parent_hash": None,
        "guard_state": {
            "semantic_similarity": None,
            "entropy_change": None,
            "logical_consistency": None,
            "token_overlap": None,
            "status": "green",
            "triggered_guards": []
        },
        "metadata": {
            "execution_time_ms": manifest.get('duration_seconds', 0) * 1000,
            "model": model,
            "deterministic": manifest.get('temperature', 0.7) == 0.0,
            "token_count": manifest.get('token_count', len(trace)),
            "temperature": manifest.get('temperature', 0.7)
        },
        "trust_diagnostics": {
            "trust_score": 1.0,
            "trust_label": "Trusted",
            "failure_reason": "",
            "root_causes": []
        },
        "trace_tokens": []  # Store token details
    }
    
    # Add token-level data
    for token_data in trace:
        step["trace_tokens"].append({
            "index": token_data.get("index", 0),
            "token": token_data.get("token", ""),
            "logprob": token_data.get("logprob", 0.0),
            "probability": 2 ** token_data.get("logprob", 0.0) if token_data.get("logprob") is not None else None
        })
    
    # Compute chain hash
    step["chain_hash"] = compute_chain_hash(
        step["hash_prompt"],
        step["hash_response"],
        step["parent_hash"]
    )
    
    steps.append(step)
    
    # Optional: Create additional steps for token chunks if trace is long
    if len(trace) > chunk_size * 2:
        # Group tokens into chunks
        for i in range(0, len(trace), chunk_size):
            chunk = trace[i:i+chunk_size]
            if not chunk:
                continue
            
            # Build chunk text
            chunk_text = "".join([t.get("token", "") for t in chunk])
            
            # Create sub-step
            step_num = len(steps) + 1
            parent_step = steps[-1]
            
            sub_step = {
                "step_number": step_num,
                "session_step_number": step_num,
                "session_id": session_id,
                "timestamp": base_ts + (i * 0.01),
                "prompt": f"[Token chunk {i//chunk_size + 1}]",
                "response": chunk_text,
                "hash_prompt": compute_hash(f"chunk_{i}"),
                "hash_response": compute_hash(chunk_text),
                "chain_hash": "",
                "parent_hash": parent_step["chain_hash"],
                "guard_state": {
                    "semantic_similarity": None,
                    "entropy_change": None,
                    "logical_consistency": None,
                    "token_overlap": None,
                    "status": "green",
                    "triggered_guards": []
                },
                "metadata": {
                    "execution_time_ms": len(chunk) * 10,
                    "model": model,
                    "deterministic": manifest.get('temperature', 0.7) == 0.0,
                    "chunk_index": i // chunk_size,
                    "is_token_chunk": True
                },
                "trust_diagnostics": {
                    "trust_score": 1.0,
                    "trust_label": "Trusted",
                    "failure_reason": "",
                    "root_causes": []
                },
                "trace_tokens": [{
                    "index": t.get("index", 0),
                    "token": t.get("token", ""),
                    "logprob": t.get("logprob", 0.0),
                    "probability": 2 ** t.get("logprob", 0.0) if t.get("logprob") is not None else None
                } for t in chunk]
            }
            
            # Compute chain hash
            sub_step["chain_hash"] = compute_chain_hash(
                sub_step["hash_prompt"],
                sub_step["hash_response"],
                sub_step["parent_hash"]
            )
            
            steps.append(sub_step)
    
    return steps


def extract_trace_to_bor(
    trace_file: str,
    manifest_file: str,
    output_file: str = "bor_inputs/visual_data_trace.json",
    chunk_size: int = 10
) -> Dict[str, Any]:
    """
    Main conversion function: trace → visual_data.json
    
    Args:
        trace_file: Path to trace_*.json
        manifest_file: Path to manifest_*.json
        output_file: Output path for visual_data.json
        chunk_size: Tokens per reasoning step
        
    Returns:
        Generated visual_data dict
    """
    # Load trace and manifest
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace = json.load(f)
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Convert to steps
    steps = chunk_tokens_to_steps(trace, manifest, chunk_size)
    
    # Build visual_data structure
    visual_data = {
        "metadata": {
            "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_directory": "llm_traces",
            "source_trace": trace_file,
            "chain_valid": True,  # Will validate later
            "hashes_valid": True,
            "total_sessions": 1,
            "guards_computed": False,
            "trace_mode": True,
            "token_count": len(trace),
            "model": manifest['model']
        },
        "steps": steps,
        "master_certificates": [],
        "session_info": {
            "session_id": manifest['session_id'],
            "total_steps": len(steps),
            "start_time": steps[0]["timestamp"] if steps else 0,
            "end_time": steps[-1]["timestamp"] if steps else 0,
            "model": manifest['model'],
            "prompt": manifest['prompt'],
            "response": manifest['response']
        }
    }
    
    # Validate chain
    chain_valid = True
    for i in range(1, len(steps)):
        expected_parent = steps[i-1]["chain_hash"]
        actual_parent = steps[i].get("parent_hash")
        if actual_parent and actual_parent != expected_parent:
            chain_valid = False
            break
    
    visual_data["metadata"]["chain_valid"] = chain_valid
    
    # Create output directory
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(visual_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Extracted {len(steps)} reasoning steps")
    print(f"   Source: {trace_file}")
    print(f"   Output: {output_file}")
    print(f"   Chain valid: {chain_valid}")
    
    return visual_data


def extract_by_session_id(session_id: str, **kwargs) -> Dict[str, Any]:
    """
    Extract trace by session ID.
    Automatically locates trace and manifest files.
    """
    trace_dir = Path("llm_traces")
    trace_file = trace_dir / f"trace_{session_id}.json"
    manifest_file = trace_dir / f"manifest_{session_id}.json"
    
    if not trace_file.exists():
        raise FileNotFoundError(f"Trace not found: {trace_file}")
    if not manifest_file.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_file}")
    
    return extract_trace_to_bor(str(trace_file), str(manifest_file), **kwargs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert LLM trace to BoR visual_data.json format"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--trace",
        type=str,
        help="Path to trace_*.json file"
    )
    group.add_argument(
        "--session",
        type=str,
        help="Session ID (auto-locates trace and manifest)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="bor_inputs/visual_data_trace.json",
        help="Output path for visual_data.json"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10,
        help="Number of tokens per reasoning step (for chunking)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.session:
            # Extract by session ID
            extract_by_session_id(
                args.session,
                output_file=args.output,
                chunk_size=args.chunk_size
            )
        else:
            # Extract by trace file path
            trace_file = args.trace
            
            # Infer manifest file
            trace_path = Path(trace_file)
            session_id = trace_path.stem.replace("trace_", "")
            manifest_file = trace_path.parent / f"manifest_{session_id}.json"
            
            if not manifest_file.exists():
                print(f"❌ Manifest not found: {manifest_file}")
                print("   Provide both trace and manifest in same directory")
                return 1
            
            extract_trace_to_bor(
                trace_file,
                str(manifest_file),
                output_file=args.output,
                chunk_size=args.chunk_size
            )
        
        print("\n📋 Next steps:")
        print(f"   1. Compute guards: python compute_hallucination_guards.py --input {args.output}")
        print(f"   2. Generate visuals: python generate_all_visualizations.py --visual-data {args.output}")
        print(f"   3. View in dashboard: streamlit run interactive_visual_dashboard.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

