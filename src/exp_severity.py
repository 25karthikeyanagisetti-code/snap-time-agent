"""
Experiment 2 — Memory severity sweep.

Question: Does the Paralysis Valley shift, deepen, or vanish as the seeded
memory's emotional intensity changes?

Hypothesis (pre-registered): The valley should be present at moderate severity
but disappear at very low severity (no real conflict) and possibly compress at
very high severity (commit-or-die). If it does NOT disappear at low severity,
that's a finding — paralysis would be cheap.

Design:
  T_snap = 12 (fixed — that's where v1 valley is sharpest)
  mem_severity ∈ [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]   # scales seeded guilt/loyalty
  kappa        ∈ [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
  episodes_per_cell = 200
  Total episodes = 6 * 7 * 200 = 8,400
"""
import csv
import os
import random
from . import sandbox

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "severity_sweep_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
SEVERITIES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
KAPPAS = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
EPISODES_PER_CELL = 200


def run():
    rows = []
    seed = 7000
    for sev in SEVERITIES:
        for k in KAPPAS:
            for ep in range(EPISODES_PER_CELL):
                rng = random.Random(seed)
                seed += 1
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=k,
                    seed_memory=(sev > 0.0),
                    mem_severity=sev,
                    rng=rng,
                )
                rows.append({
                    "severity": sev,
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
