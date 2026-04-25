"""
Emotion vector dynamics.

e_t is a dict with keys: survival, guilt, loyalty, fear, curiosity.
Each value is in [0, 1].

The framework spec is in docs/01_framework.md. Per-component update rules:
- survival   ↑ with time pressure, ↓ with homeostatic decay
- guilt      ↑ with reactivated abandonment memory, ↓ with decay
- loyalty    ↑ when adjacent to partner, ↓ with decay
- fear       ↑ with environmental threat, ↓ with decay
- curiosity  ↑ with novelty (visiting an unseen cell), ↓ with decay

No OOP. Pure functions on dicts.
"""

from . import config


def init_emotion(persona_baseline=None):
    """
    Start a fresh emotion vector. If persona_baseline is given, use it; else
    everything is at 0.0. (Persona is a v2 concern; v1 always starts neutral.)
    """
    if persona_baseline is None:
        return {dim: 0.0 for dim in config.EMOTION_DIMS}
    return dict(persona_baseline)


def _clip(x):
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def step_emotion(e, ctx):
    """
    Apply one step of emotion dynamics.

    ctx is a dict with whatever signals the environment chose to emit:
      - time_pressure   ∈ [0,1]   — how close we are to deadline
      - partner_adjacent ∈ {0,1}  — 1 if standing next to partner this step
      - threat          ∈ [0,1]   — environmental threat magnitude
      - novelty         ∈ [0,1]   — how novel the current cell is
      - guilt_recall    ∈ [0,1]   — strength of recalled abandonment memory

    Returns a NEW emotion dict (does not mutate input).
    """
    decay = config.EMOTION_DECAY
    new_e = {
        "survival": _clip(
            e["survival"] + config.SURVIVAL_RATE * ctx.get("time_pressure", 0.0) - decay
        ),
        "guilt": _clip(
            e["guilt"] + config.GUILT_RATE * ctx.get("guilt_recall", 0.0) - decay
        ),
        "loyalty": _clip(
            e["loyalty"]
            + config.LOYALTY_RATE * ctx.get("partner_adjacent", 0.0)
            - decay
        ),
        "fear": _clip(
            e["fear"] + config.FEAR_RATE * ctx.get("threat", 0.0) - decay
        ),
        "curiosity": _clip(
            e["curiosity"]
            + config.CURIOSITY_RATE * ctx.get("novelty", 0.0)
            - decay
        ),
    }
    return new_e


def emotion_magnitude(e):
    """L1 norm of the emotion vector — used in MemoryImpact."""
    return sum(abs(v) for v in e.values())


def inject_recalled_emotion(e, recalled_emotion, gain):
    """
    When a memory is reactivated above threshold, some of its stored emotion
    bleeds into current e_t. This is the "old wounds open up" mechanism.
    """
    new_e = dict(e)
    for dim in e.keys():
        new_e[dim] = _clip(e[dim] + gain * recalled_emotion.get(dim, 0.0))
    return new_e
