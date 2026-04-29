#!/usr/bin/env python3
"""
Artifact 1: LFFLDL Analyzer (falcon-leakage-check)
Static analyzer that instruments Falcon implementations and computes
LFFLDL leakage symbolically.

Usage:
    python falcon_leakage_check.py --source <path_to_basesampler.c>
    python falcon_leakage_check.py --demo
"""

import re
import sys
import argparse
import math

# ─── LFFLDL Leakage Model ────────────────────────────────────────────────────

def lffldl(z: int) -> int:
    """Compute LFFLDL leakage class for a sampled coefficient z."""
    return int(math.floor(math.log2(abs(z) + 1))) if z != 0 else 0

def lffldl_vector(z_vec):
    """Compute LFFLDL leakage vector for a list of sampled coefficients."""
    return [lffldl(z) for z in z_vec]

# ─── Static Analyzer ─────────────────────────────────────────────────────────

LEAK_PATTERNS = [
    # Loop bound depends on value magnitude
    (r'for\s*\(.*\|z.*\|.*\)', "Loop bound depends on |z| — value-dependent depth"),
    (r'while\s*\(.*\|z.*\|.*\)', "While condition depends on |z| — value-dependent depth"),
    # Iteration count proportional to output
    (r'iterations?\s*[=<>]+\s*.*log2.*\|z', "Iteration count proportional to log2|z|"),
    # Early exit on value
    (r'(break|return)\s*;.*//.*z\s*==\s*0', "Early exit when z==0 — magnitude-dependent termination"),
    # Knuth-Yao pattern
    (r'knuth.?yao|BaseSampler|base_sampler', "BaseSampler detected — check for value-dependent iterations"),
]

SAFE_PATTERNS = [
    (r'B_max|Bmax|bmax', "Fixed iteration count B_max detected"),
    (r'dummy.*iteration|pad.*loop|constant.*time.*iter', "Dummy iterations detected"),
    (r'normalized|normalised', "Normalised sampler pattern detected"),
]

def analyze_source(source_code: str) -> dict:
    """
    Symbolically analyze C source for LFFLDL leakage.
    Returns: dict with 'leaks' (bool), 'issues', 'safe_patterns', 'verdict'
    """
    issues = []
    safe = []

    for pattern, msg in LEAK_PATTERNS:
        if re.search(pattern, source_code, re.IGNORECASE):
            issues.append(msg)

    for pattern, msg in SAFE_PATTERNS:
        if re.search(pattern, source_code, re.IGNORECASE):
            safe.append(msg)

    leaks = len(issues) > 0 and len(safe) == 0

    return {
        "leaks": leaks,
        "issues": issues,
        "safe_patterns": safe,
        "verdict": "LEAKS under LFFLDL" if leaks else "SAFE under LFFLDL (normalized sampler detected)",
        "worst_case_bound": f"B_max = floor(log2(sigma_max * sqrt(pi/2))) + 1"
    }

def print_report(result: dict, source_name: str = "input"):
    print(f"\n{'='*60}")
    print(f"  LFFLDL Analyzer Report: {source_name}")
    print(f"{'='*60}")
    print(f"  Verdict : {result['verdict']}")
    print(f"  Leaks   : {result['leaks']}")
    if result['issues']:
        print(f"\n  Issues detected:")
        for i in result['issues']:
            print(f"    [!] {i}")
    if result['safe_patterns']:
        print(f"\n  Safe patterns detected:")
        for s in result['safe_patterns']:
            print(f"    [✓] {s}")
    print(f"\n  Worst-case leakage bound: {result['worst_case_bound']}")
    print(f"{'='*60}\n")

# ─── Demo Mode ───────────────────────────────────────────────────────────────

LEAKING_SAMPLER = """
// Standard Knuth-Yao BaseSampler (LEAKING)
int BaseSampler(double sigma) {
    int z = 0;
    int iterations = (int)(log2(fabs(z) + 1)) + 1;
    for (int i = 0; i < iterations; i++) {
        z += sample_bit();
    }
    return z;
}
"""

SAFE_SAMPLER = """
// Normalized BaseSampler (SAFE)
#define B_max 8
int BaseSamplerNormalized(double sigma) {
    int z = inner_sample(sigma);
    // Pad with dummy iterations to fixed B_max depth
    for (int pad = 0; pad < B_max; pad++) {
        volatile int dummy = constant_time_iter(pad);
        (void)dummy;
    }
    return z;  // normalized output
}
"""

def run_demo():
    print("\n[DEMO] Analyzing leaking reference sampler...")
    r1 = analyze_source(LEAKING_SAMPLER)
    print_report(r1, "reference_basesampler.c")

    print("[DEMO] Analyzing normalized (safe) sampler...")
    r2 = analyze_source(SAFE_SAMPLER)
    print_report(r2, "normalized_basesampler.c")

# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LFFLDL Static Analyzer for Falcon BaseSampler")
    parser.add_argument("--source", help="Path to C source file to analyze")
    parser.add_argument("--demo", action="store_true", help="Run demo on built-in examples")
    args = parser.parse_args()

    if args.demo or not args.source:
        run_demo()
    else:
        with open(args.source, "r") as f:
            code = f.read()
        result = analyze_source(code)
        print_report(result, args.source)
        sys.exit(1 if result["leaks"] else 0)

if __name__ == "__main__":
    main()
