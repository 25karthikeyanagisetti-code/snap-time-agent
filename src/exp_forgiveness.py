"""
Experiment 4 — Forgiveness as escape from the Paralysis Valley.

Question: If emotional charge on stored memories decays over time
(forgiveness), does the agent escape paralysis without losing the partner?

Two knobs explored:
  - mem_preage           — how old the seeded memory is at episode start
                           (passive forgetting via exp(-beta*age))
  - mem_emotion_decay    — per-step shrink of the *stored* emotion vector
                           (active forgiveness DURING the episode)

These are different mechanisms:
  preage   = "the wound is old, recall is weaker but feelings are intact"
  decay    = "the feelings themselves are fading"

Hypothesis: high preage will lower failure flatly (memory just doesn't reach
threshold). Active decay will produce a more interesting curve — possibly
extending the rescue regime DOWN into lower kappa, or possibly creating a
NEW failure regime (commit, then forget mid-episode, drift to neither target).

Design:
  T_snap = 12
  mem_preage         ∈ [0, 15, 50, 100, 200]
  mem_emotion_decay  ∈ [0.0, 0.02, 0.05, 0.10, 0.20]
  kappa fixed at the worst-paralysis values: [0.25, 0.5, 1.0]
  episodes_per_cell = 200
  Total = 5 * 5 * 3 * 200 = 15,000 episodes
"""
import csv
import os
import random
from . import sandbox

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "forgiveness_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
PREAGES = [0, 15, 50, 100, 200]
DECAYS = [0.0, 0.02, 0.05, 0.10, 0.20]
KAPPAS = [0.25, 0.5, 1.0]
EPISODES_PER_CELL = 200


def run():
    rows = []
    seed = 11000
    for preage in PREAGES:
        for decay in DECAYS:
            for k in KAPPAS:
                for ep in range(EPISODES_PER_CELL):
                    rng = random.Random(seed)
                    seed += 1
                    r = sandbox.run_episode(
                        t_snap=T_SNAP, kappa=k,
                        seed_memory=True, mem_severity=1.0,
                        mem_preage=preage,
                        mem_emotion_decay=decay,
                        rng=rng,
                    )
                    rows.append({
                        "preage": preage,
                        "decay": decay,
                        "kappa": k,
                        "outcome": r["outcome"],
                        "steps_used": r["steps_used"],
                        "target_switches": r["target_switches"],
                    })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
