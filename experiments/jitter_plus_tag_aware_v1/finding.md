# Finding: jitter_plus_tag_aware

**Date:** 2026-06-15
**Status:** PARTIAL — capacity prediction exceeded, divergence prediction refuted.

## Hypothesis
Combining encoding-diversity jitter (σ=0.40, verified at κ=2.0 to produce
88.8% unipolar rescuer typing) with tag-aware recall (verified to restore
divergence@5–9 under asymmetric β_guilt=0.30 laundering) in a 2×2 at
κ=1.0, N=200/cell, 20 chained episodes, would push divergence@5–9 past
+15pts — bipolar behavioral types (distinct rescuer AND failure
identities from early experience).

## Result
- Divergence@5–9: off_off −2.0, off_on +3.6, on_off −1.9, on_on +3.6pts.
  ON/ON does NOT exceed +15pts — identical to tag-aware-alone. **Bipolar
  typing prediction REFUTED.**
- Behavioral-failure rate (≤4/20): 72.0% → 14.0% (tag-aware) → 53.5%
  (jitter) → **7.5%** (both). 9.6× reduction vs legacy, largest in the
  project.
- Sustained rescue rate (ep5–9): 15.8% → 30.7% (tag-aware) → 21.5%
  (jitter) → **37.6%** (both) — close to additive (predicted 36.4%,
  observed 37.6%, within 1.2pts).
- ep15–19 = 38.5% (both), essentially flat vs ep5–9 — most stable high
  plateau measured at κ=1.0.

## Headline numbers
- Failure rate: 72.0% (legacy) → 7.5% (both), 9.6× reduction.
- Sustained rescue rate: 15.8% → 37.6% (ep5–9), 2.4×, near-additive
  (36.4% predicted).
- Divergence@5–9 ceiling: +3.6pts (both jitter and tag-aware alone reach
  this independently; combination adds nothing).

## Files
- `experiments/jitter_plus_tag_aware_v1/{README.md, results.csv, jitter_plus_tag_aware.png, finding.md}`

## Follow-ups added to backlog
- `bipolar_typing_kappa_sweep` — repeat 2×2 at κ ∈ {0.5, 2.0, 4.0}.
- `jitter_plus_tag_aware_n400` — N=400 replication of ON/ON vs OFF/ON gap
  (6.5pts, near the 2-SE noise floor).
- `additive_decomposition_other_pairs` — test additivity with other
  mechanism pairs (e.g. tag-aware recall + softmax temperature fix).
