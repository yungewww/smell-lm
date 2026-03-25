import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

# ── Load data ─────────────────────────────────────────────────
df = pd.read_csv('SmellUIST - Similarity.csv')

B = df[df['Group']=='B'].set_index('Participant')['Similarity'].sort_index()
C = df[df['Group']=='C'].set_index('Participant')['Similarity'].sort_index()
D = df[df['Group']=='D'].set_index('Participant')['Similarity'].sort_index()

idx = B.index.intersection(C.index).intersection(D.index)
B, C, D = B.loc[idx], C.loc[idx], D.loc[idx]
N = len(idx)

# ── Compute improvements ──────────────────────────────────────
data = pd.DataFrame({
    'Participant': idx,
    'bc': (C - B).values,
    'cd': (D - C).values,
    'bd': (D - B).values,
})

# Sort: descending by bd, then those with any negative segment go last
data['has_red'] = ((data['bc'] < 0) | (data['cd'] < 0)).astype(int)
data = data.sort_values(['bd', 'has_red'], ascending=[False, True]).reset_index(drop=True)

# ── Statistics ────────────────────────────────────────────────
def wilcox_r(x, y, n):
    stat, p = stats.wilcoxon(x, y)
    r = 1 - (2 * stat) / (n * (n + 1) / 2)
    return p, round(r, 3)

p_bc, r_bc = wilcox_r(C.loc[idx], B.loc[idx], N)
p_cd, r_cd = wilcox_r(D.loc[idx], C.loc[idx], N)
p_bd, r_bd = wilcox_r(D.loc[idx], B.loc[idx], N)

def sig_label(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    return 'ns'

# ── Colors ────────────────────────────────────────────────────
C_BLUE_DARK  = '#185FA5'
C_BLUE_LIGHT = '#85B7EB'
C_RED_DARK   = '#A32D2D'
C_RED_LIGHT  = '#F09595'
C_BLACK      = '#000000'

# ── Plot ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

x = np.arange(len(data)) * 0.6
bar_width = 0.3

bc_pos = data['bc'].clip(lower=0)
bc_neg = data['bc'].clip(upper=0)
cd_pos = data['cd'].clip(lower=0)
cd_neg = data['cd'].clip(upper=0)

# Stacked bars
ax.bar(x, bc_pos, bar_width, color=C_BLUE_LIGHT, label='B→C improved')
ax.bar(x, cd_pos, bar_width, bottom=bc_pos, color=C_BLUE_DARK, label='C→D improved')
ax.bar(x, bc_neg, bar_width, color=C_RED_LIGHT, label='B→C worse')
ax.bar(x, cd_neg, bar_width, bottom=bc_neg, color=C_RED_DARK, label='C→D worse')

# Total B→D line segments
seg_half = bar_width * 0.6
for i, bd_val in enumerate(data['bd']):
    ax.plot([x[i] - seg_half, x[i] + seg_half], [bd_val, bd_val],
            color=C_BLACK, linewidth=2.5, solid_capstyle='round', zorder=5)

# Zero line
ax.axhline(0, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)

# Axes
ax.set_xticks(x)
ax.set_xticklabels([f'P{p}' for p in data['Participant']], fontsize=12, rotation=45, ha='right')
ax.set_ylabel('Similarity improvement (Δ)', fontsize=15)
ax.set_xlim(-0.4, (len(data) - 1) * 0.6 + 0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color='gray', alpha=0.2, linewidth=0.8)

# Legend
patches = [
    mpatches.Patch(color=C_BLUE_LIGHT, label='B→C improved'),
    mpatches.Patch(color=C_RED_LIGHT,  label='B→C worse'),
    mpatches.Patch(color=C_BLUE_DARK,  label='C→D improved'),
    mpatches.Patch(color=C_RED_DARK,   label='C→D worse'),
    plt.Line2D([0], [0], color=C_BLACK, linewidth=2.5, label='B→D total'),
]
ax.legend(handles=patches, fontsize=11, frameon=False, loc='upper right')

# Stats annotation
stats_text = (
    f'B→C: p={p_bc:.3f} ({sig_label(p_bc)})   '
    f'C→D: p={p_cd:.3f}, r={r_cd} ({sig_label(p_cd)})   '
    f'B→D: p={p_bd:.4f}, r={r_bd} ({sig_label(p_bd)})'
)
ax.set_title(stats_text, fontsize=12, color='gray', pad=10)

plt.tight_layout()
plt.savefig('similarity.pdf', bbox_inches='tight', dpi=300)
plt.savefig('similarity.png', bbox_inches='tight', dpi=300)
print("Saved: similarity_improvement_chart.pdf / .png")