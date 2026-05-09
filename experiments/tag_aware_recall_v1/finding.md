# Finding — Tag-Aware Recall (Wave 4 cont.)

**Date:** 2026-05-09
**Hypothesis:** Pinning a memory's class identity to its encoding-time tag
(rather than its current decayed `stored.guilt > 0.4` state) restores the
committed-rescue regime under asymmetric forgiveness.
**Result:** **HELD** — strong, monotone uplift at every β_guilt cell.

## Headline

| β_guilt | LEGACY ep5–9 | TAG-AW ep5–9 | Δ           | LEGACY ep0 | TAG-AW ep0 | Δ          |
|--------:|-------------:|-------------:|------------:|-----------:|-----------:|-----------:|
| 0.05    | 21.2%        | 43.6%        | +22.4 pts   | 80%        | 78%        | -2 pts     |
| 0.15    | 20.0%        | 35.2%        | +15.2 pts   | 80%        | 70%        | -10 pts    |
| 0.30    | 11.2%        | 29.2%        | +18.0 pts   | **48%**    | **76%**    | **+28 pts** |
| 0.50    | 10.8%        | 28.8%        | +18.0 pts   | 52%        | 58%        | +6 pts     |

Two clean macro effects:

1. **Long-run rescue (ep5–9 mean) approximately doubles at every β_guilt
   cell.** Tag-aware recall keeps the guilt-recall pathway alive even when
   stored guilt has decayed past the legacy threshold.
2. **The β_guilt=0.30 regime-break vanishes.** Under legacy recall, ep0
   rescue drops 80% → 48% as β_guilt grows from 0.15 → 0.30 — the seeded
   prior's stored guilt decays past 0.4 within the first half of episode 0
   and the agent loses commitment to the partner. Under tag-aware recall,
   the seeded prior keeps counting as guilt-class throughout the episode
   and ep0 stays at 76%.

## Mechanism (why this happens)

The legacy `guilt_recall_strength` does:
```python
if m["emotion"]["guilt"] > 0.4: ...
```
This is a **current-state** classification. At β_guilt=0.30 per step, a
seeded memory with stored.guilt=0.9 reaches stored.guilt ≈ 0.15 after 5
steps (0.9 × (1-0.30)^5 = 0.151) — below the 0.4 threshold. The memory
still exists, still has a context-similarity match, still has age-decay,
but it no longer fires the guilt-recall gate that drives the
`GUILT_RATE × guilt_recall` term in `step_emotion`. The agent's emotional
pressure to rescue the partner evaporates within the first half of the
episode it most needs it.

Tag-aware recall classifies by ORIGIN. The seed memory is tagged `seed`,
failure outcomes are tagged `failure`, timeouts `timeout` — these are
permanently guilt-class regardless of how the stored channels evolve. The
guilt-recall pathway stays alive across the chain.

The ep5–9 uplift is proportional to how much of the guilt-class signal was
being lost to laundering under legacy:
- Symmetric β=0.05: little laundering, but the legacy threshold (0.4) is
  still strict enough that aged guilt memories age below it after ~12-18
  steps even at low β. Tag-aware recall captures these.
- β_guilt=0.30 / 0.50: almost all stored guilt is laundered out within an
  episode. Tag-aware recall recovers the entire signal.

## Why divergence@5–9 is muted in this run

This experiment used n=50 agents/cell (vs n=100 in the audit) to keep the
total under the 5,000-episode cap while running BOTH modes side-by-side.
The divergence@5–9 metric (ep5–9 mean rescue if ep0 rescued − if ep0 failed)
has high variance at n=50 because the "ep0 failed" subgroup can be small
(10–25 agents). The macro statistics (ep0, ep5–9 mean) are very stable;
the per-agent split is noisy. The published symmetric-β baseline of
+10–13 pts is replicated here as +9.3 pts in the tag-aware symmetric cell.

## Falsifiers

What would falsify the laundering interpretation:

- **Tag-aware recall produces the SAME ep5–9 trajectory as legacy.** Then
  the divergence-erosion in decay_asymmetry_reversed is NOT mediated by
  the guilt-recall gate at all; it must be carried by another channel
  (e.g. `inject_recalled_emotion`'s use of literal stored channels, or
  recall-event timing during deliberation). This run rules that out.
- **Tag-aware recall fully restores ep0 rescue at all β_guilt.** Would
  imply a single mechanism. The β_guilt=0.50 ep0 rate stays at 58% (vs
  78% symmetric baseline), suggesting a SECOND mechanism is in play at
  extreme decay — likely the injection pathway, since
  `inject_recalled_emotion` still bleeds in literal decayed stored
  channels even when the recall gate is tag-aware.

## Follow-up experiments

1. **`tag_aware_injection`** — extend the tag-aware approach to
   `inject_recalled_emotion`: when injecting a memory whose tag is
   guilt-class, use a *floor*-corrected emotion vector (max(stored,
   floor_template)) instead of the literal decayed stored emotion. Tests
   whether the residual β_guilt=0.50 ep0 collapse is closed by this.
2. **`recharge_on_recall`** — already on the queue. Per the
   2026-05-08 promotion note, this is the
   biologically-plausible alternative: every reactivation above
   threshold tops up stored emotion by δ. Should produce a similar
   uplift to tag-aware recall but via a stored-state mechanism rather
   than a tag-keyed gate.
3. **`tag_aware_recall_kappa`** — replicate this run at κ ∈ {0.5, 2.0}
   to test whether the uplift is regime-coupled or generic. Predicts
   regime-coupled: at κ=0.5 the boomerang regime can't sustain rescue
   at all (ep1 collapses to 0% in audit), so the uplift should be
   smaller; at κ=2.0 the agent is already saturated-committed, uplift
   should be bounded.
4. **`laundering_inflection`** (already in queue, can be tightened): now
   that we have a counter-mechanism, the fine β_guilt sweep can be done
   in the tag-aware mode to find the exact β where the second mechanism
   (injection) starts to dominate.

## What this means for the framework

Memory class identity that depends on the decayed-state of stored emotion
is brittle to forgiveness asymmetries. Pinning identity to encoding-time
tags is one fix; a per-channel floor in the decay operator
(`stored.guilt = max(decayed, floor)` for guilt-tagged memories) would be
another. Either way, the result says: **emotional content is not the same
as emotional identity** — the framework needs both to support stable
behavioral types over chained experience.
