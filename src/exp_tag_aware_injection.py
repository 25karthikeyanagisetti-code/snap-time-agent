"""
Experiment 18 — Tag-Aware Injection.

Hypothesis (top of research_backlog.md, elevated 2026-05-09 from the
tag_aware_recall residual):
  Tag-aware RECALL alone (the 2026-05-09 fix) doubles ep5–9 mean rescue at
  every β_guilt cell, but leaves a residual ep0 collapse at extreme
  asymmetry: at β_guilt=0.50 ep0 rescue stays at 58% (vs 78% symmetric
  baseline). Mechanism conjecture: the recall gate now correctly says
  "this IS a guilt memory" — but the literal stored.guilt has been
  laundered, so `inject_recalled_emotion` adds ~0 guilt to current e_t even
  when reactivation fires. Closing the same loophole on the INJECTION
  pathway — by injecting max(stored_dim, floor_dim) for each dim, where
  floor is a per-tag template — should eliminate the residual collapse.

  Two clean outcomes:
    - HELD: ep0 rescue at β_guilt=0.50 climbs from 58% (recall-only) toward
      the 78% symmetric baseline under tag-aware injection. ep5–9 mean
      rescue rises further at high β_guilt. The injection pathway IS the
      second mechanism.
    - REFUTED: ep0 rescue at β_guilt=0.50 stays near 58%. ep5–9 mean rescue
      does not shift. The injection-side floor is not the operative
      variable — something else (timing of recall, recall-event statistics,
      context-similarity drift at deliberation steps) carries the residual
      collapse.
    - SPLIT: injection-only or recall-only each partially helps; the joint
      condition closes the gap entirely. Both pathways carry independent
      contributions to the laundering signature.

Sandbox extension:
  - emotion.inject_recalled_emotion_tag_aware: NEW function. For a memory
    with an encoding-time 'tag' field, injects max(stored, floor) per dim.
    Memories without a tag fall back to the legacy literal-stored
    injection — preserves all prior experiment behavior.
  - sandbox.run_episode now accepts tag_aware_injection (default False).
    When True, routes the in-episode injection through the tag-aware
    variant. Default off — every prior experiment is byte-for-byte
    unchanged.

Design (matches tag_aware_recall_v1 exactly, plus the injection mode):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_loyalty=0.05 fixed,
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}, chain_length=10.

  Tag-aware RECALL is ON in every arm — we're isolating the injection
  contribution on top of the prior fix.

  Two arms:
    tag_aware_injection = False  (control — replicates tag_aware_recall_v1)
    tag_aware_injection = True   (treatment — routes injection through tags)

  N_AGENTS = 50 per cell.
  Total: 2 modes × 4 cells × 50 agents × 10 episodes = 4,000 episodes.

  We tag the seeded prior as 'seed' and each outcome-encoded memory by
  outcome class, AT THE EXPERIMENT LEVEL — same instrumentation as
  exp_tag_aware_recall / exp_memory_population_audit.

Headline metrics:
  - ep0 rescue rate per cell × mode (regime-break closure at β_guilt=0.50).
  - ep5–9 mean rescue per cell × mode (long-run uplift).
  - Implied gain on each metric vs the tag_aware_recall_v1 baseline.

Secondary:
  - target_switches per episode (does adding injection pressure cause more
    or less hesitation?).
  - n_memories at ep9 (population audit — same growth?).
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "tag_aware_injection_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILTS = [0.05, 0.15, 0.30, 0.50]
INJECTION_MODES = [False, True]
CHAIN_LENGTH = 10
N_AGENTS = 50


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


def run():
    rows = []
    seed = 78000
    for inj_mode in INJECTION_MODES:
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
                        tag_aware_recall=True,        # always on
                        tag_aware_injection=inj_mode, # the swept variable
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    # Tag any newly-appended outcome memory by its class so the
                    # next episode's tag-aware paths can see its origin.
                    if len(M) > len_before:
                        M[-1]["tag"] = _outcome_to_tag(outcome)
                    rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                    rows.append({
                        "tag_aware_injection": int(inj_mode),
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
