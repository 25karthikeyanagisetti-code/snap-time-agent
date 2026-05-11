# Personality Emergence — long-form

**Naming:** The Encoding Diversity Effect

**Date:** 2026-05-02

**Episodes:** 4,000 (4 conditions × 100 agents × 10 chained episodes)

## Headline

Per-agent encoding noise (Gaussian σ=0.15 on the encoded emotion vector
at episode termination) yields a **2.55× sustained rescue rate** over
the Wave-3 baseline. Sustained rescue rate (avg over episodes 5–9) goes
from **15.4% (baseline) to 39.2% (jitter only)**. Bounded memory alone
delivers a tiny gain (+4.4 pts to 19.8%) and contributes essentially
nothing on top of jitter (39.4% vs 39.2%).

This is the first POSITIVE finding in the project. Three prior
interventions (selective encoding, valenced encoding, bounded memory)
all failed to break the Homogenization Collapse. Encoding diversity
partially breaks it.

## What was held constant vs varied

A 2×2 factorial over {bounded memory, encoding jitter} × {off, on}.
Held constant: T_snap=12, κ=1.0 (committed regime — the regime Wave-3
saw lose 78%→17% in one episode), severity=1.0, additive Φ, all other
sandbox parameters at their published-experiment defaults.

The bounded condition uses `mem_capacity=3` with least-impact eviction
(every memory beyond capacity is dropped after each episode based on
its current MemoryImpact score relative to the terminal context).

The jitter condition uses `encoding_jitter=0.15` — a per-agent Gaussian
perturbation on the encoded emotion vector at episode termination. This
is a NEW parameter added to `sandbox.run_episode()`. The default is 0.0,
preserving all prior experiment behavior. With jitter ON, the same
outcome encoded by different agents lands at slightly different points
in emotion space.

## Mechanism in detail

The Homogenization Collapse mechanism (from Wave 3): all 100 agents share
the same seeded prior, the same value/conflict/Φ functions, and — crucially
— the same encoding function. After each episode they all encode the same
outcome (rescue → loyalty=0.8, failure → guilt=0.85) at the same context
features. Their memory stores rapidly converge to similar
emotion-feature distributions. Memory recall produces similar emotion
bleeds across the population. Φ becomes nearly identical. Outcomes
collapse to a single attractor.

Encoding jitter breaks this at the encoding step. With σ=0.15 on a [0,1]
emotion vector, two agents encoding the same rescue outcome might write
{loyalty: 0.93, guilt: 0.07} vs {loyalty: 0.71, guilt: 0.13}. After 5
episodes of accumulation, their stores look measurably different. Φ
diverges. Action probabilities diverge. Outcomes spread.

Why doesn't this also produce behavioral *types* (positive
divergence@5–9)? Because the divergence is in the WRONG direction — it
spreads the population across emotion-microstates, but the
emotion-to-rescue-rate function isn't monotonic in any one emotion. So
"more diverse memory stores" doesn't imply "more agents stuck in the
rescue regime" — it implies "agents distributed across many regimes
including the rescue one". Net rescue rate goes UP, but the predictability
of rescue from early-episode outcome stays low.

## What would falsify the interpretation

The interpretation is "encoding diversity protects against population
collapse by spreading across emotion microstates." If this is right:

1. The effect should be largest near the most-collapsed regime (κ=1.0)
   and smaller at κ regimes that don't collapse anyway. **Test:** sweep
   jitter ON across κ ∈ {0.1, 0.5, 1.0, 2.0, 4.0}; expect biggest gain
   at κ=1.0.
2. Sustained capacity should not depend on chain length much past the
   point where memory stores have saturated. **Test:** push chain length
   to 20 and 50 — sustained rescue rate at ep20-50 should stay near
   ~39% under jitter ON, not crash further.
3. The effect should depend on the SHAPE of the noise, not just its
   magnitude. **Test:** swap Gaussian for uniform; swap per-emotion
   independent for vector-correlated. If shape matters, it tells us
   something about how the memory→Φ map is curved in emotion space.

## Why this is more interesting than it sounds

This experiment changes the conversation about what memory-augmented
agents need in order to behave well over time. The conventional take is
"more memory, longer context, better retrieval." That has been tested
in this framework and it does not work.

What does work, here, is **a structural source of agent-to-agent
difference at the moment of encoding**. The internal state diverges
because two agents who saw the same outcome wrote it down a little
differently. That's not "more memory." That's "memory that belongs to
this agent in particular."

For the broader project — building agents that hesitate, forget, and
forgive in human-like ways — this points to a specific architectural
prescription that hasn't been on most people's roadmaps: every agent
needs its own encoder, with some noise that distinguishes it from the
average. Not random behavior. Random encoding.

## Files

- `src/exp_personality_emergence.py` — experiment driver
- `src/exp_memory_capacity.py` — sets up the null result that motivates the jitter test
- `src/sandbox.py` — added `mem_capacity` and `encoding_jitter` parameters
- `src/memory.py` — added `cap_store()` for least-impact eviction
- `experiments/personality_emergence_v1/results.csv` — 4,000 rows
- `experiments/personality_emergence_v1/personality_emergence.png` — main chart
- `experiments/memory_capacity_v1/results.csv` — supporting null
- `experiments/memory_capacity_v1/memory_capacity_null.png` — supporting chart
