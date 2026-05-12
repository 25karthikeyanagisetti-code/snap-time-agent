"""
Experiment 23 — Seed-Only Floor Ablation.

Hypothesis (top of research_backlog.md, elevated 2026-05-11 from the
tag_aware_injection FAILED-in-opposite-direction finding):
  The 2026-05-10 tag_aware_injection run produced a monotonically-decreasing
  Δep0 vector across β_guilt ∈ {0.05, 0.15, 0.30, 0.50}: {+20.0, +8.0, +14.0,
  −2.0} pts INJ-ON vs INJ-OFF. The headline cell (β_guilt=0.50) didn't move;
  the symmetric β_guilt=0.05 cell moved hardest. Mechanism interpretation:
  the floor that helps is the SEED floor — it restores the aged-prior
  abandonment memory whose stored.guilt has decayed to ~0 by the time it
  fires at ep0. The per-class outcome floors (failure/rescue/timeout) are
  inert; they fire on memories whose stored.guilt is already at or near the
  encoding magnitude (they're young), so max(stored, floor) = stored.

  Cleanest test: rerun the tag_aware_injection sweep with the floor table
  pruned to ONLY the 'seed' entry. Failure/rescue/timeout tagged memories
  fall back to the legacy literal-stored injection path (already handled by
  emotion.inject_recalled_emotion_tag_aware when a tag is not in the
  tag_floors dict — preserves prior behavior).

  Three clean outcomes:
    - HELD: seed-only floor reproduces the {+20, +8, +14, −2} Δep0 vector to
      within sampling noise. Per-class outcome floors confirmed inert. The
      operative mechanism is "the aged seeded prior is what gets laundered
      naturally over preage steps, and the floor restores it on recall."
    - REFUTED: seed-only floor produces a flat Δep0 (≈ 0 across cells).
      Then the failure/rescue/timeout floors were doing the work, contrary
      to the per-class-decay-arithmetic reading of the 2026-05-07 audit.
    - SPLIT: the symmetric β_guilt=0.05 +20 pt cell still lifts under
      seed-only floor (the seed prior IS the lever there) but the β_guilt=
      0.15 and 0.30 cells fall back toward 0. That would mean outcome
      floors carry partial responsibility at moderate asymmetry.

Sandbox extension:
  None. emotion.inject_recalled_emotion_tag_aware already accepts a
  caller-supplied tag_floors dict and falls back to legacy literal-stored
  injection for any tag not in the dict. sandbox.run_episode already
  forwards tag_floors to that path (added with exp_tag_aware_injection).

Design (matches exp_tag_aware_injection_v1 exactly, with a 3rd arm):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_loyalty=0.05 fixed,
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}, chain_length=10.

  Tag-aware RECALL is ON in every arm — we're isolating the injection
  contribution and within-injection the per-tag floor contribution.

  Three modes:
    inject_mode = "off"        — tag_aware_injection=False (control;
                                  replicates tag_aware_recall_v1 baseline).
    inject_mode = "full"       — tag_aware_injection=True with the default
                                  4-tag floor table. Replicates the 2026-05-10
                                  tag_aware_injection_v1 result.
    inject_mode = "seed_only"  — tag_aware_injection=True with floors
                                  pruned to {"seed": TAG_FLOORS_DEFAULT[
                                  "seed"]}. Outcome-tagged memories fall
                                  back to legacy literal-stored injection.

  N_AGENTS = 40 per cell.
  Total: 3 modes × 4 cells × 40 agents × 10 episodes = 4,800 episodes.

  We tag the seeded prior as 'seed' and each outcome-encoded memory by
  outcome class — same instrumentation as exp_tag_aware_injection.

Headline metrics:
  - ep0 rescue rate per cell × mode.
  - Δep0 (full − off) and Δep0 (seed_only − off) per cell.
  - "Floor-mechanism share":
      share = Δep0(seed_only − off) / Δep0(full − off)
    If share ≈ 1.0 across cells, the seed floor IS the mechanism and outcome
    floors are inert. If share ≈ 0, the seed floor is irrelevant.
  - ep5–9 mean rescue per cell × mode (long-run effect, secondary).
"""
import csv, os, random
from . import sandbox, memory, emotion


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "seed_only_floor_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILTS = [0.05, 0.15, 0.30, 0.50]
INJECT_MODES = ["off", "full", "seed_only"]
CHAIN_LENGTH = 10
N_AGENTS = 40

# Per-mode tag-floor table. "off" is unused (we route through legacy
# inject_recalled_emotion). "full" passes None to use TAG_FLOORS_DEFAULT.
# "seed_only" passes a dict with just the 'seed' entry — all other tagged
# memories (failure/rescue/timeout) fall back to legacy literal-stored
# injection inside emotion.inject_recalled_emotion_tag_aware.
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
    """Translate inject_mode into the (tag_aware_injection, tag_floors) pair
    that run_episode expects."""
    if mode == "off":
        return False, None
    if mode == "full":
        return True, None  # use TAG_FLOORS_DEFAULT
    if mode == "seed_only":
        return True, SEED_ONLY_FLOORS
    raise ValueError(f"Unknown inject_mode: {mode}")


def run():
    rows = []
    seed = 91000
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors = _mode_args(inj_mode)
        for beta_g in BETA_GUILTS:
            decay = _decay_dict(beta_g, BETA_LOYALTY)
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(
                    M, severity=SEVERITY, preage=15
                )
                # Tag the seeded prior so the tag-aware paths can see it.
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
                        tag_aware_recall=True,         # always on
                        tag_aware_injection=tag_inj,   # swept
                        tag_floors=tag_floors,         # swept (seed-only or full)
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    # Tag any newly-appended outcome memory by its class so
                    # subsequent episodes' tag-aware paths can classify it.
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
