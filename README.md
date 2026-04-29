# Arithmetic-Depth Leakage in Falcon — Code Artifacts

**Paper:** "Arithmetic-Depth Leakage in Falcon: Beyond Constant-Time and Key Recovery Attacks"  
**Venue:** CCS '26, The Hague, The Netherlands

---

## Repository Structure

```
├── README.md                        ← this file
├── paper_netherlands.tex            ← full LaTeX paper source
├── fig1_leakage_dist.png            ← Figure 1: LFFLDL distribution
├── fig2_power_trace.png             ← Figure 2: Simulated power trace
├── fig3_key_recovery.png            ← Figure 3: Estimation error vs traces
├── fig4_hoeffding.png               ← Figure 4: Hoeffding union bound
├── fig5_ml_accuracy.png             ← Figure 5: ML classifier accuracy
├── falcon_leakage_check.py          ← Artifact 1: LFFLDL static analyzer
├── falcon_attack.py                 ← Artifact 2: Key recovery attack (Alg. 1)
├── falcon_traces.py                 ← Artifact 3: Trace generator
└── falcon_normalized_sampler.py     ← Artifact 4: Normalized BaseSampler
```

---

## Requirements

```bash
pip install numpy matplotlib scikit-learn
```

---

## Usage

### Artifact 1 — LFFLDL Static Analyzer
Checks whether a Falcon BaseSampler implementation leaks under LFFLDL.
```bash
python falcon_leakage_check.py --demo
python falcon_leakage_check.py --source path/to/basesampler.c
```

### Artifact 2 — Key Recovery Attack (Algorithm 1)
Runs the full LFFLDL-based key recovery attack.
```bash
python falcon_attack.py --demo                        # all trace counts
python falcon_attack.py --n 512 --traces 5000
python falcon_attack.py --n 512 --traces 5000 --noise 10
```

### Artifact 3 — Trace Generator
Generates synthetic LFFLDL traces matching Falcon-512 hardware distribution.
```bash
python falcon_traces.py --demo
python falcon_traces.py --n 512 --m 5000 --output traces.npy
```

### Artifact 4 — Normalized BaseSampler
Reference implementation of the countermeasure (Theorem 7), with benchmark.
```bash
python falcon_normalized_sampler.py --demo
python falcon_normalized_sampler.py --benchmark --n 512
```

---

## Compiling the Paper

Place all PNG figures in the same folder as `paper_netherlands.tex`, then:

```bash
pdflatex paper_netherlands.tex
pdflatex paper_netherlands.tex   # run twice for references
```

Or upload everything to [Overleaf](https://overleaf.com) and click Compile.

---

## Results Summary

| Artifact | Theorem proved | Key result |
|----------|---------------|------------|
| Analyzer | Theorem 4 | CT Falcon leaks under LFFLDL |
| Attack   | Theorem 5 | Key recovery in O(n² log q) traces |
| Traces   | §7 empirical | 61.1% ML classifier accuracy |
| Norm. Sampler | Theorem 7 | +34% overhead, provably safe |
