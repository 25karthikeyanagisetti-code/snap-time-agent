"""
Experiment — The Universal Recipe.

The biggest possible finding for this framework: a single architectural
recipe that rescues BOTH known failure modes across the entire (κ, σ)
phase space.

Today's results so far:
  - Encoding Diversity Effect (jitter σ=0.40) rescues the Homogenization
    Collapse at high κ. Multi-seed verified: 83.9 ± 4.2% at κ=2.0
    (3.28× baseline).
  - Encoding Diversity Effect DOES NOT rescue the Paralysis Valley
    (κ=0.25–0.5): 0% gain.
  - Softmax temperature partially rescues the κ=0.5 valley shoulder
    (33% → 43%) but DOES NOT rescue the κ=0.25 lock-in.

The Paralysis Valley at κ=0.25 is the framework's ONLY un-rescued
failure mode. Its mechanism is lock-in: the agent commits deterministically
to a non-progressive argmin Φ action and 91-100% time out without ever
moving toward the partner.

Hypothesis (the Recipe Conjecture):
  Action-level exploration (ε-greedy override, random action with
  probability ε) is the missing fix for the Paralysis Valley lock-in.
  Lower softmax temperature failed because it sharpened the locked-in
  pick. Action exploration sidesteps the entire Φ landscape — with
  probability ε the agent moves in a random direction regardless of Φ,
  forcing intermittent progress.

  If ε rescues the Paralysis Valley AND σ rescues the Homogenization
  Collapse, then the joint recipe (ε ≥ 0.20, σ ≥ 0.40) should yield
  rescue rate > 30% across the ENTIRE κ range from 0.25 to 2.0.

  That would be the strongest single claim the project can make:
  THE FRAMEWORK HAS A COMPLETE RECIPE. Both named failure modes
  have fixes, and the joint recipe yields rescue across all regimes.

Design — 4 × 4 factorial (16 cells):
  κ ∈ {0.25, 0.50, 1.00, 2.00}
  (ε, σ) ∈ {(0.0, 0.0), (0.20, 0.0), (0.0, 0.40), (0.20, 0.40)}
  N_AGENTS = 50 per cell, chain_length = 5
  Total = 4 × 4 × 50 × 5 = 4,000 episodes

Headline metrics:
  - rescue rate at each (κ, ε, σ) cell
  - is there a (ε, σ) combo where rescue rate > 30% for EVERY κ?
  - is there a clean separability — ε is the κ-low lever, σ is the
    κ-high lever, both together cover the full κ range?
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "recipe_universal_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
SEVERITY = 1.0
KAPPAS = [0.25, 0.50, 1.00, 2.00]
ES_COMBOS = [
    ("baseline",       0.00, 0.00),
    ("explore_only",   0.20, 0.00),
    ("jitter_only",    0.00, 0.40),
    ("recipe",         0.20, 0.40),
]
N_AGENTS = 50
CHAIN = 5


def run():
    rows = []
    seed = 300000
    for kappa in KAPPAS:
        for label, eps, sig in ES_COMBOS:
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
                for ep_idx in range(CHAIN):
                    r = sandbox.run_episode(
                        t_snap=T_SNAP, kappa=kappa,
                        seed_memory=False,
                        mem_severity=SEVERITY,
                        carry_memory=M,
                        encode_outcome=True,
                        encoding_jitter=sig,
                        action_exploration=eps,
                        rng=rng,
                    )
                    M = r["memory_store"]
                    rows.append({
                        "kappa": kappa,
                        "condition": label,
                        "epsilon": eps,
                        "sigma": sig,
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
