# Jitter Universality — long-form

**Naming:** The κ-Scaling of the Encoding Diversity Effect

**Date:** 2026-05-02

**Episodes:** 5,000 (5 κ × 2 jitter × 50 agents × 10 chained episodes)

## Headline

Per-agent encoding noise (σ=0.15 Gaussian on encoded emotion at episode
termination) yields a **2.60× sustained rescue rate (27.2% → 70.8%) at
κ=2.0**, completely arresting the Homogenization Collapse — rescue
rate stabilizes at 76% across episodes 1-9 instead of decaying to 20%.
At the Paralysis Valley (κ=0.25–0.5), jitter has zero effect.

The strength of the encoding-diversity effect SCALES with κ:
- κ=0.10, 0.25 (rational/Paralysis Valley): no effect
- κ=0.50: marginal (+2.4 pts, 1.75×)
- κ=1.00: strong (+16.4 pts, 2.05×)
- κ=2.00: very strong, regime-stabilizing (+43.6 pts, 2.60×)

This refines this morning's `personality_emergence` finding from "the
Homogenization Collapse can be partially undone" into a more specific
claim: **encoder homogeneity is the structural cause of the population-
trajectory collapse in the committed regime — and only there. The
Paralysis Valley is a different failure mode with a different cause.**

## Mechanism in detail

The Φ formula in this framework is `Φ = -v + κ·⟨e, c⟩` (additive
coupling), where v is task value, e is the agent's current emotion
vector, and c is the per-emotion conflict cost of the candidate
action. The agent picks the action that minimizes Φ via Boltzmann
softmax.

The agent's emotion vector e at any step is jointly driven by its
internal emotion update rule AND by recall from the memory store M.
When a memory's MemoryImpact crosses threshold, its stored emotion
gets injected (with gain) into the agent's current e.

Now consider the two failure modes:

**At low-medium κ (the Paralysis Valley):** the κ multiplier in Φ is
small. The decision pressure depends primarily on -v. But emotion is
loud enough that κ·⟨e,c⟩ can occasionally edge out -v on the
preferred action. The result is that no action wins reliably — the
agent's softmax is unstable across actions, it dithers in a tight
neighborhood, and the partner deadline expires. **The failure happens
within episode 1 and is per-step.** Memory store evolution across
episodes is irrelevant because the agent fails on its first decision
chain.

**At high κ (the Homogenization Collapse):** the κ multiplier is
large. ⟨e,c⟩ dominates -v. The agent's emotion vector cleanly picks
an action — typically the partner-rescue action when emotion is
high-loyalty/guilt. So the agent rescues episode 0. Then the outcome
encodes a memory. Each subsequent episode adds another memory that
similarly biases emotion at recall. After 5–9 episodes the memory
store has converged to a similar profile across all 100 agents (they
all encoded the same outcomes the same way), so they all have
similar emotion bleeds, similar Φ surfaces, and similar action
distributions. The population homogenizes toward whatever attractor
the converged memory store creates — which empirically is failure.

Encoding jitter directly attacks the second mechanism: with σ=0.15
Gaussian noise on the encoded emotion vector, two agents writing the
same outcome record slightly different memories. After 5 episodes
their stores have measurably different distributions. Their emotion
bleeds differ, their Φ surfaces differ, their action distributions
spread, and the population stays distributed across many emotion
microstates instead of collapsing to one.

The κ-scaling of the effect makes mechanistic sense:
- At κ=0, emotion is silent in Φ; jitter on emotion-encoding is
  invisible.
- At low κ, emotion has small effect in Φ; jitter has small effect
  on actions.
- At high κ, emotion dominates Φ; jitter has large effect on actions.

This is a cleanly testable mechanistic story that predicts (and
matches) the observed κ-scaling.

## Why the κ=2.0 stabilization is striking

At κ=2.0 the agent should be MOST coupled to its memory store and
therefore MOST vulnerable to homogenization. Yet with jitter on it's
the most stable regime — rescue rate stays at 76% from episode 1 all
the way through episode 9.

The interpretation: in the high-κ regime, the agent's behavior is
nearly deterministic given its emotion vector. Without jitter, all
agents converge to the same emotion vector via memory homogenization,
so they all behave the same way (collapse). With jitter, the
population spreads in emotion space, so different agents commit to
different actions reliably — and crucially, a substantial fraction of
the population's emotion microstates support the rescue trajectory.

This means: **at high κ, with encoding diversity, the system reaches
a STABLE distribution where ~76% of the population is in
rescue-supporting microstates.** The collapse is not just slowed —
it is replaced by a stable heterogeneous equilibrium.

## What this rules in and out

Rules IN: encoder homogeneity as the mechanism behind the
Homogenization Collapse. The κ-scaling pattern, the stabilization at
κ=2.0, and the absence of effect at low κ all match this interpretation.

Rules OUT: encoder homogeneity as the mechanism behind the Paralysis
Valley. Per-step decision instability at low-medium κ has nothing to
do with population-trajectory dynamics in memory.

This is a useful sharpening because it tells us where to look (and
not look) for fixes to each failure mode.

## Open questions

1. What's the optimal jitter σ at each κ? σ=0.15 was chosen by intuition.
   At κ=2.0 with σ=0.5 the agents might saturate the [0,1] emotion
   bounds and lose all encoding signal. There should be a sweet spot.
2. Does the κ=2.0 stabilization hold past 10 episodes? Test at chain
   lengths 30, 100.
3. The Paralysis Valley remains the framework's only un-rescued
   failure mode. Candidates not yet tested: stochastic Φ (vs current
   stochastic e), per-action conflict noise, value warm-start from
   prior episodes' outcomes.

## Files

- `src/exp_jitter_universality.py` — experiment driver
- `experiments/jitter_universality_v1/results.csv` — 5,000 rows
- `experiments/jitter_universality_v1/jitter_universality.png` — 2-panel chart
