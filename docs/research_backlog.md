# Research backlog

The daily scheduled task pops the top item off this list, implements it, runs it, and commits the result. If this list is empty, the daily task generates a fresh hypothesis from the most recent findings.

## Format

Each item is a single bullet with: `<short_name>` — one-sentence hypothesis — what to vary — what to measure.

---

## Queued

- `tag_aware_recall` — Modify recall to use the tag (encoded valence at write time) for class identity rather than current stored channels. If divergence persists under asymmetric β under this recall mode, laundering IS the mechanism. (Elevated 2026-05-07; further promoted 2026-05-08 after laundering_kappa_invariance pinned the decay-arithmetic layer.)
- `laundering_inflection` — Fine sweep β_guilt ∈ {0.05, 0.07, 0.09, 0.11, 0.13, 0.15} at κ=1.0 to find the exact threshold where failure memories switch from class-preserving to class-flipping. (Elevated 2026-05-07.)
- `recharge_on_recall` — Add `+= δ` injection to stored emotion every time a memory reactivates above threshold. If this prevents laundering AND preserves divergence, we have a counter-mechanism. (Elevated 2026-05-07.)
- `decay_asymmetry_lower_kappa` — Replicate the 2026-05-05 4-cell sweep at κ=0.5 (boomerang is weaker there). Tests whether the divergence-inversion is regime-specific to deep-committed κ=1.0 or generic across the boomerang regime.
- `decay_asymmetry_fine_reversed` — Resolve whether the divergence falloff under β_guilt is monotone or has a small positive bump at low-but-asymmetric β_guilt. Sweep β_guilt ∈ {0.05, 0.10, 0.15, 0.20, 0.25, 0.30} with β_loyalty=0.05 at κ=1.0. Measure: divergence@5–9 fine-grained.
- `regime_break_check` — Re-run the 2026-05-05 loyalty-side sweep with β_loyalty extended to {0.70, 0.90} to test whether ep0 also collapses on the loyalty side at sufficiently extreme values, or whether the regime-break is unique to the guilt-side. Distinguishes "extreme asymmetry breaks regime" from "extreme guilt-side decay strips seeded prior."
- `seed_charge_match` — Scale the seeded abandonment-prior guilt charge to match the encoded rescue memory's loyalty magnitude. Re-run the reversed-asymmetry sweep. If divergence becomes signed, the cushion-vs-counterweight story partially survives — only obscured by a charge-magnitude asymmetry between seed and encoding. Falsifier of "magnitude-asymmetry alone explains the prior result."
- `rescue_payload_magnitude` — The boomerang is driven by the rescue memory's loyalty=0.8 emotion magnitude entering recall via the γ-term, not its importance. Vary: rescue payload loyalty ∈ {0.0, 0.2, 0.4, 0.6, 0.8}. Measure: ep5–9 rescue rate at κ=1.0. (Follow-up to loyalty_importance_floor null.)
- `recall_event_trace` — During a κ=1.0 chain, log every memory reactivation event (which memory fired, at what step, into what context). Hypothesis: rescue memories reactivate during deliberation steps (not only on rescue-cell terminal contexts), pulling emotion off the committed trajectory. (Follow-up to loyalty_importance_floor null.)
- `prior_dilution_rate` — At high encoding-gate τ, the seeded abandonment prior dominates indefinitely. Vary: prior preage ∈ {0, 5, 15, 30, 60}. Measure: rescue@ep9 at τ=0.7. (Follow-up to selective_encoding null.)
- `memory_consolidation` — Periodic pruning of low-impact memories preserves the committed-rescuer regime. Vary: prune_interval ∈ {1, 3, 5, 10}, prune_threshold ∈ {0.05, 0.15, 0.3}. Measure: rescue rate at episode 9 vs episode 0 across κ.
- `dynamic_kappa` — Annealing κ from high to low across episodes prevents paralysis early then allows rationality late. Vary: schedule ∈ {constant, linear_decay, step_decay}. Measure: failure rate trajectory across 10 episodes.
- `multi_memory` — Two seeded memories (loyalty AND guilt) cancel out — agent reverts to value-greedy. Vary: number of seeded memories ∈ {0, 1, 2, 3}. Measure: failure rate at κ=0.25.
- `memory_capacity` — A bounded memory store (LRU eviction) breaks the Homogenization Collapse. Vary: capacity ∈ {3, 5, 10, ∞}. Measure: rescue rate variance across initial conditions.
- `partner_deadline_sweep` — The Paralysis Valley shifts with the partner deadline. Vary: deadline ∈ {3, 5, 7, 10, 15}. Measure: κ_min of the failure peak.
- `noise_typology` — Different noise types (Gaussian on emotion vs uniform on Φ vs softmax temperature) have qualitatively different rescue effects. Vary: noise_target ∈ {emotion, phi, temperature}. Measure: failure rate at κ=0.5.
- `agent_memory_seed` — Letting the agent encode its OWN early-episode memory before the seeded one shifts the valley. Vary: warmup_episodes ∈ {0, 1, 3, 5}. Measure: failure rate distribution.
- `conflict_geometry` — A 3-objective sandbox (rescue + resource + escape) produces a different paralysis pattern than 2-objective. Build mini-sandbox; measure failure across κ.
- `outcome_boolean_gate` — Sample failure encodings with probability p (boolean, not magnitude-gated) while always encoding rescues. Vary: p ∈ {0.1, 0.25, 0.5, 1.0}. Measure: divergence@ep9 at κ=1.0. (Follow-up to signed_threshold lockout.)
- `outcome_importance_modulation` — Instead of thresholding *whether* to encode, scale per-outcome importance: rescue × m_l, failure × m_g. Vary: m_g ∈ {0.3, 0.6, 1.0}, m_l ∈ {0.3, 0.6, 1.0}. Measure: rescue rate trajectory.
- `joint_outcome_intensity_filter` — Encode IF outcome=rescue OR (outcome=failure AND e_max > τ). Cleanest decoupling of "whether" from "how loud". Vary: τ ∈ {0.0, 0.3, 0.5, 0.7}. Measure: ep9 rescue rate.

