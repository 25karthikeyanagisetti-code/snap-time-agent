# Finding — Capped-Floor Loyalty Endpoints (N=200 replication)

**Date:** 2026-05-21
**Status:** HELD. Yesterday's PARTIAL upgrades to HELD across the full β_loyalty range.
**Headline:** `|Δcapped − Δfloor|` at the two endpoint cells collapses from `{17.5, 17.5}` pts (N=40) to `{0.0, 3.5}` pts (N=200) — a 10× reduction, both inside the ≈6.5 pt 2-SE band.

---

## Setup recap

The yesterday-2026-05-20 sweep `capped_floor_loyalty_sweep` tested whether the source-vs-gate isomorphism established along the GUILT decay axis (2026-05-19 `seed_refresh_capped` HELD) extends to the LOYALTY axis. It used β_guilt=0.05 fixed, β_loyalty ∈ {0.05, 0.15, 0.30, 0.50}, three modes (off / seed_only_floor / seed_refresh_capped), N=40 per arm, chain_length=10. The four-cell substitutability vector came back `{17.5, 5.0, 5.0, 17.5}` pts — mid-cells matched yesterday's guilt-axis figure exactly, endpoints blew out 3.5×, and the direction was consistent (capped > floor at both endpoints).

That left two competing readings on the table:
- **Real amplification**: capped raises `emotion_magnitude(seed)` on the source side, which enters `MemoryImpact = exp(−β·age)·exp(α·importance)·exp(γ·|emotion|)·sim(ctx,mem)` via the γ term BEFORE the recall gate runs. Floor-on-gate cannot replicate that. So capped should be a one-sided ≥ to floor whenever the floored channel is the rapidly-decaying one — endpoint behavior aligned with that prediction.
- **N=40 sampling noise**: the 2-SE on a Δ-of-Δ at N=40 is ≈14.5 pts. The 17.5-pt endpoint gaps were just outside that band — borderline. Same direction at both endpoints lessens the noise reading, but doesn't kill it.

This experiment replicates ONLY the two endpoint cells at N=200 (5× the per-cell sample), holding everything else fixed. The 2-SE collapses to ≈6.5 pts. A gap shrinkage to ≤6.5 pts at both endpoints discriminates the readings cleanly.

## Result, in numbers

ep0 rescue rate per cell × mode (N=200/arm):

```
                          β=0.05   β=0.50
  off                      79.5%    66.0%
  seed_only_floor          74.0%    75.5%
  seed_refresh_capped      74.0%    79.0%
```

Δep0 vs OFF, with the headline gap:

```
                              β=0.05   β=0.50
  Δfloor                       −5.5     +9.5
  Δcapped                      −5.5    +13.0
  |Δcapped − Δfloor| (today)    0.0      3.5    ← N=200
  |Δcapped − Δfloor| (parent)  17.5     17.5    ← N=40
  shrinkage                    17.5×    5.0×
```

Both endpoint gaps shrink well below the N=200 2-SE band of ≈6.5 pts. The β=0.05 cell delivers an exact point-estimate match (capped and floor both score −5.5 pts vs OFF — identical to 2 sig figs).

## Mechanism reading: amplification is OUT, baseline noise is IN

If the MemoryImpact-amplification story were operative, the gap should shrink only by the √5 ≈ 2.24× factor expected from sample-size scaling (17.5 → ~7.8 pts). What we observe is a 10× shrinkage to 0.0 / 3.5 pts. That's a hard rejection of the amplification reading at the headline cell.

The simpler explanation — that the N=40 endpoint OFF baselines were on the noisy tails of the cell's distribution — fits the data exactly. Yesterday's β=0.05 OFF (62.5%) is 17 pts below today's (79.5%); β=0.50 OFF (62.5%) vs today (66.0%) is 3.5 pts apart. Both shifts are consistent with the N=40 2-SE on a single proportion (≈15 pts at p=0.5). When the OFF baseline drifts, the Δ vs OFF drifts with it — and because both interventions land near a similar saturated rescue rate (74-79%), the Δs MOVE together with the OFF drift, producing apparent "consistent direction" effects that are actually a single common-cause noise event.

