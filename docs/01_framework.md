# Framework spec

This document fixes the math that the code implements. When the code and this
doc disagree, this doc is wrong — update it.

## State

A trajectory τ = (s_0, a_0, s_1, a_1, ...) inside a Snap Time window
`t ∈ [0, T_snap]`. State `s_t` is whatever the environment exposes (positions,
clocks, partner status). The agent also carries hidden state:

- `e_t ∈ [0,1]^k` — emotion vector. We use k=5: survival, guilt, loyalty, fear, curiosity.
- `M_t` — episodic memory: a list of (event_features, emotion_at_encoding, importance, age) tuples.

## Emotion update

Emotions evolve via additive update with clipping to [0,1]:

```
e_{t+1} = clip( e_t + Δe(s_t, a_t, recall_t) − decay, 0, 1 )
```

Where:
- `Δe(s_t, a_t, recall_t)` is event-driven: time pressure raises survival; partner
  proximity raises loyalty; reactivated abandonment memory raises guilt.
- `decay` is a small per-step pull toward zero (homeostasis).

The exact per-component rules live in `src/emotion.py` and are pure functions.

## Memory impact (recall weight)

For a stored memory `m = (features_m, emotion_m, importance_m, age_m)` and current
context `c`, its impact at recall time is:

```
MemoryImpact(m | c) = exp(−β · age_m)
                    · exp( α · importance_m )
                    · exp( γ · |emotion_m| )
                    · sim(c, features_m)
```

`sim` is cosine similarity in feature space. The four factors multiply, so any
one can damp the memory toward zero. β, α, γ are global hyperparameters.

Old memories that go un-recalled fade. Recalled memories can re-inject emotion
into `e_t` (this is the contextual reactivation phenomenon).

## Decision (Phi)

At each step inside the Snap Time window, the agent scores actions:

```
Φ(v(s_t, a), e_t) = − v(s_t, a) + Σ_i w_i · e_t[i] · conflict_i(a)
```

`v(s_t, a)` is the immediate task value (reward potential). `conflict_i(a)`
captures how much action `a` violates emotion component `i` — e.g. moving toward
the resource while the partner is in danger has a high `conflict_guilt`.

The decision is `a* = argmin_a Φ(v(s_t, a), e_t)`. Note: low Φ is good. Picking
to satisfy emotion *reduces* its conflict cost.

## Snap Time loop

```
t = 0
best_a = None
best_Φ = +∞
while t < T_snap:
    a_candidate = sample_or_enumerate(actions)
    Φ_candidate = Φ(v(s, a_candidate), e_t)
    if Φ_candidate < best_Φ:
        best_a = a_candidate
        best_Φ = Φ_candidate
    e_t = step_emotion(e_t, recall(M, context))   # emotion can drift mid-window
    t += 1
commit best_a
```

A long T_snap lets the agent re-evaluate, switch its mind (hesitation), and
converge to a more stable Φ minimum. A short T_snap forces an impulsive commit.

## Hyperparameters

Defaults are in `src/config.py` (created when first needed). The two we sweep
in regime_map_v1 are:

- `T_snap` — Snap Time window length (deliberation budget in steps).
- `κ` — global scale on the emotion-weighted conflict terms in Φ. Effectively
  how much emotion is allowed to overrule pure value.
