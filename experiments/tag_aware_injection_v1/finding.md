# Tag-Aware Injection — Finding (long form)

## Headline

Tag-keyed floors on the `inject_recalled_emotion` pathway do **not** close the
residual β_guilt=0.50 ep0 collapse left over by the 2026-05-09
`tag_aware_recall` fix. At β_guilt=0.50 the INJ-ON cell shows ep0 rescue
66% vs INJ-OFF 68% (Δ = −2.0 pts, well inside the ~10-pt 2-sample SE at
N=50). The hypothesis fails in the specific question it was designed to
answer. A subsidiary effect emerges in an unexpected place: at the
**symmetric** β_guilt=0.05 cell, ep0 rescue rises +20.0 pts (60% → 80%).
The floor is real — but it is not fixing what we thought it would fix.

## Setup

Two arms with identical decay structure (`β_loyalty=0.05`,
`β_guilt ∈ {0.05, 0.15, 0.30, 0.50}`) and identical agent seeds
(`seed_base=78000`), κ=1.0, T_snap=12, chain_length=10, N=50 agents/cell.

- **Arm A (control, INJ-OFF):** `tag_aware_recall=True`,
  `tag_aware_injection=False`. Reproduces the 2026-05-09 protocol exactly.
- **Arm B (treatment, INJ-ON):** both `tag_aware_recall=True` AND
  `tag_aware_injection=True`. Floors are matched to the seeded prior /
  outcome-encoding magnitudes (seed: guilt=0.6, loyalty=0.4; failure:
  guilt=0.6, loyalty=0.5; rescue: guilt=0.0, loyalty=0.6; timeout: guilt=0.3,
  loyalty=0.3).

## What the data shows

The Δep0 vector across β_guilt is **{+20.0, +8.0, +14.0, −2.0}** pts. Read
left-to-right this is monotonically *decreasing* in β_guilt — the exact
opposite of what the laundering hypothesis predicts. If the floor were
specifically rescuing laundered failure memories, the biggest effect should
appear at the highest β_guilt where laundering is most aggressive (78%+ of
failure memories had stored.loyalty > stored.guilt at end-of-ep4 in the
2026-05-07 audit). Instead the biggest effect appears at β_guilt=0.05
where, by definition, no laundering is happening (symmetric mild decay).

The Δep5-9 vector is **{−1.2, +4.8, +1.6, +3.6}** pts — all inside
sampling noise at N=50. The long-run committed-rescuer regime is
indistinguishable across arms.

## Mechanism interpretation

The injection pathway in `sandbox.run_episode` looks like:

```
scored = memory.recall(M, ctx_features, top_k=1)
if scored and scored[0][1] >= REACTIVATION_THRESHOLD:
    e = inject_recalled_emotion(e, scored[0][0]["emotion"], gain=0.15)
```

So injection bleeds from the **single highest-impact memory** at each step.
Three properties of that pathway determine where the floor will and won't
fire:

1. **Importance dominance.** The seeded prior has importance=0.9 (set in
   `_seed_abandonment_memory`); failure memories encoded at episode-end
   carry importance=0.85; rescue memories carry rescue_importance=0.7. With
   `MEM_ALPHA=0.40`, the seed has a `exp(0.4·0.9)=1.43` importance multiplier
   vs `exp(0.4·0.85)=1.41` and `exp(0.4·0.7)=1.32`. Small but non-trivial.
2. **Context geometry.** The seed's features include
   `is_abandonment_event=1` and `agent_pos=RESOURCE_START`. Failure memories
   encoded at terminal states (RESOURCE_TAKEN, PARTNER_DEAD) live in
   different feature regions. The seed gets reactivated when the agent
   passes near (0,0)-quadrant cells; failure memories when the agent revisits
   the terminal endpoints.
3. **Aging vs decay.** At symmetric β=0.05 the seed's stored.guilt decays
   to ~5% of original by ep5. The floor restores it to 0.6. Under
   asymmetric β_guilt=0.50 the failure memories *encoded since ep0* also
   decay rapidly — but those are only top-1 recalls in a narrow band of
   contexts, not during the early-ep0 deliberation steps when the agent
   first heads partner-ward.

