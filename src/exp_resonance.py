"""
Experiment 6 — Stochastic emotion resonance.

Hypothesis: at the bottom of the Paralysis Valley, adding small Gaussian
noise to the emotion vector each step might allow the agent to break out of
oscillation and commit. Too much noise should degrade everything (random
walk). If there is a U-shaped or peaked resonance curve, that's
classical stochastic resonance — first time inside this framework.

Design:
  T_snap = 12, severity = 1.0
  emotion_noise stddev ∈ [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
  kappa ∈ [0.0, 0.25, 0.5, 1.0, 2.0]      (cover rational, valley, committed)
  episodes_per_cell = 200
  Total = 7 * 5 * 200 = 7,000 episodes.
"""
import csv, os, random
from . import sandbox

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "resonance_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
NOISES = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4]
KAPPAS = [0.0, 0.25, 0.5, 1.0, 2.0]
EPS = 200


def run():
    rows = []
    seed = 17000
    for noise in NOISES:
        for k in KAPPAS:
            for _ in range(EPS):
                rng = random.Random(seed); seed += 1
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=k,
                    seed_memory=True, mem_severity=1.0,
                    emotion_noise=noise, rng=rng,
                )
                rows.append({
                    "noise": noise, "kappa": k,
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
