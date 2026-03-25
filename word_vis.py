# import numpy as np
# import matplotlib.pyplot as plt

# categories = {
#     "Sweet":        ["sweet", "caramelized", "syrupy", "chocolate", "cinnamon", "fruity", "berry", "tropical", "ripe"],
#     "Savory":       ["savory", "meaty", "umami", "greasy", "fatty", "buttery", "cheesy", "yeasty"],
#     "Sour":         ["sour", "tart", "vinegary", "citrus", "citrusy", "bitter"],
#     "Burnt/Smoked": ["roasted", "smoky", "smoked", "charred", "roasty", "burnt", "toasted", "grilled"],
#     "Fresh":        ["fresh", "crisp", "refreshing", "floral", "flower", "fragrant", "mint", "leafy", "grassy", "spice", "earthy", "wood", "musky", "nutty"]
# }

# word_freq = {
#     "sweet": 59, "strong": 28, "fresh": 23, "sour": 22, "earthy": 19,
#     "bitter": 16, "roasted": 15, "nutty": 13, "fruity": 12,
#     "berry": 12, "burnt": 11, "greasy": 11, "caramelized": 10, "smoky": 9,
#     "citrus": 8, "roasty": 8, "citrusy": 7, "chocolate": 7,
#     "wood": 6, "tropical": 6, "flower": 6, "cheesy": 6,
#     "buttery": 6, "toasted": 6, "yeasty": 6, "smoked": 5,
#     "fatty": 5, "grilled": 5, "ripe": 5, "grassy": 5,
#     "meaty": 5, "refreshing": 4, "savory": 4, "spice": 4,
#     "charred": 4, "musky": 3, "leafy": 3, "stale": 3,
#     "floral": 2, "tart": 2, "crisp": 2, "vinegary": 2,
#     "umami": 2, "mint": 2, "cinnamon": 2, "syrupy": 2, "fragrant": 2
# }

# colors = {
#     "Sweet":        "#F4A261",
#     "Savory":       "#E76F51",
#     "Sour":         "#2A9D8F",
#     "Burnt/Smoked": "#264653",
#     "Fresh":        "#57CC99"
# }

# cat_names = list(categories.keys())
# N = len(cat_names)
# # 每个category对应的角度区间
# sector_size = 2 * np.pi / N

# fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

# max_freq = max(word_freq.values())

# for i, (cat, words) in enumerate(categories.items()):
#     center_angle = i * sector_size + sector_size / 2
#     valid_words = [(w, word_freq[w]) for w in words if w in word_freq]
#     n = len(valid_words)

#     for j, (word, freq) in enumerate(valid_words):
#         # 频率越高越靠近中心（r越小）
#         r = 1.0 - (freq / max_freq) * 0.85
#         # 在扇区内均匀分布角度
#         angle = center_angle + (j - n / 2) * (sector_size * 0.8 / max(n, 1))

#         size = (freq / max_freq) * 8000 + 60
#         # size = (freq / max_freq) * 800 + 50
#         ax.scatter(angle, r, s=size, color=colors[cat], alpha=0.75,
#                    edgecolors='white', linewidths=0.8, zorder=3)
#         ax.annotate(word, (angle, r), fontsize=12, ha='center', va='center',
#                     color='white' if freq > 20 else '#333333', fontweight='regular', zorder=4)

# # category标签
# for i, cat in enumerate(cat_names):
#     angle = i * sector_size + sector_size / 2
#     ax.annotate(cat, (angle, 1.12), fontsize=12, fontweight='bold',
#                 ha='center', va='center', color=colors[cat],
#                 annotation_clip=False)

# # 扇区分隔线
# for i in range(N):
#     angle = i * sector_size
#     ax.plot([angle, angle], [0, 1.05], color='grey', linewidth=0.8, alpha=0.4)

# ax.set_yticklabels([])
# ax.set_xticklabels([])
# ax.set_ylim(0, 1.2)
# ax.grid(alpha=0.2)
# ax.set_title("Smell Descriptors — Frequency Polar Chart\n(larger & closer to center = higher frequency)",
#              fontsize=12, pad=30)

# plt.tight_layout()
# plt.savefig("smell_polar_bubble.png", dpi=150)
# plt.show()

import numpy as np
import matplotlib.pyplot as plt

categories = {
    "Sweet":        ["sweet", "caramelized", "syrupy", "chocolate", "cinnamon", "fruity", "berry", "tropical", "ripe"],
    "Savory":       ["savory", "meaty", "umami", "greasy", "fatty", "buttery", "cheesy", "yeasty"],
    "Sour":         ["sour", "tart", "vinegary", "citrus", "citrusy", "bitter"],
    "Burnt/Smoked": ["roasted", "smoky", "smoked", "charred", "roasty", "burnt", "toasted", "grilled"],
    "Fresh":        ["fresh", "crisp", "refreshing", "floral", "flower", "fragrant", "mint", "leafy", "grassy", "spice", "earthy", "wood", "musky", "nutty"]
}

