"""
Experiment — (κ, σ) Phase Diagram + Multi-Seed Headline Verification.

This is the consolidation experiment for the Encoding Diversity Effect
line of work. It produces two deliverables in one sweep:

  (1) A 7 × 4 (κ × σ) phase diagram of sustained rescue rate in the
      chained-memory regime. The phase diagram should reveal:
        - The Paralysis Valley region at κ ≤ 0.5 (low rescue across all σ)
        - The Homogenization Collapse region at κ ≥ 1.0, σ = 0
          (committed regime that collapses without jitter)
        - The Encoding Diversity Rescue zone at κ ≥ 1.0, σ ≥ 0.10
          (where jitter restores the committed regime)
      One figure that summarises every regime finding from the last 24 hours.

  (2) Multi-seed verification of the headline cell. The 2026-05-02
      jitter_sigma_long_v1 finding (σ=0.40 at κ=2.0 → 85% sustained rescue
      at long horizons) is the project's strongest single claim. It was
      single-seed. For research credibility we need error bars.
      → 5 independent seeds × 30 agents × 10 episodes = 1,500 episodes
      → mean ± std across the 5 seed-replicates at exactly that cell.

Hypothesis for the phase diagram:
  Sustained rescue rate R(κ, σ) ≈ separates into two regimes:
    Low κ:  R(κ, σ) ≈ 0 for any σ        (Paralysis Valley insensitive to σ)
    High κ: R(κ, σ) grows monotonically in σ until plateau
  If true, the phase diagram should look like a 2D step in the
  high-κ × high-σ corner.

Hypothesis for the multi-seed verification:
  The σ=0.40 κ=2.0 cell yields mean sustained rescue rate (ep5–9) ≥ 70%
  with standard deviation across seeds ≤ 10 pts (i.e., the headline is
  not an artifact of one favorable seed).

Design:
  T_snap=12, severity=1.0.
  PHASE GRID:
    κ ∈ {0.10, 0.25, 0.50, 1.00, 1.50, 2.00, 3.00}
    σ ∈ {0.00, 0.10, 0.20, 0.40}
    N_AGENTS_GRID = 25 per cell, chain_length = 5
    → 7 × 4 × 25 × 5 = 3,500 episodes
  MULTI-SEED HEADLINE:
    κ = 2.0, σ = 0.40
    5 seed groups × 30 agents × 10 episodes = 1,500 episodes
  TOTAL: 5,000 episodes (at the cap)

Headline metrics:
  - Phase diagram: sustained rescue rate, avg ep3-4, per cell
  - Multi-seed: mean ± std of sustained rescue rate ep5-9 across 5 seeds
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "phase_diagram_kappa_sigma_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_GRID = os.path.join(OUT_DIR, "results_grid.csv")
OUT_SEED = os.path.join(OUT_DIR, "results_seedverify.csv")

T_SNAP = 12
SEVERITY = 1.0

GRID_KAPPAS = [0.10, 0.25, 0.50, 1.00, 1.50, 2.00, 3.00]
GRID_SIGMAS = [0.00, 0.10, 0.20, 0.40]
GRID_N_AGENTS = 25
GRID_CHAIN = 5

VERIFY_KAPPA = 2.0
VERIFY_SIGMA = 0.40
VERIFY_N_SEEDS = 5
VERIFY_N_AGENTS = 30
VERIFY_CHAIN = 10


def run():
    # --- Phase diagram ---
    grid_rows = []
    seed = 100000
    for kappa in GRID_KAPPAS:
        for sigma in GRID_SIGMAS:
            for agent_id in range(GRID_N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
                for ep_idx in range(GRID_CHAIN):
                    r = sandbox.run_episode(
                        t_snap=T_SNAP, kappa=kappa,
                        seed_memory=False,
                        mem_severity=SEVERITY,
                        carry_memory=M,
                        encode_outcome=True,
                        encoding_jitter=sigma,
                        rng=rng,
                    )
                    M = r["memory_store"]
                    grid_rows.append({
                        "kappa": kappa, "sigma": sigma,
                        "agent_id": agent_id, "episode_idx": ep_idx,
                        "outcome": r["outcome"],
                        "rescued": 1 if r["outcome"] == "PARTNER_RESCUED" else 0,
                    })
    with open(OUT_GRID, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=grid_rows[0].keys())
        w.writeheader(); w.writerows(grid_rows)
    print(f"Wrote {len(grid_rows)} grid rows to {OUT_GRID}")

    # --- Multi-seed verification at headline cell ---
    seed_rows = []
    base_seed = 200000
    for seed_group in range(VERIFY_N_SEEDS):
        # Each seed group uses a disjoint RNG stream
        seed_g = base_seed + seed_group * 100000
        for agent_id in range(VERIFY_N_AGENTS):
            rng = random.Random(seed_g); seed_g += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
            for ep_idx in range(VERIFY_CHAIN):
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=VERIFY_KAPPA,
                    seed_memory=False,
                    mem_severity=SEVERITY,
                    carry_memory=M,
                    encode_outcome=True,
                    encoding_jitter=VERIFY_SIGMA,
                    rng=rng,
                )
                M = r["memory_store"]
                seed_rows.append({
                    "seed_group": seed_group,
                    "agent_id": agent_id,
                    "episode_idx": ep_idx,
                    "outcome": r["outcome"],
                    "rescued": 1 if r["outcome"] == "PARTNER_RESCUED" else 0,
                })
    with open(OUT_SEED, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=seed_rows[0].keys())
        w.writeheader(); w.writerows(seed_rows)
    print(f"Wrote {len(seed_rows)} seed-verify rows to {OUT_SEED}")


if __name__ == "__main__":
    run()
