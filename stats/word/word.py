# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context
# import nltk
# import os
# import json
# import pandas as pd
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import RegexpTokenizer
# from collections import Counter
# import matplotlib.pyplot as plt
# import numpy as np
# import matplotlib.gridspec as gridspec

# from word_frequency import get_word_frequency, process_text

# # ── Load CSV ──────────────────────────────────────────────────────────────────
# df = pd.read_csv("/Users/yungew/Documents/GitHub/smell-lm/stats/word/SmellUIST - Foramtive Task 3.csv")
# df = df[["Strawberry", "Coffee Beans", "Burger", "Banana"]]

# # ── Step 1: Word frequency > 2 ───────────────────────────────────────────────
# total_counter = get_word_frequency(
#     "/Users/yungew/Documents/GitHub/smell-lm/stats/word/SmellUIST - Foramtive Task 3.csv",
#     ["Strawberry", "Coffee Beans", "Burger", "Banana"],
#     save_path="word_frequency.csv"
# )

# total_freq_df = pd.DataFrame(
#     sorted(total_counter.items(), key=lambda x: -x[1]),
#     columns=["word", "frequency"]
# )

# # ── Top-5 per food ────────────────────────────────────────────────────────────
# food_name_tokens = set()
# for food in df.columns:
#     for w in process_text(food):
#         food_name_tokens.add(w)

# # ── Categories ────────────────────────────────────────────────────────────────
# with open("categories.json", "r") as f:
#     categories = json.load(f)

# category_words = {w for words in categories.values() for w in words}

# food_top5 = {}
# for food in df.columns:
#     text = ' '.join(df[food].dropna().astype(str))
#     words = [w for w in process_text(text) if w not in food_name_tokens and w in category_words]
#     food_top5[food] = Counter(words).most_common(5)

# word_freq = {}
# for cat, words in categories.items():
#     for w in words:
#         if total_counter.get(w, 0) > 0:
#             word_freq[w] = total_counter[w]

# colors = {
#     "Sweet":        "#E8635A",
#     "Savory":       "#F4A261",
#     "Sour":         "#F7C948",
#     "Burnt/Smoked": "#6C6FC5",
#     "Fresh":        "#5BAFD6"
# }

# word_to_color = {}
# for cat, words in categories.items():
#     for w in words:
#         word_to_color[w] = colors[cat]

# # ── Smell words frequency list ────────────────────────────────────────────────
# smell_freq = {w: total_counter[w] for w in category_words if w in total_counter}
# smell_freq_df = pd.DataFrame(
#     sorted(smell_freq.items(), key=lambda x: -x[1]),
#     columns=["word", "frequency"]
# )
# smell_freq_df.to_csv("word_frequency_smell.csv", index=False)

# # ── Figure layout ─────────────────────────────────────────────────────────────
# fig = plt.figure(figsize=(8, 10))
# gs = gridspec.GridSpec(2, 1, height_ratios=[5, 1], hspace=0)

# # ── Polar chart ───────────────────────────────────────────────────────────────
# ax_polar = fig.add_subplot(gs[0], polar=True)

# cat_names = list(categories.keys())
# N = len(cat_names)
# sector_size = 2 * np.pi / N
# max_freq = max(word_freq.values()) if word_freq else 1
# MIN_SIZE, MAX_SIZE = 100, 10000

# r_ticks = [0.2, 0.4, 0.6, 0.8, 1.0]
# freq_labels = [int((1 - r) * max_freq) for r in r_ticks]
# for r in r_ticks:
#     theta = np.linspace(0, 2 * np.pi, 300)
#     ax_polar.plot(theta, [r] * 300, color='grey', linewidth=0.5, alpha=0.25, zorder=1)

# label_angle = np.pi - 0.63
# for r, label in zip(r_ticks, freq_labels):
#     ax_polar.annotate(str(label), (label_angle, r), fontsize=8,
#                       color='grey', ha='left', va='center')

# for i in range(N):
#     angle = i * sector_size
#     ax_polar.plot([angle, angle], [0, 1.05], color='grey', linewidth=0.8, alpha=0.25)

