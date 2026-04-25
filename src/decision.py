"""
Decision pressure Phi(v, e) and the Snap Time deliberation loop.

Low Phi = good. The agent picks argmin Phi over candidate actions.

For the Rescue-vs-Resource sandbox the only conflict axes that matter are:
  - guilt vs survival: moving toward resource while partner is in danger raises
    guilt-conflict; moving toward partner reduces it.
  - loyalty: same direction as guilt for the partner action — being near
    partner also satisfies loyalty.
  - fear: would steer away from threat (not used in v1 sandbox).

Conflict terms are passed in by the sandbox; this module is sandbox-agnostic.
"""


def phi(value, emotion, conflict, kappa):
    """
    Additive coupling (default). Phi = -value + kappa * <emotion, conflict>.

    Properties:
    - emotion adds a constant pressure regardless of value
    - produces the Paralysis Valley (see experiments/regime_map_v1/)
    """
    base = -value
    emo_term = 0.0
    for dim, conflict_val in conflict.items():
        emo_term += emotion.get(dim, 0.0) * conflict_val
    return base + kappa * emo_term


def phi_multiplicative(value, emotion, conflict, kappa):
    """
    Multiplicative coupling. Phi = -value * (1 + kappa * <emotion, conflict>).

    Properties (expected, to be verified experimentally):
    - emotion scales the value, rather than adding beside it
    - when value is large, emotion is amplified; when small, emotion matters less
    - may avoid the Paralysis Valley because emotion cannot overwhelm a strong
      value signal
    - but may introduce its own failure modes (e.g., bistability)
    """
    base = -value
    emo_term = 0.0
    for dim, conflict_val in conflict.items():
        emo_term += emotion.get(dim, 0.0) * conflict_val
    return base * (1.0 + kappa * emo_term)


def phi_max(value, emotion, conflict, kappa):
    """
    Max coupling: Phi = -value + kappa * max_dim(emotion[d] * conflict[d]).
    Only the SINGLE strongest emotion-conflict dimension matters.
    Models "winner-take-all" affect — one feeling at a time.
    """
    base = -value
    if not conflict:
        return base
    max_term = 0.0
    for dim, conflict_val in conflict.items():
        term = emotion.get(dim, 0.0) * conflict_val
        if term > max_term:
            max_term = term
    return base + kappa * max_term


def phi_logsumexp(value, emotion, conflict, kappa, beta=4.0):
    """
    Soft-max coupling. beta -> 0 recovers additive (averaging); beta -> inf
    recovers max (winner-take-all). beta=4 is "soft winner-take-all".
    Phi = -value + kappa * (1/beta) * log(sum exp(beta * e_d * c_d))
    """
    import math
    base = -value
    if not conflict:
        return base
    terms = [emotion.get(dim, 0.0) * conflict_val
             for dim, conflict_val in conflict.items()]
    m = max(terms)
    s = sum(math.exp(beta * (t - m)) for t in terms)
    lse = m + math.log(s) / beta
    return base + kappa * lse


def phi_by_mode(mode, value, emotion, conflict, kappa):
    """Dispatcher — lets sandbox pick coupling form via config."""
    if mode == "additive":
        return phi(value, emotion, conflict, kappa)
    if mode == "multiplicative":
        return phi_multiplicative(value, emotion, conflict, kappa)
    if mode == "max":
        return phi_max(value, emotion, conflict, kappa)
    if mode == "logsumexp":
        return phi_logsumexp(value, emotion, conflict, kappa)
    raise ValueError(f"unknown phi mode: {mode}")


def deliberate(state, candidate_actions, score_action_fn, t_snap):
    """
    Snap Time loop. Re-evaluates actions over up to t_snap iterations,
    tracking how often the best-action-so-far changes (hesitation).

    score_action_fn(state, action, iteration) -> Phi (float)
        The scorer can be stateful via closures (e.g., it can mutate emotion
        as iterations proceed if you want emotion to drift mid-deliberation).

    Returns:
        chosen_action,
        hesitation_count (int — how many times the leader changed),
        deliberation_trace (list of (iter, leader_action, leader_phi))
    """
    best_a = None
    best_phi = float("inf")
    hesitation_count = 0
    trace = []

    iters = max(1, int(t_snap))
    for it in range(iters):
        for a in candidate_actions:
            score = score_action_fn(state, a, it)
            if score < best_phi:
                if best_a is not None and a != best_a:
                    hesitation_count += 1
                best_a = a
                best_phi = score
        trace.append((it, best_a, best_phi))

    return best_a, hesitation_count, trace
