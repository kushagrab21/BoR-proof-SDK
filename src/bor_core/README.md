# BoR Core - Invariant Framework

## Overview

The **BoR Core** module implements a Deterministic Reasoning Compiler layer for the BoR-Proof SDK. It continuously validates the **BoR invariant** during development and runtime:

> *Given identical canonical inputs and environment, the system must always yield identical outputs, hashes, and proofs.*

## Module Structure

```
src/bor_core/
├── __init__.py          # Module exports
├── init_hooks.py        # Lifecycle hooks (pre/post-run, transform, register, drift)
├── registry.py          # State and metrics management
├── env_utils.py         # Environment capture and hashing
└── hooks.py             # Convenient hook re-exports
```

## Core Components

### 1. Lifecycle Hooks (`init_hooks.py`)

- **`pre_run_hook(initial, config, version)`**: Captures environment and input hashes before execution
- **`post_run_hook(step_name, result)`**: Verifies determinism after each step
- **`transform_hook(func)`**: Decorator ensuring referential transparency
- **`register_proof_hook(bundle_path)`**: Compares stored vs recomputed proof hashes
- **`drift_check_hook(prev_hash, curr_hash)`**: Detects and logs drift between runs

### 2. Registry (`registry.py`)

Manages persistent state and metrics:
- `log_state(entry)`: Append state entries to state.json
- `update_metric(key, value)`: Update metrics in metrics.json
- `compare_hashes(h1, h2)`: Compare hash equality

### 3. Environment Utils (`env_utils.py`)

- `capture_env_hash()`: Creates deterministic hash of execution environment (Python version, OS, timestamp, BoR SDK version)

## Usage

### Basic Example

```python
from bor_core.hooks import pre_run_hook, transform_hook

# Capture initial state
h_env, h_input = pre_run_hook(initial_value, config, "v1.0")

# Decorate functions to ensure determinism
@transform_hook
def process_data(x):
    return x * 2

result = process_data(5)  # Automatically logged and hashed
```

### Invariant Validation

Run the invariant evaluator from the repo root:

```bash
python evaluate_invariant.py
```

Expected output when invariant holds:
```
[BoR-Invariant] VERIFIED
```

## Testing

Run the test suite:

```bash
python tests/test_invariant_hooks.py
```

All tests should pass with:
```
✓ All invariant hook tests passed
```

## Next Steps

The framework is designed to be integrated into the main BoR workflow (P₀–P₂):
1. Hook into `bor/core.py` execution lifecycle
2. Integrate with `bor/verify.py` validation checks
3. Add drift detection across proof generations
4. Extend metrics collection for analysis

## Files Generated

During execution, the framework generates:
- `state.json`: Sequential log of all state transitions
- `metrics.json`: Key metrics and hash values

