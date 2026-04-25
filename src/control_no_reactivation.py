"""
Control experiment: keep the seeded memory in the store, but disable the
reactivation gain so memory exists but does NOT bleed emotion into e_t.

If the paralysis valley persists -> failure is from memory's MERE PRESENCE.
If the paralysis valley disappears -> failure is specifically from emotional
reactivation (the contextual recall mechanism).

Run: python -m src.control_no_reactivation
"""

import csv
import os
import random
from . import sandbox, config

T_SNAP_VALUES = [8, 12, 20]
KAPPA_VALUES = [0.0, 0.25, 0.5, 1.0, 2.0]
N_EPISODES = 200

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "regime_map_v1", "control_no_reactivation.csv"
)


def run():
    # Save original gain, then disable
    original_gain = config.REACTIVATION_GAIN
    config.REACTIVATION_GAIN = 0.0
    try:
        rows = []
        for t_snap in T_SNAP_VALUES:
            for kappa in KAPPA_VALUES:
                outcomes = []
                switches = []
                for ep in range(N_EPISODES):
                    res = sandbox.run_episode(
                        t_snap=t_snap, kappa=kappa, seed_memory=True,
                        rng=random.Random(ep + hash((t_snap, kappa)) & 0xFFFF)
                    )
                    outcomes.append(res["outcome"])
                    switches.append(res["target_switches"])
                rescue = sum(1 for o in outcomes if o == "PARTNER_RESCUED") / N_EPISODES
                resource = sum(1 for o in outcomes if o == "RESOURCE_TAKEN") / N_EPISODES
                timeout = sum(1 for o in outcomes if o == "TIMEOUT") / N_EPISODES
                pdead = sum(1 for o in outcomes if o == "PARTNER_DEAD") / N_EPISODES
                hesit = sum(1 for s in switches if s >= 1) / N_EPISODES
                rows.append({
                    "t_snap": t_snap, "kappa": kappa,
                    "rescue": rescue, "resource": resource,
                    "timeout": timeout, "partner_dead": pdead,
                    "failure": timeout + pdead, "hesitation": hesit,
                })
                print(f"  T={t_snap} kappa={kappa} -> failure={timeout + pdead:.2f} hesit={hesit:.2f}")
    finally:
        config.REACTIVATION_GAIN = original_gain

    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    run()
