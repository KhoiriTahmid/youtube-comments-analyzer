from fastapi import FastAPI, HTTPException, BackgroundTasks
import pandas as pd
from fastapi.concurrency import run_in_threadpool
import nltk
nltk.download('punkt_tab')
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from youtube_comment_downloader import *
import itertools

import services
from db_services import db_connect, db_disconnect
from preprocess import preprocess_text
from load_comments import get_video_comments
from ngrok import run_ngrok

# --- Muat Model dan Objek ---
try:
    model = load_model('my_model.keras')
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    with open('scaler.pickle', 'rb') as handle:
        scaler = pickle.load(handle)
except Exception as e:
    raise RuntimeError(f"Gagal memuat model atau file pendukung: {e}")

# Inisialisasi FastAPI App
app = FastAPI(
    title="API Prediksi Komentar (Colab)",
    description="API untuk prediksi komentar judi online, berjalan di Google Colab via ngrok.",
)

@app.on_event("startup")
async def startup():
    await db_connect()

@app.on_event("shutdown")
async def shutdown():
    await db_disconnect()

# --- GANTI ENDPOINT LAMA ANDA DENGAN YANG INI ---
@app.post("/predict_comments/")
async def predict_comments(video_id: str, background_tasks: BackgroundTasks):
    return await services.predict_comments(video_id, scaler, tokenizer, model, background_tasks)

@app.get("/predict_comments/")
async def predict_comments(video_id: str, max_comments: int = 10000):
    """
    Mengambil komentar dari video YouTube, memprosesnya, dan memprediksi apakah
    komentar tersebut terkait judi online.
    """
    try:
        # Menjalankan fungsi blocking 'get_video_comments' di thread terpisah
        # untuk mencegah konflik dengan server asynchronous FastAPI.
        original_comments = await run_in_threadpool(get_video_comments, video_id)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error di thread pool: {str(e)}")
    if not original_comments:
        return {"message": "Tidak ada komentar yang dapat diambil untuk video ini.", "predictions": []}

    # Sisa dari kode ini sama persis seperti sebelumnya
    processed_texts, feature_list = [], []
    for comment in original_comments:
        processed_text, features = preprocess_text(comment)
        processed_texts.append(processed_text)
        feature_list.append(features)

    features_df = pd.DataFrame(feature_list)
    feature_cols = [
        'stylized_alphanum_count', 'emoji_count', 'numeric_count',
        "is_alpha_num_mixed_and_not_alpha_then_num", 'uppercase_count',
        'word_space_count', 'is_alpha_then_num', 'word_count', 'has_judol_phrase'
    ]

    X_features = features_df[feature_cols].values
    X_features_scaled = scaler.transform(X_features)
    sequences = tokenizer.texts_to_sequences(processed_texts)
    X_text = pad_sequences(sequences, maxlen=100, padding='post')
    predictions_prob = model.predict([X_text, X_features_scaled])
    predictions = (predictions_prob > 0.5).astype(int).flatten().tolist()

    results = []
    for i, comment in enumerate(original_comments):
        results.append({
            "comment": comment,
            "prediction": "Judi Online" if predictions[i] == 1 else "Bukan Judi Online",
            "probability": float(predictions_prob[i][0])
        })

    return {"video_id": video_id, "total":len(results), "predictions": results}

run_ngrok(app)