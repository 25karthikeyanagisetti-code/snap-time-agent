# Daily research log

One entry per scheduled-task run. Most recent at the bottom.

## 2026-05-01 — selective_encoding
- Hypothesis: Encoding only high-magnitude emotional outcomes (gate on max(final_emotion)) prevents the Homogenization Collapse at κ=1.0.
- Result: failed — magnitude-gating produces a U-shaped homogenization: too little encoding floods the store, too much lets the seeded prior dominate; rescue rate at ep9 stays ≤15% across all τ.
- Headline number: max divergence@ep9 = 11.5 pts at τ=0.3 (vs 0.8 pts baseline; 0 pts at τ≥0.5).
- Files: experiments/selective_encoding_v1/results.csv, selective_encoding_collapse.png, finding.md

## 2026-05-02 — personality_emergence (THE HEADLINE)
- Hypothesis: bounded memory + per-agent encoding jitter (joint sufficiency) produces behavioral types and breaks the Homogenization Collapse.
- Result: PARTIAL POSITIVE — encoding jitter ALONE delivers a 2.55× sustained rescue rate (15.4% → 39.2% avg ep5-9). Bounded memory alone is null. Behavioral TYPES still don't emerge (divergence@5-9 stays ~+3pts), but population-level CAPACITY is restored. First positive finding in the project. Naming: The Encoding Diversity Effect.
- Headline number: 2.55× sustained rescue rate from encoding noise σ=0.15.
- Files: experiments/personality_emergence_v1/{README.md, results.csv, personality_emergence.png, finding.md}
- Companion null: experiments/memory_capacity_v1 — bounded memory alone delivers nothing (max +4.4 pts at cap=3).

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

## 2026-05-05 — decay_asymmetry
- Hypothesis: Faster decay on loyalty memories than on guilt memories ("forgiveness for self, not others") preserves rescue capacity over chained episodes — should lift ep5–9 rescue rate at κ=1.0 toward the rescue-encoding-OFF baseline of 28%.
- Result: failed in opposite direction — ep5–9 mean rescue is flat (range 2.0 pts across β_loyalty ∈ {0.05, 0.15, 0.30, 0.50} with β_guilt=0.05), but the population divergence@5–9 INVERTS sign monotonically from +13.3 pts (symmetric) to −18.8 pts (extreme asymmetry). Asymmetric forgiveness erases experience-driven type formation rather than enabling it.
- Headline number: ep5–9 mean rescue {20.8, 19.4, 19.0, 18.8}% (range 2.0 pts); divergence@5–9 {+13.3, +4.2, −14.6, −18.8} pts (32-pt swing).
- Files: experiments/decay_asymmetry_v1/README.md, results.csv, decay_asymmetry.png, finding.md
- Follow-ups added to backlog: reversed-asymmetry falsifier; κ=0.5 replication; memory-population audit.

## 2026-05-06 — decay_asymmetry_reversed
- Hypothesis: Reversing the 2026-05-05 sweep (β_loyalty=0.05 fixed, sweep β_guilt) should produce monotone GROWTH in divergence@5–9 if the loyalty-cushion-vs-guilt-counterweight interpretation is correct. Cleanest single falsifier.
- Result: failed — divergence does NOT grow with β_guilt; it falls toward 0 across the first three cells (+10.6 → +3.6 → −1.5 pts) then β_guilt=0.50 breaks the committed regime entirely (ep0 collapses 84% → 44%). The cushion-vs-counterweight interpretation is falsified; the operative mechanism is "any imbalance erases experience-driven type formation," not directional. Symmetric mild decay (β=0.05 both sides) is now confirmed across two independent runs as the only regime that preserves +10–13 pts divergence.
- Headline number: divergence@5–9 {+10.6, +3.6, −1.5, +10.9} pts; ep5–9 mean rescue {19.4, 20.8, 17.4, 9.4}%; ep0 rescue {84, 75, 59, 44}% (regime break at β_guilt=0.50).
- Files: experiments/decay_asymmetry_reversed_v1/README.md, results.csv, decay_asymmetry_reversed.png, finding.md
- Follow-ups added to backlog: fine-grained reversed sweep (β_guilt ∈ 0.05–0.30); regime-break check on the prior loyalty-side sweep; seed-charge magnitude match.

