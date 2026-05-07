# Finding — Memory Laundering under asymmetric forgiveness

**Run:** `memory_population_audit_v1` · 2026-05-07 · 4,000 episodes · 6,800 memory snapshot rows
**Context:** instrumentation pass over the four cells from `decay_asymmetry_reversed_v1`
**Headline:** **78% of failure-tagged memories at β_guilt=0.15 have stored loyalty > stored guilt at end of episode 4 (vs 0% in the symmetric β=0.05 cell)**

## Background and the gap this run closes

Two prior sweeps showed divergence@5–9 collapse under asymmetric `mem_emotion_decay`. Neither sweep DIRECTLY measured the M store, so the explanation for the divergence-erosion was inferred from outcomes alone. `findings_v3` proposed a "loyalty-cushion vs guilt-counterweight" reading; the 2026-05-06 reversed sweep falsified the directional component of that reading and replaced it with a more general "imbalance erases differentiation" framing. That framing was correct but vague: it didn't say WHERE in the framework imbalance was being applied. The γ·|emotion| factor in MemoryImpact is the only place where stored emotion magnitudes affect anything downstream of encoding, so a snapshot of M is the right instrument to localize the mechanism.

## What the snapshot shows

Per-agent total stored guilt channel (Σ over all memories in M at end-of-ep4):
| β_guilt | Σ guilt /agent | Σ loyalty /agent | G/L |
|---:|---:|---:|---:|
| 0.05 | 0.95 | 0.99 | 0.97 |
| 0.15 | 0.53 | 1.06 | 0.50 |
| 0.30 | 0.48 | 1.08 | 0.44 |
| 0.50 | 0.48 | 0.97 | 0.50 |

The guilt-channel total drops ~50% from the symmetric to the asymmetric regime, then plateaus. Loyalty stays flat. So the per-channel weight asymmetry HAS shifted, as the prior reading predicted — but only by a factor of ~2 in the channel sum, which is too gentle to drive a 32-pt divergence swing on its own.

The sharper finding is in the **per-memory class flip**. Each failure-tagged memory was encoded with `(guilt=0.85, loyalty=0.5)`. Under the per-dim decay, after ~60 steps:
- Cell 0.05 (symmetric): guilt → 0.85·0.95⁶⁰ ≈ 0.039; loyalty → 0.5·0.95⁶⁰ ≈ 0.023. Ratio preserved at 1.7×. **Class identity preserved: 100% still classify as guilt-dominant.**
- Cell 0.15: guilt → 0.85·0.85⁶⁰ ≈ 5×10⁻⁵; loyalty → 0.5·0.95⁶⁰ ≈ 0.023. Ratio inverts to 1:460. **78% of failure memories now classify as loyalty-dominant at recall.**
- Cell 0.30 / 0.50: guilt is negligible across the board; the class flip rate plateaus around 75–78%.

The reason the rate plateaus at ~78% rather than reaching 100% is that some failure memories were encoded only a few steps before the ep4 snapshot (most recent episode); those still have non-negligible guilt because decay hasn't compounded long enough. The plateau is about the age distribution of failure memories within the rolling window, not a saturation in the laundering mechanism itself.

This is what "imbalance erases differentiation" actually means at the substrate level. The agent's M store still holds the COUNT of past failures. What it loses is the EMOTIONAL FINGERPRINT that distinguishes a failure memory from a rescue memory at recall time. From the recall machinery's point of view (γ·|emotion| · sim(ctx,mem)), three out of four failures now look like rescues.

## Why this is the mechanism

A previously-published model of why divergence@5–9 should exist: ep1-non-rescuers encode a guilt-charged failure memory that pulls them toward the partner in subsequent episodes (via guilt_recall feeding the emotion update), and ep1-rescuers encode a loyalty-charged rescue memory that does the same thing through a different channel. The two sub-populations diverge because their per-step recalled emotion differs as a function of which class of memories dominates their store.

In the symmetric β=0.05 cell, that mechanism intact: the two classes maintain distinct stored emotion profiles. Divergence is positive (~+10 pts).

In the asymmetric β_guilt cell, three out of four ep1-non-rescuer-encoded memories no longer carry their guilt distinction. To recall, they look like rescue memories — small loyalty channel, near-zero guilt. So the ep1-non-rescuer subpopulation gets pulled by recall the same way the ep1-rescuer subpopulation does. Divergence approaches zero: not because either subpopulation changed behavior, but because their memory stores have become indistinguishable in the variable that matters for recall.

This also predicts something new: the laundering effect should be largely independent of κ. The κ knob scales how much emotion matters in Φ; it does not affect the stored emotion channel itself. The laundering rate at κ=0.5 should be the same ~78%, even though the macro divergence may be smaller because emotion has less weight in the action choice. The queued `decay_asymmetry_lower_kappa` experiment is a direct test of that prediction.

## What would falsify this interpretation

A clean falsifier would be: re-running `recall_event_trace` (queued) and finding that during deliberation in the asymmetric cells, the modal recall is still a guilt-charged memory (the seeded prior is the obvious candidate, since its guilt is small but not zero, and there is exactly one of it in the store). If the seeded prior is doing all the recall work, then the agent-encoded failure memories' class flip might not matter; the divergence-erosion would have to come from somewhere else.

A weaker but interesting falsifier: if the laundering rate at β_guilt=0.15 turns out to be highly sensitive to seed (e.g. ranges from 50–95% across rng seeds), then the +10.6 → −1.5 divergence pattern in the prior sweep cannot be cleanly attributed to laundering. Worth a 5-seed bootstrap follow-up.

Magnitude-comparison falsifier: the per-channel TOTAL guilt drops from 0.95 to 0.48 (factor ~2). But the per-failure-memory class flip is 0% to 78% (a much bigger qualitative change). If we ablate the classification effect by forcing failure memories to retain their class label even when channel ordering flips (e.g. tag-aware recall), divergence should NOT erode. That's a clean intervention experiment that should be added to the backlog.

## Follow-up experiments worth queuing

- `laundering_kappa_invariance` — repeat this audit at κ=0.5 (the "shoulder" of the boomerang). Predicts laundering rate ~78% at β_guilt=0.15 even if macro divergence is muted.
- `tag_aware_recall` — add a recall mode where memory class is determined by the encoded valence at write time rather than current stored channels. If divergence persists under this recall, laundering is the mechanism.
- `laundering_inflection` — fine sweep β_guilt ∈ {0.05, 0.07, 0.09, 0.11, 0.13, 0.15} to find the threshold where laundering switches on. Should be near β_guilt = β_loyalty + small ε once the age horizon dominates.
- `recharge_on_recall` — add a small `+= δ` injection to stored emotion every time a memory is reactivated above threshold. If this prevents laundering AND preserves divergence, we have a counter-mechanism.

## Notes for posterity

The chart's bottom panel collapses to a single number per cell: % of failure-tagged memories at end-of-ep4 with stored loyalty > stored guilt. That number is the cleanest statement of the mechanism in the entire findings stack to date — it is more concrete than "imbalance erases differentiation" and more general than "loyalty cushion vs guilt counterweight." Worth promoting to the README hero chart for `decay_asymmetry_reversed` if the writeup gets re-edited.
