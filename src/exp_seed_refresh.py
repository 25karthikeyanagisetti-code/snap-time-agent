"""
Experiment — Seed-Refresh Bypass.

Hypothesis (top of research_backlog.md, elevated 2026-05-13 after
seed_only_floor_b30_n200 closed the last cell of seed_only_floor as
full-table-equivalent at ep0):
  The 2026-05-12/13 chain established that pruning the tag-aware injection
  floor table to {"seed": ...} reproduces the full-floor Δep0 vector across
  all four β_guilt cells. The remaining question: is the FLOOR mechanism
  (max(stored, floor) at injection time) essential, or is the operative
  mechanism simply "keep the aged prior loud at the source — bypass the
  injection table entirely"?

  Cleanest test: on every step BEFORE recall is computed, RESET the seed-
  tagged memory's stored.emotion back to its encoding-time template. This
  rejuvenates the aged prior at the SOURCE — both the impact-time
  emotion_magnitude term and the legacy literal-stored injection path now
  see a non-decayed prior. No tag-aware injection table needed.

  Three clean outcomes:
    - HELD: seed-refresh delivers the same Δep0 vector as seed_only_floor at
      all four cells (within sampling noise). The floor table is a non-
      essential intermediate construct; the operative mechanism is "keep
      the aged prior loud, full stop."
    - REFUTED: seed-refresh delivers a flat (or differently-shaped) Δep0
      vector. The floor mechanism — max-at-injection — is doing real work
      beyond just restoring the source magnitude.
    - PARTIAL: seed-refresh matches at some cells but exceeds floor at
      others (e.g., bigger lift at β_guilt=0.50 because refreshed magnitude
      also boosts impact-time recall-strength). That would say the floor
      and the source-refresh diverge at higher in-chain decay rates.

Sandbox extension:
  src/sandbox.py: new optional run_episode kwarg `seed_refresh_on_recall`
  (default False — preserves all prior experiment behavior). When True,
  every step BEFORE recall iterates the memory store and snaps the stored
  emotion of any memory carrying tag='seed' and an 'encoding_emotion'
  template back to that template. The memory's age keeps ticking up — only
  the stored emotion is refreshed.

Design (matches exp_seed_only_floor_v1 exactly, with the floor arm replaced
by seed_refresh):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_loyalty=0.05 fixed,
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}, chain_length=10.

  Tag-aware RECALL is ON in every arm — we're isolating the injection-side
  / source-refresh contribution.

  Three modes:
    inject_mode = "off"             — baseline (no tag-aware injection, no
                                       seed refresh). Replicates the
                                       tag_aware_recall_v1 INJ-OFF arm.
    inject_mode = "seed_only_floor" — tag_aware_injection=True with floors
                                       pruned to {"seed": SEED_FLOOR}.
                                       Replicates seed_only_floor_v1.
    inject_mode = "seed_refresh"    — seed_refresh_on_recall=True with the
                                       legacy literal-stored injection
                                       path. NO floor table.

  We tag the seeded prior as 'seed' AND copy its encoding-time emotion to
  m["encoding_emotion"] so the seed_refresh path can find the template at
  every step. Outcome-encoded memories are tagged by class but are NOT
  given an encoding_emotion field — so the seed_refresh path is a no-op on
  them (matches the hypothesis: the refresh is seed-only).

  N_AGENTS = 40 per cell.
  Total: 3 modes × 4 cells × 40 agents × 10 episodes = 4,800 episodes.

Headline metrics:
  - ep0 rescue rate per cell × mode.
  - Δep0 (seed_only_floor − off) and Δep0 (seed_refresh − off) per cell.
  - "Source-refresh substitutability":
      |Δep0(seed_refresh) − Δep0(seed_only_floor)| per cell.
    If ≤ ~5 pts at every cell, the two mechanisms are operationally
    interchangeable and the floor table is non-essential.
  - ep5–9 mean rescue per cell × mode (long-run secondary).
"""
import csv, os, random
from . import sandbox, memory, emotion


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "seed_refresh_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILTS = [0.05, 0.15, 0.30, 0.50]
INJECT_MODES = ["off", "seed_only_floor", "seed_refresh"]
CHAIN_LENGTH = 10
N_AGENTS = 40

# Same seed-only floor table used by exp_seed_only_floor.py — single entry.
SEED_ONLY_FLOORS = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}

# Encoding-time emotion template attached to the seeded prior. Matches
# sandbox._seed_abandonment_memory exactly (severity=1.0 used here).
SEED_ENCODING_EMOTION = {
    "survival": 0.2,
    "guilt": 0.9 * SEVERITY,
    "loyalty": 0.6 * SEVERITY,
    "fear": 0.1,
    "curiosity": 0.0,
}


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
    seed_refresh_on_recall) triple that run_episode expects."""
    if mode == "off":
        return False, None, False
    if mode == "seed_only_floor":
        return True, SEED_ONLY_FLOORS, False
    if mode == "seed_refresh":
        return False, None, True
    raise ValueError(f"Unknown inject_mode: {mode}")


def run():
    rows = []
    seed = 92000
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors, seed_refresh = _mode_args(inj_mode)
        for beta_g in BETA_GUILTS:
            decay = _decay_dict(beta_g, BETA_LOYALTY)
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(
                    M, severity=SEVERITY, preage=15
                )
                # Tag the seeded prior AND record its encoding-time emotion
                # so the seed_refresh path can find the template.
                M[0]["tag"] = "seed"
                M[0]["encoding_emotion"] = dict(SEED_ENCODING_EMOTION)
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
                        tag_aware_recall=True,                # always on
                        tag_aware_injection=tag_inj,          # swept
                        tag_floors=tag_floors,                # swept
                        seed_refresh_on_recall=seed_refresh,  # swept
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    # Tag any newly-appended outcome memory by class so future
                    # episodes' tag-aware paths can classify it. Outcome
                    # memories deliberately do NOT get encoding_emotion — the
                    # seed_refresh hook is seed-only by construction.
                    if len(M) > len_before:
                        M[-1]["tag"] = _outcome_to_tag(outcome)
                    rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                    rows.append({
                        "inject_mode": inj_mode,
                        "beta_guilt": beta_g,
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
