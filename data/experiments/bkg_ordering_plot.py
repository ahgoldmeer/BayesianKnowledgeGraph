import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- Data ---
labels = [
    "Anemia\ncaused_by\nIron_Def",
    "Influenza\ntreated_with\nOseltamivir",
    "Fever\nis_symptom_of\nInfluenza",
    "COVID-19\ncaused_by\nViral_Inf",
    "Migraine\ntreated_with\nTriptans",
    "Pneumonia\ntreated_with\nAntibiotics",
]

baseline = [0.8184, 0.7995, 0.6867, 0.8525, 0.8654, 0.8439]
reversed_ = [0.8128, 0.8238, 0.6822, 0.8000, 0.8080, 0.8163]
# cluster  = [0.8184, 0.7995, 0.6867, 0.8525, 0.8654, 0.8439]
random   = [0.7525, 0.8632, 0.6737, 0.8105, 0.8280, 0.8513]
original = [0.87,   0.93,   0.78,   0.95,   0.92,   0.91]

orderings = [baseline, reversed_, random]
ordering_labels = ["Baseline", "Reversed", "Random"]
colors = ["#378ADD", "#D85A30", "#BA7517"]

n_groups = len(labels)
n_bars = len(orderings)
x = np.arange(n_groups)
bar_width = 0.18
offsets = np.linspace(-(n_bars - 1) / 2, (n_bars - 1) / 2, n_bars) * bar_width

# --- Figure 1: grouped bars + original confidence dashed line ---
fig1, ax1 = plt.subplots(figsize=(12, 5.2))
for i, (data, label, color) in enumerate(zip(orderings, ordering_labels, colors)):
    ax1.bar(x + offsets[i], data, width=bar_width, label=label, color=color,
            zorder=3, linewidth=0)

ax1.plot(x, original, color="#888888", linestyle="--", linewidth=1.5,
         marker="o", markersize=4, label="Original confidence", zorder=4)

ax1.set_ylim(0.55, 1.0)
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=9)
ax1.set_ylabel("Confidence", fontsize=10)
ax1.set_title("BKG confidence by input ordering", fontsize=12, fontweight="normal", pad=10)
ax1.yaxis.grid(True, color="#e0e0e0", linewidth=0.6, zorder=0)
ax1.set_axisbelow(True)
ax1.spines[["top", "right"]].set_visible(False)
ax1.tick_params(axis="both", labelsize=9)

# Custom legend
bar_patches = [mpatches.Patch(color=c, label=l) for c, l in zip(colors, ordering_labels)]
orig_line = plt.Line2D([0], [0], color="#888888", linestyle="--", linewidth=1.5,
                       marker="o", markersize=4, label="Original confidence")
ax1.legend(handles=bar_patches + [orig_line], fontsize=8.5, frameon=False,
           ncol=5, loc="upper left")
fig1.savefig("bkg_ordering_confidence.png", dpi=150, bbox_inches="tight")

# --- Figure 2: ordering sensitivity (range bars) ---
ranges = [max(baseline[i], reversed_[i], random[i]) -
          min(baseline[i], reversed_[i], random[i])
          for i in range(n_groups)]

range_colors = ["#D85A30" if r > 0.05 else "#BA7517" if r > 0.03 else "#1D9E75"
                for r in ranges]

fig2, ax2 = plt.subplots(figsize=(12, 3.2))
ax2.bar(x, ranges, color=range_colors, zorder=3, linewidth=0, width=0.5)
ax2.set_ylim(0, 0.12)
ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontsize=9)
ax2.set_ylabel("Max − Min", fontsize=10)
ax2.set_title("Ordering sensitivity (confidence range across three runs)", fontsize=10,
              fontweight="normal", pad=6)
ax2.yaxis.grid(True, color="#e0e0e0", linewidth=0.6, zorder=0)
ax2.set_axisbelow(True)
ax2.spines[["top", "right"]].set_visible(False)
ax2.tick_params(axis="both", labelsize=9)

# Value labels on range bars
for xi, r in zip(x, ranges):
    ax2.text(xi, r + 0.002, f"{r:.3f}", ha="center", va="bottom", fontsize=8,
             color="#444444")

fig2.savefig("bkg_ordering_sensitivity.png", dpi=150, bbox_inches="tight")
plt.show()
