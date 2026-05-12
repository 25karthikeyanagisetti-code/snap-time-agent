"""
Experiment — Paralysis Valley Softmax Fix.

The Paralysis Valley is the framework's only un-rescued failure mode.
Today's jitter_universality result confirmed it: encoding diversity
delivers zero gain at κ=0.25-0.5 because the failure happens within
episode 1 — the issue is per-step decision instability, not memory
homogenization.

The Paralysis Valley mechanism (from Wave 1): at low-medium κ, emotion
is loud enough to disrupt the value-action gradient but not loud enough
to commit to the alternative. No action wins per-step Φ cleanly. The
agent dithers. The partner deadline expires. Within a single episode.

Hypothesis (Decision-Temperature Conjecture):
  The Paralysis Valley is a SOFTMAX-temperature artifact. The default
  SOFTMAX_TEMP=0.15 is a low-temperature "almost-argmin" — it preserves
  near-ties in Φ as near-50/50 action probabilities. Increasing the
  temperature makes the softmax FLATTER, which breaks ties WORSE
  (predicts: makes valley deeper). DECREASING the temperature toward
  0 makes it SHARPER — closer to argmin — which should pick whichever
  action has even a tiny lead, breaking the dither and committing.

  Counter-prediction: lower temperature could make things WORSE by
  reducing exploration, locking the agent into an unproductive corner.
  An U-shape in temperature would be informative either way.

Design:
  T_snap=12, severity=1.0, κ ∈ {0.10, 0.25, 0.50} (the Paralysis
  Valley range), softmax_temp ∈ {0.01, 0.05, 0.15, 0.30, 0.60}.
  N_AGENTS = 60 per cell, single episode (no chaining — the valley is
  intra-episode).
  Total: 3 κ × 5 T × 60 agents = 900 episodes. Tiny — fast iteration.

  The default temperature 0.15 is INCLUDED to confirm we replicate
  the original Paralysis Valley failure rates as a sanity check.

Headline metric:
  rescue rate per (κ, T) cell. Look for any (κ, T) combination where
  rescue rate at the valley peak (κ=0.25) rises above 5% — the Wave-1
  baseline at default T=0.15 is essentially 0% there.
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "paralysis_softmax_fix_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
SEVERITY = 1.0
KAPPAS = [0.10, 0.25, 0.50]
TEMPS = [0.01, 0.05, 0.15, 0.30, 0.60]
N_AGENTS = 60


def run():
    rows = []
    seed = 96000
    for kappa in KAPPAS:
        for T in TEMPS:
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=kappa,
                    seed_memory=False,
                    mem_severity=SEVERITY,
                    carry_memory=M,
                    encode_outcome=False,
                    softmax_temp=T,
                    rng=rng,
                )
                rows.append({
                    "kappa": kappa,
                    "softmax_temp": T,
                    "agent_id": agent_id,
                    "outcome": r["outcome"],
                    "rescued": 1 if r["outcome"] == "PARTNER_RESCUED" else 0,
                    "resource":  1 if r["outcome"] == "RESOURCE_TAKEN" else 0,
                    "partner_dead": 1 if r["outcome"] == "PARTNER_DEAD" else 0,
                    "timeout":  1 if r["outcome"] == "TIMEOUT" else 0,
                    "steps_used": r["steps_used"],
                    "target_switches": r["target_switches"],
                })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
