import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import pandas as pd

# ── Load CSV ──────────────────────────────────────────────────────────────────
df = pd.read_csv("word_frequency_smell.csv")
word_freq = dict(zip(df["word"], df["frequency"]))

words = list(word_freq.keys())
freqs = np.array([word_freq[w] for w in words])

print("Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
vectors = model.encode(words)

pca = PCA(n_components=2)
coords = pca.fit_transform(vectors)

k = 6
kmeans = KMeans(n_clusters=k, random_state=42)
labels = kmeans.fit_predict(vectors)

colors = plt.cm.Set2(np.linspace(0, 1, k))

fig, ax = plt.subplots(figsize=(14, 10))
for word, x, y, label, freq in zip(words, coords[:, 0], coords[:, 1], labels, freqs):
    ax.scatter(x, y, color=colors[label], s=freq * 3 + 20, alpha=0.8)
    ax.annotate(word, (x, y), fontsize=9, ha='center', va='bottom',
                xytext=(0, 5), textcoords='offset points')

ax.set_title("Smell Descriptors: PCA + K-Means (bubble size = frequency)")
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("smell_pca_clusters.png", dpi=150)
plt.show()