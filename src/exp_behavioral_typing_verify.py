"""
Experiment — Multi-Seed Verification of the Behavioral Typing Finding.

The 2026-05-29 per-agent re-analysis of jitter_sigma_long_v1 revealed
the project's biggest finding: at κ=2.0, σ=0.40, over 20 chained
episodes, 86% of agents become behavioral rescuers (rescue ≥15 of 20
episodes) and 0% become behavioral failures (rescue ≤4). At σ=0
baseline: 0% rescuers, 10% failures, 64% middling.

That re-analysis was single-seed (the original jitter_sigma_long_v1
ran with one RNG seed). For research-paper credibility, we need to
verify the behavioral typing claim survives multi-seed replication.

Hypothesis:
  Across 5 independent seed groups, σ=0.40 produces:
    - mean rescuer rate (% with ≥15/20 rescues) ≥ 70% with SD ≤ 10pts
    - mean failure rate (% with ≤4/20 rescues) ≤ 5%
  Across 5 independent seed groups, σ=0 produces:
    - mean rescuer rate ≤ 10%
    - mean failure rate ≥ 5%
  The separation between conditions is reproducible and the effect
  size is not driven by a single lucky seed.

Design:
  T_snap=12, κ=2.0, severity=1.0, chain_length=20.
  2 conditions × 5 seed groups × 25 agents × 20 episodes = 5,000 episodes.
  Each seed group uses a disjoint RNG stream.

Headline metrics, per condition:
  - mean ± SD of "rescuer rate" across 5 seed groups
  - mean ± SD of "failure rate" across 5 seed groups
  - 95% CI on rescuer rate
  - separation: rescuer rate (σ=0.40) - rescuer rate (σ=0)
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "behavioral_typing_verify_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 2.0
SEVERITY = 1.0
CONDITIONS = [
    ("control",   0.00),
    ("treatment", 0.40),
]
N_SEED_GROUPS = 5
N_AGENTS = 25
CHAIN = 20


def run():
    rows = []
    base_seed = 400000
    for cond_label, sigma in CONDITIONS:
        for seed_group in range(N_SEED_GROUPS):
            seed = base_seed + seed_group * 100000
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
                for ep_idx in range(CHAIN):
                    r = sandbox.run_episode(
                        t_snap=T_SNAP, kappa=KAPPA,
                        seed_memory=False,
                        mem_severity=SEVERITY,
                        carry_memory=M,
                        encode_outcome=True,
                        encoding_jitter=sigma,
                        rng=rng,
                    )
                    M = r["memory_store"]
                    rows.append({
                        "condition": cond_label,
                        "sigma": sigma,
                        "seed_group": seed_group,
                        "agent_id": agent_id,
                        "episode_idx": ep_idx,
                        "outcome": r["outcome"],
                        "rescued": 1 if r["outcome"] == "PARTNER_RESCUED" else 0,
                    })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
