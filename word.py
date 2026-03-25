import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from collections import Counter

# force a known download directory
nltk_data_dir = os.path.expanduser("~/nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)

# register path
nltk.data.path.append(nltk_data_dir)

# download all required resources to that directory
for pkg in [
    "stopwords",
    "wordnet",
    "omw-1.4"
]:
    nltk.download(pkg, download_dir=nltk_data_dir, quiet=True)

# read file
with open("word.txt", "r", encoding="utf-8") as f:
    text = f.read().lower()

# tokenizer (no punkt dependency)
tokenizer = RegexpTokenizer(r"\w+")
tokens = tokenizer.tokenize(text)

# stopwords + lemmatizer
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# process words
words = []
for w in tokens:
    if len(w) > 2:
        w = lemmatizer.lemmatize(w)
        if w not in stop_words:
            words.append(w)

# count
counter = Counter(words)

# output
for word, count in counter.most_common():
    if count >= 2:
        print(f"{word}: {count}")