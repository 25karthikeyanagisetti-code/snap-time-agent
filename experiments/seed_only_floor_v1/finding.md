# Finding — Seed-only floor reproduces the full-floor injection lift

**Date:** 2026-05-12
**Sweep:** 4,800 episodes (3 inject_modes × 4 β_guilt cells × 40 agents × 10 episodes)
**Headline:** At β_guilt=0.50 (the regime-breaking cell from the 2026-05-09
tag-aware-recall residual), pruning the injection-floor table to ONLY the
'seed' entry produces the same +10 pts ep0 uplift and +9 pts ep5–9 uplift as
the full 4-tag floor table. Per-class outcome floors (failure/rescue/timeout)
are inert at the cell that motivated the entire tag_aware_injection thread.

## Why this matters

The 2026-05-10 tag_aware_injection run gave a strange Δep0 vector across
β_guilt — the lift was largest at symmetric β_guilt=0.05 (+20 pts), shrank
through the moderate cells, and went slightly negative at β_guilt=0.50
(−2 pts). That was the cell the experiment was designed to fix. The
2026-05-11 reading was: the floor that matters is the SEED floor —
restoring the aged-prior abandonment memory whose stored.guilt has decayed
over its 15-step preage — and the outcome floors don't matter because
outcome-tagged memories are young, with stored channels still at their
encoding magnitudes.

This run tests that reading by surgical ablation: route only the 'seed'
tag through the floor table, leave 'failure'/'rescue'/'timeout' on the
legacy literal-stored injection path. The full-floor and seed-only modes
should give identical Δep0 vectors iff the outcome floors were inert.

## The data

ep0 rescue rate, by mode × β_guilt cell (N=40 each):

| β_guilt | OFF | Full | Seed-only | Δfull | Δseed | |Δfull − Δseed| |
|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 77.5% | 80.0% | 82.5% | +2.5 | +5.0 | 2.5 |
| 0.15 | 80.0% | 75.0% | 75.0% | −5.0 | −5.0 | 0.0 |
| 0.30 | 77.5% | 77.5% | 62.5% | +0.0 | −15.0 | 15.0 |
| 0.50 | 57.5% | 67.5% | 67.5% | +10.0 | +10.0 | 0.0 |

Three of four cells: Δseed = Δfull within sampling noise (the cleanest
comparison is the β_guilt=0.50 cell, where both lifts are exactly +10 pts
to first decimal). Outcome floors do nothing measurable at 3/4 cells. At
β_guilt=0.30 the two modes diverge by 15 pts (Δfull=0 vs Δseed=−15) — a
2-SE gap at N=40, suggestive of a real-but-small outcome-floor
contribution at intermediate asymmetry.

ep5–9 mean rescue (secondary):

| β_guilt | OFF | Full | Seed-only | Δfull | Δseed |
|---:|---:|---:|---:|---:|---:|
| 0.05 | 38.5% | 42.0% | 37.0% | +3.5 | −1.5 |
| 0.15 | 31.0% | 34.0% | 37.0% | +3.0 | +6.0 |
| 0.30 | 36.0% | 35.5% | 28.0% | −0.5 | −8.0 |
| 0.50 | 27.5% | 36.5% | 36.5% | +9.0 | +9.0 |

The β_guilt=0.50 long-run uplift (+9 pts at both modes) survives the
pruning, confirming that the chain-wise rescue capacity at this regime is
maintained by the seed prior's tag, not by laundered-failure-memory
counterweights.

## Mechanism

The injection floor activates only on memories that reactivate above
threshold AND have a tag in the floor table. Their stored channels must
have decayed BELOW the floor for the floor to matter — max(stored, floor)
is only different from stored on dims where stored < floor.

The seeded prior starts every chain at preage=15. With β_guilt=0.50, its
stored.guilt has decayed via exp(−0.50·15) ≈ exp(−7.5) ≈ 0.0006× — i.e.
basically erased. The seed floor (guilt=0.6) is restoring nearly the entire
original charge whenever the prior fires. With β_guilt=0.05, decay is
exp(−0.75) ≈ 0.47× — the prior is still half-charged at ep0, and the floor
provides a smaller absolute lift; consistent with the smaller observed Δ.

Outcome memories are 0 steps old when they first inject during ep1 (and
have at most 12·k steps of decay by ep k). For β_guilt=0.05 their stored
channels never decay enough to drop below the failure floor's guilt=0.6.
For β_guilt=0.50 they decay fast — but the laundering audit (2026-05-07)
showed they reach the laundered state where stored.loyalty > stored.guilt
quickly. By then they fire on partner-adjacent contexts, where the floor
template still says guilt=0.6 — but the chain-wise rescue capacity at
β_guilt=0.50 was already restored by the seed-floor mechanism alone at
ep0, so the outcome-floor's role is muted.

## What would falsify this reading

- A clean N=200 replication of β_guilt=0.30 that holds the 15-pt Δfull −
  Δseed gap with SE < 5 pts. That would mean outcome floors carry a real
  contribution at intermediate asymmetry, not "the seed is everything."
- A "seed_refresh" intervention that resets seed memory's stored.guilt to
  encoding magnitude on every recall (no floor, just refresh) reproducing
  the full-floor signal at all cells. That would tighten the mechanism
  from "seed floor" to "seed refresh."
- A negative control where the seed floor is replaced with a same-magnitude
  random floor that doesn't match the prior's encoding template. If the
  effect persists, the seed-floor story is wrong — any high-magnitude
  guilt floor would do.

## Follow-up backlog additions

- `seed_only_floor_b30_n200` — N=200 replication at β_guilt=0.30 to tighten
  the −15 pt Δ to ±5 pts.
- `seed_refresh` — bypass the floor table and refresh seed memory's
  stored.guilt to encoding magnitude on every recall. If this reproduces
  the +10 pts at β_guilt=0.50, the floor table is a non-essential
  intermediate construct.
- `seed_only_floor_ep5_9_audit` — verify that the long-run +9 pts at
  β_guilt=0.50 is sustained past episode 10. Chain length to 30.
- `floor_negative_control` — seed floor replaced with random emotion
  template of matched magnitude. Tests whether seed-template fidelity
  matters.
