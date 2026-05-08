# Finding — Laundering κ-Invariance

**Headline:** At κ=0.5 (boomerang shoulder), 80.7% of failure-tagged memories at β_guilt=0.15 are stored with loyalty > guilt at recall time, against 78% at κ=1.0. The valence-laundering microstructure does not depend on the agent's regime — it is determined entirely by per-channel decay arithmetic acting on the encoded outcome vector.

## Direct comparison to the κ=1.0 audit

| β_guilt | laundering @ κ=0.5 | laundering @ κ=1.0 | Δ |
|---:|---:|---:|---:|
| 0.05 (symmetric) |  0.0% (0/115) |  0.0% (0/56) | 0 pts |
| 0.15 | 80.7% (113/140) | 78.3% (72/92) | +2.4 pts |
| 0.30 | 76.5% (117/153) | 75.2% (91/121) | +1.3 pts |
| 0.50 (extreme) | 81.1% (133/164) | 77.9% (106/136) | +3.2 pts |

The pairwise differences are within sampling noise for n in the hundreds. Three independent replications (κ=1.0 with N_AGENTS=100, κ=0.5 with N_AGENTS=100, three asymmetric cells each) all converge to a 75–81% laundering plateau as soon as β_guilt moves off symmetric. The pattern is mechanism-driven, not regime-driven.

The channel-total comparison is the same story. Per-agent stored guilt drops from 1.12 (symmetric) to ~0.55 (asymmetric plateau) at κ=0.5; from 0.95 to ~0.50 at κ=1.0. Loyalty-channel total stays in the 0.83–0.92 range across all asymmetric cells at κ=0.5, and 0.97–1.08 at κ=1.0. The slight cross-κ offset on the absolute totals (κ=0.5 sees marginally lower loyalty totals because rescue-tagged memories are rarer at the boomerang shoulder) does not affect the conclusion about laundering rate, which is normalized per failure memory.

## Mechanism — confirmed at the level of decay arithmetic

The laundering rate is determined by:

1. The encoded failure vector `(guilt=0.85, loyalty=0.5)`. Encoded ratio guilt/loyalty = 1.7.
2. The age of the memory at recall time. For ep4-snapshot, ages range from 0 (encoded in ep4) to ~60 (encoded in ep0).
3. The two decay rates β_guilt, β_loyalty applied per step.

After `n` steps, stored guilt = `0.85 · (1−β_guilt)^n` and stored loyalty = `0.5 · (1−β_loyalty)^n`. The flip condition (loyalty > guilt) reduces to `n > log(1.7) / log((1−β_loyalty)/(1−β_guilt))`. At β_guilt=0.15, β_loyalty=0.05 this gives n_flip ≈ 4.7 — so any failure memory older than ~5 steps has flipped. Most ep4-snapshot failure memories satisfy this, hence ~80% laundering. The same calculation applies at κ=0.5 because κ doesn't enter the decay equation. Confirmed.

The plateau across β_guilt ∈ {0.15, 0.30, 0.50} also has a clean explanation: at any of these rates, n_flip for the typical age (~30 steps) is well below the typical age, so essentially every failure memory older than a single episode flips. Increasing β_guilt further can't push the laundering rate above 100% — it just makes individual flips happen sooner. The remaining 19–24% un-flipped failures are the ones encoded at ep4 itself (age 0 at snapshot).

## What would falsify this

The κ-invariance reading would be wrong if the κ=0.5 laundering rates had landed materially below the κ=1.0 numbers — say, 30–50% at β_guilt=0.15 — because the decay equation would still predict ~80% but the snapshot wouldn't show it. That would imply some other mechanism was selectively preserving guilt in failure memories at low κ, e.g. via more frequent reactivation refreshing them. The actual data shows the opposite: laundering rate is slightly HIGHER at κ=0.5 than at κ=1.0 in three of four cells, consistent with the prediction (and likely a small additional effect from less-aggressive recall reinforcement at low κ — but this is a secondary interpretation; the primary number is the agreement between the two regimes).

A weaker falsifier would be a kappa-by-cell interaction: if the κ=0.5 laundering rates DROPPED with increasing β_guilt while the κ=1.0 rates plateaued, that would suggest the mechanism is not just decay arithmetic but a balance between decay and reactivation-driven refresh that itself depends on κ. The actual data shows both regimes plateau together — neither drops, neither grows.

## What this DOESN'T tell us

It does NOT tell us that laundering is the operative cause of divergence-erosion at κ=0.5, because **divergence-erosion cannot be measured at κ=0.5** in this configuration: ep1 rescue rate is 0% across all four cells, and the divergence@5–9 metric is conditioned on ep1 outcome. The boomerang shoulder is so committed-deficient that no agent rescues in ep1 from a partner-already-dead state at step 7. The behavioral pieces of the audit story require κ=1.0 (or some other regime where ep0 and ep1 produce a non-trivial distribution of outcomes) to be visible. The arithmetic pieces are visible at any κ, and they all hold.

This decoupling is itself useful: it pins down two separate layers of the boomerang mechanism that prior runs had bundled together. The decay-arithmetic layer is regime-independent and is what `recharge_on_recall` should target. The behavioral-coupling layer (how much laundered memories actually pull the agent off-policy) is regime-dependent and is what experiments that vary κ within the audit chassis would test.

## Follow-up experiments

- `tag_aware_recall` (top of queue) — replace stored-channel comparison with the encoded valence tag for class identity at recall time. If divergence persists under asymmetric β under tag-aware recall, the laundering identification is confirmed by a surgical removal. If divergence still erodes, there's a second mechanism we haven't isolated.
- `recharge_on_recall` (queued) — `+= δ` injection into stored emotion every reactivation above threshold. Should restore both Σ stored guilt per agent and (at κ=1.0) divergence@5–9. The κ=0.5 prediction is null on macro outcomes but full restoration on the laundering rate.
- `laundering_inflection` (queued) — fine sweep β_guilt ∈ {0.05, 0.07, 0.09, 0.11, 0.13, 0.15} at κ=1.0. The arithmetic predicts a step-function-like transition near β_guilt ≈ 0.10 (where n_flip drops below the typical age range). The 05-07 audit + this run both show a plateau above β_guilt=0.15; the inflection sweep should resolve where the rise happens.

The above closes the κ-invariance gap left open in the κ=1.0 audit's `finding.md` and promotes `tag_aware_recall` and `recharge_on_recall` as the cleanest next experiments — both targeting the now-pinned decay-arithmetic layer rather than chasing further regime-by-regime macro replications.
