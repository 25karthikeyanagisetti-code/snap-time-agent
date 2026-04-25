# Post 5 — The Homogenization Collapse

> Suggested image order:
>   1. hysteresis_collapse.png   (the headline — three panels)
>   2. couplings_zoo.png         (no-free-lunch across four Φ forms)
>   3. phase_boundary.png        (valley narrows but never vanishes)

---

Third wave of results from my human-like AI agent project.

I expected to find that early luck shapes long-term behavior. Agents that
happen to rescue someone in their first episode should encode a positive
loyalty memory and become more rescue-prone. Agents that fail should fail
more. Personality from experience.

I ran 100 agents per condition, 10 episodes per chain, with memory carrying
forward and outcomes encoded into the memory store at the end of each
episode. Did luck matter?

No.

What I got instead is one of the strongest negative findings I've measured.

At κ=1.0, the "committed rescuer" regime where agents reliably save the
partner — episode 0 saw 78% rescue rate. By episode 1, after exactly ONE
outcome-encoded memory had been added to the store, rescue rate collapsed to
17% and stayed there for the rest of the chain.

The committed regime evaporates in a single round of self-experience.

Looking at episode-1-outcome conditional behavior in episodes 5–9: the gap
between "rescued in ep 1" and "failed in ep 1" agents is small and shrinking.
The framework does not produce behavioral types. All initial conditions
converge to the same stable failure attractor — chronic rescue collapse with
intermittent resource grabs.

I'm calling it the Homogenization Collapse.

The mechanism is mechanical. Every episode that doesn't end in rescue
encodes a guilt-charged memory. Memories accumulate. Reactivation gain
compounds. The agent's emotion gets pulled toward the seeded pattern more
and more reliably. Even agents who STARTED as confident rescuers can't keep
up with their own growing pile of failure memories.

In human terms, the architecture is saying: "you cannot become a person
through experience here — experience flattens you toward the average."

That's a real failure of the framework, and it's the kind of failure that's
worth knowing about. Building toward human-like behavior requires more than
a memory store with sensible decay terms. It requires SELECTIVE encoding,
emotional valence learning that distinguishes good outcomes from bad, or
some consolidation/forgetting mechanism that keeps the memory population
from degenerating into a single dominant attractor.

Two more findings from the same wave:

NO FREE LUNCH ACROSS FOUR Φ COUPLINGS. I tested four Φ forms (additive,
multiplicative, max, log-sum-exp). Each one has a distinct pathology:
additive has the original valley but lets agents commit; multiplicative
removes the valley but eliminates rescue capacity entirely; max produces
PERMANENT paralysis at high κ; log-sum-exp is a mix. None give both
"no paralysis" AND "robust rescue." The trade-off appears intrinsic to
this class of architectures.

VALLEY SHAPE WITH HIGH RESOLUTION. A 41-point κ scan shows the valley
narrows and shifts right as Snap Time grows — but at T_snap=20 there is
still a 63% failure peak. More deliberation time helps, but it does not
eliminate paralysis.

Code, data, sweeps for all four experiments in the repo: [link to GitHub repo]

For others working on memory-augmented agents — does your system show this
flatten-after-experience pattern, or does cumulative memory differentiate
your population? Curious whether this is universal to outcome-encoding
schemes or specific to this framework.

#AIResearch #AgentSystems #CognitiveArchitecture #HumanLikeAI #MemorySystems
