# Finding — Impact Decomp β-Sweep

**Date:** 2026-06-04  
**Experiment:** `impact_decomp_beta_sweep_v1`  
**Episodes:** 6,000 (3 modes × 5 β_loyalty cells × 40 agents × 10 episodes)

---

## Extended Analysis

This experiment was designed to sharpen one specific claim from `capped_floor_impact_decomp`
(2026-05-29): that at high β_loyalty, `seed_refresh_capped` over-steers by amplifying
the seed memory's MemoryImpact term and that this translates into a rescue penalty.
The prior experiment observed a 7.5 pt rescue penalty at β_loyalty=0.50 alongside
a 0.113 impact gap — and attributed the penalty to the amplified recall.

The fine sweep confirms the first half and falsifies the second half at N=40.

**What is confirmed:** The impact gap from 0.016 at β_loyalty=0.10 to 0.077 at
β_loyalty=0.50 is clean, monotone, and mechanistically coherent. The `seed_refresh_capped`
mode refreshes the seed memory's stored emotion to its encoding-floor values on
every recall event, which at high β_loyalty means restoring significantly more guilt
charge than the memory has naturally decayed to. This boosts the γ·|emotion| term in
MemoryImpact, increasing the seed's competitive weight in the store's top-1 recall
slot. The threshold where the gap crosses 0.05 — the level where the prior experiment
argued the mechanism "activates" — falls between β_loyalty=0.30 and β_loyalty=0.40,
consistent with the prior endpoint reading.

**What is not confirmed:** The rescue penalty. Across all five β_loyalty cells, the
rescue-rate difference between floor and capped is: −2.5, −7.5, +7.5, −2.5, −2.5 pts
(positive = floor rescues more). This is not a monotone signal; it is white noise around
zero. At N=40 with base rates near 70%, the standard error on a single rescue-rate
estimate is ≈ √(0.7×0.3/40) ≈ 7.2 pts, meaning 2-SE ≈ 14.4 pts on a difference.
None of the five penalty readings exceed that threshold. The 7.5 pt penalty in the
prior experiment's β_loyalty=0.50 cell was almost certainly noise.

**Mechanistic interpretation:** The impact inflation is real, but it does not produce
a detectable behavioral outcome at this sample size. One plausible explanation is that
a higher impact seed is not harmful in isolation — it still needs to be recalled at the
right decision step, and whether the recall fires at the right step versus one step
early or late is dominated by Φ stochasticity and the T_snap horizon. The binary
outcome (rescue vs not) is too coarse to pick up the timing difference that the impact
inflation induces. A finer-grained metric — such as the distribution of decision steps
at which the seed's top-1 recall fires, or the frequency of "premature commitment"
events — might reveal the over-steering even where binary rescue rates do not.

**What would falsify the interpretation:** If a targeted N=200 replication at
β_loyalty=0.30 and β_loyalty=0.40 (the threshold-straddling cells) yields a penalty
inside the ±4 pt 2-SE band, the impact inflation is mechanistically inert and the
source-vs-gate isomorphism is complete. If the penalty emerges at −5 pts or deeper at
those cells, the over-steering story survives and the N=40 signal was suppressed by
variance, not absence.

---

## Follow-up Experiments

1. **`impact_vs_injection_dissociation`** (next in queue) — isolates whether the 7.5 pt
   endpoint penalty from the prior run is injection-mediated (guilt bleed-in) or
   impact-mediated (seed monopolizing top-1). This is now more urgent given the null
   rescue penalty in the interior cells.

2. **`impact_decomp_n200_threshold`** — N=200 replication at β_loyalty ∈ {0.30, 0.40},
   the two threshold-straddling cells. Would definitively settle whether the 0.05 gap
   threshold matters behaviorally or is inert.

3. **`impact_decomp_kappa_sweep`** — Re-run the fine sweep at κ=0.5. At the valley
   shoulder the committed-vs-paralyzed boundary is tighter and the impact penalty may
   become detectable at lower N.

4. **`decision_step_trace`** — Log the step at which the top-1 recall fires in each
   episode. Test whether seed_refresh_capped shifts the modal firing step earlier
   (over-steering) vs seed_only_floor. This is the finer-grained metric needed to
   confirm the impact-timing story without requiring N=200.
