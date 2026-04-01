import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
fig.patch.set_facecolor('white')

# ── Chart 1: Donut ──────────────────────────────────────────
sizes = [6, 11, 6, 3]
labels = ['0 turns / zero-shot (n=6)', '1 turn (n=11)', '2 turns (n=6)', '3 turns (n=3)']
colors = ['#EFEFEF', '#D4D4D4', '#888888', '#444444']

wedges, _ = ax1.pie(
    sizes,
    colors=colors,
    startangle=90,
    center=(0, 80), 
    radius=0.7,
    wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
)

ax1.set_title('Turns to satisfaction', fontsize=16, fontweight='normal',
              loc='center', pad=0)

legend_handles = [
    mpatches.Patch(color=c, label=l)
    for c, l in zip(colors, labels)
]
ax1.legend(handles=legend_handles,
           loc='lower center',
           bbox_to_anchor=(0.5, -0.2),
           ncol=1,
           frameon=False, fontsize=16)

# ── Chart 2: Horizontal bar ──────────────────────────────────
strategies = [
    'Duration adjustment',
    'Full recomposition',
    'Single-scent swap',
    'Element substitution',
    'No change (correct)',
]
counts = [10, 10, 8, 5, 1]
bar_colors = ['#888888'] * 5

y = np.arange(len(strategies))
bars = ax2.barh(y, counts, color=bar_colors, height=0.5,
                zorder=3)

ax2.set_xlim(0, 12)
ax2.set_yticks(y)
ax2.set_yticklabels(strategies, fontsize=16)
ax2.invert_yaxis()
ax2.set_xlabel('Sessions', fontsize=16)
ax2.set_title('AI adjustment strategies',
              fontsize=16, fontweight='normal', loc='center', pad=0)

ax2.set_facecolor('white')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.tick_params(left=False)
ax2.xaxis.grid(True, color='#eeeeee', zorder=0)

for bar, val in zip(bars, counts):
    ax2.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
             str(val), va='center', fontsize=16,
             color='#444444')


plt.tight_layout(pad=0)
plt.savefig('turns.pdf', dpi=300, bbox_inches='tight', facecolor='white')
print("saved")
plt.show()