import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# n=21: 排除 000,017,018,019,023
data = {
    'B_mental':      [6,5,2,1,7,3,3,1,8,2,7,8,7,7,2,6,4,2,8,5,3],
    'B_physical':    [2,6,2,1,2,6,1,1,6,1,1,6,1,2,1,1,8,3,7,2,1],
    'B_temporal':    [7,7,1,1,3,4,1,2,2,2,5,5,1,5,4,5,6,3,1,4,2],
    'B_performance': [5,5,6,7,5,8,3,9,3,9,3,2,3,2,5,6,3,4,7,5,7],
    'B_effort':      [6,6,2,3,3,5,6,1,6,2,4,4,2,6,5,7,5,3,1,2,4],
    'B_frustration': [5,7,1,1,5,5,2,1,7,2,2,5,2,7,2,2,1,4,1,1,1],
    'D_mental':      [6,3,4,1,7,4,4,2,7,1,5,3,2,5,2,2,7,3,8,4,5],
    'D_physical':    [3,3,1,1,2,7,1,1,7,1,1,2,1,1,1,1,8,2,3,2,1],
    'D_temporal':    [7,1,1,1,2,3,1,1,2,1,2,2,1,3,2,2,5,2,1,1,5],
    'D_performance': [5,3,6,8,5,8,2,8,4,9,3,4,4,6,6,9,4,5,7,6,9],
    'D_effort':      [5,2,5,2,3,4,3,8,5,1,3,2,1,4,3,2,7,3,2,2,3],
    'D_frustration': [5,5,2,1,3,3,1,1,5,1,2,3,1,3,3,1,1,3,1,1,1],
}

df = pd.DataFrame(data)
dimensions = ['mental','physical','temporal','performance','effort','frustration']
dim_labels = ['Mental\n Demand','Physical\n Demand','Temporal\n Demand','Performance','Effort','Frustration']

def sig_str(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    return 'ns'

# ── stats ──
results = {}
for dim in dimensions:
    b = df[f'B_{dim}'].values
    d = df[f'D_{dim}'].values
    stat, p = wilcoxon(b, d, alternative='two-sided')
    med_b = np.median(b); iqr_b = np.percentile(b,75)-np.percentile(b,25)
    med_d = np.median(d); iqr_d = np.percentile(d,75)-np.percentile(d,25)
    results[dim] = dict(n=len(df), B_med=med_b, B_iqr=iqr_b,
                        D_med=med_d, D_iqr=iqr_d, W=stat, p=p, p_adj=min(p*7,1.0))

df['B_comp'] = df[[f'B_{d}' for d in dimensions]].mean(axis=1)
df['D_comp'] = df[[f'D_{d}' for d in dimensions]].mean(axis=1)
stat, p = wilcoxon(df['B_comp'], df['D_comp'], alternative='two-sided')
results['composite'] = dict(n=len(df),
    B_med=np.median(df['B_comp']), B_iqr=np.percentile(df['B_comp'],75)-np.percentile(df['B_comp'],25),
    D_med=np.median(df['D_comp']), D_iqr=np.percentile(df['D_comp'],75)-np.percentile(df['D_comp'],25),
    W=stat, p=p, p_adj=min(p*7,1.0))

# ── print table ──
header = f"{'Dimension':<14} {'B Mdn±IQR':>11} {'D Mdn±IQR':>11} {'W':>7} {'p':>12} {'p_adj':>12}"
print(header)
print("-"*72)
for dim in dimensions + ['composite']:
    r = results[dim]
    sig_p    = sig_str(r['p'])
    sig_padj = sig_str(r['p_adj'])
    bold = "**" if r['p'] < 0.05 else ""
    print(f"{bold+dim.capitalize():<14} "
          f"{r['B_med']:.1f}±{r['B_iqr']:.1f}  "
          f"{r['D_med']:.1f}±{r['D_iqr']:.1f}  "
          f"{r['W']:>7.1f}  "
          f"{r['p']:>7.3f} {sig_p:<3}  "
          f"{r['p_adj']:>7.3f} {sig_padj:<3}")

# ── visualization ──
COLOR_B = '#185FA5'
COLOR_D = '#F4A736'

fig, axes = plt.subplots(len(dimensions), 1, figsize=(7, 8))
fig.subplots_adjust(hspace=0.15, left=0.28, right=0.88)

for i, (dim, label) in enumerate(zip(dimensions, dim_labels)):
    ax = axes[i]
    b_data = df[f'B_{dim}'].values
    d_data = df[f'D_{dim}'].values

    bp = ax.boxplot(
        [b_data, d_data],
        vert=False,
        positions=[1, 0],
        widths=0.45,
        patch_artist=True,
        medianprops=dict(color='white', linewidth=2),
        whiskerprops=dict(color='#555', linewidth=1.2),
        capprops=dict(color='#555', linewidth=1.2),
        flierprops=dict(marker='o', color='#999', markersize=4, linestyle='none'),
        boxprops=dict(linewidth=0)
    )
    bp['boxes'][0].set_facecolor(COLOR_B)
    bp['boxes'][1].set_facecolor(COLOR_D)

    ax.set_xlim(0, 10)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['D (HITL)', 'B (Human)'], fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='x', labelsize=8)

    ax.text(-0.27, 0.5, label, transform=ax.transAxes,
            ha='right', va='center', fontsize=12, fontweight='bold')

    p   = results[dim]['p']
    sig = sig_str(p)
    color = '#A32D2D' if p < 0.05 else '#999'
    ax.text(1.02, 0.5, f'{sig}\np={p:.3f}', transform=ax.transAxes,
            ha='left', va='center', fontsize=12, color=color)

    if i < len(dimensions) - 1:
        ax.set_xticklabels([])
        ax.tick_params(axis='x', bottom=False)

axes[-1].set_xlabel('Rating (1–10)', fontsize=12)

patch_b = mpatches.Patch(color=COLOR_B, label='B: Human')
patch_d = mpatches.Patch(color=COLOR_D, label='D: HITL')
fig.legend(handles=[patch_b, patch_d], ncol=2, fontsize=12, frameon=False)

plt.savefig('nasa.pdf', bbox_inches='tight')
plt.savefig('nasa.png', dpi=150, bbox_inches='tight')
print("\nSaved: nasa_n21.pdf / nasa_n21.png")