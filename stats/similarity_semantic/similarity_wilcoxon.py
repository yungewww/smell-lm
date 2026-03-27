import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

df = pd.read_csv('SmellUIST - Similarity.csv')

B = df[df['Group']=='B'].set_index('Participant')['Similarity'].sort_index()
C = df[df['Group']=='C'].set_index('Participant')['Similarity'].sort_index()
D = df[df['Group']=='D'].set_index('Participant')['Similarity'].sort_index()

idx = B.index.intersection(C.index).intersection(D.index)
B, C, D = B.loc[idx], C.loc[idx], D.loc[idx]
N = len(idx)

print(f"N = {N}")
for label, g in [('B', B), ('C', C), ('D', D)]:
    q1, med, q3 = np.percentile(g, [25, 50, 75])
    print(f"{label}: Mdn={med:.1f}, IQR=[{q1:.1f}, {q3:.1f}]")

# ── 1. Friedman test (overall) ────────────────────────────────
f_stat, f_p = stats.friedmanchisquare(B, C, D)
print(f"\nFriedman: chi2 = {f_stat:.3f}, p = {f_p:.4f}")

# ── 2. Post-hoc Wilcoxon + FDR ───────────────────────────────
def wilcox(x, y, n):
    stat, p = stats.wilcoxon(x, y)
    r = 1 - (2 * stat) / (n * (n + 1) / 2)
    return p, round(r, 3)

pairs = [('B vs C', B, C), ('C vs D', C, D), ('B vs D', B, D)]
results = []
for label, g1, g2 in pairs:
    p, r = wilcox(g1, g2, N)
    results.append({'pair': label, 'p_raw': p, 'r': r})

df_res = pd.DataFrame(results)
_, p_fdr, _, _ = multipletests(df_res['p_raw'], method='fdr_bh')
df_res['p_fdr'] = p_fdr
df_res['sig'] = df_res['p_fdr'].apply(
    lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
)

print("\nPost-hoc Wilcoxon (FDR-corrected):")
print(df_res[['pair', 'p_raw', 'p_fdr', 'sig', 'r']].to_string(index=False))

# ── 3. Summary table ─────────────────────────────────────────
def fmt_iqr(g):
    q1, med, q3 = np.percentile(g, [25, 50, 75])
    return f"{med:.1f} [{q1:.1f}, {q3:.1f}]"

def fmt_pair(row):
    if row['sig'] == 'ns':
        return f"p={row['p_fdr']:.3f}, ns"
    return f"p={row['p_fdr']:.3f}, r={row['r']}{row['sig']}"

row = {
    'Mdn (IQR) B': fmt_iqr(B),
    'Mdn (IQR) C': fmt_iqr(C),
    'Mdn (IQR) D': fmt_iqr(D),
    'Friedman': f"chi2={f_stat:.2f}, p<.0001",
    'B vs C': fmt_pair(df_res[df_res['pair']=='B vs C'].iloc[0]),
    'C vs D': fmt_pair(df_res[df_res['pair']=='C vs D'].iloc[0]),
    'B vs D': fmt_pair(df_res[df_res['pair']=='B vs D'].iloc[0]),
}

summary = pd.DataFrame([row], index=['Similarity'])
print("\n=== Summary Table ===")
print(summary.to_string())