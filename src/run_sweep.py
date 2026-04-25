"""
Sweep driver for the regime_map_v1 experiment.

Sweeps T_snap and kappa over the Rescue-vs-Resource sandbox. For each
(T_snap, kappa) cell, runs N_EPISODES with seeded abandonment memory and
N_EPISODES with no memory (control). Logs everything to results.csv.

Usage:
    python -m src.run_sweep
"""

import csv
import os
import random
import time

from . import sandbox

T_SNAP_VALUES = [3, 5, 8, 12, 20, 40]
KAPPA_VALUES = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
N_EPISODES = 200

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "regime_map_v1"
)


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "results.csv")
    t0 = time.time()

    fields = [
        "t_snap", "kappa", "seeded_memory", "episode",
        "outcome", "steps_used", "target_switches",
        "final_survival", "final_guilt", "final_loyalty",
        "final_fear", "final_curiosity",
    ]

    total_cells = len(T_SNAP_VALUES) * len(KAPPA_VALUES) * 2  # x2 for memory on/off
    cell_idx = 0
    rows = []

    for t_snap in T_SNAP_VALUES:
        for kappa in KAPPA_VALUES:
            for seed_mem in (True, False):
                cell_idx += 1
                rng = random.Random(hash((t_snap, kappa, seed_mem)) & 0xFFFFFFFF)
                for ep in range(N_EPISODES):
                    res = sandbox.run_episode(
                        t_snap=t_snap,
                        kappa=kappa,
                        seed_memory=seed_mem,
                        rng=random.Random(rng.random()),
                    )
                    rows.append({
                        "t_snap": t_snap,
                        "kappa": kappa,
                        "seeded_memory": int(seed_mem),
                        "episode": ep,
                        "outcome": res["outcome"],
                        "steps_used": res["steps_used"],
                        "target_switches": res["target_switches"],
                        "final_survival": res["final_emotion"]["survival"],
                        "final_guilt": res["final_emotion"]["guilt"],
                        "final_loyalty": res["final_emotion"]["loyalty"],
                        "final_fear": res["final_emotion"]["fear"],
                        "final_curiosity": res["final_emotion"]["curiosity"],
                    })
                print(
                    f"  cell {cell_idx}/{total_cells} done — "
                    f"T_snap={t_snap} kappa={kappa} seeded={seed_mem}"
                )

    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    dt = time.time() - t0
    print(f"\nDone. {len(rows)} episodes in {dt:.1f}s. Wrote {out_path}")


if __name__ == "__main__":
    run()
