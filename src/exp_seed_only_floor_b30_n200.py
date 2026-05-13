"""
Experiment 24 — Seed-Only Floor Ablation: β_guilt=0.30 N=200 replication.

Hypothesis (top of research_backlog.md, queued 2026-05-12):
  The 2026-05-12 seed_only_floor run (N=40 per cell × 4 cells × 3 modes) found
  3/4 cells agree between full-floor and seed-only-floor on Δep0. The lone
  disagreement was at β_guilt=0.30: Δfull = 0 pts, Δseed = −15 pts — roughly
  a 2-SE gap with the N=40 sample. Either:
    (a) the gap is real and per-class outcome floors do carry a small
        positive contribution at this intermediate-asymmetry cell, OR
    (b) the gap is sampling noise at N=40 — the N=200 cell should collapse
        toward |Δfull − Δseed| ≤ 5 pts.

  Cleanest test: rerun the β_guilt=0.30 cell only at N=200 (5× the prior
  per-cell N). Keep all other settings identical to exp_seed_only_floor so the
  arms are directly comparable. If the gap closes, outcome floors are inert
  even at moderate asymmetry. If it persists, the floor table is not
  reducible to a single seed-template intervention.

Sandbox extension:
  None. This is a higher-N replication of one cell of exp_seed_only_floor.
  All injection-pathway plumbing (tag_aware_injection, tag_floors) already
  exists in sandbox.run_episode and emotion.inject_recalled_emotion_tag_aware
  from the 2026-05-11 / 2026-05-12 experiments.

Design (matches exp_seed_only_floor_v1 except β_guilt scope and N):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_loyalty=0.05 fixed, β_guilt=0.30 only,
  chain_length=8.

  Tag-aware RECALL is ON in every arm.

  Three modes:
    inject_mode = "off"        — tag_aware_injection=False (control).
    inject_mode = "full"       — tag_aware_injection=True with the default
                                  4-tag floor table.
    inject_mode = "seed_only"  — tag_aware_injection=True with floors pruned
                                  to {"seed": ...}. Outcome-tagged memories
                                  fall back to legacy literal-stored
                                  injection.

  Why chain_length=8 (vs 10 in exp_seed_only_floor): 5,000-episode cap.
  3 modes × 200 agents × 10 episodes = 6,000 (over cap). Truncating to
  episodes 0–7 = 4,800 (under cap). The headline metric is ep0 rescue rate,
  which is unaffected by chain truncation. The secondary "ep5–9 mean" is
  reported here as "ep5–7 mean" — 3 episodes of long-run signal vs the
  prior 5. We do NOT widen the comparison to other cells; this is a
  targeted single-cell replication.

  N_AGENTS = 200 per cell.
  Total: 3 modes × 1 cell × 200 agents × 8 episodes = 4,800 episodes.

  We use seed=92000+ (the prior exp_seed_only_floor used 91000+) so the agent
  populations are statistically independent draws.

Headline metrics:
  - ep0 rescue rate per mode at β_guilt=0.30.
  - Δep0(full − off), Δep0(seed_only − off).
  - |Δfull − Δseed|  — should be ≤ 5 pts if the prior 15-pt gap was noise.
  - ep5–7 mean rescue rate per mode (long-run secondary).
"""
import csv, os, random
from . import sandbox, memory, emotion


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "seed_only_floor_b30_n200_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILT = 0.30          # single cell — the replication target
INJECT_MODES = ["off", "full", "seed_only"]
CHAIN_LENGTH = 8
N_AGENTS = 200

SEED_ONLY_FLOORS = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}


def _decay_dict(beta_guilt, beta_loyalty):
    return {
        "survival": 0.0,
        "guilt": beta_guilt,
        "loyalty": beta_loyalty,
        "fear": 0.0,
        "curiosity": 0.0,
    }


def _outcome_to_tag(outcome):
    if outcome == "PARTNER_RESCUED":
        return "rescue"
    if outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
        return "failure"
    return "timeout"


def _mode_args(mode):
    if mode == "off":
        return False, None
    if mode == "full":
        return True, None
    if mode == "seed_only":
        return True, SEED_ONLY_FLOORS
    raise ValueError(f"Unknown inject_mode: {mode}")


def run():
    rows = []
    seed = 92000
    decay = _decay_dict(BETA_GUILT, BETA_LOYALTY)
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors = _mode_args(inj_mode)
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
            M[0]["tag"] = "seed"
            for ep_idx in range(CHAIN_LENGTH):
                len_before = len(M)
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=KAPPA,
                    seed_memory=False,
                    mem_severity=SEVERITY,
                    mem_emotion_decay=decay,
                    carry_memory=M,
                    encode_outcome=True,
                    positive_encoding=True,
                    rescue_importance=RESCUE_IMP,
                    rng=rng,
                    tag_aware_recall=True,
                    tag_aware_injection=tag_inj,
                    tag_floors=tag_floors,
                )
                M = r["memory_store"]
                outcome = r["outcome"]
                if len(M) > len_before:
                    M[-1]["tag"] = _outcome_to_tag(outcome)
                rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                rows.append({
                    "inject_mode": inj_mode,
                    "beta_guilt": BETA_GUILT,
                    "beta_loyalty": BETA_LOYALTY,
                    "kappa": KAPPA,
                    "agent_id": agent_id,
                    "episode_idx": ep_idx,
                    "outcome": outcome,
                    "rescued": rescued,
                    "n_memories": len(M),
                    "target_switches": r["target_switches"],
                })

    with open(OUT_RESULTS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} episode rows to {OUT_RESULTS}")


if __name__ == "__main__":
    run()
