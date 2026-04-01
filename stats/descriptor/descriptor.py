import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import matplotlib.patches as mpatches
import sys


# ── Load data ──────────────────────────────────────────────────────────────────
csv_path = sys.argv[1] if len(sys.argv) > 1 else '/Users/yungew/Documents/GitHub/smell-lm/stats/similarity_semantic/SmellUIST - Semantic.csv'
df = pd.read_csv(csv_path)
df = df[df.iloc[:, 2] != 'n.a.'].copy()
for col in df.columns[2:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

descriptors = ['sweet', 'savory', 'sour', 'burnt/smoked', 'fresh', 'chemical/artificial']
groups = ['A', 'B', 'C', 'D']
# group_labels = {'A': 'A (real)', 'B': 'B (human)', 'C': 'C (AI)', 'D': 'D (HITL)'}
group_labels = {'A': 'Real', 'B': 'Human', 'C': 'w/o Learning', 'D': 'AromaAI'}

# ── Medians ────────────────────────────────────────────────────────────────────
print("=" * 60)
print("MEDIAN RATINGS BY CONDITION")
print("=" * 60)
medians = {}
for g in groups:
    sub = df[df['Group'] == g]
    medians[g] = {d: sub[d].median() for d in descriptors}
    print(f"\n{group_labels[g]} (N={len(sub)}):")
    for d in descriptors:
        print(f"  {d:25s}: {medians[g][d]:.1f}")

# ── Per-descriptor Wilcoxon vs A (FDR-corrected) ───────────────────────────────
print("\n" + "=" * 60)
print("PER-DESCRIPTOR WILCOXON SIGNED-RANK TESTS (vs A, FDR-corrected)")
print("=" * 60)

A_df = df[df['Group'] == 'A']
results = []
for d in descriptors:
    for g in ['B', 'C', 'D']:
        G_df = df[df['Group'] == g]
        merged = A_df[['Participant', d]].merge(G_df[['Participant', d]], on='Participant', suffixes=('_A', '_G'))
        stat, p = stats.wilcoxon(merged[f'{d}_A'], merged[f'{d}_G'])
        results.append({'descriptor': d, 'group': g, 'p_raw': p, 'n': len(merged)})

res_df = pd.DataFrame(results)
_, p_fdr, _, _ = multipletests(res_df['p_raw'], method='fdr_bh')
res_df['p_fdr'] = p_fdr
res_df['sig'] = res_df['p_fdr'].apply(
    lambda p: '***' if p < .001 else ('**' if p < .01 else ('*' if p < .05 else 'ns'))
)

print(f"\n{'Descriptor':<25} {'vs':>3}  {'p_raw':>8}  {'p_fdr':>8}  {'sig':>4}")
print("-" * 55)
for _, row in res_df.iterrows():
    print(f"{row['descriptor']:<25} {row['group']:>3}  {row['p_raw']:>8.4f}  {row['p_fdr']:>8.4f}  {row['sig']:>4}")

# ── chemical/artificial: D vs B, D vs C ───────────────────────────────────────
print("\n" + "=" * 60)
print("CHEMICAL/ARTIFICIAL: D vs B and D vs C")
print("=" * 60)
d = 'chemical/artificial'
for g in ['B', 'C']:
    G_df = df[df['Group'] == g]
    D_df = df[df['Group'] == 'D']
    merged = G_df[['Participant', d]].merge(D_df[['Participant', d]], on='Participant', suffixes=('_G', '_D'))
    stat, p = stats.wilcoxon(merged[f'{d}_G'], merged[f'{d}_D'])
    sig = '***' if p < .001 else ('**' if p < .01 else ('*' if p < .05 else 'ns'))
    print(f"  D vs {g}: p = {p:.4f}  {sig}")

# ── Build sig lookup ───────────────────────────────────────────────────────────
sig_lookup = {(row['descriptor'], row['group']): row['sig'] for _, row in res_df.iterrows()}

# ── Radar chart ────────────────────────────────────────────────────────────────
N = len(descriptors)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]

colors = {
    'A': ('#AAAAAA', 0.10),  # 灰色 neutral
    'B': ('#185FA5', 0.12),  # 蓝
    'C': ('#A32D2D', 0.12),  # 红
    'D': ('#F4A736', 0.12),  # 黄
}
# colors = {
#     'A': ('#888780', 0.12),
#     'B': ('#378ADD', 0.12),
#     'C': ('#1D9E75', 0.12),
#     'D': ('#D85A30', 0.10),
# }
linewidths = {'A': 1.8, 'B': 2.2, 'C': 2.2, 'D': 1.8}

fig, ax = plt.subplots(figsize=(10, 4), subplot_kw=dict(polar=True)) # figsize
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# highlight chemical/artificial axis
sig_idx = descriptors.index('chemical/artificial')
sig_angle = angles[sig_idx]
wedge_half = np.pi / N * 0.72
theta = np.linspace(sig_angle - wedge_half, sig_angle + wedge_half, 50)
r_fill = np.full_like(theta, 10.8)
ax.fill_between(theta, 0, r_fill, color='#000000', alpha=0.10, zorder=0)
ax.plot([sig_angle, sig_angle], [0, 10.5], color='#000000', linewidth=1.8, zorder=1)

# plot each group
for g in groups:
    vals = [medians[g][d] for d in descriptors]
    vals += vals[:1]
    color, alpha = colors[g]
    ax.plot(angles, vals, color=color, linewidth=linewidths[g], zorder=3)
    ax.fill(angles, vals, color=color, alpha=alpha, zorder=2)
    ax.scatter(angles[:-1], vals[:-1], color=color, s=30, zorder=4)

# axis labels
ax.set_xticks(angles[:-1])
label_texts = []
for i, d in enumerate(descriptors):
    sigs = [sig_lookup.get((d, g), 'ns') for g in ['B', 'C', 'D']]
    any_sig = any(s != 'ns' for s in sigs)
    label_texts.append(d)

ax.set_xticklabels([])
for i, (angle, d) in enumerate(zip(angles[:-1], descriptors)):
    sigs = [sig_lookup.get((d, g), 'ns') for g in ['B', 'C', 'D']]
    is_sig_axis = d == 'chemical/artificial'
    # color = '#888780' if is_sig_axis else '#3d3d3a'
    color = '#000000'
    # weight = 'bold' if is_sig_axis else 'normal'
    weight = 'normal'
    ha = 'center'
    pad = 1.22
    x = pad * np.cos(angle - np.pi / 2)
    y = pad * np.sin(angle - np.pi / 2)
    ax.text(angle, 11.5, d, ha='center', va='center',
            fontsize=16, color=color, fontweight=weight,
            transform=ax.transData)

# grid
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=10, color='#888780')
ax.grid(color="#929292", linewidth=0.5, linestyle='--', alpha=0.6)
ax.spines['polar'].set_visible(False)

# legend
patches = [mpatches.Patch(color=colors[g][0], label=group_labels[g]) for g in groups]
sig_patch = mpatches.Patch(color='#000000', alpha=0.4, label='* p < .05 vs A (FDR-corrected)')
# ax.legend(handles=patches + [sig_patch], loc='upper right',
#           bbox_to_anchor=(1.35, 1.15), fontsize=9, frameon=False)
ax.legend(handles=patches, loc='upper right',
          bbox_to_anchor=(1.75, 1), fontsize=16, frameon=False)

plt.tight_layout()
out_path = 'descriptor.png'
# plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.savefig('descriptor.pdf', bbox_inches='tight', dpi=300)
print("Saved: similarity_improvement_chart.pdf / .png")
print(f"\nRadar chart saved to: {out_path}")
plt.show()