word_freq = {
    "sweet": 59, "strong": 28, "fresh": 23, "sour": 22, "earthy": 19,
    "bitter": 16, "roasted": 15, "nutty": 13, "fruity": 12,
    "berry": 12, "burnt": 11, "greasy": 11, "caramelized": 10, "smoky": 9,
    "citrus": 8, "roasty": 8, "citrusy": 7, "chocolate": 7,
    "wood": 6, "tropical": 6, "flower": 6, "cheesy": 6,
    "buttery": 6, "toasted": 6, "yeasty": 6, "smoked": 5,
    "fatty": 5, "grilled": 5, "ripe": 5, "grassy": 5,
    "meaty": 5, "refreshing": 4, "savory": 4, "spice": 4,
    "charred": 4, "musky": 3, "leafy": 3, "stale": 3,
    "floral": 2, "tart": 2, "crisp": 2, "vinegary": 2,
    "umami": 2, "mint": 2, "cinnamon": 2, "syrupy": 2, "fragrant": 2
}

MIN_SIZE = 100
MAX_SIZE = 10000

colors = {
    "Sweet":        "#E8635A",
    "Savory":       "#F4A261",
    "Sour":         "#F7C948",
    "Burnt/Smoked": "#6C6FC5",
    "Fresh":        "#5BAFD6"
}

cat_names = list(categories.keys())
N = len(cat_names)
sector_size = 2 * np.pi / N
max_freq = max(word_freq.values())

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

# 蜘蛛网刻度
r_ticks = [0.2, 0.4, 0.6, 0.8, 1.0]
freq_labels = [int((1 - r) * max_freq) for r in r_ticks]  # 反映频率
for r in r_ticks:
    theta = np.linspace(0, 2 * np.pi, 300)
    ax.plot(theta, [r] * 300, color='grey', linewidth=0.5, alpha=0.25, zorder=1)

# 刻度数字，放在固定角度
label_angle = np.pi -0.63
for r, label in zip(r_ticks, freq_labels):
    ax.annotate(str(label), (label_angle, r), fontsize=8,
                color='grey', ha='left', va='center')

# 扇区分隔线
for i in range(N):
    angle = i * sector_size
    ax.plot([angle, angle], [0, 1.05], color='grey', linewidth=0.8, alpha=0.25)

# bubble
for i, (cat, words) in enumerate(categories.items()):
    center_angle = i * sector_size + sector_size / 2
    valid_words = [(w, word_freq[w]) for w in words if w in word_freq]
    n = len(valid_words)

    # for j, (word, freq) in enumerate(valid_words):
    #     r = 1.0 - (freq / max_freq) * 0.85
    #     angle = center_angle + (j - n / 2) * (sector_size * 0.8 / max(n, 1))

    #     # 指数缩放让大小差异更明显
    #     size = MIN_SIZE + (MAX_SIZE - MIN_SIZE) * ((freq / max_freq) ** 1.8)


    #     ax.scatter(angle, r, s=size, color=colors[cat], alpha=0.15,
    #                edgecolors='white', linewidths=0.8, zorder=3)
    #     # ax.annotate(word, (angle, r), fontsize=12, ha='center', va='center',
    #     #             color='white' if freq > 15 else '#333333',
    #     #             fontweight='regular', zorder=4)
    #     ax.annotate(word, (angle, r), fontsize=10, ha='center', va='center',
    #         # color=colors[cat], 
    #         color='#000000',
            
    #         fontweight='regular', zorder=3)
        
    for j, (word, freq) in enumerate(valid_words):
        r = 1.0 - (freq / max_freq) * 0.85
        angle = center_angle + (j - n / 2) * (sector_size * 0.8 / max(n, 1))
        # fontsize = 7 + (freq / max_freq) ** 1.2 * 16

                # 指数缩放让大小差异更明显
        size = MIN_SIZE + (MAX_SIZE - MIN_SIZE) * ((freq / max_freq) ** 1.8)


        ax.scatter(angle, r, s=size, color=colors[cat], alpha=0.35,
                   edgecolors='white', linewidths=0.8, zorder=3)

        # 转成角度，让文字朝向中心
        # rotation = np.degrees(angle) - 90
        rotation = np.degrees(angle)
        if np.pi / 2 < angle < 3 * np.pi / 2:
            rotation += 180

        ax.annotate(word, (angle, r), fontsize=12,
                    ha='center', va='center',
                    color='#000000', 
                    fontweight='regular',
                    rotation=rotation, rotation_mode='anchor', zorder=3)

# category标签
for i, cat in enumerate(cat_names):
    angle = i * sector_size + sector_size / 2
    ax.annotate(cat, (angle, 1.15), fontsize=14, fontweight='bold',
                ha='center', va='center', color=colors[cat],
                annotation_clip=False)

ax.set_yticklabels([])
ax.set_xticklabels([])
ax.set_ylim(0, 1.25)
ax.spines['polar'].set_visible(False)
ax.grid(False)
# ax.set_title("Smell Descriptors — Frequency Polar Chart\n(larger & closer to center = higher frequency)",
#              fontsize=12, pad=30)

plt.tight_layout()
# plt.savefig("smell_polar_bubble.png", dpi=150)
plt.savefig("word.pdf", dpi=300)
plt.show()