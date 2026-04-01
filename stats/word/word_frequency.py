import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk
import os
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from collections import Counter

nltk_data_dir = os.path.expanduser("~/nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)
for pkg in ["stopwords", "wordnet", "omw-1.4"]:
    nltk.download(pkg, download_dir=nltk_data_dir, quiet=True)

tokenizer = RegexpTokenizer(r"\w+")
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

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

def get_word_frequency(csv_path, columns, min_freq=2, save_path="word_frequency.csv"):
    df = pd.read_csv(csv_path)
    df = df[columns]
    all_text = ' '.join(df.values.flatten().astype(str))
    total_counter = Counter(process_text(all_text))
    result = {w: c for w, c in total_counter.items() if c > min_freq}
    
    if save_path:
        step1_df = pd.DataFrame(
            sorted(result.items(), key=lambda x: -x[1]),
            columns=["word", "frequency"]
        )
        step1_df.to_csv(save_path, index=False)
    
    return result