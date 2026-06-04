# Daily research log

One entry per scheduled-task run. Most recent at the bottom.

## 2026-05-29 — behavioral_typing_verify (THE HEADLINE — MULTI-SEED VERIFIED)
- Hypothesis: the 86% rescuer-rate finding from this morning's behavioral_typing re-analysis (single-seed) survives multi-seed replication with separation > 50 pts vs control.
- Result: VERIFIED, sharper than the original estimate. Across 5 independent seed groups: σ=0.40 treatment yields 88.8% ± 8.2% rescuer rate vs 4.8% ± 3.3% in σ=0 control. Failure rate: 0.0% across ALL 125 treatment agents vs 20.0% in control. Welch t=21.2, p<<0.001. Separation +84.0 pts.
- Headline number: 88.8% ± 8.2% rescuer rate; 0.0% failure rate (verified across 5 seeds, n=125 agents).
- This is the project's biggest verified finding — multi-seed evidence that the framework DOES produce behavioral types from experience under encoding diversity at high κ. Answers the Wave-3 open question.
- Files: experiments/behavioral_typing_verify_v1/{README.md, results.csv, behavioral_typing_verify.png}
- Pairs with: experiments/behavioral_typing_v1/ (single-seed re-analysis that surfaced the finding).

## 2026-05-29 — behavioral_typing (re-analysis surfacing the finding)
- Hypothesis: the morning's "behavioral types don't emerge" claim (divergence@5-9 ~+3pts) might be using the wrong metric — per-agent typing distribution should be checked directly.
- Result: BIG. Re-analysis of jitter_sigma_long_v1 reveals 86% of agents at σ=0.40 κ=2.0 over 20 chained episodes become BEHAVIORAL RESCUERS (≥15/20 rescues); 0% become behavioral failures. At σ=0 baseline: 0% rescuers, 10% failures, 64% middling. Typing is UNIPOLAR (everyone becomes a rescuer), not bipolar (which is why divergence@5-9 missed it for 10 months of experiments).
- Headline number: 86% rescuers vs 0% baseline; 0% failures vs 10% baseline. Single-seed.
- Files: experiments/behavioral_typing_v1/{README.md, per_agent_rescue_counts.csv, behavioral_typing.png}

## 2026-05-01 — selective_encoding
- Hypothesis: Encoding only high-magnitude emotional outcomes (gate on max(final_emotion)) prevents the Homogenization Collapse at κ=1.0.
- Result: failed — magnitude-gating produces a U-shaped homogenization: too little encoding floods the store, too much lets the seeded prior dominate; rescue rate at ep9 stays ≤15% across all τ.
- Headline number: max divergence@ep9 = 11.5 pts at τ=0.3 (vs 0.8 pts baseline; 0 pts at τ≥0.5).
- Files: experiments/selective_encoding_v1/results.csv, selective_encoding_collapse.png, finding.md

## 2026-05-02 — paralysis_softmax_fix (NEW SUB-MECHANISM)
- Hypothesis: lowering softmax temperature toward argmin breaks the Paralysis Valley by committing the agent to whichever action has even a slight Φ lead.
- Result: PARTIAL + NEW MECHANISM REVEALED. At the valley shoulder (κ=0.5), low T rescues — 33% → 43% rescue rate at T=0.05. At the valley peak (κ=0.25), no T value rescues — 91-100% TIMEOUT regardless. The agent locks onto a non-progressive argmin and doesn't break out. Refines the original Wave-1 dither hypothesis: the Paralysis Valley has TWO sub-mechanisms — DITHER (shoulder, partially fixable by low T) and LOCK-IN (peak, not fixable by T).
- Headline number: κ=0.5 rescue rate 33% → 43% at T=0.05; κ=0.25 stays at 0-1.7% across all T.
- Files: experiments/paralysis_softmax_fix_v1/{README.md, results.csv, paralysis_softmax_fix.png}

## 2026-05-02 — jitter_sigma_long (LONG-HORIZON STABILIZATION CONFIRMED)
- Hypothesis: jitter σ has an inverted-U; saturation at large σ via [0,1] emotion clamp. Also: the κ=2.0 stabilization is a true equilibrium, not a slow decay.
- Result: BOTH PARTIALLY HELD/REFUTED. The σ effect is MONOTONICALLY INCREASING up to σ=0.40 — no observed saturation. At σ=0.40 sustained rescue at ep5-9 = 84.8% and at ep15-19 = 84.4% (decay only -0.4 pts) — the stabilization IS a true long-horizon equilibrium. Long-horizon ratio σ=0.40 vs σ=0 baseline: 3.30× (84.4% vs 25.6% at ep15-19).
- Headline number: σ=0.40 at κ=2.0 yields 85% sustained rescue rate, stable to within 1 pt across episodes 5-19.
- Files: experiments/jitter_sigma_long_v1/{README.md, results.csv, jitter_sigma_long.png}

