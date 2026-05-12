"""
Experiment — Jitter σ Sweep at Long Chain Length.

Two-purpose experiment, run in a single sweep at κ=2.0 (the regime where
this morning's jitter_universality experiment found the strongest
stabilization):

  1) Find the optimal encoding-jitter σ. The 2026-05-02 jitter_universality
     used σ=0.15 — chosen by intuition, not optimization. There should be a
     sweet spot: too small → no spread, collapse continues; too large →
     emotion vector saturates against [0,1] bounds, encoding signal is
     destroyed and the agent can't behaviorally distinguish outcomes.

  2) Verify the κ=2.0 stabilization holds beyond the 10-episode chains
     used in jitter_universality. If the 76% rescue rate truly is a STABLE
     equilibrium (vs a slow decay), it should hold at chain length 20.

Hypothesis:
  - σ has a sweet spot around 0.10–0.20. σ=0.0 → baseline collapse.
    σ=0.40+ → degradation as encoding signal is destroyed by noise.
  - At the optimal σ, sustained rescue rate at ep15-19 should be within a
    few pts of ep5-9 (true stabilization, not slow decay).

Design:
  T_snap=12, κ=2.0, severity=1.0, chain_length=20.
  σ values to sweep: [0.00, 0.05, 0.10, 0.20, 0.40]
  N_AGENTS = 50 per cell.
  Total: 5 × 50 × 20 = 5,000 episodes.

Headline metrics:
  - sustained rescue rate ep5–9 vs ep15–19, per σ
  - which σ maximizes ep15-19 rate?
  - is there a clean inverted-U shape vs σ?
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "jitter_sigma_long_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 2.0
SEVERITY = 1.0
SIGMAS = [0.00, 0.05, 0.10, 0.20, 0.40]
CHAIN_LENGTH = 20
N_AGENTS = 50


def run():
    rows = []
    seed = 95000
    for sigma in SIGMAS:
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
            for ep_idx in range(CHAIN_LENGTH):
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
                    "sigma": sigma,
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
