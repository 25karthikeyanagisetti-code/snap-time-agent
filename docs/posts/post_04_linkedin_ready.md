# Post 4 — LinkedIn ready (Wave 2 + Wave 3 combined)

> Copy the body below into LinkedIn. Attach the four images in this order:
>   1. hysteresis_collapse.png
>   2. aging_collapse.png
>   3. couplings_zoo.png
>   4. severity_threshold.png
> Repo link goes where it says [link to GitHub repo].

---

I expected experience to make my AI agent more like a person.

I built 100 agents, gave each one a chain of 10 episodes in a rescue-vs-resource dilemma, let them carry their memories forward, and encoded the outcome of each episode into the memory store at the end. The hypothesis was simple: agents that happen to rescue someone in their first episode should encode a positive memory and become more rescue-prone over time. Agents that fail should fail more. Behavioral types from experience.

What I got was the opposite — and it's the most astonishing result the framework has produced so far.

In the regime where the agent is RELIABLY a rescuer (κ=1.0), 78% of agents save the partner in episode 0. By episode 1, after exactly ONE outcome-encoded memory has been added to the store, rescue rate collapses to 17% and stays there for the rest of the chain.

The committed regime evaporates in a single round of self-experience.

I'm calling it the Homogenization Collapse.

The mechanism turned out to be mechanical and inevitable. Every episode that doesn't end in rescue encodes a guilt-charged memory. Memories accumulate. Reactivation gain compounds. The agent's emotion gets pulled toward the seeded pattern more and more reliably. Even agents who STARTED as confident rescuers cannot keep up with their own growing pile of failure memories. All initial conditions converge to the same stable failure attractor.

In human terms, the architecture is saying: you cannot become a person through experience here — experience flattens you toward the average regardless of what you do.

That's a real failure of the framework. And it's the kind of failure worth knowing about, because it tells us exactly what's missing: there is no SELECTIVE encoding, no valence learning that distinguishes good from bad, no consolidation mechanism that prunes the memory population. Build any of those in and the result might change. Without them, cumulative memory does not produce personality — it produces regression to a single attractor.

This came out of a much larger run. Two more findings from the same wave that matter:

THE FORGIVENESS TRADEOFF. I tested whether the agent could escape the original Paralysis Valley by forgetting the past. Aging the seeded memory dramatically rescued the agent from paralysis (98% failure → 40% at κ=0.25). But it ALSO stripped out the committed-rescuer regime — at κ=1.0 where the agent USED to reliably rescue (22% failure), aging pushed it back UP to ~38%. There is no pre-age in the sweep where the agent both escapes paralysis AND keeps the capacity to commit. Forgetting the wound costs the lesson the wound taught. Forgiveness in this architecture is a flattener, not a balancer.

NO FREE LUNCH ACROSS FOUR COUPLINGS. The original valley used the additive form Φ = -v + κ⟨e,c⟩. I tested four different mathematical forms (additive, multiplicative, max, log-sum-exp). Each one produced a distinct pathology. Multiplicative removes the valley but never rescues anyone — value-greedy at all κ. Max produces PERMANENT paralysis at high κ — winner-take-all emotion is catastrophic. Log-sum-exp partially rescues but with a worse middle. None of the four hand-crafted Φ forms gives both no-paralysis AND robust rescue. The trade-off appears intrinsic to this class of architecture, not an artifact of one formula.

And one cleaner sub-finding worth noting: the original Paralysis Valley has a memory-severity threshold. Below severity ≈ 0.4 it does not exist at all. The agent only paralyzes when the seeded emotion is strong enough to disrupt the value path but not strong enough to commit to the alternative. There is an actual onset.

The pattern across the whole wave is: the framework has rich failure modes that mirror real human ones — paralysis when emotion is moderate, regression to baseline after forgetting, collapse of differentiation under cumulative memory — and the algebra ALONE is not enough to produce robust adaptive behavior. You need structural mechanisms (selective encoding, valence learning, consolidation) layered on top of the math.

Across waves 1, 2, and 3 the project has now run 80,800 episodes, four control conditions, and four Φ formulations. Code, data, full sweep results in the repo: [link to GitHub repo]

For others working on memory-augmented agents — does this homogenization-after-experience pattern show up in your work? Or does cumulative memory differentiate your population the way I expected mine to?

#AIResearch #AgentSystems #CognitiveArchitecture #HumanLikeAI #MemorySystems
