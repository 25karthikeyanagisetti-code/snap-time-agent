# snap-time-agent

A research codebase for **human-like AI agents** — agents that behave like people behave, not like solvers solve.

Modern AI optimizes correctness:

```
θ* = argmin_θ [ E(-log p_θ(y|x)) - β·E(r(x,y)) + γ·KL(π_θ ‖ π_ref) ]
```

This repo extends that objective with internal state — emotion, memory, and bounded autonomy time — so agents can hesitate, forget, forgive, and make calculated mistakes:

```
θ* = argmin_θ E_τ [
        Σ_{t=0}^{T_snap} (
            L(f_θ(x_t), y_t)
          + Φ( v(s_t, a_t), e_t )
          + λ · MemoryImpact_t
        )
      ]
```

Where:

- **e_t = [survival, guilt, loyalty, fear, curiosity] ∈ [0,1]^5** — emotion as a vector, not a scalar.
- **MemoryImpact = exp(−β·age) · exp(α·importance) · exp(γ·|emotion|) · sim(context, memory)** — memory fades with age, persists with importance and emotion, and reactivates by similarity.
- **t ∈ [0, T_snap]** — *Snap Time*: a bounded autonomy window during which the agent thinks, hesitates, and commits.
- **Φ(v, e_t)** — emotion-weighted decision pressure where guilt or loyalty can override survival.

## What's in this repo

```
src/                  core framework — emotion, memory, decision, sandbox
experiments/          experiments by name; each folder has config + results + notes
docs/                 framework spec, open questions, the LinkedIn posts
tests/                sanity checks on the dynamics
```

## Current experiment: regime_map_v1

We sweep `T_snap` and the emotion-weight scalar `κ` over a Rescue-vs-Resource gridworld and measure four behavior signatures: hesitation rate, loyalty-override rate, path-dependence on seeded memories, and decision entropy.

The hypothesis: **human-like behavior is a narrow regime, not a property** — outside a specific (T_snap, κ) band, the agent collapses into pure optimizer or pure noise.

```
pip install -r requirements.txt
python -m src.run_sweep
```

Outputs land in `experiments/regime_map_v1/`.

## Status

Active research. Findings get posted as I run them — see `docs/posts/`.
