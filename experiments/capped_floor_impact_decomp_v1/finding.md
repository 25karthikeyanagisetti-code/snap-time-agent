# Finding — Capped Floor Impact Decomposition

**Date:** 2026-05-29
**Experiment:** `capped_floor_impact_decomp_v1`
**Headline:** Downstream cancellation confirmed. At β_loyalty=0.50, `seed_refresh_capped` carries 0.113 more seed-memory MemoryImpact than `seed_only_floor` by the end of ep0, yet achieves 7.5 pts lower rescue rate (72.5% vs 80.0%).

---

## Context

The `capped_loyalty_n200_endpoints` HELD result (2026-05-21) established that the macro ep0 rescue gap between `seed_only_floor` and `seed_refresh_capped` is within the 2-SE band at N=200 — closing the source-vs-gate isomorphism at the population rescue-rate level. The outstanding question was whether this equivalence extends to the recall-mechanics level, or whether the two modes compute their way to similar macro outcomes via mechanistically different recall traces.

This experiment instruments `memory_impact(seed_mem, ctx_features)` at every step of ep0 for both β_loyalty endpoint cells (0.05 and 0.50), with all three modes active: `off`, `seed_only_floor`, `seed_refresh_capped`.

---

## What the trace data shows

At β_loyalty=0.05, the impact traces diverge only in the last 2 steps of ep0 (max gap 0.041 at step 11). This is consistent with the HELD interpretation: at low loyalty decay the seed memory's stored emotion doesn't decay fast enough for the capped guardrail to engage until very late.

At β_loyalty=0.50, the impact divergence starts at step 1 and grows monotonically to 0.113 by steps 10–11. The mechanism is straightforward: with β_loyalty=0.50, the loyalty channel in stored memory decays by half each step. By step 2, stored loyalty ≈ 0.6 × 0.5² ≈ 0.15. In `capped` mode, however, the max-guardrail is applied at the START of every step, writing max(stored_k, floor_k) back into `M[0]["emotion"]`. The floor for the seed memory is `TAG_FLOORS_DEFAULT["seed"]` = {guilt: 0.6, loyalty: 0.4, ...}. So even as loyalty decays, the capped mode holds stored.guilt at 0.6 and stored.loyalty at 0.4 throughout — boosting exp(γ·|emotion|) in MemoryImpact continuously.

In `seed_only_floor` mode, stored emotion decays without any guardrail. The impact score falls faster. At injection time, max(stored, floor) is still applied, delivering the floor-level guilt pulse — but the lower MemoryImpact means the seed memory less reliably wins the top-1 recall slot.

---

## Why more impact hurts

The counterintuitive result — higher impact, lower rescue rate — is explained by over-steering.

The `guilt_recall_strength_tag_aware` function returns `min(1.0, impact)` of the top guilt-tagged memory, and this value feeds directly into the `guilt_recall` context variable that drives `e["guilt"]` upward via `step_emotion`. When `capped` inflates seed impact, it inflates `guilt_recall` in EVERY step of the episode, not just when the agent is near a conflict decision point.

In the committed regime (κ=1.0), the agent is already behaviorally oriented toward rescue — the guilt channel is doing its job. Adding excess guilt via continuously inflated recall doesn't help it commit faster. What it does is compound with late-episode guilt accumulation (steps 8–12, after the partner deadline), keeping e["guilt"] high when the agent is now in a "post-deadline" state where guilt no longer maps to a productive action. The agent commits to partner-direction actions but the partner is already dead — leading to PARTNER_DEAD or TIMEOUT outcomes that would have been PARTNER_RESCUED under the softer floor mode.

The `seed_only_floor` avoids this because its lower impact score means the seed memory is less dominant late in the episode. Outcome-encoded rescue memories compete more effectively for the top-1 slot, injecting loyalty rather than guilt, pulling the agent's emotion balance toward the action that most benefits from loyalty: early, decisive movement toward the partner.

---

## What this means for the architecture

The source-vs-gate isomorphism is real but bounded. It holds for rescue-rate prediction at reasonable sample sizes. It fails at the recall-mechanics level at extreme β_loyalty decay values.

For practical purposes: if you only care about macro rescue rates and you're operating in the mid-asymmetry range (β_loyalty ≤ 0.30), architectural compression to a per-memory floor field is safe — the two implementations are operationally interchangeable within sampling noise.

If you care about the MemoryImpact trace itself — e.g. for debugging, for multi-memory blending, or for extending the injection rule to use impact-weighted averaging — then `seed_refresh_capped` and `seed_only_floor` are genuinely different architectures and should not be treated as equivalent.

The direction of the failure is informative: **amplified impact hurts**. This adds to the accumulating evidence that in the committed regime, the bottleneck is not the strength of guilt recall, but its TIMING and the emotion-state it creates at the action-selection moment. Any architectural choice that inflates recall strength uniformly throughout an episode — rather than delivering it at the right phase — will tend to produce excess post-deadline guilt and worse rescue rates.

---

## What would falsify this interpretation

1. If suppressing the injection path entirely (delivering impact boost without the emotion bleed-in) shows that capped and floor rescue rates converge, the hurt is injection-mediated, not impact-mediated.
2. If the capped-vs-floor rescue gap disappears at β_loyalty=0.30 (the mid-asymmetry cell where the N=200 replication was HELD at macro level), the over-steering story is confined to the extreme decay end.
3. If adding encoding jitter on top of capped mode (to diversify outcome-memory competition) restores rescue parity with floor, the problem is seed-dominance duration, not the impact inflation per se.

---

## Follow-up experiments

- `impact_decomp_beta_sweep` — fine sweep β_loyalty ∈ {0.10, 0.20, 0.30, 0.40, 0.50} to find the threshold where the impact gap and rescue penalty appear together.
- `impact_vs_injection_dissociation` — suppress injection when seed fires in capped mode; test whether rescue rate recovers to floor's 80%.
- `capped_floor_n200` (already queued) — replicate the β_guilt=0.05 cell at N=200. This result (72.5% off and capped, 75.0% floor) suggests floor may have a genuine +5-7 pt edge even at low decay, but N=40 is too noisy to confirm.
