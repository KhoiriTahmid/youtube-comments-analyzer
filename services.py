from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from youtube_comment_downloader import *
from fastapi import HTTPException
import nltk
nltk.download('punkt_tab')
import pandas as pd
import difflib
import pickle
import csv

from db_services import update_bulk

try:
    model = load_model('credentials/my_model.keras')
    with open('credentials/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    with open('credentials/scaler.pickle', 'rb') as handle:
        scaler = pickle.load(handle)
except Exception as e:
    raise RuntimeError(f"Gagal memuat model atau file pendukung: {e}")


feature_cols = [
        'stylized_alphanum_count', 'emoji_count', 'numeric_count',
        "is_alpha_num_mixed_and_not_alpha_then_num", 'uppercase_count',
        'word_space_count', 'is_alpha_then_num', 'word_count', 'has_judol_phrase'
    ]
lexicon_positive = dict()
lexicon_negative = dict()

def add_lexicon():
    try:
        with open("csv/lexicon_positive.csv", newline='', encoding='utf-8') as csvpositive:
            reader = csv.reader(csvpositive, delimiter=',')
            for row in reader:
                lexicon_positive[row[0]] = int(row[1])
        with open("csv/lexicon_negative.csv", newline='', encoding='utf-8') as csvnegative:
            reader = csv.reader(csvnegative, delimiter=',')
            for row in reader:
                lexicon_negative[row[0]] = int(row[1])
    except FileNotFoundError:
        print("CSV file not found! Please make sure 'colloquial-indonesian-lexicon.csv' is in the project folder.")

async def predict_sentimen_comments(cids, texts):
    sentiments=[]
    for text in texts:
        score = 0
        for word in text.split(" "):
            if (word in lexicon_positive):
                score = score + lexicon_positive[word]
            if (word in lexicon_negative):
                score = score + lexicon_negative[word]

        polarity=''

        if score > 0:
            polarity = 1   # Positive
        elif score < 0:
            polarity = -1  # Negative
        else:
            polarity = 0   # Neutral
        sentiments.append(polarity)

    await update_bulk(col='sentimen', cids=cids, predictions=sentiments)

def are_similar(a, b, threshold=0.80):
    return difflib.SequenceMatcher(None, a, b).ratio() >= threshold

async def predict_spam_comments(data):
    spam_cids = set()

    for author, comments in data.items():
        if len(comments) < 3:
            continue

        for i in range(len(comments)):
            for j in range(i + 1, len(comments)):
                if are_similar(comments[i]["text"], comments[j]["text"]):
                    spam_cids.add(comments[i]["cid"])
                    spam_cids.add(comments[j]["cid"])
    if(len(spam_cids)):
        await update_bulk(col='is_spam', cids=list(spam_cids), predictions=[1] * len(spam_cids))


async def predict_judol_comments(cids, processed_texts, feature_list):
    try:
    
        features_df = pd.DataFrame(feature_list)
    
        X_features = features_df[feature_cols].values
        X_features_scaled = scaler.transform(X_features)
        sequences = tokenizer.texts_to_sequences(processed_texts)
        X_text = pad_sequences(sequences, maxlen=100, padding='post')
        predictions_prob = model.predict([X_text, X_features_scaled])
        predictions = (predictions_prob > 0.5).astype(int).flatten().tolist()

        await update_bulk(col="is_judol", cids=cids, predictions=predictions)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error di thread pool: {str(e)}")

