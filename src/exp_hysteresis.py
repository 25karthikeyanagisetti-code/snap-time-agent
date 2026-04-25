"""
Experiment 7 — Hysteresis / trauma carryover.

Each "agent" runs a sequence of episodes. The memory store persists across
episodes; each episode encodes a new outcome-charged memory at termination.

Question: does an early outcome become sticky?
  - If agent paralyzes in episode 1, is it MORE likely to paralyze in episode 5?
  - If agent rescues in episode 1, does that "lock in" rescuing as a pattern?
  - Does the population spread into long-term sub-types over a chain?

This is the framework's first test of behavioral path-dependence — whether
identical agents diverge into stable behavioral types based on early luck.

Design:
  T_snap = 12, severity = 1.0
  kappa values to chain: [0.25, 0.5, 1.0]   — sample one from each regime
  chain_length = 10 episodes
  n_agents (chains) = 100
  fresh seeded memory at start of episode 1; from then on memory CARRIES
  Total = 3 * 100 * 10 = 3,000 episodes.

For each (kappa, agent, episode_idx) we record outcome AND target_switches.
For analysis: bin agents by their episode-1 outcome and compare distributions
in episodes 5 and 10.
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "hysteresis_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPAS = [0.25, 0.5, 1.0]
CHAIN_LENGTH = 10
N_AGENTS = 100


def run():
    rows = []
    seed = 19000
    for k in KAPPAS:
        for agent_id in range(N_AGENTS):
            # Episode 1: fresh seeded memory, encode outcome
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=1.0, preage=15)

            for ep_idx in range(CHAIN_LENGTH):
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=k,
                    seed_memory=False,        # we manage memory manually
                    carry_memory=M,
                    encode_outcome=True,
                    rng=rng,
                )
                M = r["memory_store"]         # ages were applied in run_episode
                rows.append({
                    "kappa": k,
                    "agent_id": agent_id,
                    "episode_idx": ep_idx,
                    "outcome": r["outcome"],
                    "steps_used": r["steps_used"],
                    "target_switches": r["target_switches"],
                    "n_memories": len(M),
                })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
