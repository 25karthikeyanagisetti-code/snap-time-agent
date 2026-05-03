"""
Experiment 9 — Valenced Encoding.

Hypothesis (from research_backlog.md):
  Encoding loyalty memories on RESCUE (not just guilt on failure) restores
  behavioral types. Population should DIVERGE — agents who happen to rescue
  early should encode a positive memory and remain rescue-prone, while agents
  who fail should encode guilt and stay paralyzed.

Why this is worth testing:
  The Wave-3 Homogenization Collapse used positive_encoding=ON (the default).
  Behavioral types collapsed anyway — committed-rescuer regime evaporated in
  ONE episode. The hypothesis being tested here is essentially the
  counter-claim: that the loyalty channel IS doing useful work, and turning
  it OFF should make collapse even worse (or at minimum, change its shape).
  The selective_encoding null (2026-05-01) showed magnitude-gating doesn't
  rescue divergence; this experiment asks whether the rescue-side encoding
  channel matters at all.

Design:
  T_snap = 12, severity = 1.0, kappa = 1.0 (committed regime — where
  Wave 3 saw the strongest collapse: 78% → 17% in one episode).
  Two conditions:
    OFF: positive_encoding=False  (only guilt-on-failure encoded; rescue
                                   leaves the memory store unchanged)
    ON:  positive_encoding=True   (current behavior — both encoded)
  chain_length = 10 episodes.
  n_agents per condition = 100.
  Total = 2 * 100 * 10 = 2,000 episodes.

Headline metric:
  divergence@ep9 := rescue_rate(agents who rescued in ep1)
                  - rescue_rate(agents who failed in ep1)
  averaged across episodes 5..9 for stability.
  Compute under each condition. If hypothesis holds: ON > OFF substantially.
  If null: |ON - OFF| < ~5pts.
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "valenced_encoding_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
CHAIN_LENGTH = 10
N_AGENTS = 100
CONDITIONS = [("off", False), ("on", True)]


def run():
    rows = []
    seed = 91000
    for cond_name, pos_enc in CONDITIONS:
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
                    positive_encoding=pos_enc,
                    rng=rng,
                )
                M = r["memory_store"]
                rows.append({
                    "condition": cond_name,
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
