"""
Experiment 13 — Decay Asymmetry ("forgiveness for self, not others").

Hypothesis (top of research_backlog.md, elevated by the 2026-05-04
loyalty_importance_floor null):
  Faster decay on loyalty memories than on guilt memories preserves rescue
  capacity over chained episodes. Concretely: with β_guilt fixed at 0.05 and
  β_loyalty swept up to 0.30, the encoded rescue memories' loyalty charge
  fades fast, weakening their per-step recall pull while leaving the seeded
  abandonment prior's guilt channel intact.

Why this is the right next dial:
  - The 2026-05-02 valenced_encoding finding (Loyalty Boomerang) showed
    encoding rescue memories CUTS long-term rescue rate from 28% (OFF) to
    15% (ON, importance=0.7) at κ=1.0.
  - The 2026-05-04 loyalty_importance_floor null showed importance is the
    wrong dial — sweeping rescue_importance ∈ {0.0, …, 0.7} produced a flat
    14–17% ep5–9 rescue band (range 2.4 pts).
  - That null leaves DECAY RATE as the next-most-likely lever. If asymmetric
    decay raises ep5–9 rescue rate toward the OFF baseline (28%), the
    boomerang IS countered — by *weight via emotion-magnitude*, not by count
    or by per-encoding importance.

Sandbox extension:
  memory.decay_memory_emotion now accepts either a scalar (legacy uniform
  decay) OR a dict {emotion_dim: rate}. The sandbox already passes this
  parameter through to the memory module each step; no sandbox change is
  required. Defaults preserve all prior experiment behavior.

Design (all at the committed-regime cell where the boomerang lives):
  T_snap = 12, kappa = 1.0, severity = 1.0
  positive_encoding = True   (the regime that exhibits the boomerang)
  rescue_importance = 0.7    (default — match valenced/floor baseline)
  chain_length = 10
  n_agents     = 100

  Cells (β_guilt fixed at 0.05 throughout):
    A: β_loyalty = 0.05   (symmetric mild decay — control)
    B: β_loyalty = 0.15   (asymmetric, loyalty fades 3× faster)
    C: β_loyalty = 0.30   (asymmetric, loyalty fades 6× faster)
    D: β_loyalty = 0.50   (extreme asymmetry, loyalty cleared in ~2 steps)

  Total = 4 * 100 * 10 = 4,000 episodes (well under 5k cap).

Headline metric:
  ep5–9 mean rescue rate per cell. If it climbs from ~15% baseline toward
  the rescue-encoding-OFF figure of 28%, the hypothesis is supported.

Secondary metrics:
  - ep0 rescue rate (sanity — should be near committed-regime ~78%)
  - divergence@5–9 := rescue_rate(ep1_rescuers) − rescue_rate(ep1_non_rescuers)
  - mean memory store size at ep9 (should be 11 in every cell — store
    geometry is unchanged; only stored emotion is modulated)

Expected pattern under hypothesis:
  Monotone increase in ep5–9 rescue rate with β_loyalty. The C or D cell
  approaches the 28% OFF baseline. If D overshoots OFF (say >32%), this
  asymmetric-decay channel actually beats removal because guilt memories
  retain their corrective signal.

  Plausible failure modes worth naming up front:
  - NULL flat curve (~15% across cells): boomerang isn't bottled up in the
    γ·|emotion| recall term, so weakening loyalty magnitude does not free
    the agent.
  - INVERTED curve (decay HURTS): faster loyalty decay could also reduce a
    helpful loyalty pull during the deliberation steps when the partner is
    nearby, costing rescues directly. If C/D fall BELOW A, the "loyalty as
    pure liability" framing is wrong.
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "decay_asymmetry_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_GUILT = 0.05
BETA_LOYALTIES = [0.05, 0.15, 0.30, 0.50]
CHAIN_LENGTH = 10
N_AGENTS = 100


def _decay_dict(beta_guilt, beta_loyalty):
    """
    Build the per-dim decay rate dict. Other emotion dims get rate=0 (no
    decay) so that we isolate the guilt-vs-loyalty contrast.
    """
    return {
        "survival": 0.0,
        "guilt": beta_guilt,
        "loyalty": beta_loyalty,
        "fear": 0.0,
        "curiosity": 0.0,
    }


def run():
    rows = []
    seed = 61000
    for beta_l in BETA_LOYALTIES:
        decay = _decay_dict(BETA_GUILT, beta_l)
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
            for ep_idx in range(CHAIN_LENGTH):
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
                )
                M = r["memory_store"]
                rows.append({
                    "beta_guilt": BETA_GUILT,
                    "beta_loyalty": beta_l,
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
