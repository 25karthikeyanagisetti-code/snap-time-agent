"""
Experiment 11 — Signed Threshold Encoding.

Hypothesis (from research_backlog.md):
  Asymmetric gates — different τ for guilt-charged vs loyalty-charged
  outcomes — sort the population. The selective_encoding null (2026-05-01)
  showed that a single magnitude threshold cannot distinguish rescue from
  failure (at κ=1.0 both saturate `e_max` near 1.0). The valenced_encoding
  boomerang (2026-05-02) showed that turning the rescue channel ON or OFF
  symmetrically only changes how fast the regime collapses. This experiment
  asks: if we threshold rescue and failure encodings INDEPENDENTLY, can we
  produce a configuration that yields lasting divergence?

Why this is worth testing:
  Both prior selectivity / valence experiments treated the two channels as
  symmetric. But the seeded abandonment prior is asymmetric to start with
  (high guilt + moderate loyalty), and the encoder's importance values are
  asymmetric too (failure 0.85 vs rescue 0.7). It's plausible that the
  Homogenization Collapse can only be unwound by a SIGNED gate — e.g. log
  rescue events liberally (low τ_loyalty) but require strong intensity to
  log failures (high τ_guilt), starving the guilt memory population.

Sandbox extension note: this experiment does NOT modify sandbox.run_episode.
We pass encode_outcome=False and apply the gated encoder locally (mirroring
exp_selective_encoding).

Design:
  T_snap = 12, severity = 1.0, kappa = 1.0   (committed regime, max collapse)
  τ_guilt   ∈ {0.3, 0.7}                       — gate for guilt-charged ends
  τ_loyalty ∈ {0.3, 0.7}                       — gate for loyalty-charged ends
  chain_length = 10
  n_agents     = 100
  Total = 2 * 2 * 100 * 10 = 4,000 episodes (under cap).

Naming convention for cells:
  G=guilt threshold, L=loyalty threshold.
    (G=0.3, L=0.3)  symmetric-low      — encode almost everything (≈baseline)
    (G=0.3, L=0.7)  loyalty-stingy     — easy to log failures, hard rescues
    (G=0.7, L=0.3)  guilt-stingy       — easy to log rescues, hard failures
    (G=0.7, L=0.7)  symmetric-high     — only intense events leave a trace

Headline metric:
  divergence@ep5–9  := mean over ep5..ep9 of
                       rescue_rate(ep1_rescuers) - rescue_rate(ep1_non_rescuers)
  ep9 rescue rate (population avg)
  ep9 - ep0 rescue rate (collapse magnitude)

Expected pattern under hypothesis:
  guilt-stingy (G=0.7, L=0.3) yields highest ep9 rescue rate AND highest
  divergence (rescue events dominate the memory store; rescuers stay
  rescuers). The other three cells either flood (G=0.3, L=0.3) or starve
  the rescue channel (G=0.3, L=0.7) or starve both (G=0.7, L=0.7).
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "signed_threshold_encoding_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
TAUS_GUILT = [0.3, 0.7]
TAUS_LOYALTY = [0.3, 0.7]
CHAIN_LENGTH = 10
N_AGENTS = 100


# Mirrors sandbox.run_episode's outcome-encoding payload semantics so we can
# gate independently on guilt-charged vs loyalty-charged ends.
def _is_guilt_charged(outcome):
    return outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN", "TIMEOUT")


def _is_loyalty_charged(outcome):
    return outcome == "PARTNER_RESCUED"


def _outcome_payload(outcome):
    if outcome == "PARTNER_RESCUED":
        return ({"survival": 0.1, "guilt": 0.0, "loyalty": 0.8,
                 "fear": 0.1, "curiosity": 0.0}, 0.7)
    if outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
        return ({"survival": 0.3, "guilt": 0.85, "loyalty": 0.5,
                 "fear": 0.2, "curiosity": 0.0}, 0.85)
    # TIMEOUT
    return ({"survival": 0.2, "guilt": 0.4, "loyalty": 0.3,
             "fear": 0.2, "curiosity": 0.0}, 0.5)


def _final_positions(r):
    """Re-walk the action history to recover the terminal positions
    sandbox.run_episode would have used in its own encode-outcome path."""
    agent_pos = sandbox.AGENT_START
    for a in r["action_history"]:
        agent_pos = sandbox._apply(agent_pos, a)
        if agent_pos == sandbox.RESOURCE_START or agent_pos == sandbox.PARTNER_START:
            break
    partner_pos = sandbox.PARTNER_START
    resource_pos = sandbox.RESOURCE_START
    partner_alive = (r["outcome"] == "PARTNER_RESCUED") or (
        r["steps_used"] < sandbox.PARTNER_DEADLINE
        and r["outcome"] == "RESOURCE_TAKEN"
    )
    return agent_pos, partner_pos, resource_pos, partner_alive


def _maybe_encode(M, r, tau_guilt, tau_loyalty):
    """Apply the SIGNED threshold gate. Returns (was_encoded, gate_used).

    Gate variable: the agent's terminal-emotion L_∞ norm (max over emotion
    dims) — same as exp_selective_encoding. The DIFFERENCE here is that the
    threshold itself depends on the OUTCOME's valence:
      - guilt-charged outcome   → must clear tau_guilt
      - loyalty-charged outcome → must clear tau_loyalty
    """
    e_final = r["final_emotion"]
    e_max = max(e_final.values()) if e_final else 0.0
    outcome = r["outcome"]
    if _is_loyalty_charged(outcome):
        threshold = tau_loyalty
    else:
        threshold = tau_guilt
    if e_max < threshold:
        return 0, e_max
    agent_pos, partner_pos, resource_pos, partner_alive = _final_positions(r)
    features = sandbox._build_features(
        agent_pos=agent_pos, partner_pos=partner_pos,
        resource_pos=resource_pos, partner_alive=partner_alive,
        is_abandonment_event=(outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN")),
    )
    ep_emotion, importance = _outcome_payload(outcome)
    memory.encode(M, features, ep_emotion, importance)
    return 1, e_max


def run():
    rows = []
    seed = 47000
    for tau_g in TAUS_GUILT:
        for tau_l in TAUS_LOYALTY:
            cell = f"G{tau_g}_L{tau_l}"
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(M, severity=1.0, preage=15)
                for ep_idx in range(CHAIN_LENGTH):
                    r = sandbox.run_episode(
                        t_snap=T_SNAP, kappa=KAPPA,
                        seed_memory=False,
                        carry_memory=M,
                        encode_outcome=False,    # we gate locally
                        rng=rng,
                    )
                    M = r["memory_store"]
                    was_encoded, e_max = _maybe_encode(M, r, tau_g, tau_l)
                    rows.append({
                        "cell": cell,
                        "tau_guilt": tau_g,
                        "tau_loyalty": tau_l,
                        "agent_id": agent_id,
                        "episode_idx": ep_idx,
                        "outcome": r["outcome"],
                        "rescued": 1 if r["outcome"] == "PARTNER_RESCUED" else 0,
                        "n_memories": len(M),
                        "e_max": round(e_max, 4),
                        "was_encoded": was_encoded,
                        "target_switches": r["target_switches"],
                    })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
