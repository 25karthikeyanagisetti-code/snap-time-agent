"""
Sanity checks on emotion + memory dynamics.
Run with: python -m tests.test_emotion_updates
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import emotion, memory


def test_init_neutral():
    e = emotion.init_emotion()
    assert all(v == 0.0 for v in e.values())
    print("OK: init neutral")


def test_decay_on_quiet_step():
    e = {"survival": 0.5, "guilt": 0.5, "loyalty": 0.5, "fear": 0.5, "curiosity": 0.5}
    e2 = emotion.step_emotion(e, ctx={})
    for v in e2.values():
        assert v < 0.5, f"expected decay, got {v}"
    print("OK: decay on quiet step")


def test_survival_responds_to_pressure():
    e = emotion.init_emotion()
    for _ in range(10):
        e = emotion.step_emotion(e, {"time_pressure": 1.0})
    assert e["survival"] > 0.3, f"survival should rise under pressure, got {e['survival']}"
    print("OK: survival responds to pressure")


def test_clipping():
    e = emotion.init_emotion()
    for _ in range(100):
        e = emotion.step_emotion(e, {"time_pressure": 1.0, "guilt_recall": 1.0,
                                     "partner_adjacent": 1.0, "threat": 1.0,
                                     "novelty": 1.0})
    for k, v in e.items():
        assert 0.0 <= v <= 1.0, f"{k} out of range: {v}"
    print("OK: clipping holds under sustained input")


def test_memory_aging_decays_impact():
    M = memory.init_store()
    e_charged = {"survival": 0.0, "guilt": 0.9, "loyalty": 0.5, "fear": 0.0, "curiosity": 0.0}
    feats = [1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0]
    memory.encode(M, feats, e_charged, importance=0.9)
    impact_fresh = memory.memory_impact(M[0], feats)
    for _ in range(50):
        memory.age_all(M)
    impact_old = memory.memory_impact(M[0], feats)
    assert impact_old < impact_fresh, f"old should be lower; fresh={impact_fresh}, old={impact_old}"
    print(f"OK: aging decays impact (fresh={impact_fresh:.3f}, old={impact_old:.3f})")


def test_similarity_zero_kills_recall():
    M = memory.init_store()
    e_charged = {"survival": 0.0, "guilt": 0.9, "loyalty": 0.5, "fear": 0.0, "curiosity": 0.0}
    feats_a = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    feats_b = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    memory.encode(M, feats_a, e_charged, importance=0.9)
    impact = memory.memory_impact(M[0], feats_b)
    assert impact == 0.0, f"all-zero context should give zero impact, got {impact}"
    print("OK: zero-similarity context gives zero impact")


if __name__ == "__main__":
    test_init_neutral()
    test_decay_on_quiet_step()
    test_survival_responds_to_pressure()
    test_clipping()
    test_memory_aging_decays_impact()
    test_similarity_zero_kills_recall()
    print("\nAll tests passed.")
