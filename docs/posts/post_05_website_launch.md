# Post 5 — Website launch (LinkedIn ready, optimized for reach)

> Suggested image attachments (in order — pick 3 of these):
>   1. screenshot_hero.png         — the 3D hero with the master equation
>   2. screenshot_emotion_card.png — the emotion radar + sliders panel
>   3. screenshot_simulation.png   — the live Rescue-vs-Resource sandbox running
>   4. screenshot_findings.png     — the 4 finding cards
>
> To capture: open https://25karthikeyanagisetti-code.github.io/snap-time-agent/
> on a desktop, Cmd-Shift-4 + Space, click the section.
>
> Image best practice: vertical / square images get more LinkedIn feed real
> estate than landscape. If you have time, take portrait-orientation phone
> screenshots from the live site instead.

---

I built an AI agent, gave it five emotions, a memory that ages, and a deadline.

It paralyzed itself.

For the last few months I've been running an experiment most AI labs aren't: instead of making agents smarter, I've been trying to make them more HUMAN — not human-sounding, but human in the broken, hesitant, forgiving way actual people are.

The framework adds three things to a standard LLM objective:

— An emotion vector e_t = [survival, guilt, loyalty, fear, curiosity]
— A memory store that decays with age and intensifies with emotional charge
— "Snap Time": a bounded window that forces the agent to commit before it runs out

Across 80,800 simulated episodes, three failure modes appeared that mirror real human ones:

THE PARALYSIS VALLEY — a SMALL amount of emotion makes the agent fail MORE than no emotion at all. Worst point: 98% failure.

THE FORGIVENESS TRADEOFF — aging the memory escapes paralysis but strips the capacity to commit. You can have peace OR principles. Not both.

THE HOMOGENIZATION COLLAPSE — cumulative experience doesn't differentiate the agents. It flattens them. Every initial condition collapses to the same failure attractor in ONE episode of self-experience.

Until today, those findings lived in CSV files in a repo nobody could see.

Today I'm launching the interactive site where anyone can run the experiments themselves. In a browser. In 10 seconds. No signup. No install. Works on a phone.

What you can do on it:

— Drag five emotion sliders and watch a live radar respond
— Change the memory decay rate β and watch memory orbs brighten or fade
— Switch between four mathematical formulations of decision pressure (Φ) and watch the same agent behave four different ways
— Run the full Rescue-vs-Resource sandbox in a 7×7 grid in your browser. Set κ=0.3, hit Run. Watch the agent freeze.

You just reproduced the Paralysis Valley.

Try it → https://25karthikeyanagisetti-code.github.io/snap-time-agent/

If you build AI agents: set κ=0.3, run an episode, and tell me in the comments — would you call what the agent does "thinking" or "stalling"?

If you don't build agents: just play with it. The hesitation feels real, even in something this small.

Save this post — you'll want to come back to the simulator.

Code, data, every sweep: https://github.com/25karthikeyanagisetti-code/snap-time-agent

#AI #ArtificialIntelligence #MachineLearning #AIResearch #AIAgents
