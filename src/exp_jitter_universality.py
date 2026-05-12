"""
Experiment — Jitter Universality (the regime-coupling test for the Encoding
Diversity Effect).

The 2026-05-02 personality_emergence experiment found that per-agent
encoding noise (σ=0.15 Gaussian on encoded emotion) yields a 2.55×
sustained rescue rate at κ=1.0 — partially undoing the Wave-3
Homogenization Collapse.

That finding is regime-local: tested only at κ=1.0. The structural
question this leaves open is whether encoder homogeneity is a property
of the κ=1.0 collapse specifically, or whether it is the common
substrate of MULTIPLE collapse modes in this framework.

Hypothesis (the Universality Conjecture):
  Encoder homogeneity is the substrate of every population-level
  collapse mode in this framework. Per-agent encoding jitter should
  therefore rescue:
    - The Homogenization Collapse at κ=1.0 (already shown: 15% → 39%)
    - The Paralysis Valley at κ=0.25–0.5 (Wave-1 finding)
    - Should not noticeably help in regimes that don't collapse
      anyway (κ≈0 rational regime, κ=2+ saturated-committed regime)

If this holds, encoder homogeneity unifies the framework's two named
failure modes under a single mechanism — and the Encoding Diversity
Effect is no longer a quirky local fix; it's a structural prescription
for the entire collapse landscape.

Design:
  T_snap=12, severity=1.0, chain_length=10.
  κ values to sweep: [0.1, 0.25, 0.5, 1.0, 2.0]
  jitter values:     [0.0, 0.15]
  N_AGENTS = 50 per cell.
  Total: 5 × 2 × 50 × 10 = 5,000 episodes.

Headline metric:
  Per-κ sustained rescue rate (avg ep5–9), jitter ON vs OFF.
  Per-κ gain in pts.
  Pattern prediction: jitter helps most where collapse is deepest
  (κ ∈ {0.25, 0.5} — Paralysis Valley, and κ=1.0 — Homogenization
  Collapse), and minimally elsewhere.
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "jitter_universality_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
SEVERITY = 1.0
KAPPAS = [0.1, 0.25, 0.5, 1.0, 2.0]
JITTERS = [0.0, 0.15]
CHAIN_LENGTH = 10
N_AGENTS = 50


def run():
    rows = []
    seed = 94000
    for kappa in KAPPAS:
        for jit in JITTERS:
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
                for ep_idx in range(CHAIN_LENGTH):
                    r = sandbox.run_episode(
                        t_snap=T_SNAP, kappa=kappa,
                        seed_memory=False,
                        mem_severity=SEVERITY,
                        carry_memory=M,
                        encode_outcome=True,
                        encoding_jitter=jit,
                        rng=rng,
                    )
                    M = r["memory_store"]
                    rows.append({
                        "kappa": kappa,
                        "encoding_jitter": jit,
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
