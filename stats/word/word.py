import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from collections import Counter

# ── NLTK setup (only wordnet needed, no stopwords download) ──────────────────
nltk_data_dir = os.path.expanduser("~/nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
for pkg in ["wordnet", "omw-1.4"]:
    nltk.download(pkg, download_dir=nltk_data_dir, quiet=True)

tokenizer = RegexpTokenizer(r"\w+")
lemmatizer = WordNetLemmatizer()

# ── Hardcoded stopwords ───────────────────────────────────────────────────────
stop_words = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","d","ll",
    "m","o","re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn","wasn","weren",
    "won","wouldn","like","smell","smells","smelling","taste","tastes","tasting",
    "think","feel","feels","felt","know","knew","say","said","says","get","got",
    "gets","go","goes","went","gone","come","came","comes","see","saw","seen",
    "look","looks","looked","seem","seems","seemed","want","wanted","wants",
    "need","needs","needed","try","tried","tries","use","used","uses","make",
    "makes","made","put","puts","let","lets","one","two","three","four","five",
    "six","seven","yeah","yes","okay","ok","oh","ah","uh","um","hmm","mm","hm",
    "well","also","really","quite","very","pretty","bit","lot","much","even",
    "still","already","yet","always","never","usually","normally","actually",
    "probably","definitely","maybe","perhaps","kind","way","back","though",
    "although","however","because","since","whether","either","neither","both",
    "just","still","already","always","never","actually","probably","definitely",
    "maybe","perhaps","quite","really","something","anything","nothing","someone",
    "anyone","everyone","thing","things","time","times","point","bit","little",
    "kind","sort","type","real","artificial","similarity","compared","similar",
    "different","note","overall","mean","means","meant","think","thought",
    "sure","guess","suppose","suppose","find","found","give","given","gave",
    "take","taken","took","start","started","end","ended","first","last","next",
    "right","left","high","low","big","small","long","short","new","old",
    "good","bad","great","little","own","same","another","every","per",
    "would","could","should","might","must","shall","will","may","can",
    "tell","told","tells","told","said","ask","asked","asks","answer",
    "artificial","real","sample","samples","participant","participants",
    "describe","described","describes","description","note","noted",
    "compared","compare","comparison","similarity","similar","different",
    "difference","definitely","probably","actually","basically","generally",
    "specifically","particularly","especially","instead","rather","quite",
    "almost","nearly","exactly","completely","totally","absolutely","clearly"
}

# ── Load CSV ──────────────────────────────────────────────────────────────────
df = pd.read_csv("/Users/yungew/Documents/GitHub/smell-lm/stats/word/SmellUIST - Foramtive Task 3.csv")
df = df[["Strawberry", "Coffee Beans", "Burger", "Banana"]]

# ── Helper ────────────────────────────────────────────────────────────────────
def process_text(text):
    tokens = tokenizer.tokenize(text.lower())
    words = []
    for w in tokens:
        if len(w) > 2 and w not in stop_words:
            try:
                w = lemmatizer.lemmatize(w)
            except Exception:
                pass
            if w not in stop_words:
                words.append(w)
    return words

# ── word_freq from ALL foods ──────────────────────────────────────────────────
all_text = ' '.join(df.values.flatten().astype(str))
total_counter = Counter(process_text(all_text))

# ── Top-5 per food ────────────────────────────────────────────────────────────
food_name_tokens = set()
for food in df.columns:
    for w in process_text(food):
        food_name_tokens.add(w)

# ── Categories ────────────────────────────────────────────────────────────────
categories = {
    "Sweet":        ["sweet", "caramelized", "syrupy", "chocolate", "cinnamon", "fruity", "berry", "tropical", "ripe"],
    "Savory":       ["savory", "meaty", "umami", "greasy", "fatty", "buttery", "cheesy", "yeasty"],
    "Sour":         ["sour", "tart", "vinegary", "citrus", "citrusy", "bitter"],
    "Burnt/Smoked": ["roasted", "smoky", "smoked", "charred", "roasty", "burnt", "toasted", "grilled"],
    "Fresh":        ["fresh", "crisp", "refreshing", "floral", "flower", "fragrant", "mint", "leafy",
                     "grassy", "spice", "earthy", "wood", "musky", "nutty"]
}

category_words = {w for words in categories.values() for w in words}

food_top5 = {}
for food in df.columns:
    text = ' '.join(df[food].dropna().astype(str))
    words = [w for w in process_text(text) if w not in food_name_tokens and w in category_words]
    food_top5[food] = Counter(words).most_common(5)

word_freq = {}
for cat, words in categories.items():
    for w in words:
        if total_counter[w] > 0:
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

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(8, 10))
gs = gridspec.GridSpec(2, 1, height_ratios=[5, 1], hspace=0) # ⭕️

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
        ax_polar.annotate(word, (angle, r), fontsize=11,
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

# ── Bar charts ────────────────────────────────────────────────────────────────
gs_bar = gridspec.GridSpecFromSubplotSpec(1, len(df.columns), subplot_spec=gs[1], wspace=0.8) # ⭕️

for idx, food in enumerate(df.columns):
    ax = fig.add_subplot(gs_bar[idx])
    top5 = food_top5[food]
    words_bar = [w for w, _ in top5]
    freqs_bar = [c for _, c in top5]

    bar_colors = [word_to_color.get(w, '#AAAAAA') for w in words_bar[::-1]]

    bars = ax.barh(words_bar[::-1], freqs_bar[::-1],
                   color=bar_colors, alpha=0.75,
                   edgecolor='white', linewidth=0.5, height=0.6)

    for bar, val in zip(bars, freqs_bar[::-1]):
        ax.text(val + 0.15, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', ha='left', fontsize=9, color='#444444')

    ax.set_title(food, fontsize=12, fontweight='bold', color='black', pad=6)
    ax.set_xlim(0, max(freqs_bar) * 1.35)
    ax.tick_params(axis='y', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.xaxis.set_visible(False)

plt.savefig("word.pdf", dpi=300, bbox_inches='tight')
plt.savefig("word.png", dpi=150, bbox_inches='tight')
plt.show()