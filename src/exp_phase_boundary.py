"""
Experiment 8 — Phase boundary at high resolution.

The original sweep used 7 kappa points spanning 4 orders of magnitude.
We saw a sharp valley but with only 2 points inside it (k=0.25, k=0.5).
This sweep zooms in on the boundary with 41 kappa points across 0..1.0.

Design:
  T_snap ∈ [8, 12, 20]                   — three time horizons
  severity = 1.0
  kappa = linspace(0.0, 1.0, 41)         — high resolution
  episodes_per_cell = 200
  Total = 3 * 41 * 200 = 24,600 episodes.

Looking for:
  - Is the descent smooth or step-like?
  - Where exactly is the failure peak?
  - Does the peak shift with T_snap?
"""
import csv, os, random
from . import sandbox

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "phase_boundary_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAPS = [8, 12, 20]
KAPPAS = [round(i / 40.0, 4) for i in range(41)]  # 0.000 .. 1.000 step 0.025
EPS = 200


def run():
    rows = []
    seed = 23000
    for t_snap in T_SNAPS:
        for k in KAPPAS:
            for _ in range(EPS):
                rng = random.Random(seed); seed += 1
                r = sandbox.run_episode(
                    t_snap=t_snap, kappa=k,
                    seed_memory=True, mem_severity=1.0,
                    rng=rng,
                )
                rows.append({
                    "t_snap": t_snap, "kappa": k,
                    "outcome": r["outcome"],
                    "steps_used": r["steps_used"],
                    "target_switches": r["target_switches"],
                })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