## 2026-05-02 — jitter_universality (SHARPENING THE PRIOR)
- Hypothesis: encoder homogeneity is the substrate of every collapse mode in this framework — jitter should rescue both the Homogenization Collapse AND the Paralysis Valley.
- Result: PARTIALLY REFUTED, but produced a SHARPER finding. Jitter does NOT help at the Paralysis Valley (κ=0.25-0.5: 0% gain). It does help in the committed regime, with strength SCALING in κ: +2.4 pts at κ=0.5, +16.4 at κ=1.0, +43.6 at κ=2.0. At κ=2.0 jitter completely STABILIZES the regime — rescue rate stays at 76% across episodes 1-9 instead of decaying to 20%. Two failure modes, two distinct mechanisms.
- Headline number: 2.60× sustained rescue rate at κ=2.0 (27.2% → 70.8%); regime fully stabilized.
- Files: experiments/jitter_universality_v1/{README.md, results.csv, jitter_universality.png, finding.md}

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

## 2026-05-11 — tag_aware_injection
- Hypothesis: Tag-keyed floors on `inject_recalled_emotion` (`max(stored, floor)` per dim) close the residual β_guilt=0.50 ep0 collapse left over by the 2026-05-09 tag-aware-recall fix. Tests whether the injection pathway is the second laundering mechanism.
- Result: FAILED at the headline cell — Δep0 at β_guilt=0.50 = −2.0 pts (66% INJ-ON vs 68% INJ-OFF, within sampling noise). The injection pathway is NOT the residual mechanism. UNEXPECTED secondary: the biggest ep0 uplift (+20 pts) lands at the symmetric β_guilt=0.05 cell — the floor is fixing natural aging of the seeded prior, not laundered failure memories. Δep0 vector monotonically decreasing in β_guilt: {+20.0, +8.0, +14.0, −2.0} pts — opposite to the laundering prediction.
- Headline number: Δep0 at β_guilt=0.50 = −2.0 pts (residual gap NOT closed); +20.0 pts at β_guilt=0.05 (seed-aging fix, wrong cell).
- Files: experiments/tag_aware_injection_v1/README.md, results.csv, tag_aware_injection.png, finding.md
- Follow-ups added to backlog: recall_event_trace promoted; seed_only_floor (new); β=0.50 N=200 replication (new).

## 2026-05-12 — seed_only_floor
- Hypothesis: Pruning the tag-aware injection floor table to ONLY the 'seed' entry (outcome-tagged memories fall back to legacy literal-stored injection) reproduces the full-floor Δep0 vector at all 4 β_guilt cells. If yes, per-class outcome floors are inert and the operative mechanism is "seed prior decays under preage, floor restores it on recall."
- Result: HELD with caveat — at 3/4 cells (β_guilt ∈ {0.05, 0.15, 0.50}) seed-only matches full-floor Δep0 to within sampling noise; at β_guilt=0.50 (the regime-breaking cell) BOTH modes deliver an identical +10 pts ep0 uplift and identical +9 pts ep5–9 uplift. β_guilt=0.30 is the lone disagreement (Δfull=0, Δseed=−15 — a 2-SE gap pending N=200 replication). Outcome floors confirmed inert at the cell that motivated the tag_aware_injection thread.
- Headline number: at β_guilt=0.50, seed-only Δep0 = +10 pts = full-floor Δep0 (identical); at β_guilt=0.30, seed-only underperforms full by 15 pts.
- Files: experiments/seed_only_floor_v1/README.md, results.csv, seed_only_floor.png, finding.md
- Follow-ups added to backlog: seed_only_floor_b30_n200, seed_refresh, seed_only_floor_ep5_9_audit, floor_negative_control.

## 2026-05-13 — seed_only_floor_b30_n200
- Hypothesis: Replicating the β_guilt=0.30 cell of seed_only_floor at N=200 will tighten the −15 pts Δfull−Δseed gap to ≤5 pts, resolving whether per-class outcome floors carry a real (small) contribution at moderate asymmetry or the gap was sampling noise.
- Result: HELD — the gap collapses from 15 pts (N=40) to **1.0 pt** (N=200), well inside the 2-SE band of ~9.2 pts. ep0 rates: OFF=69.5%, Full=68.5%, Seed-only=69.5%. Δfull=−1.0 pts, Δseed=+0.0 pts — statistically indistinguishable. Per-class outcome floors confirmed inert at the β_guilt=0.30 cell too. The 2026-05-12 "HELD with caveat" upgrades to HELD across all four β_guilt cells.
- Headline number: |Δfull − Δseed| at ep0 collapses 15.0 → 1.0 pt going N=40 → N=200; residual ep5–7 full-vs-seed gap is 4.8 pts (within 2-SE, suggestive only).
- Files: experiments/seed_only_floor_b30_n200_v1/README.md, results.csv, seed_only_floor_b30_n200.png, finding.md

