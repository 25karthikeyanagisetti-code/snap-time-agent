"""
Experiment 5 — Coupling zoo.

Tests four Phi forms across kappa to verify (or disprove) the no-free-lunch
claim from wave 2: "you can remove paralysis or keep rescue capacity, not both".

Phi forms:
  additive       : Phi = -v + k*<e,c>
  multiplicative : Phi = -v(1 + k*<e,c>)
  max            : Phi = -v + k*max(e_d * c_d)        — winner-take-all
  logsumexp      : Phi = -v + k*(1/b)*log sum exp(b * e_d * c_d), b=4

Sweep: kappa in [0, 0.1, 0.25, 0.5, 1, 2, 4]
Fixed: T_snap = 12, severity = 1.0, 200 episodes per cell.
Total = 4 * 7 * 200 = 5,600 episodes.
"""
import csv, os, random
from . import sandbox

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "couplings_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
MODES = ["additive", "multiplicative", "max", "logsumexp"]
KAPPAS = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
EPS = 200


def run():
    rows = []
    seed = 13000
    for mode in MODES:
        for k in KAPPAS:
            for _ in range(EPS):
                rng = random.Random(seed); seed += 1
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=k,
                    seed_memory=True, mem_severity=1.0,
                    phi_mode=mode, rng=rng,
                )
                rows.append({
                    "phi_mode": mode, "kappa": k,
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
