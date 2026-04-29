#!/usr/bin/env python3
"""
Artifact 2: Attack Implementation — Algorithm 1
LFFLDL-based key recovery for Falcon-n.

Usage:
    python falcon_attack.py --n 512 --traces 5000
    python falcon_attack.py --demo
"""

import numpy as np
import math
import argparse
from collections import defaultdict

# ─── LFFLDL Oracle (Simulated) ───────────────────────────────────────────────

def lffldl(z: int) -> int:
    return int(math.floor(math.log2(abs(z) + 1))) if z != 0 else 0

def simulate_base_sampler(sigma: float) -> int:
    """Simulate discrete Gaussian sample ~ D_{Z, sigma}."""
    z = int(np.round(np.random.normal(0, sigma)))
    return z

def signing_oracle(sigma_vec, noise_cycles=0):
    """
    Simulate one Falcon signing operation.
    Returns (z_vec, lffldl_vec) — sampled coefficients and their leakage.
    noise_cycles: add timing noise (cycles) to simulate real hardware.
    """
    n = len(sigma_vec)
    z_vec = np.array([simulate_base_sampler(s) for s in sigma_vec])
    lffldl_vec = np.array([lffldl(z) for z in z_vec])
    if noise_cycles > 0:
        lffldl_vec = lffldl_vec + np.random.randint(-noise_cycles, noise_cycles+1, n) // 30
        lffldl_vec = np.clip(lffldl_vec, 0, 9)
    return z_vec, lffldl_vec

# ─── Key Generation (Simulated) ──────────────────────────────────────────────

def simulate_falcon_keygen(n: int, q: int = 12289):
    """
    Simulate Falcon-n key generation.
    Returns sigma_vec (secret GS norms), public key stub.
    Real Falcon uses NTRU; here we simulate GS norms directly.
    """
    # GS norms are roughly sqrt(q) / 2^(level/2) at each tree level
    # Simulate realistic range [4.54, 165.59] for Falcon-512
    np.random.seed(42)
    sigma_vec = np.random.uniform(4.54, 165.59, n)
    sigma_vec[0] = 4.54
    sigma_vec[-1] = 165.59
    # Public key stub (hash placeholder)
    h = np.random.randint(0, q, n)
    return sigma_vec, h

# ─── Phase 1: Collect Traces ─────────────────────────────────────────────────

def collect_traces(sigma_vec, m: int, noise_cycles: int = 0):
    """
    Collect m LFFLDL traces from the signing oracle.
    Returns Lambda matrix (m x n).
    """
    n = len(sigma_vec)
    Lambda = np.zeros((m, n), dtype=int)
    print(f"  Collecting {m} traces (n={n}, noise={noise_cycles} cycles)...")
    for j in range(m):
        _, lffldl_vec = signing_oracle(sigma_vec, noise_cycles)
        Lambda[j] = lffldl_vec
        if (j+1) % 1000 == 0:
            print(f"    Trace {j+1}/{m} collected")
    return Lambda

# ─── Phase 2: Estimate Leaf Standard Deviations ──────────────────────────────

def estimate_sigma(Lambda: np.ndarray):
    """
    Algorithm 1, lines 4-7: bias-corrected inversion of empirical means.
    Returns sigma_hat vector.
    """
    mu_hat = Lambda.mean(axis=0)
    # Bias-corrected inversion: sigma_hat = 2^(mu_hat + 0.5) * sqrt(pi/2)
    sigma_hat = (2 ** (mu_hat + 0.5)) * math.sqrt(math.pi / 2)
    return mu_hat, sigma_hat

# ─── Phase 3: Gram-Schmidt Recovery (Simulated) ──────────────────────────────

def gs_recover(sigma_hat, h):
    """
    Recover approximate Gram-Schmidt basis from estimated norms.
    In real Falcon: full NTRU-structure orthogonalization.
    Here: return sigma_hat as the recovered norms (stub).
    """
    return sigma_hat  # placeholder for full GS orthogonalization

def ntru_extract(B_tilde, h):
    """
    Extract (f, g) from recovered GS basis and public key h.
    In real Falcon: lattice reduction (LLL/BKZ-2.0).
    Here: simulated stub.
    """
    n = len(B_tilde)
    # Stub: in practice, run BKZ-2.0 on NTRU lattice Lambda_h
    f = np.random.randint(-1, 2, n)  # placeholder
    g = np.random.randint(-1, 2, n)  # placeholder
    return f, g

# ─── Evaluation Metrics ───────────────────────────────────────────────────────

def compute_metrics(sigma_true, sigma_hat):
    rel_err = np.abs(sigma_hat - sigma_true) / sigma_true
    return {
        "mean_rel_error": rel_err.mean(),
        "max_rel_error":  rel_err.max(),
        "coeff_lt1pct":   (rel_err < 0.01).mean() * 100,
    }

# ─── Main Attack (Algorithm 1) ───────────────────────────────────────────────

def run_attack(n: int, m: int, q: int = 12289, noise_cycles: int = 0):
    print(f"\n{'='*60}")
    print(f"  LFFLDL Key Recovery Attack — Falcon-{n}")
    print(f"  m={m} traces, q={q}, noise={noise_cycles} cycles")
    print(f"{'='*60}")

    # Key generation
    print("\n[1] Simulating Falcon key generation...")
    sigma_true, h = simulate_falcon_keygen(n, q)
    print(f"    sigma range: [{sigma_true.min():.2f}, {sigma_true.max():.2f}], mean={sigma_true.mean():.2f}")

    # Trace collection
    print("\n[2] Collecting LFFLDL traces...")
    Lambda = collect_traces(sigma_true, m, noise_cycles)

    # Estimation
    print("\n[3] Estimating leaf standard deviations (bias-corrected)...")
    mu_hat, sigma_hat = estimate_sigma(Lambda)
    metrics = compute_metrics(sigma_true, sigma_hat)
    print(f"    Mean relative error : {metrics['mean_rel_error']:.3f}")
    print(f"    Max relative error  : {metrics['max_rel_error']:.3f}")
    print(f"    Coeff < 1% error    : {metrics['coeff_lt1pct']:.1f}%")

    # GS Recovery
    print("\n[4] Recovering Gram-Schmidt basis...")
    B_tilde = gs_recover(sigma_hat, h)

    # Key extraction (lattice reduction stub)
    print("\n[5] Extracting secret key via lattice reduction (BKZ-2.0 stub)...")
    f, g = ntru_extract(B_tilde, h)
    print(f"    Key extraction complete (stub — plug in real BKZ for full attack)")

    print(f"\n{'='*60}")
    print(f"  Attack complete.")
    print(f"{'='*60}\n")
    return sigma_hat, metrics

# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LFFLDL Key Recovery Attack (Algorithm 1)")
    parser.add_argument("--n", type=int, default=512, choices=[64, 128, 256, 512, 1024])
    parser.add_argument("--traces", type=int, default=5000)
    parser.add_argument("--noise", type=int, default=0, help="Timing noise in cycles")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.demo:
        for m in [100, 500, 1000, 2000, 5000]:
            run_attack(n=512, m=m, noise_cycles=0)
    else:
        run_attack(n=args.n, m=args.traces, noise_cycles=args.noise)

if __name__ == "__main__":
    main()
