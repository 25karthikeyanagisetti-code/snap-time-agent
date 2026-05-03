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