So the floor's mechanism is "**anti-aging on the seeded prior**" — it
restores the seed's eroded guilt charge into the agent's e_t during early
deliberation steps. This helps ep0 most at β_guilt=0.05 because that's the
cell where (a) the seed is still aging, AND (b) the GUILT_RATE channel is
not being aggressively counteracted by anything else. At β_guilt=0.50 the
seed itself loses out — the recall top-1 may have shifted to a rescue
memory (which has loyalty floor=0.6, guilt floor=0.0, contributing the
wrong sign to drive partner-ward motion).

## What would falsify this interpretation

- **Per-step recall-event traces:** log which memory wins top-1 at each
  step of ep0 across the four cells × both arms. If the seed is the top-1
  >80% of the time across all cells under INJ-OFF and >80% under INJ-ON,
  the "recall-event statistics shift at high β_guilt" story is wrong.
- **Seed-only floor ablation:** set the floor template to `{}` for
  `failure`, `rescue`, `timeout` tags but keep it active for `seed`. If the
  pattern of deltas {+20, +8, +14, −2} pts is preserved, the seed is doing
  all the work and the per-class floors for outcome-encoded memories are
  inert.
- **Floor magnitude ablation:** sweep the guilt floor magnitude for the
  seed tag ∈ {0.0, 0.2, 0.4, 0.6, 0.8} at β=0.05 only. If the +20 pts
  monotonically increases with seed-floor magnitude, the seed-aging
  mechanism is confirmed.

## Why the residual β_guilt=0.50 ep0 collapse persists

Most likely candidates, in order of plausibility given today's data:

1. **Recall-event statistics drift.** Once the chain has run for 5+
   episodes and rescue memories have accumulated in the store, the top-1
   recall during ep0 deliberation may shift away from the seed toward a
   rescue memory at the partner-adjacent context (whose features include
   `partner_alive=False`). This would route the injection through a
   loyalty-floor template, which actively *opposes* partner-motivated
   conflict because loyalty injection makes the agent feel rewarded for
   the partner-adjacency it already enjoyed in past rescues.
2. **Agent-side decay arithmetic.** `step_emotion` applies a flat
   homeostatic decay of 0.04 each step. At GUILT_RATE=0.12 a guilt_recall
   signal of 0.4 yields a per-step net change of +0.048 − 0.04 = +0.008.
   At β_guilt=0.50 the stored emotion that the recall-strength function
   reads decays so fast that guilt_recall itself dips, dropping below
   net-zero contribution within ~3 steps. Tag-aware recall fixes the
   "below-threshold" classifier flip but doesn't restore signal magnitude
   on the **stored** channels, which is what `guilt_recall_strength_tag_aware`
   still depends on for the *recall impact* score even if it pins the
   guilt-class classification.
3. **Sampling noise.** At N=50 the 2-sample ep0 SE is ~10 pts. The "−2.0
   pts" delta could be a +5 to +10 effect we missed.

## Follow-ups now sharper

- **`recall_event_trace`** — already in the queue (2026-05-04 vintage),
  now promoted: log every reactivation event during κ=1.0 chains.
- **`seed_only_floor`** — new: ablation isolating the seed-aging fix from
  the outcome-tag floors. Cleanest test of the mechanism interpretation
  above.
- **`recharge_on_recall`** — biologically-motivated alternative: every
  reactivation above threshold adds δ back to stored emotion on the
  reactivated memory. Tests whether decay-vs-rehearsal balance restores
  signal magnitude (mechanism (2) above) without the artificial-floor
  artifact of this experiment.
- **N=200 replication at β_guilt=0.50 only** to tighten the −2.0 pts
  finding to ±5 pts.

## Bottom line

This run flips the burden of proof: the 2026-05-09 tag-aware-recall
residual is **not** an injection-pathway problem. The simplest model that
fits today's data is "tag-aware recall already fixed laundering for failure
memories, and what's left at β_guilt=0.50 is a recall-event-statistics or
stored-magnitude effect, not an injection-pathway one." The injection floor
is real but operates on a different memory class than the one it was
designed for.
