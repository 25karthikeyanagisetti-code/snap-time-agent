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


# Tag-keyed injection floor templates. When a memory carries an encoding-time
# 'tag' field (set at the experiment level — same instrumentation as
# memory_population_audit and tag_aware_recall), the injection pathway can
# look up a per-tag "essence" floor and inject max(stored_dim, floor_dim) on
# each emotion channel. This neutralizes the second mechanism flagged at the
# end of 2026-05-09 tag_aware_recall: under asymmetric β_guilt the recall
# gate may say "this IS a guilt memory" but the literal stored.guilt has been
# laundered to ~0, so the injection contributes no guilt to current e_t even
# when the gate fires. Floors restore the channel that the tag implies.
#
# Values are chosen to roughly match the seeded prior / outcome-encoding
# magnitudes used in sandbox.py: the 'seed' floor matches the seeded
# abandonment prior; 'failure' matches the failure-outcome encoding;
# 'rescue' matches the rescue-outcome encoding; 'timeout' is a softer
# variant.
TAG_FLOORS_DEFAULT = {
    "seed":    {"survival": 0.2, "guilt": 0.6, "loyalty": 0.4,
                "fear": 0.1, "curiosity": 0.0},
    "failure": {"survival": 0.3, "guilt": 0.6, "loyalty": 0.5,
                "fear": 0.2, "curiosity": 0.0},
    "timeout": {"survival": 0.2, "guilt": 0.3, "loyalty": 0.3,
                "fear": 0.2, "curiosity": 0.0},
    "rescue":  {"survival": 0.1, "guilt": 0.0, "loyalty": 0.6,
                "fear": 0.1, "curiosity": 0.0},
}


def inject_recalled_emotion_tag_aware(e, m, gain, tag_floors=None):
    """
    Tag-keyed variant of inject_recalled_emotion. For tagged memories,
    injection on each emotion dim is gain * max(stored_dim, floor_dim) where
    the floor is a template keyed by the memory's encoding-time tag.

    A memory without a 'tag' key (or with an unknown tag) falls back to the
    legacy literal-stored-channels injection — preserves the behavior of
    every prior experiment that did not tag the store.

    Used by exp_tag_aware_injection (2026-05-10) to test whether closing the
    injection-side laundering pathway eliminates the residual β_guilt=0.50
    ep0 collapse left over after the recall-side fix from tag_aware_recall.
    """
    if tag_floors is None:
        tag_floors = TAG_FLOORS_DEFAULT
    tag = m.get("tag")
    stored = m.get("emotion", {})
    if tag is None or tag not in tag_floors:
        return inject_recalled_emotion(e, stored, gain)
    floor = tag_floors[tag]
    new_e = dict(e)
    for dim in e.keys():
        s = stored.get(dim, 0.0)
        f = floor.get(dim, 0.0)
        injection_amt = s if s > f else f
        new_e[dim] = _clip(e[dim] + gain * injection_amt)
    return new_e
