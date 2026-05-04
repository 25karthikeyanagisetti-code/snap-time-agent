# Daily research log

One entry per scheduled-task run. Most recent at the bottom.

## 2026-05-01 — selective_encoding
- Hypothesis: Encoding only high-magnitude emotional outcomes (gate on max(final_emotion)) prevents the Homogenization Collapse at κ=1.0.
- Result: failed — magnitude-gating produces a U-shaped homogenization: too little encoding floods the store, too much lets the seeded prior dominate; rescue rate at ep9 stays ≤15% across all τ.
- Headline number: max divergence@ep9 = 11.5 pts at τ=0.3 (vs 0.8 pts baseline; 0 pts at τ≥0.5).
- Files: experiments/selective_encoding_v1/results.csv, selective_encoding_collapse.png, finding.md

## 2026-05-02 — valenced_encoding
- Hypothesis: Encoding loyalty memories on RESCUE (not just guilt on failure) restores behavioral types — the population should DIVERGE based on early-episode outcome.
- Result: failed in the OPPOSITE direction. Turning OFF the rescue-side encoding nearly DOUBLES long-term rescue rate (28% vs 15% at ep9). Both conditions show NEGATIVE divergence (anti-types). Naming this The Loyalty Boomerang — bidirectional outcome encoding accelerates the Homogenization Collapse rather than counteracting it.
- Headline number: ep9 rescue rate 28% (off) vs 15% (on); div@5–9 = −2.2 pts (off) vs −10.0 pts (on).
- Files: experiments/valenced_encoding_v1/results.csv, valenced_encoding.png, finding.md
- Follow-ups added to backlog: asymmetric importance gates, decay asymmetry.

## 2026-05-03 — signed_threshold_encoding
- Hypothesis: Asymmetric encoding gates (different τ for guilt-charged vs loyalty-charged outcomes) sort the population and preserve behavioral types at κ=1.0.
- Result: failed in opposite direction — high τ_guilt cells collapse to 0% rescue rate by ep9 (a NEW failure mode: prior-dilution lockout); the predicted "guilt-stingy" sweet spot (G=0.7, L=0.3) is the WORST cell, not the best.
- Headline number: ep9 rescue rate = 0.0% at both (G=0.7, L=0.3) and (G=0.7, L=0.7); best divergence@5–9 = +5.1 pts at (G=0.3, L=0.7) — INFERIOR to single-τ=0.3 baseline (+11.5 pts).
- Files: experiments/signed_threshold_encoding_v1/README.md, results.csv, signed_threshold_encoding.png, finding.md
- Follow-ups added to backlog: outcome-class boolean gate; per-outcome importance modulation; joint outcome×intensity filter.

## 2026-05-04 — loyalty_importance_floor
- Hypothesis: Throttling rescue-side encoding importance from the default 0.7 toward 0 recovers ep9 rescue rate without triggering the Loyalty Boomerang (i.e. there is a low-volume loyalty signal regime).
- Result: NULL — ep5–9 rescue rate stays flat across rescue_importance ∈ {0.0, 0.1, 0.3, 0.5, 0.7}; range 2.4 pts; none come within 12 pts of the rescue-encoding-OFF baseline. The boomerang is structural, not importance-driven.
- Headline number: ep5–9 rescue rate = {15.0, 14.2, 16.6, 14.6, 16.2}% (range 2.4 pts) vs OFF baseline 28%.
- Files: experiments/loyalty_importance_floor_v1/README.md, results.csv, loyalty_importance_floor.png, finding.md
- Follow-ups added to backlog: rescue-payload loyalty-magnitude ablation; recall event-trace sub-study.
