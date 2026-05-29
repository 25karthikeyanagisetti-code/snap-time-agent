"""
Experiment — Capped-Floor Loyalty Endpoints: N=200 replication of the two
endpoint cells (β_loyalty ∈ {0.05, 0.50}) of exp_capped_floor_loyalty_sweep.

Hypothesis (top of research_backlog.md, queued 2026-05-20):
  The 2026-05-20 capped_floor_loyalty_sweep PARTIAL result reported
  |Δcapped − Δfloor| = 17.5 pts at BOTH endpoint cells (β_loyalty ∈ {0.05,
  0.50}) and 5.0 pts at both mid-cells (β_loyalty ∈ {0.15, 0.30}) — yielding
  the vector {17.5, 5.0, 5.0, 17.5}. The mid-cell gaps reproduce yesterday's
  guilt-axis figure exactly; the endpoint gaps are 3.5× larger and consistent
  in direction (capped > floor at both ends). Two readings are compatible
  with N=40 data:
    (a) Real MemoryImpact-amplification: floor-on-source raises the seed
        memory's exp(γ·|emotion|) recall-impact term BEFORE the recall gate
        runs. Floor-on-gate cannot replicate that. Whenever the floored
        channel is the rapidly-decaying one (loyalty at β=0.05 and β=0.50
        endpoints, where the OFF baseline either has unusually weak or
        unusually strong seed dominance), the impact-side bonus is largest.
    (b) N=40 sampling artifact: the 2-SE band on a Δ-of-Δ at N=40 per arm
        is ≈ 14.5 pts. The 17.5 pts endpoint gap is just outside that band.
        Two consistent endpoints lessens the artifact reading but doesn't
        eliminate it.

  Cleanest test: replicate ONLY the two endpoint cells at N=200 (5× the
  per-cell N), holding everything else fixed. The 2-SE at N=200 collapses
  to ≈ 6.5 pts on Δ-of-Δ.
    - If both endpoint gaps shrink to ≤ 6.5 pts, the 17.5-pt readings were
      N=40 noise. The source-vs-gate isomorphism is channel-symmetric across
      the full β_loyalty range — yesterday's PARTIAL upgrades to HELD.
    - If both endpoint gaps STAY ≥ ~10 pts, the MemoryImpact-amplification
      reading is consolidated. The architectural compression survives only
      as a one-sided ≥ (capped ≥ floor), not as an isomorphism.
    - Asymmetric outcome (one endpoint shrinks, the other doesn't) would
      point to a cell-specific mechanism rather than a generic amplification.

Sandbox usage:
  No extension required. Reuses the seed_refresh_capped_on_recall hook from
  exp_seed_refresh_capped (2026-05-19) plus the tag-aware injection floors
  from exp_tag_aware_injection (2026-05-11). All defaults preserve all
  prior experiment behavior.

Design (mirrors exp_capped_floor_loyalty_sweep exactly except cell scope,
chain length, and N):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_guilt=0.05 fixed,
  β_loyalty ∈ {0.05, 0.50} only (the two endpoints — the contested cells),
  chain_length=4.

  Tag-aware RECALL is ON in every arm — same as yesterday.

  Three modes (same as yesterday):
    inject_mode = "off"                  — baseline (no injection floor, no
                                            source refresh).
    inject_mode = "seed_only_floor"      — tag_aware_injection=True with the
                                            floor table pruned to {seed}.
    inject_mode = "seed_refresh_capped"  — seed_refresh_capped_on_recall=True
                                            with the legacy literal-stored
                                            injection path; the floor lives
                                            on the seed memory itself.

  Why chain_length=4 (vs 10 in the parent sweep): 5,000-episode cap. The
  headline metric is ep0 rescue rate — chain length is essentially irrelevant
  to it (the ep0 outcome depends on the carried memory state at episode
  start, which for ep0 is the seeded prior alone). 3 modes × 2 cells × 200
  agents × 4 episodes = 4,800 episodes — under cap with full N=200 power on
  the headline cell.

  The parent run used seed=122000+. We use seed=130000+ so the agent
  populations are statistically independent draws from the same generator
  family (no overlap with yesterday's 4800-stream draw).

Headline metrics:
  - ep0 rescue rate per cell × mode (N=200 per arm).
  - Δep0 (seed_only_floor − off) and Δep0 (seed_refresh_capped − off) per cell.
  - |Δcapped − Δfloor| per cell.
       → ≤ 6.5 pts (≈ 2-SE at N=200) ⇒ endpoint blowouts were N=40 noise.
       → ≥ 10 pts ⇒ MemoryImpact-amplification confirmed.
  - OFF-baseline drift check: today's OFF ep0 vs the 2026-05-20 OFF ep0 at
    the same cell. If the OFF baselines diverge >10 pts at N=200, the
    parent sweep's OFF was itself noisy, which would also explain the
    endpoint gaps.
"""
import csv, os, random
from . import sandbox, memory, emotion


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "capped_loyalty_n200_endpoints_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_GUILT = 0.05
BETA_LOYALTYS = [0.05, 0.50]            # endpoints only
INJECT_MODES = ["off", "seed_only_floor", "seed_refresh_capped"]
CHAIN_LENGTH = 4
N_AGENTS = 200

# Same seed-only floor table used by the parent sweep / exp_seed_only_floor.
SEED_ONLY_FLOORS = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}

# Per-memory floor template attached to the seeded prior for the capped
# variant. Numerically identical to TAG_FLOORS_DEFAULT['seed'] — the whole
# point is to test whether moving the SAME numeric floor from the injection
# gate to the stored-state guardrail is operationally equivalent at the
# endpoint cells (β_loyalty ∈ {0.05, 0.50}).
SEED_REFRESH_FLOOR = dict(emotion.TAG_FLOORS_DEFAULT["seed"])


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
    """Translate inject_mode into the (tag_aware_injection, tag_floors,
    seed_refresh_capped) triple that run_episode expects."""
    if mode == "off":
        return False, None, False
    if mode == "seed_only_floor":
        return True, SEED_ONLY_FLOORS, False
    if mode == "seed_refresh_capped":
        return False, None, True
    raise ValueError(f"Unknown inject_mode: {mode}")


def run():
    rows = []
    seed = 130000
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors, capped = _mode_args(inj_mode)
        for beta_l in BETA_LOYALTYS:
            decay = _decay_dict(BETA_GUILT, beta_l)
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(
                    M, severity=SEVERITY, preage=15
                )
                # Tag the seeded prior AND attach the per-memory floor
                # template so the capped path can find it. Outcome memories
                # deliberately do NOT get encoding_emotion_floor — the
                # capped hook is seed-only by construction.
                M[0]["tag"] = "seed"
                M[0]["encoding_emotion_floor"] = dict(SEED_REFRESH_FLOOR)
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
                        tag_aware_recall=True,                       # always on
                        tag_aware_injection=tag_inj,                 # swept
                        tag_floors=tag_floors,                       # swept
                        seed_refresh_capped_on_recall=capped,        # swept
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    if len(M) > len_before:
                        M[-1]["tag"] = _outcome_to_tag(outcome)
                    rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                    rows.append({
                        "inject_mode": inj_mode,
                        "beta_guilt": BETA_GUILT,
                        "beta_loyalty": beta_l,
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
