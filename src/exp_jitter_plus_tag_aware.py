"""
Experiment — Jitter + Tag-Aware Recall (THE BIG ONE: full behavioral types?).

Hypothesis (top of research_backlog.md, "jitter_plus_tag_aware"):

  Two independent mechanisms have each been verified separately:

    1. Encoding-diversity jitter (sigma=0.40) produces UNIPOLAR
       behavioral typing at kappa=2.0: 88.8% of agents converge to
       "rescuer" identity regardless of early experience, 0% failures
       (behavioral_typing_verify_v1, +84.0pts, Welch t=21.2, p<<0.001).
       This identity is NOT contingent on what happened to the agent
       early on -- everyone ends up the same.

    2. Tag-aware recall fixes "valence laundering" under asymmetric
       memory decay: at beta_guilt=0.30 (mild laundering regime),
       legacy recall erodes divergence@5-9 toward 0, while tag-aware
       recall restores it to the symmetric-decay baseline of
       +10-13pts (tag_aware_recall_v1).

  Neither mechanism alone has produced BIPOLAR behavioral types --
  agents whose long-run rescue rate depends on their OWN early
  experience (some become reliable rescuers, others become reliable
  failures, diverging from each other). Personality_emergence's
  jitter-only cell showed divergence@5-9 ~= +3-6pts: a small,
  experience-linked effect, dwarfed by jitter's experience-INDEPENDENT
  pull toward "everyone rescues."

  This experiment combines both mechanisms in a single 2x2 under
  asymmetric memory decay (beta_guilt=0.30, beta_loyalty=0.05 -- the
  laundering regime where tag-aware recall is known to matter):

    jitter in {0.00, 0.40} x tag_aware_recall in {False, True}

  Prediction:
    OFF/OFF (legacy baseline):        divergence@5-9 eroded toward ~0
    OFF/ON  (tag-aware alone):        divergence@5-9 restored to +10-13pts
    ON /OFF (jitter alone):           divergence@5-9 small (~+3-6pts),
                                       but sustained rescue rate boosted
    ON /ON  (BOTH, the test cell):    divergence@5-9 > +15pts AND a
                                       nonzero behavioral-failure rate
                                       (>0%) alongside a high rescuer
                                       rate -- i.e. BIPOLAR typing:
                                       distinct, stable rescuer AND
                                       failure identities emerging from
                                       early experience, on top of
                                       jitter's per-agent signature.

  If ON/ON does NOT exceed +15pts, or if the behavioral-failure rate
  stays at 0% (same as jitter-alone unipolar convergence), bipolar
  typing remains unreached and jitter's pull toward "everyone rescues"
  dominates tag-aware recall's experience-linked divergence.

Design:
  T_snap=12, kappa=1.0 (the homogenization-collapse regime where
  divergence@5-9 has historically been measured -- kappa=2.0 is
  already saturated at 0% failures under jitter, leaving no room for
  a failure type).
  severity=1.0, positive_encoding=True, rescue_importance=0.7.
  mem_emotion_decay = {survival:0, guilt:0.30, loyalty:0.05, fear:0,
  curiosity:0} -- the laundering regime from tag_aware_recall_v1.
  chain_length=20 (long enough for divergence@5-9 AND ep15-19
  sustained-rescue / behavioral-typing classification).
  N_AGENTS=200 per cell (big-experiment statistical power).

  Total: 4 cells x 200 agents x 20 episodes = 16,000 episodes.

Headline metrics, per cell:
  - divergence@5-9 := rescue_rate(succeeded ep0) - rescue_rate(failed ep0),
    averaged across episodes 5..9.
  - rescuer rate: % of agents with >=15/20 episode rescues.
  - failure rate: % of agents with <=4/20 episode rescues.
  - mean rescues per agent (0..20).
"""
import csv, os, random
from . import sandbox, memory

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "jitter_plus_tag_aware_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
DECAY = {
    "survival": 0.0,
    "guilt": 0.30,
    "loyalty": 0.05,
    "fear": 0.0,
    "curiosity": 0.0,
}
CHAIN_LENGTH = 20
N_AGENTS = 200

CELLS = [
    # (label, jitter, tag_aware)
    ("off_off", 0.00, False),
    ("off_on",  0.00, True),
    ("on_off",  0.40, False),
    ("on_on",   0.40, True),
]


def _outcome_to_tag(outcome):
    if outcome == "PARTNER_RESCUED":
        return "rescue"
    if outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
        return "failure"
    return "timeout"


def run():
    rows = []
    seed = 600000
    for label, jit, tag_aware in CELLS:
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
                    mem_emotion_decay=DECAY,
                    carry_memory=M,
                    encode_outcome=True,
                    positive_encoding=True,
                    rescue_importance=RESCUE_IMP,
                    encoding_jitter=jit,
                    tag_aware_recall=tag_aware,
                    rng=rng,
                )
                M = r["memory_store"]
                outcome = r["outcome"]
                if len(M) > len_before:
                    M[-1]["tag"] = _outcome_to_tag(outcome)
                rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                rows.append({
                    "cell": label,
                    "jitter": jit,
                    "tag_aware": int(tag_aware),
                    "agent_id": agent_id,
                    "episode_idx": ep_idx,
                    "outcome": outcome,
                    "rescued": rescued,
                    "n_memories": len(M),
                    "target_switches": r["target_switches"],
                })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
