# Finding — Decay Asymmetry (2026-05-05)

## Headline

**Hypothesis FAILED in opposite direction.** With β_guilt held fixed at 0.05 and β_loyalty swept from 0.05 to 0.50 (a 10× range), the ep5–9 mean rescue rate stayed in a 2.0-pt band (20.8% → 19.4% → 19.0% → 18.8%) and never approached the 28% rescue-encoding-OFF baseline that this experiment was designed to recover. Worse, the population-divergence@5–9 metric — rescue rate of ep1-rescuers minus rescue rate of ep1-failers — monotonically inverted from +13.3 pts at the symmetric control (β_l=β_g=0.05) to −18.8 pts at the extreme asymmetry cell.

## Background and motivation

This run was prioritized as a direct successor to two negative results on the Loyalty Boomerang from `valenced_encoding_v1` (2026-05-02):

1. The 2026-05-04 `loyalty_importance_floor_v1` null showed that throttling the *importance* of encoded rescue memories from 0.7 down to 0.0 produced a 2.4-pt range on the same headline metric. Importance is a per-encoding flat amplifier; reducing it does not touch the γ·|emotion| recall term that sits between the rescue memory's stored emotion and its momentary recall impact.

2. The 2026-04-30s sweep across hand-crafted Φ couplings (`couplings_v1`) ruled out the coupling-form hypothesis. The boomerang therefore lives somewhere in MEMORY, not in DECISION.

Decay rate on the stored emotion is the natural next lever. `memory.decay_memory_emotion` was already implemented as a uniform per-step shrinker; this experiment extends it to accept a per-dimension dict so that loyalty memories can be decayed independently of guilt memories. The framing in the backlog ("forgiveness for self, not others") was that asymmetric decay would weaken the rescue-memory recall pull while leaving the seeded prior's guilt charge intact — a neat scalpel on the boomerang.

## What the data actually shows

Three observations:

**(1) The headline is null at higher resolution than expected.** All four cells produce ep5–9 means within 2.0 pts of one another (n = 500 episodes per cell in the late window). The 2.0-pt range is well inside the run-to-run stochastic noise we have estimated from `valenced_encoding_v1` and `loyalty_importance_floor_v1`. There is no signal here; the rescue-encoding-ON cap of ~15–20% holds across a 10× sweep of the loyalty-side decay rate.

**(2) The divergence inversion is the actual finding.** At β_loyalty=β_guilt=0.05 (symmetric mild decay), agents who happened to rescue in ep1 ended up rescuing 13.3 pts more often in ep5–9 than agents who failed in ep1. That is positive type formation — the classical "personality from experience" signature. As β_loyalty grows, the cells walk through +4.2, then −14.6, then −18.8 pts. Asymmetric decay does not just fail to differentiate the population; it actively flips the sign of the differentiation.

**(3) The ep0 rescue rate varies by ~7 pts across cells.** This is in-episode. Higher β_loyalty means the seeded memory's loyalty=0.6 channel decays faster during ep0, weakening the prior's |emotion| → exp(γ·|emotion|) recall term. The ep0 effect is small but it DOES show that asymmetric decay reaches into the first episode's behavior, not just the chained dynamics.

## Mechanism (interpretation)

The most parsimonious read: **uniform mild forgiveness preserves the cushion-vs-counterweight balance between rescue-encoded and failure-encoded memories**, while asymmetric forgiveness clears the cushion without touching the counterweight.

In the symmetric β=0.05 cell, an agent who rescues in ep1 acquires a loyalty-charged memory with stored emotion {loyalty=0.8, ...}. That memory's loyalty fades at 0.05/step alongside the guilt of any failure memories from later episodes. The early loyalty cushion stays measurably above the average for several episodes — long enough that the agent is more likely to rescue again in ep5–9. Hence positive divergence.

In the β_loyalty=0.50 cell, that loyalty cushion is gone within ~2 episode-steps. The guilt side of every subsequent failure stays at full strength because β_guilt=0.05. The ep1-rescuer's emotional history collapses to "guilt accumulation that everyone else also has." Worse, the ep1-rescuer probably failed at least once in ep2–ep4 (since chained rescue is rare at this κ), and that failure's guilt is now LOUDER relative to the agent's own loyalty record than it would be in the symmetric cell. The asymmetric cell therefore produces a sub-baseline class — one with the same guilt budget as everyone else but a structurally smaller loyalty signal. Hence the inverted divergence.

## What would falsify this interpretation

- **Reversed asymmetry test (β_guilt > β_loyalty).** If the mechanism is "loyalty cushion vs guilt counterweight," reversing the asymmetry should produce the OPPOSITE pattern: *increased* positive divergence and possibly higher mean rescue rate. This is the cleanest single falsifier.
- **Per-class memory population audit.** The interpretation predicts that in the symmetric cell, ep1-rescuers carry ~1 high-|emotion| loyalty memory and ~3–4 high-|emotion| guilt memories at ep5; in the asymmetric cell they carry ~0 loyalty (decayed away) and the same guilt count. A direct snapshot of the memory store at ep5 would resolve this.
- **κ=0.5 replication.** The boomerang is weaker at κ=0.5 (rescue rate ~22% baseline). If the divergence inversion replicates there, the mechanism is generic; if it disappears, it is specific to the deep-committed regime.

## What this tells us about the framework

This is the second lever (after `loyalty_importance_floor`) that targets a multiplicative term inside `MemoryImpact = exp(−β·age)·exp(α·imp)·exp(γ·|emotion|)·sim(ctx,mem)` and produces no movement on the headline. The boomerang is robust to both the importance term (α) and the emotion-magnitude term (γ when restricted to one valence). The remaining levers are:

- The age term (β·age) — `prior_dilution_rate` and similar sweeps in the queue
- The similarity term (sim) — would require either richer feature space or context-aware encoding
- The store-population side — `memory_capacity` (LRU eviction), `memory_consolidation` (periodic prune)

The divergence inversion is also a quiet-but-novel finding on its own: in this framework, **uniform mild forgiveness is a necessary condition for experience-driven type formation**, and even at the symmetric β=0.05 cell the divergence (+13 pts) is well below human-like personality drift (~50+ pts in repeated-task psychology). This bounds how much "personality from experience" the current architecture can produce before more structural changes are required.

## Follow-up experiments worth queuing

- `decay_asymmetry_reversed` — sweep β_guilt while holding β_loyalty fixed (the cleanest falsifier).
- `decay_asymmetry_lower_kappa` — the same 4 cells at κ=0.5 to test whether the divergence inversion is regime-dependent.
- `memory_population_audit` — instrumentation experiment: snapshot the M store at ep5 by cell, count loyalty-vs-guilt memories and their |emotion| magnitudes.
- Promote the open `memory_capacity` test in the queue — count-side eviction is now the most likely lever.
