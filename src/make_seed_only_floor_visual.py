"""Visual for exp_seed_only_floor."""
import csv, os
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, "experiments", "seed_only_floor_v1", "results.csv")
OUT = os.path.join(ROOT, "experiments", "seed_only_floor_v1", "seed_only_floor.png")

BETAS = [0.05, 0.15, 0.30, 0.50]
MODES = ["off", "full", "seed_only"]
LABELS = {"off": "INJ-OFF", "full": "Full floors", "seed_only": "Seed-only floor"}
COLORS = {"off": "#c084fc", "full": "#4fc3f7", "seed_only": "#ffe2ac"}

rows = []
with open(IN) as f:
    r = csv.DictReader(f)
    for row in r:
        row["beta_guilt"] = float(row["beta_guilt"])
        row["episode_idx"] = int(row["episode_idx"])
        row["rescued"] = int(row["rescued"])
        rows.append(row)

def rate(mode, bg, ep_filter):
    sel = [x for x in rows if x["inject_mode"] == mode and x["beta_guilt"] == bg and ep_filter(x["episode_idx"])]
    return 100.0 * sum(x["rescued"] for x in sel) / len(sel)

# Panel A: ep0 rescue per mode × beta
# Panel B: Δep0 (full − off) vs Δep0 (seed_only − off)
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2),
                        facecolor="#0e131f", gridspec_kw={"wspace": 0.30})
for ax in axes:
    ax.set_facecolor("#131927")
    ax.tick_params(colors="#e8edf5")
    for spine in ax.spines.values():
        spine.set_color("#1f2638")
    ax.grid(True, color="#1f2638", linewidth=0.8, alpha=0.8)

ax = axes[0]
x = np.arange(len(BETAS))
width = 0.27
for i, m in enumerate(MODES):
    vals = [rate(m, bg, lambda e: e == 0) for bg in BETAS]
    ax.bar(x + (i - 1) * width, vals, width, color=COLORS[m],
           edgecolor="#0e131f", linewidth=0.8, label=LABELS[m])
    for j, v in enumerate(vals):
        ax.text(j + (i - 1) * width, v + 1.2, f"{v:.0f}",
                ha="center", color="#e8edf5", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels([f"{b:.2f}" for b in BETAS], color="#e8edf5")
ax.set_xlabel("β_guilt (β_loyalty=0.05 fixed)", color="#e8edf5")
ax.set_ylabel("ep0 rescue rate (%)", color="#e8edf5")
ax.set_title("ep0 rescue rate — seed-only floor reproduces full-floor lift",
             color="#ffe2ac", fontsize=12, pad=10)
ax.set_ylim(0, 100)
leg = ax.legend(facecolor="#0e131f", edgecolor="#1f2638", labelcolor="#e8edf5",
                loc="lower left", fontsize=9)

ax = axes[1]
d_full = np.array([rate("full", b, lambda e: e == 0) - rate("off", b, lambda e: e == 0) for b in BETAS])
d_seed = np.array([rate("seed_only", b, lambda e: e == 0) - rate("off", b, lambda e: e == 0) for b in BETAS])
ax.bar(x - 0.20, d_full, 0.40, color="#4fc3f7", edgecolor="#0e131f",
       linewidth=0.8, label="Δep0 full − off")
ax.bar(x + 0.20, d_seed, 0.40, color="#ffe2ac", edgecolor="#0e131f",
       linewidth=0.8, label="Δep0 seed_only − off")
ax.axhline(0, color="#1f2638", linewidth=1.0)
for i, (df, ds) in enumerate(zip(d_full, d_seed)):
    ax.text(i - 0.20, df + (1.0 if df >= 0 else -2.5), f"{df:+.1f}",
            ha="center", color="#e8edf5", fontsize=9)
    ax.text(i + 0.20, ds + (1.0 if ds >= 0 else -2.5), f"{ds:+.1f}",
            ha="center", color="#e8edf5", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels([f"{b:.2f}" for b in BETAS], color="#e8edf5")
ax.set_xlabel("β_guilt", color="#e8edf5")
ax.set_ylabel("Δ ep0 rescue (pts vs INJ-OFF)", color="#e8edf5")
ax.set_title("Pruning to seed-only matches full-floor Δep0 at 3 of 4 cells",
             color="#ffe2ac", fontsize=12, pad=10)
ax.set_ylim(-20, 20)
ax.legend(facecolor="#0e131f", edgecolor="#1f2638", labelcolor="#e8edf5",
          loc="lower left", fontsize=9)

fig.suptitle("Seed-only floor ablation — outcome-class floors are inert at the regime-breaking cell",
             color="#ffe2ac", fontsize=13, y=0.995)
plt.savefig(OUT, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print(f"Wrote {OUT}")
