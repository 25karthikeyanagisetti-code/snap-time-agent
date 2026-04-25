# Push this repo to your GitHub

I cannot push from the Cowork sandbox — it has no GitHub network access and
cannot authenticate `gh`. Run the commands below in your own Terminal on your
Mac. Your GitHub username is hard-coded into the commands.

GitHub: https://github.com/25karthikeyanagisetti-code

## One-time prerequisites

If you don't have GitHub CLI installed:
```bash
brew install gh
gh auth login    # GitHub.com → HTTPS → Login with a web browser
```

## Push everything in one shot

Open Terminal and paste the entire block:

```bash
cd ~/Documents/Claude/Projects/"AI system"/snap-time-agent

# Clear any stuck git locks left by the sandbox
rm -f .git/index.lock .git/HEAD.lock

# Stage and commit waves 1, 2, 3 — full project
git add -A
git commit -m "snap-time-agent: framework + 3 waves of experiments

Wave 1 (regime_map_v1, 14,400 episodes):
- src/: emotion.py, memory.py, decision.py, sandbox.py (Rescue-vs-Resource),
  run_sweep.py, analyze.py, control_no_reactivation.py, make_post_visuals.py
- Headline: Paralysis Valley at low-medium kappa with seeded memory.

Wave 2 (severity_sweep_v1, phi_mode_v1, forgiveness_v1, 26,200 episodes):
- exp_severity.py:    valley has a memory-severity threshold (~0.4)
- exp_phi_mode.py:    multiplicative coupling kills valley AND rescue capacity
- exp_forgiveness.py: aging escapes valley by FLATTENING all kappa regimes
                      to neutral rationality (Forgiveness Tradeoff)
- src/make_v2_visuals.py renders aging_collapse.png, severity_threshold.png,
  phi_mode_comparison.png, forgiveness_heatmap.png
- docs/findings_v2.md and post_04_forgiveness_tradeoff.md draft

Wave 3 (couplings_v1, resonance_v1, hysteresis_v1, phase_boundary_v1, 40,200 episodes):
- exp_couplings.py:      no-free-lunch confirmed across 4 Phi forms
- exp_resonance.py:      stochastic resonance is local — rescues at the
                         valley shoulder but not at the bottom
- exp_hysteresis.py:     SELF-MEMORY HOMOGENIZATION (headline) — committed
                         regime collapses within ONE episode of outcome
                         encoding; no behavioral types emerge
- exp_phase_boundary.py: 41-point high-res kappa sweep at 3 T_snap values
- src/make_v3_visuals.py renders hysteresis_collapse.png, couplings_zoo.png,
                                  resonance_curve.png, phase_boundary.png
- docs/findings_v3.md and post_05_homogenization_collapse.md draft
- post_04_linkedin_ready.md combines wave 2 + wave 3 for LinkedIn

Total: 80,800 episodes across 8 sweeps, 4 control conditions, 4 Phi formulations."

# Create the GitHub repo and push in one shot
gh repo create snap-time-agent \
  --public --source=. --push \
  --description "Human-like AI agent framework: emotion vector + aging memory + Snap Time. Findings include the Paralysis Valley, Forgiveness Tradeoff, and Homogenization Collapse."
```

After it pushes, your repo will be live at:

**https://github.com/25karthikeyanagisetti-code/snap-time-agent**

Paste that URL into `docs/posts/post_04_linkedin_ready.md` where it says
`[link to GitHub repo]` before posting on LinkedIn.

## If `gh` is not installed and you don't want to install it

```bash
cd ~/Documents/Claude/Projects/"AI system"/snap-time-agent
rm -f .git/index.lock .git/HEAD.lock
git add -A
git commit -m "snap-time-agent: framework + 3 waves of experiments"

# Then go to https://github.com/new
#   - owner: 25karthikeyanagisetti-code
#   - repo name: snap-time-agent
#   - public
#   - DO NOT initialize with README, license, or .gitignore (the repo already has them)
# Then come back to Terminal and run:

git remote add origin https://github.com/25karthikeyanagisetti-code/snap-time-agent.git
git branch -M main
git push -u origin main
```

## After the push — recommended polish

1. Visit https://github.com/25karthikeyanagisetti-code/snap-time-agent
2. The README will render with the headline images embedded
3. Add repo "About" tags for discoverability:
   `human-like-ai`, `cognitive-architecture`, `agent-simulation`,
   `emotion-modeling`, `memory-systems`, `snap-time`
4. Post `docs/posts/post_04_linkedin_ready.md` on LinkedIn with these images:
   - hysteresis_collapse.png
   - aging_collapse.png
   - couplings_zoo.png
   - severity_threshold.png

## What others will see when they land on the repo

- README explaining the framework + all three waves of findings, with three
  headline images embedded
- `src/` — clean Python modules, one experiment per file, no OOP
- `experiments/<name>_v1/` — for each sweep, the CSV results and the rendered
  charts side-by-side
- `docs/findings_v2.md` and `docs/findings_v3.md` — written-up analyses
- `docs/posts/` — LinkedIn drafts in social-post form
- LICENSE (MIT) so others can fork and extend
