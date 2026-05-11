"""
Experiment — Memory Capacity.

The Big Question.

Every prior chained-memory experiment in this project has documented a
failure mode: behavioral types collapse, the Homogenization Collapse holds,
selective encoding doesn't save it, valenced encoding makes it worse. The
single open structural variable left untested is the size of the memory
store itself. Every prior run used unbounded memory.

Hypothesis:
  The Homogenization Collapse is NOT a fundamental property of the
  framework. It is an artifact of unbounded memory accumulation. Capping
  the store with least-impact eviction will produce ACTUAL behavioral
  types — agents who happen to rescue early should accumulate
  loyalty-rich stores and remain rescue-prone; agents who fail should
  accumulate guilt-rich stores and stay paralyzed. The two populations
  will diverge instead of converge.

If true, this is the framework's first POSITIVE finding and inverts the
standard ML wisdom that more memory is always better.

Design:
  T_snap = 12, severity = 1.0, kappa = 1.0 (committed regime).
  capacities to sweep: [2, 3, 5, 10, 9999]   (9999 = effectively unbounded)
  chain_length = 10 episodes, n_agents per cap = 100.
  Total = 5 * 100 * 10 = 5,000 episodes.

Headline metric:
  divergence@5–9 := rescue_rate(succeeded ep1) - rescue_rate(failed ep1),
  averaged across episodes 5..9.
  PRIOR baseline (Wave 3 hysteresis, unbounded): ≈ -10 pts (anti-types)
  Hypothesis prediction: small capacity → +20 pts or more (real types).
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "memory_capacity_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
CHAIN_LENGTH = 10
N_AGENTS = 100
CAPACITIES = [2, 3, 5, 10, 9999]


def run():
    rows = []
    seed = 92000
    for cap in CAPACITIES:
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=1.0, preage=15)
            for ep_idx in range(CHAIN_LENGTH):
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=KAPPA,
                    seed_memory=False,
                    carry_memory=M,
                    encode_outcome=True,
                    mem_capacity=cap,
                    rng=rng,
                )
                M = r["memory_store"]
                rows.append({
                    "capacity": cap,
                    "agent_id": agent_id,
                    "episode_idx": ep_idx,
                    "outcome": r["outcome"],
                    "rescued": 1 if r["outcome"] == "PARTNER_RESCUED" else 0,
                    "n_memories": len(M),
                    "target_switches": r["target_switches"],
                })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
