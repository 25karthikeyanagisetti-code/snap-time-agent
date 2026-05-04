"""
Experiment 12 — Loyalty Importance Floor.

Hypothesis (from research_backlog.md):
  Reducing the rescue-side encoding importance (from the default 0.7 toward
  0) recovers a benefit from the loyalty channel WITHOUT triggering the
  Loyalty Boomerang (valenced_encoding, 2026-05-02). The boomerang showed
  that turning rescue-side encoding fully ON (importance=0.7) cut ep9 rescue
  rate roughly in half versus turning it OFF (15% vs 28%). The interpretation
  was that rescue memories at importance 0.7 over-saturate the recall
  competition. If true, dialing rescue_importance down toward 0 should
  produce a U-shape or a monotone improvement: ep9 rescue rate climbing as
  rescue_importance falls, eventually meeting (or beating) the OFF baseline.

Why this is worth testing:
  The valenced experiment treated rescue-encoding as a binary switch. The
  question this run actually asks: is there a "low-volume loyalty signal"
  regime where the agent benefits from a rescue memory existing in the store
  without being dominated by it? If we see a sweet-spot at rescue_importance
  ∈ (0, 0.7) — a nonmonotone curve — that is novel and bounds the boomerang.
  If the curve is monotone-flat (no benefit at any importance), the
  boomerang is structural and lowering importance only attenuates harm.

Sandbox extension:
  sandbox.run_episode now takes rescue_importance (default 0.7, preserves
  prior behavior). When positive_encoding=True and outcome=PARTNER_RESCUED,
  the encoded memory's importance is set from this parameter rather than
  the previous hard-coded 0.7. Failure-side importance (0.85) is unchanged.

Design:
  T_snap = 12, severity = 1.0, kappa = 1.0  (committed regime — where
  Wave-3 saw the strongest collapse and the boomerang appeared).
  rescue_importance ∈ {0.0, 0.1, 0.3, 0.5, 0.7}
  positive_encoding = True throughout (the whole point is to keep encoding
                                        on while throttling its strength).
  chain_length = 10
  n_agents     = 100
  Total = 5 * 100 * 10 = 5,000 episodes (at the cap).

Headline metric:
  ep9 rescue rate, population-averaged, per cell.
  Secondary: ep0 rescue rate, mean memory store size at ep9, divergence@5–9
             := rescue_rate(ep1_rescuers) - rescue_rate(ep1_non_rescuers).

Expected pattern under hypothesis:
  ep9 rescue rate INCREASES as rescue_importance DECREASES. The cell at
  rescue_importance=0.0 should approach the valenced "OFF" baseline (~28%)
  while remaining nominally within the positive-encoding regime.
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "loyalty_importance_floor_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
RESCUE_IMPORTANCES = [0.0, 0.1, 0.3, 0.5, 0.7]
CHAIN_LENGTH = 10
N_AGENTS = 100


def run():
    rows = []
    seed = 53000
    for rim in RESCUE_IMPORTANCES:
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
                    positive_encoding=True,
                    rescue_importance=rim,
                    rng=rng,
                )
                M = r["memory_store"]
                rows.append({
                    "rescue_importance": rim,
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
