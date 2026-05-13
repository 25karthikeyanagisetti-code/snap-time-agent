# Finding — seed_only_floor_b30_n200

**Date:** 2026-05-13
**Status:** HELD. The 2026-05-12 N=40 disagreement at β_guilt=0.30 is
resolved as sampling noise. At N=200, |Δfull − Δseed| at ep0 = **1.0 pt**.

## Headline numbers

At β_guilt=0.30, kappa=1.0, T_snap=12, severity=1.0, rescue_importance=0.7,
β_loyalty=0.05, chain_length=8, tag_aware_recall=ON in all arms:

```
                  N=40 (2026-05-12)        N=200 (this run)
                  -----------------        ----------------
ep0 OFF              77.5%                    69.5%
ep0 Full             77.5%                    68.5%
ep0 Seed-only        62.5%                    69.5%
Δfull   (ep0)         0.0 pts                 −1.0 pts
Δseed   (ep0)       −15.0 pts                 +0.0 pts
|Δfull − Δseed|      15.0 pts                  1.0 pt
2-SE on diff-of-diff  ~21 pts                  ~9.2 pts
```

The 15-pt apparent gap at N=40 lived entirely inside the 2-SE band for
that sample size. Five-fold replication has shrunk it to a single point
of residual difference — well below even one standard error of the
estimator.

## Mechanism

The seed-only floor preserves the seed-prior restoration pathway:
`max(stored_seed.guilt, 0.6)` at recall, applied to a memory whose
stored.guilt has decayed from 0.9 toward 0 over its 15-step preage plus
in-chain decay.

The "full" mode adds three more entries (failure / rescue / timeout
templates) on the same `max(stored, floor)` operator. Those memories
are at age 0 when their first injection happens, so for guilt-charged
failure memories the stored channel still equals the encoding magnitude
and `max(stored, 0.6)` is a no-op. For rescue / timeout templates,
stored.guilt is already low and the floor cannot fire above it
either. Net contribution at ep0: zero.

This explains why pruning the floor table down to one entry is
indistinguishable from the four-entry default at ep0, in this cell, at
this sample size.

## What would falsify this interpretation

1. **A return of the N=40-style 15-pt gap at higher N (≥300).** That would
   mean the gap is real and the N=200 run hit a lucky-sample outlier on
   the other side. Probability: very low given the magnitude collapse to 1
   pt (closer to N=40 expectation under the null of equal means).

2. **A consistent ep5–7 long-run gap of ≥10 pts in a chain_length=20
   replication.** The current 4.8-pt residual is suggestive but
   agent-correlated noise. A long-chain replication where the same lift
   survives past ep10 would re-open outcome-floor relevance at the
   long-horizon layer (already queued as `seed_only_floor_ep5_9_audit`
   for β_guilt=0.50, which is the cell where ep5–9 also moved by +9 pts).

3. **A null result on `seed_refresh`.** If literally resetting seed.stored
   on recall doesn't reproduce the +10 pts ep0 lift at β_guilt=0.50, the
   "seed prior aging" mechanism is wrong even for the original headline
   cell — which would also undermine the inference here that the same
   mechanism is responsible at β_guilt=0.30.

## ep5–7 residual

The ep5–7 mean rescue picture:

```
INJ-OFF      31.5%
Full        37.5%   (+6.0 pts vs OFF)
Seed-only   32.7%   (+1.2 pts vs OFF)

|Δfull − Δseed| ep5-7  ≈ 4.8 pts
```

With N=200 agents × 3 episodes per agent, episodes within an agent are
strongly correlated (memory store carries forward). Effective N is closer
to 200 than 600, so SE per arm is roughly the same as the ep0 SE
(~3.3 pts) and 2-SE on the diff-of-diff is again ~9 pts. The 4.8-pt gap
is inside noise but represents the only place in this experiment where
outcome floors might be doing something. It's small, it's underpowered,
and it's queued for a follow-up rather than reported as a finding.

## Follow-up experiments worth queuing

- **`seed_only_floor_ep5_9_audit`** (already queued for β_guilt=0.50).
  Would also be worth running at β_guilt=0.30 at chain_length=20+ to
  confirm or kill the 4.8-pt ep5–7 residual seen here. If both audits
  return null, outcome floors are fully inert across the chain, not just
  at ep0.
- **`floor_negative_control`** (already queued). Replace the seed floor
  with a random emotion template of matched magnitude but different
  direction. Tests whether the seed-template's *direction* matters or
  whether the operative mechanism is "any magnitude-matched template at
  recall."
- **`seed_refresh`** (already queued). The cleanest version of the
  "keep the aged prior loud" intervention — just reset seed.stored to
  encoding magnitude on every recall, no floor table at all. If this
  reproduces the +10 pts ep0 lift at β_guilt=0.50, the floor table is a
  non-essential intermediate construct.

## Why this matters in one paragraph

The "seed-prior aging" story crystallized in the 2026-05-12 finding was
provisional because one of the four cells didn't fit. That cell — the
intermediate-asymmetry one — was the most damning for a clean
mechanistic reading: if outcome floors carry partial responsibility
exactly at moderate β_guilt, the mechanism would need a second moving
part keyed to chain-wise outcome-memory aging. The N=200 replication
removes that requirement. The injection-side fix is, at ep0, a
one-template intervention across the full β_guilt axis tested so far.
That is a substantially smaller architectural claim than the four-tag
floor table looked like a week ago.