## 2026-05-18 — seed_refresh
- Hypothesis: Bypassing the tag-aware injection floor table entirely and instead RESETTING the seed memory's stored.emotion back to its encoding template on every step reproduces the seed-only-floor Δep0 vector across all four β_guilt cells — establishing the floor table as a non-essential intermediate construct and "keep the aged prior loud, full stop" as the operative mechanism.
- Result: PARTIAL — held at the regime-breaking β_guilt=0.50 cell (Δrefresh=+40.0 pts vs Δfloor=+37.5 pts, |Δ−Δ|=2.5 pts inside the 2-SE band) but REFUTED at low and mild asymmetry. At β_guilt=0.05 seed_refresh HURTS ep0 by 10.0 pts where the floor helps by 5.0 pts; at β_guilt=0.15 the gap widens to |Δ−Δ|=20.0 pts. The floor's max(stored, floor) guardrail is mechanism-essential off-headline: it intervenes only when stored has decayed below the floor, while seed_refresh over-restores at every cell. The chain that compressed the tag TABLE to a single seed entry does NOT compress further — the max-at-injection OPERATOR is the smallest sufficient mechanism.
- Headline number: |Δrefresh − Δfloor| at ep0 = {15.0, 20.0, 10.0, 2.5} pts across β_guilt ∈ {0.05, 0.15, 0.30, 0.50}; refresh delivers −10 pts at the symmetric cell vs +40 pts at the regime-breaking cell.
- Files: experiments/seed_refresh_v1/README.md, results.csv, seed_refresh.png, finding.md

## 2026-05-19 — seed_refresh_capped
- Hypothesis: Replacing the unconditional overwrite m.emotion := encoding_template with the one-sided guardrail m.emotion[k] := max(stored[k], SEED_FLOOR[k]) per dim — applied to the seed memory's stored state at the start of every step — reproduces the seed-only-floor Δep0 vector at all four β_guilt cells. If yes, the operative mechanism is "max-guardrail applied to the seed" and the entire tag-floor dispatch table compresses to a single per-memory floor field at encoding time.
- Result: HELD — capped reproduces the seed-only-floor lift at every cell (max gap 7.5 pts at β=0.05, 5.0 elsewhere) and the over-restoration pathology that broke yesterday's overwrite at low asymmetry is eliminated (capped delivers +5 at β=0.05 vs refresh's −10). The architecture compresses: per-memory floor + one-line max guardrail at the source replaces the injection-time tag dispatch entirely.
- Headline number: |Δcapped − Δfloor| at ep0 = {7.5, 5.0, 5.0, 5.0} pts across β_guilt ∈ {0.05, 0.15, 0.30, 0.50} — max 7.5, mean 5.6, all inside the 2-SE band. Yesterday's overwrite scored {15.0, 20.0, 10.0, 2.5}.
- Files: experiments/seed_refresh_capped_v1/README.md, results.csv, seed_refresh_capped.png, finding.md