## Done (most recent at top)

- 2026-05-08: laundering_kappa_invariance — held; failure-memory laundering rate at end-of-ep4 = {0%, 80.7%, 76.5%, 81.1%} across β_guilt ∈ {0.05, 0.15, 0.30, 0.50} at κ=0.5, max cross-κ Δ = 3.2 pts vs the κ=1.0 audit. Mechanism pinned to decay arithmetic; macro divergence unmeasurable at κ=0.5 because ep1 collapses to 0% rescue universally.
- 2026-05-07: memory_population_audit — confirmed per-class memory weight as the divergence-erosion mediator; sharper mechanism is "valence laundering": 78% of failure-tagged memories at β_guilt=0.15 have stored loyalty > stored guilt at recall time (vs 0% at symmetric β=0.05); per-agent guilt-channel total drops 0.95 → 0.48.
- 2026-05-06: decay_asymmetry_reversed — falsifies the 2026-05-05 cushion-vs-counterweight interpretation; divergence@5–9 falls toward 0 across β_guilt ∈ {0.05, 0.15, 0.30} (+10.6 → +3.6 → −1.5 pts) instead of growing positive, and β_guilt=0.50 breaks the committed regime (ep0 84% → 44%). Symmetric mild decay (β=0.05) confirmed across two independent runs as the only regime preserving experience-driven type formation.
- 2026-05-05: decay_asymmetry — failed in opposite direction; ep5–9 mean rescue flat at 18.8–20.8% (range 2.0 pts) across β_loyalty ∈ {0.05, 0.15, 0.30, 0.50} with β_guilt=0.05, but divergence@5–9 inverts sign monotonically from +13.3 pts (symmetric) to −18.8 pts (extreme asymmetry).
- 2026-05-04: loyalty_importance_floor — NULL: ep5–9 rescue rate flat at 14–17% across rescue_importance ∈ {0.0, 0.1, 0.3, 0.5, 0.7}, range 2.4 pts; all ≥12 pts below 28% OFF baseline. Boomerang is structural, not importance-driven.
- 2026-05-03: signed_threshold_encoding — asymmetric τ_guilt/τ_loyalty gates FAIL in opposite direction; high-τ_guilt cells collapse to 0% ep9 rescue (prior-dilution lockout), best divergence +5.1 pts (inferior to symmetric baseline).
- 2026-05-02: valenced_encoding — bidirectional outcome encoding makes collapse WORSE, not better. ep9 rescue rate 28% (off) vs 15% (on); div@5–9 = −10 pts (on). Naming: The Loyalty Boomerang.
- 2026-05-01: selective_encoding — magnitude-gated outcome encoding does NOT prevent the Homogenization Collapse; produces a U-shape (max divergence@ep9 = 11.5 pts at τ=0.3, 0 pts at τ≥0.5).
