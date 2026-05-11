"""
Experiment — Personality Emergence (the 2x2 that should answer the big question).

This experiment is the synthesis of every chained-memory result so far.

Wave 3's Homogenization Collapse showed that with unbounded memory and
identical encoding, all initial conditions converge to the same failure
attractor — no behavioral types emerge from experience. Selective encoding
(2026-05-01), valenced encoding (2026-05-02), and bounded memory (today's
exp_memory_capacity) all FAILED to break this. The collapse keeps holding
across architectural variations of the memory system.

But every prior chained run has held one variable IDENTICAL across the
population: the encoding function. Each agent encodes the same outcome with
the same emotion vector. The agents differ only in softmax-noise random
draws — micro-noise on action selection, not macro-noise on identity.

Hypothesis (the Joint-Sufficiency Conjecture):
  Behavioral types from experience require BOTH (a) bounded memory AND
  (b) per-agent encoding diversity. Either alone is insufficient. Together
  they are the minimal sufficient condition for the framework to produce
  behavioral types — agents who happen to rescue early should accumulate
  loyalty-weighted memory profiles that diverge persistently from agents
  who fail.

Design — 2x2 factorial:
  bounded ∈ {OFF (mem_capacity=∞), ON (mem_capacity=3)}
  jitter  ∈ {OFF (0.0), ON (0.15 stddev Gaussian on encoded emotion)}
  4 cells × 100 agents × 10 chained episodes = 4,000 episodes total.

  T_snap=12, kappa=1.0, severity=1.0 — the committed regime where
  Wave-3 saw the most dramatic collapse (78% → 17% in one episode).

Headline metric:
  divergence@5–9 := rescue_rate(succeeded ep1) - rescue_rate(failed ep1),
  averaged across episodes 5..9.
  Hypothesis prediction:
    OFF/OFF (baseline, Wave 3):        ~0 pts (collapse, possibly negative)
    ON /OFF (today's mem_cap):         ~0 pts (already shown null)
    OFF/ON (jitter alone):             small positive
    ON /ON (BOTH):                     >+15 pts (true behavioral types)
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "personality_emergence_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
CHAIN_LENGTH = 10
N_AGENTS = 100
CONDITIONS = [
    # (label, mem_capacity, encoding_jitter)
    ("baseline",         9999, 0.00),  # unbounded, no jitter (Wave-3 default)
    ("bounded_only",        3, 0.00),  # bounded memory only
    ("jitter_only",      9999, 0.15),  # encoding jitter only
    ("bounded_and_jitter",  3, 0.15),  # the joint hypothesis
]


def run():
    rows = []
    seed = 93000
    for label, cap, jit in CONDITIONS:
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
                    encoding_jitter=jit,
                    rng=rng,
                )
                M = r["memory_store"]
                rows.append({
                    "condition": label,
                    "mem_capacity": cap,
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