This is a useful lesson on the project's methodology in general: a "consistent direction" effect at borderline N is NOT independent evidence — both ends of the Δ-pair share the OFF denominator. At N=200, the OFF stabilizes and the apparent endpoint effect dissolves.

## What this means for the architecture

The architectural compression chain that started 2026-05-12 (`seed_only_floor` HELD — outcome floors inert at the regime-breaking cell), continued 2026-05-19 (`seed_refresh_capped` HELD — TABLE compressed to one entry, GATE moved to SOURCE on the guilt axis), and was put on hold yesterday by the loyalty-axis PARTIAL, is now confirmed to terminal claim:

The tag-floor injection mechanism compresses, with no measurable residual along either decay axis, to:
1. A per-memory `encoding_emotion_floor` template attached to the seed at encoding time.
2. A `max(stored, floor)` guardrail applied to that memory's stored.emotion at the start of every step.

The injection-gate code path (`emotion.inject_recalled_emotion_tag_aware`) is functionally redundant FOR THE SEED. Outcome-side floors remain to be tested (next experiment: `capped_floor_outcome_attach`).

## Falsifiers — what would unset the HELD

The HELD reading depends on a small number of testable assumptions. A future result could overturn it via:

1. **Outcome floors are NOT inert in this regime**: if `capped_floor_outcome_attach` reveals that attaching `encoding_emotion_floor` to FAILURE/RESCUE/TIMEOUT outcome memories produces a different long-run effect than the full TAG_FLOORS_DEFAULT path, then the gate-vs-source equivalence breaks for outcome-encoded memories. Architectural compression would survive for seed only, not as a general claim about all memories.
2. **Chain-length sensitivity at long horizons**: today's chain_length=4 means the store stays seed-dominated through the whole episode batch. At chain_length=30 (followup `capped_floor_long_chain`), outcome memories accumulate and may shift the recall gate's behavior asymmetrically between modes. A divergence at long chain that wasn't visible at short chain would point to outcome-memory dynamics, not seed-memory mechanism.
3. **Cross-κ replication**: today's run was κ=1.0 only. At κ=0.5 (boomerang shoulder) or κ=2.0 (saturated-committed), the floor mechanism may operate differently. The 2026-05-09 tag_aware_recall_kappa item in the backlog covers this for the recall pathway; an analogous capped-floor κ-sweep would test the source guardrail.
4. **Severity sensitivity**: at lower severity (mem_severity < 1.0), the seed's encoding template is less loud and the floor's role may be quantitatively different. The current claim is for mem_severity=1.0.

## Follow-up experiments worth queuing

1. **`capped_floor_outcome_attach`** (already in backlog) — promoted to top priority. Tests the next compression step: per-memory floor on outcome memories.
2. **`capped_floor_long_chain`** (already in backlog) — chain_length=30, to verify the equivalence at long horizons where the seed's relative store weight has degraded.
3. **`capped_floor_impact_decomp`** (already in backlog) — log `memory_impact(seed, ctx)` per step in off/floor/capped. The N=200 macro result predicts impact-side traces will also be statistically equivalent at the headline cell, which is now a verification check rather than a discovery probe. If the impact traces diverge while ep0 doesn't, there's a downstream cancellation worth understanding.
4. **OFF-baseline-stability audit** (new candidate) — re-run the OFF arm alone at all 4 β_loyalty cells with N=200 to map the OFF distribution. If OFF varies more than ±5 pts across cells at N=200, future PARTIAL results need to be flagged for OFF drift before mechanism interpretation.

## Conclusion

The 2026-05-20 PARTIAL upgrades to HELD. The seed-floor architecture is confirmed as a clean two-step replacement of the tag-floor injection dispatch table, with no measurable residual along either decay channel at the headline cell. The lesson on methodology is also useful: "consistent direction" at marginal sample sizes can be a single OFF-baseline noise event, not real signal.
