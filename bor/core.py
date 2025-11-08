"""
Module: core
------------
Implements BoRRun, BoRStep, and Proof structures.
Each step in reasoning emits a fingerprint hi,
and all fingerprints concatenate into HMASTER.
"""

import inspect
import sys
import os
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List

from bor.exceptions import DeterminismError, HashMismatchError
from bor.hash_utils import canonical_bytes, content_hash, env_fingerprint

# Import invariant hooks with backward compatibility
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
    from bor_core.hooks import pre_run_hook, post_run_hook, transform_hook
    INVARIANT_HOOKS_AVAILABLE = True
except ImportError:
    # Graceful fallback if hooks not available
    pre_run_hook = lambda *a, **k: (None, None)
    post_run_hook = lambda *a, **k: None
    transform_hook = lambda f: f
    INVARIANT_HOOKS_AVAILABLE = False


@dataclass
class BoRStep:
    """Represents a single deterministic reasoning step."""

    fn_name: str
    input_state: Any
    output_state: Any
    config: Dict
    code_version: str
    fingerprint: str = None

    def compute_fingerprint(self):
        """Compute and store fingerprint for this step."""
        payload = {
            "fn": self.fn_name,
            "input": self.input_state,
            "config": self.config,
            "version": self.code_version,
        }
        self.fingerprint = content_hash(payload)
        return self.fingerprint


@dataclass(frozen=True)
class Proof:
    """Holds complete proof chain: meta, steps, stage_hashes, and HMASTER."""

    meta: Dict[str, Any]
    steps: List[Dict[str, Any]]
    stage_hashes: List[str]
    master: str


class BoRRun:
    """
    Controller for executing deterministic reasoning chains.
    Usage:
        run = BoRRun(S0, C, V)
        run.add_step(fn1).add_step(fn2)
        proof = run.finalize()
        run.verify()
    """

    def __init__(self, S0: Any, C: Dict, V: str):
        self.S0 = S0
        self.S0_initial = S0  # Keep original S0 for meta
        self.C = C
        self.V = V
        self.initial_state = S0  # Backward compatibility
        self.config = C  # Backward compatibility
        self.code_version = V  # Backward compatibility
        self.env = env_fingerprint()
        # Compute initialization proof hash P₀
        self.P0 = content_hash(
            {"S0": self.S0, "C": self.C, "V": self.V, "env": self.env}
        )
        # Optional console confirmation
        print(f"[BoR P₀] Initialization Proof Hash = {self.P0}")

        # Invariant Framework: Capture pre-run state
        if INVARIANT_HOOKS_AVAILABLE:
            self.h_env, self.h_input = pre_run_hook(S0, C, V)
        else:
            self.h_env, self.h_input = None, None

        self.steps: List[BoRStep] = []
        self._final_state = None
        self.proof: Proof | None = None

    # --- Step execution ---
    def add_step(self, fn: Callable):
        """Apply a deterministic function and record its fingerprint."""
        if not callable(fn):
            raise DeterminismError("Step must be a callable.")
        prev_state = self.initial_state if not self.steps else self._final_state

        # Invariant Framework: Wrap function with transform_hook
        deterministic_fn = transform_hook(fn) if INVARIANT_HOOKS_AVAILABLE else fn

        try:
            output_state = deterministic_fn(prev_state, self.config, self.code_version)
        except Exception as e:
            raise DeterminismError(
                f"Function {fn.__name__} failed deterministically: {e}"
            )

        # Prefer decorator-provided name if present
        fn_name = getattr(fn, "__bor_step_name__", fn.__name__)
        step = BoRStep(
            fn_name, prev_state, output_state, self.config, self.code_version
        )
        step.compute_fingerprint()
        self.steps.append(step)
        self._final_state = output_state

        # Emit P₁ step-level proof hash
        step_num = len(self.steps)
        print(f"[BoR P₁] Step #{step_num} '{fn_name}' → hᵢ = {step.fingerprint}")

        # Invariant Framework: Post-run verification
        if INVARIANT_HOOKS_AVAILABLE:
            post_run_hook(fn_name, {"output": output_state, "fingerprint": step.fingerprint})

        return self

    def _stage_hashes(self) -> List[str]:
        """Return ordered list of step fingerprints (hᵢ)."""
        return [s.fingerprint for s in self.steps]

    # --- Final proof computation ---
    def finalize(self) -> Proof:
        """
        Aggregate step fingerprints into HMASTER and construct primary proof.
        HMASTER = H(h1 || h2 || ... || hn)
        """
        stage_hashes = self._stage_hashes()

        # Domain-separate the aggregation string (defensive)
        concat = "P2|" + "|".join(stage_hashes)
        HMASTER = content_hash(concat)

        # Build canonical primary proof object (P0–P2)
        step_records = [
            {
                "i": i + 1,
                "fn": s.fn_name,
                "input": s.input_state,
                "output": s.output_state,
                "config": s.config,
                "version": s.code_version,
                "fingerprint": s.fingerprint,
            }
            for i, s in enumerate(self.steps)
        ]

        meta = {
            "S0": self.S0_initial,
            "C": self.C,
            "V": self.V,
            "env": self.env,
            "H0": self.P0,
        }

        self.proof = Proof(
            meta=meta, steps=step_records, stage_hashes=stage_hashes, master=HMASTER
        )
        print(f"[BoR P₂] HMASTER = {HMASTER}")
        
        # Invariant Framework: Emit telemetry
        if INVARIANT_HOOKS_AVAILABLE:
            print(f"[BoR-Invariant] HMASTER = {HMASTER[:16]}... | Steps = {len(self.steps)} | Hooks = Active")
        
        return self.proof

    def to_primary_proof(self) -> Dict[str, Any]:
        """
        Return the canonical primary proof JSON-ready dict.
        Requires finalize() to have been called.
        """
        if self.proof is None:
            raise RuntimeError("Call finalize() before exporting the primary proof.")
        return {
            "meta": self.proof.meta,
            "steps": self.proof.steps,
            "stage_hashes": self.proof.stage_hashes,
            "master": self.proof.master,
        }

    def run_steps(self, stage_fns):
        """
        Convenience wrapper: execute a sequence of functions as steps.
        """
        for fn in stage_fns:
            self.add_step(fn)
        return self

    # --- Verification ---
    def verify(self) -> bool:
        """Recompute proof deterministically and check master equality."""
        if not self.proof:
            raise DeterminismError("Run must be finalized before verification.")
        old_master = self.proof.master
        recomputed = self.finalize()
        if recomputed.master != old_master:
            raise HashMismatchError("Master proof mismatch: reasoning diverged.")
        return True

    def summary(self) -> Dict:
        """Return dictionary summary of current run."""
        return {
            "initial_state": self.initial_state,
            "num_steps": len(self.steps),
            "fingerprints": [s.fingerprint for s in self.steps],
            "HMASTER": self.proof.master if self.proof else None,
        }
