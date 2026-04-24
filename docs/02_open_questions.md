# Open questions

Live list. Each entry is a real ambiguity that will affect results until resolved.

## 1. The argmin-vs-imperfection tension
The objective minimizes Φ + L. Minimization tends to sand off imperfections.
We get imperfect behavior here only because (a) Snap Time can cut deliberation
short before convergence, and (b) emotion injects shifting cost surfaces. If
neither were true the agent would always be optimal.
**Status:** monitor. If sweep results show no imperfection at any setting,
add explicit decision noise.

## 2. Is Φ a cost or a drive?
We currently treat Φ as a cost (low Φ = good). "Guilt overrides survival"
means the action that satisfies guilt has *lower* Φ than the one that satisfies
survival, *because* current guilt is high. This is internally consistent but
opposite to a naive read where "high guilt = high pressure to act on guilt."
**Status:** locked in as a cost. Documented here so the next reader doesn't
flip it.

## 3. Importance — what is it?
Currently set at memory-encoding time as a function of |emotion at encoding|
and surprise (deviation from expected reward). Other plausible definitions:
downstream consequence, recall frequency, social weight.
**Status:** v1 uses encoding-time emotion+surprise. Revisit after first results.

## 4. No persona anchor
Two agents trained on different histories may converge on the same e_t given
the same recent inputs. There's no persistent persona vector pulling e_t toward
a baseline. The framework has no identity, only state.
**Status:** known gap. Add a `persona_baseline` term in v2 if results show
identity drift.

## 5. Single agent
loyalty and guilt are inherently relational. The current sandbox has a "partner"
but that partner is scripted, not a fellow agent. Multi-agent dynamics are
deferred.
**Status:** parked.

## 6. Saturation
With e ∈ [0,1], extreme events saturate emotion to the ceiling. After saturation,
further evidence has no effect — the agent loses sensitivity. This may produce
surprising "numb" behavior at high κ.
**Status:** intentional. May be a feature (matches human numbness under
prolonged stress) or a bug (kills information).
