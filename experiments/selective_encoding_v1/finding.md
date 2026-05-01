# Finding 9 — Selective encoding does not save the population (hypothesis failed, with a twist)

**Hypothesis.** Only encoding HIGH-MAGNITUDE emotional outcomes prevents the
Homogenization Collapse. We expected that gating the outcome-encoder on
terminal emotion would let early luck (a successful ep0 rescue) propagate
into stable behavioral types across the chain.

**Sweep.** κ = 1.0, T_snap = 12, severity = 1.0, 100 agents × 10-episode
chains × 5 thresholds τ ∈ {0.0, 0.3, 0.5, 0.7, 0.9}. Gate variable:
`max(final_emotion)` (L_∞ norm, bounded in [0, 1]). 5,000 episodes total.

**Headline:** max divergence-index at episode 9 = **11.5 pts at τ = 0.3**,
versus 0.8 pts at τ = 0.0 (baseline always-encode). At every threshold τ ≥
0.5, divergence collapses to **0.0 pts**. The Homogenization Collapse is
not avoided.

```
   tau |  enc% | rescue@ep0 | rescue@ep9 | div@ep9
  ----------------------------------------------------
  0.00 | 100.0 |       73.0 |        8.0 |     0.8
  0.30 |  98.6 |       82.0 |       15.0 |    11.5
  0.50 |  37.7 |       86.0 |        0.0 |     0.0
  0.70 |  23.1 |       80.0 |        0.0 |     0.0
  0.90 |  18.6 |       78.0 |        0.0 |     0.0
```

**The unexpected pattern: a U-shape in homogenization.** Too little
selectivity (τ = 0.0) homogenizes by *flooding* — the memory store fills
with mostly-failure outcomes regardless of what happened in episode 0.
*Too much* selectivity (τ ≥ 0.5) homogenizes by *prior-dominance* — when
fresh outcomes rarely earn the right to be encoded, the seeded abandonment
memory's influence is never diluted, and every agent converges to
chronic-failure behavior dictated by the prior alone. Only mild gating
(τ = 0.3) leaves a thin window where ep0-rescuers retain a measurable edge
over ep0-non-rescuers nine episodes later, and even there the population
rescue rate has dropped from 82% to 15%.

**Why selectivity-on-magnitude doesn't sort outcomes.** At κ = 1.0, both
rescue and failure trajectories drive emotion magnitude near saturation
(`e_max` is at or near 1.0 in both groups), so a threshold on `max(e)` is
*not* a threshold on outcome valence — it is a threshold on overall
intensity, which both regret-laden failures and gratitude-laden rescues
clear. The gate filters by *whether anything happened*, not by *what
happened*.

**What this points at next.** A *valenced* gate — encode loyalty memories
on rescue but require a higher bar to encode guilt memories on failure
(or vice versa) — should sort the population in a way magnitude cannot.
That is exactly the next item on the queued backlog (`valenced_encoding`),
and this finding strengthens the case for testing it: the failure mode of
selectivity is signed, not scalar.

**Verdict:** the hypothesis as stated does not hold. Selective encoding
on magnitude alone trades one homogenization mechanism (flooding) for
another (prior-dominance). The Homogenization Collapse is robust to this
intervention.
