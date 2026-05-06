# Finding — Decay Asymmetry REVERSED falsifies the 2026-05-05 mechanism story

## TL;DR

The 2026-05-05 `decay_asymmetry` sweep produced a 32-pt divergence-inversion swing as β_loyalty grew from 0.05 to 0.50 with β_guilt held at 0.05. The interpretation in `findings_v3` was a **loyalty-cushion vs guilt-counterweight** mechanism — clear loyalty fast, the guilt prior dominates, and ep1-rescuers no longer differ from ep1-failers. That interpretation makes a sharp signed prediction under reversal: hold β_loyalty fixed, sweep β_guilt, and divergence should GROW positive monotonically.

It does not. Across β_guilt ∈ {0.05, 0.15, 0.30, 0.50} with β_loyalty=0.05, divergence@5–9 falls toward zero across the first three cells (+10.6 → +3.6 → −1.5 pts) and the fourth cell exits the committed regime (ep0 rescue rate collapses from 84% to 44%, indicating the seeded abandonment prior is being stripped of its guilt charge during the first episode itself).

The headline is therefore: **the 2026-05-05 inversion is symmetric in asymmetry-magnitude, not signed in direction.** Any imbalance between guilt-side and loyalty-side decay rates erodes experience-driven type formation. The prior interpretation that singled out loyalty-cushion erosion as the operative mechanism is falsified.

## Stronger statement of the result

Two cells share a forgiveness configuration whose stored emotion bleeds at a uniform mild rate of 0.05 per step on both channels: this sweep's `β_guilt=0.05` cell and the prior sweep's `β_loyalty=0.05` cell. Both produce positive ep1-driven divergence (+10.6 and +13.3 pts respectively), and both produce ep5–9 mean rescue rates near 20% in the locked boomerang band. The two independent runs are consistent within sampling noise. This is the only forgiveness configuration under which the population in this framework exhibits experience-driven type formation.

Three cells in this sweep (β_guilt=0.15, 0.30, 0.50) introduce asymmetry on the opposite channel from the prior sweep. None of them produces the predicted divergence-growth. β_guilt=0.15 already drops divergence to +3.6 pts, β_guilt=0.30 reverses it to −1.5 pts. The sign goes negative at lower β_guilt than the prior sweep's β_loyalty (which crossed zero between 0.15 and 0.30 also), and the negative magnitudes are smaller (−1.5 vs −14.6 at the matching position).

The amplitude asymmetry between the two sweeps is the most natural way to localize WHICH stored-emotion magnitude is operative. The prior sweep clears the rescue memory's loyalty charge fully and produces a −18.8-pt swing at β=0.50 (still inside the committed regime, ep0=74%). The reversed sweep clears the seeded abandonment prior's guilt charge fully and at β=0.50 produces a regime change (ep0=44%). That asymmetry is consistent with the seeded prior carrying more emotion magnitude on its dominant channel than the encoded rescue memory does on its dominant channel — and with the sandbox responding to that prior's dissolution by losing its committed-regime grip rather than by inverting type-formation.

## What this would take to be falsified itself

- A reversed-axis run at β_guilt extending finer between 0.05 and 0.30 (e.g. {0.05, 0.10, 0.15, 0.20, 0.25, 0.30}) that resolves whether divergence crosses zero earlier or whether it actually rises before falling. The current sweep is too coarse to rule out a small but real positive bump at β_guilt ≈ 0.10 — which would partially rescue the directional interpretation.
- A controlled run that scales emotion magnitudes rather than decay rates: cap the seeded prior's guilt charge at the rescue memory's loyalty charge magnitude, so the two channels carry equal stored weight. If divergence is then signed under reversed asymmetry, the magnitude-asymmetry framing is wrong and the prior interpretation was right but obscured by a hidden asymmetry in seed-vs-encoding charge sizes.
- A `memory_population_audit` that snapshots the M store at ep5 in each cell, counts memories by class, and logs |emotion| magnitudes per class. Mediates the headline claim: if loyalty-class memories outweigh guilt-class memories at ep5 by a ratio that scales with β_guilt yet divergence still falls, the cushion-counterweight story is decisively dead. If the ratio is roughly constant across cells, the operative mechanism may be reactivation timing rather than memory weight.

## Follow-up experiments queued

- `memory_population_audit` (already in queue): instrumentation pass — count loyalty-vs-guilt memories and their |emotion| magnitudes at ep5 by cell.
- `decay_asymmetry_lower_kappa` (already in queue): replicate at κ=0.5 to test whether the divergence-erosion-from-imbalance pattern is regime-specific to the deep-committed κ=1.0 regime.
- `decay_asymmetry_fine_reversed` (NEW): sweep β_guilt ∈ {0.05, 0.10, 0.15, 0.20, 0.25, 0.30} with β_loyalty=0.05 to resolve whether there is a small positive bump in divergence at low-but-asymmetric β_guilt that the coarse sweep missed.
- `regime_break_check` (NEW): re-run the prior decay_asymmetry sweep at β_loyalty extended to 0.70 and 0.90 to see whether ep0 also collapses on the loyalty side at sufficiently extreme values, or whether the regime-break is unique to the guilt-side.
- `seed_charge_match` (NEW): scale seeded abandonment guilt to match the encoded rescue memory's loyalty magnitude (~0.4 vs current ~1.0 effective at preage=15). If divergence then becomes signed under reversed asymmetry, the cushion-counterweight story partially survives — only obscured by a charge-magnitude asymmetry.

## Connection back to the framework

What survives across both decay-asymmetry runs is a single positive claim: **symmetric mild stored-emotion decay (β=0.05 on every channel) is the only forgiveness regime under which the population in this framework shows experience-driven differentiation.** All asymmetric variants — in either direction, at any moderate magnitude tested — erode divergence@5–9 toward zero. At extreme magnitudes the asymmetry can also break the committed regime, depending on which channel hosts the seeded prior.

That positive claim is small compared to the magnitude of human personality drift (∼50–70 pts of behavior gap between early-rescuers and early-failers in human longitudinal studies) but it is the first stable signal we have that the framework can encode experience-driven types AT ALL. The next experimental wave should focus on amplifying this signal rather than chasing the boomerang on the headline-mean axis. Concretely: under symmetric mild forgiveness, can other interventions (memory eviction, recall-event-gating) push divergence from +13 toward +30 pts? That is now the most promising lever in this region of the parameter space.