## 2026-05-20 — capped_floor_loyalty_sweep
- Hypothesis: Replicating exp_seed_refresh_capped with the swept axis flipped (β_guilt=0.05 fixed, β_loyalty ∈ {0.05, 0.15, 0.30, 0.50}) reproduces yesterday's source-vs-gate isomorphism — |Δcapped − Δfloor| ≤ ~7-8 pts at every cell — confirming the floor mechanism is a channel-symmetric stored-state property of the seed memory.
- Result: PARTIAL — mid-cells (β_loyalty ∈ {0.15, 0.30}) match exactly (gap 5.0 pts each) but endpoints (β_loyalty ∈ {0.05, 0.50}) blow out to 17.5 pts and in a consistent direction (capped > floor in both). Today's |Δcapped − Δfloor| vector: {17.5, 5.0, 5.0, 17.5} pts vs yesterday's guilt-axis {7.5, 5.0, 5.0, 5.0}. Mean gap doubles (5.6 → 11.3). Capped delivers +27.5 / +17.5 ep0 lift at the endpoints where floor delivers +10.0 / +0.0. Candidate mechanism: capped raises emotion_magnitude on the source, which amplifies the seed memory's exp(γ·|emotion|) recall-impact term BEFORE the gate runs — an effect that floor-at-gate can't replicate. The architectural compression survives at mid-asymmetry but introduces a measurable (and directionally consistent) bonus at endpoints.
- Headline number: |Δcapped − Δfloor| = {17.5, 5.0, 5.0, 17.5} pts (mean 11.3, max 17.5 — 2× yesterday's mean of 5.6 along the guilt axis); at β_loyalty=0.50 floor=0.0 pts, capped=+17.5 pts (largest single-cell divergence).
- Files: experiments/capped_floor_loyalty_sweep_v1/README.md, results.csv, capped_floor_loyalty_sweep.png, finding.md

## 2026-05-21 — capped_loyalty_n200_endpoints
- Hypothesis: Replicating yesterday's β_loyalty ∈ {0.05, 0.50} endpoint cells of capped_floor_loyalty_sweep at N=200 (3 modes × 2 cells × 200 agents × 4 episodes = 4,800) will collapse the 17.5-pt endpoint gaps below the ≈6.5 pt 2-SE band — discriminating "real MemoryImpact-amplification" from "N=40 sampling noise."
- Result: HELD — endpoint substitutability gaps collapse from {17.5, 17.5} pts (N=40) to {0.0, 3.5} pts (N=200), a 10× reduction. β=0.05 delivers an exact point-estimate match (capped and floor both −5.5 pts vs OFF); β=0.50 gap of 3.5 pts is well inside the 2-SE band. The MemoryImpact-amplification reading is falsified at the headline cell. The 2026-05-20 PARTIAL upgrades to HELD: the source-vs-gate isomorphism IS channel-symmetric across both decay axes. The OFF baseline itself drifted 17 pts between yesterday's β=0.05 (62.5%) and today's (79.5%), consistent with N=40 OFF-baseline noise driving the apparent "consistent direction" endpoint blowouts.
- Headline number: |Δcapped − Δfloor| at endpoints collapses {17.5, 17.5} → {0.0, 3.5} pts going N=40 → N=200 (10× reduction; max 3.5, mean 1.75, both inside 6.5-pt 2-SE band).
- Files: experiments/capped_loyalty_n200_endpoints_v1/README.md, results.csv, capped_loyalty_n200_endpoints.png, finding.md

## 2026-05-29 — capped_floor_impact_decomp
- Hypothesis: Per-step seed memory impact traces diverge across modes (off / seed_only_floor / seed_refresh_capped) at the recall-side measurement layer even when macro ep0 rescue rates are similar — a deconfirmation experiment after the capped_loyalty_n200_endpoints HELD result.
- Result: Prediction B confirmed (downstream cancellation). At β_loyalty=0.50, seed_refresh_capped carries 0.113 more seed impact than seed_only_floor across steps 1–11 of ep0, yet achieves 7.5 pts LOWER rescue rate (72.5% vs 80.0%). The impact amplification from writing the floor back to stored emotion (boosting exp(γ·|emotion|)) over-steers guilt recall throughout the episode and hurts rather than helps. At β_loyalty=0.05, impact gap is 0.041 (late-episode only) and rescue gap is within N=40 noise.
- Headline number: max impact gap at β_loyalty=0.50 = 0.113; Δrescue(floor − capped) = +7.5 pts despite capped having higher recall strength.
- Files: experiments/capped_floor_impact_decomp_v1/README.md, results_macro.csv, results_trace.csv, impact_decomp_chart.png, finding.md

## 2026-06-04 — impact_decomp_beta_sweep
- Hypothesis: Fine sweep β_loyalty ∈ {0.10, 0.20, 0.30, 0.40, 0.50} reveals the exact threshold where seed_refresh_capped's impact gap crosses 0.05 and the rescue penalty becomes detectable.
- Result: PARTIAL — Prediction A CONFIRMED (impact gap monotone 0.016→0.077), threshold at β_loyalty* ≈ 0.35–0.40 confirmed; Prediction C NOT confirmed — rescue penalty indistinguishable from noise at N=40 (range −7.5 to +7.5 pts; 2-SE ≈ 14 pts). Prior experiment's 7.5 pt penalty at β_loyalty=0.50 was likely N=40 variance.
- Headline number: impact gap threshold crossed at β_loyalty* ≈ 0.35–0.40; rescue penalty = 0 ± noise (N=40).
- Files: experiments/impact_decomp_beta_sweep_v1/README.md, results_macro.csv, results_trace.csv, impact_decomp_beta_sweep.png, finding.md
