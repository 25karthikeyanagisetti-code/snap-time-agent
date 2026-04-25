"""
Experiment 3 — Multiplicative Phi formulation.

Question: Is the Paralysis Valley a property of the additive coupling
Phi = -value + kappa * <emotion, conflict>, or does it survive a different
mathematical formulation?

If a multiplicative coupling (Phi = -value * (1 + kappa*<emo, conflict>))
removes the valley, then "small emotion paralyzes" was a feature of the
algebra, not the architecture.

If the valley survives or moves, that's a stronger architectural claim:
emotion + bounded deliberation has an inherent indecision regime.

Design:
  T_snap = 12
  phi_mode ∈ {additive, multiplicative}
  kappa    ∈ [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
  episodes_per_cell = 200
  Total = 2 * 7 * 200 = 2,800 episodes
"""
import csv
import os
import random
from . import sandbox

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "phi_mode_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
PHI_MODES = ["additive", "multiplicative"]
KAPPAS = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
EPISODES_PER_CELL = 200


def run():
    rows = []
    seed = 9000
    for mode in PHI_MODES:
        for k in KAPPAS:
            for ep in range(EPISODES_PER_CELL):
                rng = random.Random(seed)
                seed += 1
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=k,
                    seed_memory=True, mem_severity=1.0,
                    phi_mode=mode,
                    rng=rng,
                )
                rows.append({
                    "phi_mode": mode,
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
