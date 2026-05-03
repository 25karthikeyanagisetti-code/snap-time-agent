# Finding 11 — Signed-threshold encoding fails by exposing a prior-dilution lockout

**Hypothesis.** Asymmetric encoding gates — independent thresholds τ_guilt
and τ_loyalty applied per outcome valence — should sort the population
where a single magnitude threshold cannot. Both prior memory-curation
sweeps (`selective_encoding_v1`, `valenced_encoding_v1`) treated the rescue
and failure channels symmetrically; we expected that combining a *liberal*
loyalty gate with a *stringent* guilt gate (G=0.7, L=0.3) would let
successful rescues dominate the memory store and stabilize a
rescue-disposed population across the chain.

**Sweep.** κ = 1.0, T_snap = 12, severity = 1.0, 100 agents × 10-episode
chains × 4 (τ_g, τ_l) cells over {0.3, 0.7}². Gate variable:
`max(final_emotion)` (the same L_∞ norm used in selective_encoding); the
threshold itself depends on the outcome's valence. 4,000 episodes total.

**Headline.** Both high-τ_guilt cells collapse to **0% rescue rate at
episode 9** (G=0.7, L=0.3 and G=0.7, L=0.7). The best-divergence cell is
the *opposite* of what was predicted — G=0.3, L=0.7 (loyalty-stingy)
yields divergence@ep5–9 of **+5.1 pts** — and even that is worse than the
+11.5 pts produced by the simpler symmetric τ=0.3 sweep in
`selective_encoding_v1`. The hypothesis fails in the opposite direction.

```
   cell           |  enc% | ep0   | ep9    | div@5–9   | n_mem@ep9
  ----------------------------------------------------------------------
   G=0.3, L=0.3   |  98.9 |  74.0 |  14.0  |   −0.9    |   10.9
   G=0.3, L=0.7   |  96.6 |  81.0 |  17.0  |  +5.1     |   10.7
   G=0.7, L=0.3   |  24.8 |  75.0 |   0.0  |  +0.9     |    3.5
   G=0.7, L=0.7   |  23.8 |  80.0 |   0.0  |   −0.3    |    3.4
```

**Mechanism: the prior-dilution lockout.** The encoder's per-outcome
emotion magnitudes are wildly asymmetric, and the signed-threshold scheme
amplifies that asymmetry in a way the hypothesis didn't anticipate.
`PARTNER_RESCUED` ends with `e_max ≈ 0.88` — the rescue path drives
emotion toward saturation. `RESOURCE_TAKEN` (the agent quietly abandons
and grabs the resource) ends with `e_max ≈ 0.10` — a calm exit. `TIMEOUT`
sits in the middle (`e_max ≈ 0.55`). When τ_guilt = 0.7, RESOURCE_TAKEN
is *eliminated* from the store (0/308 encoded at G=0.7, L=0.3) and ~76%
of TIMEOUTs are silenced. With failure events blocked, the seeded
abandonment memory remains the highest-impact memory in the store
indefinitely — its guilt-recall stays at saturation forever, the agent
keeps switching between resource and partner, and the partner deadline
expires every single chain. The architecture flips from "experience drowns
out the prior" to "the prior cannot be drowned out by anything."

This means the signed-threshold scheme has a hidden first-order failure
mode: any τ_guilt above the noise floor of `RESOURCE_TAKEN`'s terminal
emotion (≈ 0.4) creates the lockout. The rescue side, because rescue is
emotionally intense, never has this problem — even τ_loyalty = 0.9 would
encode the bulk of rescues. The two channels are not symmetric across
this gate variable, and choosing them independently exposes the
asymmetry.

**What would falsify this interpretation?** If we *raise* the seeded
prior's preage (so it's weaker at episode start), the high-G lockout
should vanish — the prior is no longer dominant from move one, and even
sparse failure encoding can dilute it to baseline. The queued
`prior_dilution_rate` experiment tests exactly this. If the lockout
*persists* at very high preage, the mechanism story is wrong and we'd
need to look at recall-gain compounding instead.

**Why divergence still rises at G=0.3, L=0.7.** The +5.1 pts of
ep5–9 divergence in this cell is the residue of the Loyalty Boomerang
finding from 2026-05-02. Mildly suppressing rescue-side encoding (here,
~13% of PARTNER_RESCUED events get filtered) lets the seeded prior keep
some teeth, which is enough to preserve a thin trace of behavioral type
information. But the effect is much weaker than the 28% ep9 rescue rate
seen with rescue encoding fully OFF (`valenced_encoding_v1`) — partial
suppression sits in a worse spot than full off.

**Verdict.** The hypothesis as stated is rejected. The Homogenization
Collapse cannot be defeated by per-channel emotion-magnitude thresholds.
The deeper lesson is methodological: the gate variable used by both
selectivity experiments (`max(final_emotion)`) does not correlate with
outcome valence, so any threshold-on-magnitude scheme inherits the
asymmetry between rescue (loud) and failure (often quiet) and produces
unintended biases.

**Follow-up experiments worth running.**

1. `prior_dilution_rate` (already queued) — sweep seeded preage ∈ {0, 5,
   15, 30, 60} at the worst cell (G=0.7, L=0.3) and check whether the 0%
   ep9 rescue rate persists.
2. **Outcome-class boolean gate** — instead of thresholding `e_max`, gate
   directly on the categorical outcome (e.g. encode 100% of rescues but
   only 25% of failures, sampled). Decouples *whether* from *intensity*.
3. **Per-outcome importance modulation** — scale the encoded *importance*
   by category rather than thresholding entry. The store fills uniformly
   but with skewed weights, so reactivation should differ.
4. **Joint filter on outcome × intensity** — encode IF (outcome is rescue)
   OR (outcome is failure AND e_max > τ). Cleanest test of the asymmetric
   intuition without the magnitude proxy bug.