# for i, (cat, words) in enumerate(categories.items()):
#     center_angle = i * sector_size + sector_size / 2
#     valid_words = [(w, word_freq[w]) for w in words if w in word_freq]
#     n = len(valid_words)
#     for j, (word, freq) in enumerate(valid_words):
#         r = 1.0 - (freq / max_freq) * 0.9
#         angle = center_angle + (j - n / 2) * (sector_size * 0.8 / max(n, 1))
#         size = MIN_SIZE + (MAX_SIZE - MIN_SIZE) * ((freq / max_freq) ** 1.8)
#         ax_polar.scatter(angle, r, s=size, color=colors[cat], alpha=0.35,
#                          edgecolors='white', linewidths=0.8, zorder=3)
#         rotation = np.degrees(angle)
#         if np.pi / 2 < angle < 3 * np.pi / 2:
#             rotation += 180
#         ax_polar.annotate(word, (angle, r), fontsize=12,
#                           ha='center', va='center', color='#000000',
#                           fontweight='regular', rotation=rotation,
#                           rotation_mode='anchor', zorder=3)

# for i, cat in enumerate(cat_names):
#     angle = i * sector_size + sector_size / 2
#     ax_polar.annotate(cat, (angle, 1.15), fontsize=14, fontweight='bold',
#                       ha='center', va='center', color=colors[cat],
#                       annotation_clip=False)

# ax_polar.set_yticklabels([])
# ax_polar.set_xticklabels([])
# ax_polar.set_ylim(0, 1.25)
# ax_polar.spines['polar'].set_visible(False)
# ax_polar.grid(False)

# # ── Bar charts ────────────────────────────────────────────────────────────────
# gs_bar = gridspec.GridSpecFromSubplotSpec(1, len(df.columns), subplot_spec=gs[1], wspace=0.8)

# for idx, food in enumerate(df.columns):
#     ax = fig.add_subplot(gs_bar[idx])
#     top5 = food_top5[food]
#     words_bar = [w for w, _ in top5]
#     freqs_bar = [c for _, c in top5]

#     bar_colors = [word_to_color.get(w, '#AAAAAA') for w in words_bar[::-1]]

#     bars = ax.barh(words_bar[::-1], freqs_bar[::-1],
#                    color=bar_colors, alpha=0.75,
#                    edgecolor='white', linewidth=0.5, height=0.6)

#     for bar, val in zip(bars, freqs_bar[::-1]):
#         ax.text(val + 0.15, bar.get_y() + bar.get_height() / 2,
#                 str(val), va='center', ha='left', fontsize=9, color='#444444')

#     ax.set_title(food, fontsize=12, fontweight='bold', color='black', pad=6)
#     ax.set_xlim(0, max(freqs_bar) * 1.35)
#     ax.tick_params(axis='y', labelsize=9)
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['left'].set_visible(False)
#     ax.spines['bottom'].set_visible(False)

#     ax.xaxis.set_visible(False)

# plt.savefig("word.pdf", dpi=300, bbox_inches='tight')
# # plt.savefig("word.png", dpi=300, bbox_inches='tight')
# plt.show()


import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk
import os
import json
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

from word_frequency import get_word_frequency, process_text

# ── Load CSV ──────────────────────────────────────────────────────────────────
df = pd.read_csv("/Users/yungew/Documents/GitHub/smell-lm/stats/word/SmellUIST - Foramtive Task 3.csv")
df = df[["Strawberry", "Coffee Beans", "Burger", "Banana"]]

# ── Step 1: Word frequency > 2 ───────────────────────────────────────────────
total_counter = get_word_frequency(
    "/Users/yungew/Documents/GitHub/smell-lm/stats/word/SmellUIST - Foramtive Task 3.csv",
    ["Strawberry", "Coffee Beans", "Burger", "Banana"],
    save_path="word_frequency.csv"
)

total_freq_df = pd.DataFrame(
    sorted(total_counter.items(), key=lambda x: -x[1]),
    columns=["word", "frequency"]
)

# ── Top-5 per food ────────────────────────────────────────────────────────────
food_name_tokens = set()
for food in df.columns:
    for w in process_text(food):
        food_name_tokens.add(w)

# ── Categories ────────────────────────────────────────────────────────────────
with open("categories.json", "r") as f:
    categories = json.load(f)

category_words = {w for words in categories.values() for w in words}

food_top5 = {}
for food in df.columns:
    text = ' '.join(df[food].dropna().astype(str))
    words = [w for w in process_text(text) if w not in food_name_tokens and w in category_words]
    food_top5[food] = Counter(words).most_common(5)

word_freq = {}
for cat, words in categories.items():
    for w in words:
        if total_counter.get(w, 0) > 0:
            word_freq[w] = total_counter[w]

colors = {
    "Sweet":        "#E8635A",
    "Savory":       "#F4A261",
    "Sour":         "#F7C948",
    "Burnt/Smoked": "#6C6FC5",
    "Fresh":        "#5BAFD6"
}

