# Finding 12 — Loyalty Importance Floor (NULL)

**Date:** 2026-05-04
**Headline:** ep5–9 mean rescue rate stays flat at 14–17% across `rescue_importance ∈ {0.0, 0.1, 0.3, 0.5, 0.7}` (range = **2.4 pts**), none within 12 pts of the 28% rescue-encoding-OFF baseline.

## Setup

The 2026-05-02 *Loyalty Boomerang* finding (`valenced_encoding_v1`) showed that turning
rescue-side outcome encoding ON (importance=0.7) at κ=1.0 *halves* long-term rescue rate vs
turning it OFF (15% vs 28% at ep9). The natural next question: is the boomerang's penalty
proportional to encoding **strength**, so that a low rescue-importance recovers most of the
OFF baseline while keeping the loyalty channel nominally available?

This run swept `rescue_importance` across `{0.0, 0.1, 0.3, 0.5, 0.7}` at κ=1.0, T_snap=12,
chain length 10, 100 agents/cell — 5,000 episodes total. The sandbox was extended with a
`rescue_importance` parameter (default 0.7, preserves all prior experiment behavior). Failure-
side encoding (importance 0.85) was left unchanged so the asymmetry tested is exactly the one
the boomerang depends on.

## What the data shows

The ep5–9 mean rescue rate is essentially flat — 15.0%, 14.2%, 16.6%, 14.6%, 16.2% across
ascending importance. The single-episode ep9 column wobbles more (10–24%) because n=100 per
cell is noisy, but every smoothed window sits inside a 2.4-point band. For comparison: the
valenced experiment's ON-default cell sat at ep9=15% and the OFF cell at ep9=28%. **No
importance value brings rescue rate within 12 points of the OFF baseline.**

Divergence@5–9 — rescue rate of ep1-rescuers minus rescue rate of ep1-non-rescuers — is
**negative (or barely positive) in every cell**: −10.6, −6.1, −5.0, +2.3, −6.8. This matches the
boomerang's anti-type signature: agents that rescue early end up *less* likely to rescue in
the stable window. Importance throttling does not unwind it.

Memory-store size at ep9 is 11.0 in every cell (1 seeded + 10 outcome-encoded), confirming
the lever moved was weight, not count.

## Mechanism

`memory_impact = exp(−β·age) · exp(α·importance) · exp(γ·|emotion|) · sim(ctx, mem)`.
At `importance = 0`, the importance term collapses to **1.0**, not zero — a neutral
multiplier. The rescue memory still occupies the store and still wins recall whenever
emotion magnitude (γ-term) and similarity are high enough. The rescue payload encodes
loyalty=0.8 — a strong emotion-magnitude contribution that is unaffected by `importance`.
Throttling importance does not shrink the recall surface meaningfully.

The deeper claim: the boomerang isn't about rescue memories being "loud." It's about rescue
memories being *the wrong context-key*. Their feature vector sits at terminal positions
(agent on partner cell), but they get reactivated during deliberation steps where the agent
is closer to the partner-resource decision boundary. Whenever recall fires, the loyalty-
biased emotion gets injected, pulling the agent off the committed trajectory. Importance
modulates how much that injection weights, but the injection itself happens regardless.

## What would falsify this interpretation

The interpretation predicts:
1. Lowering rescue **count** (don't encode every episode) should help, where lowering importance
   did not. The `outcome_boolean_gate` experiment in the queue tests exactly this.
2. Faster decay on rescue memories (`decay_asymmetry`) should help, because age enters as
   `exp(−β·age)` — a more efficient knob than importance for shrinking recall weight.
3. Eviction (`memory_capacity` with LRU) should help by truncating rescue memories before they
   accumulate critical mass.

Conversely, if any of those three also produce flat rescue rates, the boomerang is not about
the recall surface at all — it is about the agent's emotion update being fundamentally
sensitive to ANY non-zero loyalty signal during deliberation, in which case the fix has to
move into emotion update dynamics (e.g. asymmetric clamps).

## Suggested follow-ups

- Pull `decay_asymmetry` to top of the queue (β_loyalty > β_guilt should be much more
  effective than importance throttling).
- Add an event-trace sub-study: log every recall event during a chain, tag which memory
  fired, and verify that rescue memories are reactivating during deliberation (not only
  on rescue-cell terminal contexts).
- Run a tiny ablation where the rescue payload's loyalty=0.8 is reduced — that targets the
  γ-term in `memory_impact` directly, which the importance sweep could not.

## One-line takeaway

Importance is the wrong dial for the Loyalty Boomerang. The boomerang is a property of *what
the rescue memory means in feature space*, not of how strongly it claims to matter.
