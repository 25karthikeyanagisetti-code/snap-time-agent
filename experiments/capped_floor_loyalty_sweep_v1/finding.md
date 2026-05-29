# Finding — Capped-Floor Loyalty Sweep (2026-05-20)

## Headline

The source-vs-gate isomorphism that yesterday's `seed_refresh_capped` established along the guilt decay axis is **NOT** channel-symmetric. Reversing the swept axis (β_guilt=0.05 fixed, β_loyalty ∈ {0.05, 0.15, 0.30, 0.50}) holds the |Δcapped − Δfloor| substitutability gap at 5.0 pts at the asymmetric mid-cells (β_loyalty ∈ {0.15, 0.30}) but blows it out to 17.5 pts at both endpoints (β_loyalty ∈ {0.05, 0.50}). Yesterday's guilt-axis vector was `{7.5, 5.0, 5.0, 5.0}`; today's loyalty-axis vector is `{17.5, 5.0, 5.0, 17.5}`. Mean gap roughly doubles (5.6 → 11.3 pts).

Crucially the endpoint divergence has a sign: capped delivers a LARGER ep0 lift than floor in both endpoint cells. At β_loyalty=0.50 floor delivers Δep0=0.0 pts while capped delivers Δep0=+17.5 pts. At β_loyalty=0.05 floor delivers +10.0 pts and capped delivers +27.5 pts.

## Why the mid-cells still match

At β_loyalty=0.15 and 0.30 the seed's stored.loyalty has decayed below the 0.4 floor but the legacy literal-stored injection pathway is no longer completely dry (β_guilt=0.05 means stored.guilt holds at ~0.5 after a full episode). Capped-on-source raises stored.loyalty back to 0.4 at the start of every step, and the legacy injection picks up that lifted value via `e[k] += gain · stored[k]`. Seed_only_floor at the gate does the same: `max(stored, floor)` is applied at injection time, so injection_amt[loyalty] is also 0.4. By the time agent-emotion has been updated, the two pathways are pumping the same numeric loyalty into Φ, and the two paths converge — gap stays inside sampling noise (5.0 pts at both cells).

## What the endpoint divergence implies

Two candidate mechanisms:

**1. MemoryImpact amplification.** The seed memory's recall weight is
`exp(−β·age) · exp(α·importance) · exp(γ·|emotion|) · sim(ctx, mem)`.
Capped raises `emotion_magnitude(m.emotion)` at the SOURCE, which lifts the `exp(γ·|emotion|)` factor for the impact computation itself. That changes the seed's recall RANKING relative to outcome-encoded competitors, not just the post-recall injection. seed_only_floor at the gate does not touch the impact term — it only enters after recall has already selected. The size of the amplification grows with how much the floored channel was decayed: at β_loyalty=0.50 the gap between stored.loyalty (~0.0001) and floor.loyalty (0.4) is largest, so the impact lift is biggest, and capped's recall-ranking advantage is biggest. This predicts the endpoint divergence in the direction observed (capped > floor) and predicts that the same amplification would fade toward zero in cells where the floored channel doesn't decay much (β=0.05 has the smallest decay-drop, so this mechanism does NOT cleanly explain the β=0.05 endpoint). The β=0.05 endpoint may be a separate, second mechanism — or noise.

**2. Sampling noise at N=40.** The β_loyalty=0.05 cell is the same symmetric (β=0.05, β=0.05) numeric cell that yesterday's β_guilt=0.05 sweep already exercised; today's OFF baseline (62.5%) differs from yesterday's (77.5%) by 15 pts despite identical code. Same RNG-seed family, different starting offset. The 2-SE band on a Δ-of-Δ at N=40 binomial is roughly 2·√(4·p·(1−p)/N) ≈ 14.5 pts, so the 17.5-pt endpoint gaps are just outside the 2-SE band — borderline but not eye-popping. Mid-cells matching at exactly 5.0 pts in both runs DOES suggest the mid-cell agreement is mechanism-real, not noise; the endpoint gaps may be a mix of real amplification plus 2-SE noise.

## How to falsify the amplification interpretation

The cleanest falsifier is a "floor-on-injection-only-with-source-frozen" arm — apply the seed memory's max(stored, floor) operator JUST before `inject_recalled_emotion` consumes it, without leaving the modified emotion on the memory object. If that arm matches seed_only_floor exactly, then capped's advantage at the endpoints is the impact-term lift, not anything in the injection path. Conversely if that arm matches seed_refresh_capped, the mechanism is post-recall and the impact-term story is wrong.

A secondary falsifier: log `memory_impact(seed_memory, ctx)` per step in each mode. If capped's seed-impact is systematically higher than floor's at every recall step at β_loyalty=0.50, the impact-amplification story is supported.

## Long-run signal

ep5–9 mean rescue under loyalty-axis decay is flat across modes — all three within ~5 pts at every cell. The endpoint divergence is ep0-specific. The seeded prior has been mostly aged out of recall by ep5–9 (its age is preage+5·T_snap=75 steps; even at MEM_BETA=0.01 that's an `exp(-0.75) ≈ 0.47` impact-side discount), so any source-vs-gate divergence on the seed becomes invisible at the long horizon.

## Open follow-up experiments

1. `capped_loyalty_n200_endpoints` — replicate β_loyalty ∈ {0.05, 0.50} at N=200 to pin down whether the 17.5-pt endpoint gaps are real or N=40 noise. 2 cells × 3 modes × 200 agents × 10 episodes = 12,000 episodes — would have to drop modes (just off + floor + capped at the two cells) or shrink chain to fit under the 5,000 cap. Suggest 200 agents × 3 modes × 2 cells × 4 episodes = 4,800 (truncate chain to 4 since the signal is ep0).
2. `capped_floor_impact_decomp` — instrument `memory_impact` logging at every recall step in each mode at β_loyalty=0.50; compare the seed memory's per-step impact ranking across modes. If capped's seed rank > floor's seed rank monotonically across the episode, the amplification story is confirmed.
3. `floor_on_gate_with_source_max_inject` — a third mode that applies the floor at injection time but reads stored.emotion from a `max(stored, floor)` view (without overwriting the memory). Should match seed_only_floor exactly if amplification is the mechanism.

## What this rules out

It rules out a clean source-vs-gate isomorphism. The architectural compression sketched yesterday — "drop the dispatch table, store the floor on the memory, apply max(stored, floor) at one source point" — needs a caveat: doing so introduces a measurable advantage (or, at worst, a measurable difference) along axes where the floored channel decays harder than the injection-time gate can compensate for, because the impact-side `exp(γ·|emotion|)` term sees the lifted value too. Whether that's a feature or a bug depends on whether you want recall ranking to be sensitive to the floor — yesterday's design was neutral on this, today's run reveals the design choice is forced.

If the answer the framework wants is "the floor matters at the post-recall step only", the source-vs-gate compression is too aggressive and the dispatch table has to stay. If the framework is fine with the floor influencing recall ranking too (arguably more cognitively plausible — a strong-enough remembered prior gets reactivated MORE, not just LOUDER once activated), then capped is the more parsimonious architecture and yesterday's "isomorphism" framing should be reframed as "compression with a small principled enhancement."