word_to_color = {}
for cat, words in categories.items():
    for w in words:
        word_to_color[w] = colors[cat]

# ── Smell words frequency list ────────────────────────────────────────────────
smell_freq = {w: total_counter[w] for w in category_words if w in total_counter}
smell_freq_df = pd.DataFrame(
    sorted(smell_freq.items(), key=lambda x: -x[1]),
    columns=["word", "frequency"]
)
smell_freq_df.to_csv("word_frequency_smell.csv", index=False)

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(9, 6))
gs = gridspec.GridSpec(1, 2, width_ratios=[7, 2], hspace=0, wspace=0.3)

# ── Polar chart ───────────────────────────────────────────────────────────────
ax_polar = fig.add_subplot(gs[0], polar=True)

cat_names = list(categories.keys())
N = len(cat_names)
sector_size = 2 * np.pi / N
max_freq = max(word_freq.values()) if word_freq else 1
MIN_SIZE, MAX_SIZE = 100, 10000

r_ticks = [0.2, 0.4, 0.6, 0.8, 1.0]
freq_labels = [int((1 - r) * max_freq) for r in r_ticks]
for r in r_ticks:
    theta = np.linspace(0, 2 * np.pi, 300)
    ax_polar.plot(theta, [r] * 300, color='grey', linewidth=0.5, alpha=0.25, zorder=1)

label_angle = np.pi - 0.63
for r, label in zip(r_ticks, freq_labels):
    ax_polar.annotate(str(label), (label_angle, r), fontsize=8,
                      color='grey', ha='left', va='center')

for i in range(N):
    angle = i * sector_size
    ax_polar.plot([angle, angle], [0, 1.05], color='grey', linewidth=0.8, alpha=0.25)

for i, (cat, words) in enumerate(categories.items()):
    center_angle = i * sector_size + sector_size / 2
    valid_words = [(w, word_freq[w]) for w in words if w in word_freq]
    n = len(valid_words)
    for j, (word, freq) in enumerate(valid_words):
        r = 1.0 - (freq / max_freq) * 0.9
        angle = center_angle + (j - n / 2) * (sector_size * 0.8 / max(n, 1))
        size = MIN_SIZE + (MAX_SIZE - MIN_SIZE) * ((freq / max_freq) ** 1.8)
        ax_polar.scatter(angle, r, s=size, color=colors[cat], alpha=0.35,
                         edgecolors='white', linewidths=0.8, zorder=3)
        rotation = np.degrees(angle)
        if np.pi / 2 < angle < 3 * np.pi / 2:
            rotation += 180
        ax_polar.annotate(word, (angle, r), fontsize=12,
                          ha='center', va='center', color='#000000',
                          fontweight='regular', rotation=rotation,
                          rotation_mode='anchor', zorder=3)

for i, cat in enumerate(cat_names):
    angle = i * sector_size + sector_size / 2
    ax_polar.annotate(cat, (angle, 1.15), fontsize=14, fontweight='bold',
                      ha='center', va='center', color=colors[cat],
                      annotation_clip=False)

ax_polar.set_yticklabels([])
ax_polar.set_xticklabels([])
ax_polar.set_ylim(0, 1.25)
ax_polar.spines['polar'].set_visible(False)
ax_polar.grid(False)
ax_polar.set_position(ax_polar.get_position().expanded(1.2, 1.2)) # ⭕️

# ── Bar charts ────────────────────────────────────────────────────────────────
gs_bar = gridspec.GridSpecFromSubplotSpec(len(df.columns), 1, subplot_spec=gs[1], hspace=0.5)


for idx, food in enumerate(df.columns):
    ax = fig.add_subplot(gs_bar[idx])
    top5 = food_top5[food]
    words_bar = [w for w, _ in top5]
    freqs_bar = [c for _, c in top5]

    bar_colors = [word_to_color.get(w, '#AAAAAA') for w in words_bar[::-1]]

    bars = ax.barh(words_bar[::-1], freqs_bar[::-1],
                   color=bar_colors, 
                   alpha=1,
                   height=0.2
                   )

    for bar, val in zip(bars, freqs_bar[::-1]):
        ax.text(val + 0.15, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', ha='left', fontsize=12, color='#444444')

    ax.set_title(food, fontsize=12, 
                #  fontweight='semibold', 
                 color='black')
    ax.set_xlim(0, max(freqs_bar))
    ax.tick_params(axis='y', labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.xaxis.set_visible(False)

plt.savefig("word.pdf", dpi=300, bbox_inches='tight')
# plt.savefig("word.png", dpi=300, bbox_inches='tight')
plt.show()