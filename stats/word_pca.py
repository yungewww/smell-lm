import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

word_freq = {
    "sweet": 59, "strong": 28, "fresh": 23, "sour": 22, "earthy": 19,
    "bitter": 16, "flavor": 16, "roasted": 15, "nutty": 13, "fruity": 12,
    "berry": 12, "burnt": 11, "greasy": 11, "caramelized": 10, "smoky": 9,
    "citrus": 8, "roasty": 8, "citrusy": 7, "chocolate": 7, "light": 6,
    "wood": 6, "tropical": 6, "flower": 6, "cheesy": 6, "rich": 6,
    "buttery": 6, "toasted": 6, "yeasty": 6, "dry": 5, "smoked": 5,
    "fatty": 5, "grilled": 5, "ripe": 5, "grassy": 5, "warm": 5,
    "meaty": 5, "leathery": 4, "refreshing": 4, "savory": 4, "spice": 4,
    "charred": 4, "sickly": 4, "musky": 3, "leafy": 3, "subtle": 3,
    "stale": 3, "floral": 2, "tart": 2, "crisp": 2, "rubbery": 2,
    "vinegary": 2, "umami": 2, "mint": 2, "cinnamon": 2, "nauseating": 2,
    "syrupy": 2, "artificial": 2, "fragrant": 2
}

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