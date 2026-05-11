"""
Episodic memory with aging, importance, emotion-weighting, and contextual
reactivation via similarity.

A memory is a dict:
    {
      "features": list[float],       # event feature vector
      "emotion":  dict,              # emotion vector at time of encoding
      "importance": float,           # ∈ [0, 1]
      "age": int,                    # steps since encoding
    }

The store M is a list of such dicts. No OOP.

MemoryImpact (recall weight) =
    exp(-β · age) · exp(α · importance) · exp(γ · |emotion|) · sim(ctx, features)
"""

import math
from . import config
from .emotion import emotion_magnitude


def init_store():
    return []


def encode(M, features, emotion_at_encoding, importance):
    """Append a memory. Pure-ish: appends to list M in place and returns M."""
    M.append({
        "features": list(features),
        "emotion": dict(emotion_at_encoding),
        "importance": float(importance),
        "age": 0,
    })
    return M


def age_all(M):
    """Increment age on every memory by 1."""
    for m in M:
        m["age"] += 1
    return M


def _cosine(a, b):
    """Cosine similarity. Returns 0 if either vector is all-zero."""
    if len(a) != len(b):
        # Pad shorter with zeros
        n = max(len(a), len(b))
        a = list(a) + [0.0] * (n - len(a))
        b = list(b) + [0.0] * (n - len(b))
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def memory_impact(m, context_features):
    """
    Recall weight for a single memory given current context.
    """
    sim = _cosine(context_features, m["features"])
    # If similarity is negative (vectors point opposite), zero it — context
    # actively unrelated shouldn't have meaning here.
    if sim < 0:
        sim = 0.0
    age_term = math.exp(-config.MEM_BETA * m["age"])
    imp_term = math.exp(config.MEM_ALPHA * m["importance"])
    emo_term = math.exp(config.MEM_GAMMA * emotion_magnitude(m["emotion"]))
    return age_term * imp_term * emo_term * sim


def recall(M, context_features, top_k=3):
    """
    Returns the top_k memories by MemoryImpact, each with its impact score.
    Format: list of (memory_dict, impact_float), sorted by impact desc.
    """
    scored = [(m, memory_impact(m, context_features)) for m in M]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]


def decay_memory_emotion(M, rate):
    """
    Forgiveness operator. Each step, multiplicatively shrink the *emotion stored
    on each memory* (NOT the agent's current emotion vector — that decays in
    emotion.step_emotion). This models gradually forgetting what an event felt
    like, even if you still remember it happened.

      stored_emotion[k] *= (1 - rate)   for each emotion dim k

    rate may be either a scalar (uniform decay across emotion dims, the
    original behavior) OR a dict mapping emotion-dim → per-dim rate. Missing
    dims in the dict default to 0 (no decay) — used by exp_decay_asymmetry to
    test whether faster decay on the loyalty channel than the guilt channel
    ("forgiveness for self, not others") preserves rescue capacity across a
    chained-memory run.

    rate = 0   → no forgiveness (current behavior)
    rate = 0.01 → halves every ~70 steps
    rate = 0.05 → halves every ~14 steps
    rate = 0.20 → halves every ~3 steps  (fast forgiveness)
    """
    # Per-dim dict path (asymmetric decay)
    if isinstance(rate, dict):
        if not rate:
            return M
        # Precompute factors per dim. Missing dims → factor 1.0 (no decay).
        factors = {k: max(0.0, 1.0 - float(v)) for k, v in rate.items()}
        if all(f >= 1.0 for f in factors.values()):
            return M
        for m in M:
            for k in m["emotion"]:
                if k in factors:
                    m["emotion"][k] = m["emotion"][k] * factors[k]
        return M
    # Scalar path (legacy behavior)
    if rate <= 0.0:
        return M
    factor = max(0.0, 1.0 - rate)
    for m in M:
        for k in m["emotion"]:
            m["emotion"][k] = m["emotion"][k] * factor
    return M


def cap_store(M, capacity, context_features):
    """
    Bounded-memory eviction: keep only the top-`capacity` memories by current
    MemoryImpact score relative to `context_features`. Mutates M in place.

    Used by exp_memory_capacity to test whether bounding the memory store
    breaks the Homogenization Collapse — i.e. whether unbounded accumulation
    is the structural cause of behavioral-type collapse.

    capacity = None or capacity <= 0 → no eviction (legacy behavior).
    """
    if capacity is None or capacity <= 0:
        return M
    if len(M) <= capacity:
        return M
    scored = [(memory_impact(m, context_features), m) for m in M]
    scored.sort(key=lambda p: p[0], reverse=True)
    kept = [pair[1] for pair in scored[:capacity]]
    M.clear()
    M.extend(kept)
    return M


def guilt_recall_strength(M, context_features):
    """
    Specialized helper: returns the maximum impact across memories whose stored
    emotion has high guilt. This is what feeds ctx['guilt_recall'] in the
    emotion update.
    """
    best = 0.0
    for m in M:
        if m["emotion"].get("guilt", 0.0) > 0.4:  # was a guilt-charged memory
            impact = memory_impact(m, context_features)
            if impact > best:
                best = impact
    # Squash to [0,1] — impact can exceed 1 due to exp terms
    return min(1.0, best)


# Encoding-time tags that mark a memory as "originally guilt-charged". Used by
# guilt_recall_strength_tag_aware below.
_GUILT_TAGS = ("seed", "failure", "timeout")


def guilt_recall_strength_tag_aware(M, context_features):
    """
    Tag-aware variant of guilt_recall_strength.

    A memory qualifies as "guilt-class" if its 'tag' (set at encoding time
    by the experiment) is one of {seed, failure, timeout} — i.e. it was
    a guilt-charged event when written, regardless of how much its stored
    guilt may have decayed since.

    This isolates the "valence laundering" mechanism identified in the
    2026-05-07 memory_population_audit: under asymmetric β_guilt, failure
    memories lose their guilt class by current-state classification (their
    stored guilt drops below threshold) but their identity-of-origin is
    unchanged. Tag-aware recall pins class identity to the encoding tag, so
    if asymmetric-β divergence-erosion is driven by laundering, this mode
    should restore the symmetric-β divergence@5–9 even at high β_guilt.

    Memories without a 'tag' key fall back to the legacy criterion
    (stored.guilt > 0.4), preserving the behavior of prior experiments
    that did not tag the store.
    """
    best = 0.0
    for m in M:
        tag = m.get("tag")
        if tag is None:
            qualifies = m["emotion"].get("guilt", 0.0) > 0.4
        else:
            qualifies = tag in _GUILT_TAGS
        if qualifies:
            impact = memory_impact(m, context_features)
            if impact > best:
                best = impact
    return min(1.0, best)