## 2026-05-07 — memory_population_audit
- Hypothesis: Snapshotting the M store at end-of-ep4 across the 4 decay_asymmetry_reversed cells will resolve whether divergence-erosion under asymmetric forgiveness is mediated by per-class memory weight in the γ·|emotion| recall term.
- Result: confirmed with a sharper mechanism. Asymmetric forgiveness "launders" failure-tagged memories — at β_guilt=0.15 the guilt channel decays so fast that 78% of failure memories now have stored loyalty > stored guilt at recall time (vs 0% in the symmetric β=0.05 cell). The outcome ledger of M collapses into one effective valence class. Per-channel guilt total per agent drops from 0.95 to 0.48 (factor ~2); the laundering rate plateaus at 75–78% across all asymmetric cells.
- Headline number: % of failure-tagged memories with stored loyalty > stored guilt at end-of-ep4 = {0%, 78%, 75%, 78%} across β_guilt ∈ {0.05, 0.15, 0.30, 0.50}.
- Files: experiments/memory_population_audit_v1/README.md, results.csv, memory_snapshot.csv, memory_population_audit.png, finding.md
- Follow-ups added to backlog: laundering_kappa_invariance, tag_aware_recall, laundering_inflection (fine β_guilt sweep), recharge_on_recall counter-mechanism.

## 2026-05-08 — laundering_kappa_invariance
- Hypothesis: Replicate the memory_population_audit at κ=0.5 (boomerang shoulder). Predicts laundering rate ~78% at β_guilt=0.15 even if macro divergence is muted.
- Result: held — laundering rate at κ=0.5 is statistically indistinguishable from κ=1.0 across all four cells; mechanism pinned to decay arithmetic, not regime-coupled. Macro divergence is unmeasurable at κ=0.5 because ep1 collapses universally to 0% rescue, so the audit's behavioral slice can't be applied at this regime — confirms the audit's prediction that "the macro divergence may not invert at κ=0.5, but the laundering microstructure should be identical."
- Headline number: failure-memory laundering rate at end-of-ep4 = {0.0%, 80.7%, 76.5%, 81.1%} across β_guilt ∈ {0.05, 0.15, 0.30, 0.50} at κ=0.5; κ=1.0 reference {0%, 78%, 75%, 78%} (max cross-κ Δ = 3.2 pts).
- Files: experiments/laundering_kappa_invariance_v1/README.md, results.csv, memory_snapshot.csv, laundering_kappa_invariance.png, finding.md
- Follow-ups: tag_aware_recall and recharge_on_recall promoted as next priorities — both target the decay-arithmetic layer that is now pinned by this κ-invariance.

## 2026-05-09 — tag_aware_recall
- Hypothesis: Pinning a memory's class identity to its encoding-time tag (instead of its current decayed `stored.guilt > 0.4` state) restores the committed-rescue regime under asymmetric forgiveness. If divergence persists under asymmetric β_guilt under this recall mode, laundering IS the mechanism.
- Result: held — long-run rescue (ep5–9 mean) approximately doubles at every β_guilt cell under tag-aware recall, and the regime-break at β_guilt=0.30 (ep0 rescue 80% → 48% under legacy) is fully eliminated (ep0 stays at 76% under tag-aware). Confirms valence laundering at the recall gate as the mechanism behind the 2026-05-06 divergence-erosion. A residual β_guilt=0.50 ep0 collapse (52% legacy → 58% tag-aware, vs 78% symmetric baseline) suggests a SECOND mechanism on the injection pathway.
- Headline number: ep5–9 mean rescue uplift across β_guilt ∈ {0.05, 0.15, 0.30, 0.50} = {+22.4, +15.2, +18.0, +18.0} pts (factors {2.06×, 1.76×, 2.61×, 2.67×}); β_guilt=0.30 ep0 rescue 48% → 76% (+28 pts).
- Files: experiments/tag_aware_recall_v1/README.md, results.csv, tag_aware_recall.png, finding.md
- Follow-ups added to backlog: tag_aware_injection, tag_aware_recall_kappa.
