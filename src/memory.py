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

    rate = 0   → no forgiveness (current behavior)
    rate = 0.01 → halves every ~70 steps
    rate = 0.05 → halves every ~14 steps
    rate = 0.20 → halves every ~3 steps  (fast forgiveness)
    """
    if rate <= 0.0:
        return M
    factor = max(0.0, 1.0 - rate)
    for m in M:
        for k in m["emotion"]:
            m["emotion"][k] = m["emotion"][k] * factor
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
