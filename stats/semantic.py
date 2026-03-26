import pandas as pd
import numpy as np
from scipy.stats import wilcoxon, friedmanchisquare
from statsmodels.stats.multitest import multipletests

df = pd.read_csv('SmellUIST - Semantic.csv')
dims = ['sweet', 'savory', 'sour', 'burnt/smoked', 'fresh', 'chemical/artificial']
df[dims] = df[dims].replace('n.a.', np.nan).astype(float)

A = df[df.Group == 'A'].set_index('Participant')[dims]
B = df[df.Group == 'B'].set_index('Participant')[dims]
C = df[df.Group == 'C'].set_index('Participant')[dims]
D = df[df.Group == 'D'].set_index('Participant')[dims]

def euclid(a, b):
    return np.sqrt(np.sum((a.values - b.values) ** 2))

def wilcox_r(x, y):
    res = wilcoxon(x, y)
    n = len(x)
    mu = n * (n + 1) / 4
    sigma = np.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    Z = (res.statistic - mu) / sigma
    r = abs(Z) / np.sqrt(n)
    return res.pvalue, r

rows = []
for p in A.index:
    if all(p in t.index for t in [B, C, D]):
        a, b, c, d = A.loc[p], B.loc[p], C.loc[p], D.loc[p]
        if all(x.notna().all() for x in [a, b, c, d]):
            rows.append({'p': p, 'B': euclid(a, b), 'C': euclid(a, c), 'D': euclid(a, d)})

dist_df = pd.DataFrame(rows)
print(f"N = {len(dist_df)}")

for cond in ['B', 'C', 'D']:
    v = dist_df[cond]
    print(f"{cond}: Mdn={v.median():.2f}, IQR=[{v.quantile(.25):.2f}, {v.quantile(.75):.2f}]")

stat, p = friedmanchisquare(dist_df['B'], dist_df['C'], dist_df['D'])
print(f"Friedman: chi2={stat:.3f}, p={p:.4f}")

pairs = [('B', 'C'), ('C', 'D'), ('B', 'D')]
raw_p, rs = [], []
for a, b in pairs:
    p_raw, r = wilcox_r(dist_df[a], dist_df[b])
    raw_p.append(p_raw)
    rs.append(r)

_, p_fdr, _, _ = multipletests(raw_p, method='fdr_bh')

print("Post-hoc Wilcoxon (FDR-corrected):")
print(f"  {'pair':>6}  {'p_raw':>10}  {'p_fdr':>10}  {'sig':>5}  {'r':>6}")
for (a, b), p_raw, p_adj, r in zip(pairs, raw_p, p_fdr, rs):
    sig = '***' if p_adj < .001 else '**' if p_adj < .01 else '*' if p_adj < .05 else 'ns'
    print(f"  {a} vs {b}  {p_raw:10.6f}  {p_adj:10.6f}  {sig:>5}  {r:.3f}")