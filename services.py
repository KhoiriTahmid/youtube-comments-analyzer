from fastapi import BackgroundTasks, HTTPException
import pandas as pd
from fastapi.concurrency import run_in_threadpool
import nltk
nltk.download('punkt_tab')
from tensorflow.keras.preprocessing.sequence import pad_sequences
from youtube_comment_downloader import *
import itertools


from preprocess import preprocess_text
from load_comments import get_video_comments

feature_cols = [
        'stylized_alphanum_count', 'emoji_count', 'numeric_count',
        "is_alpha_num_mixed_and_not_alpha_then_num", 'uppercase_count',
        'word_space_count', 'is_alpha_then_num', 'word_count', 'has_judol_phrase'
    ]

async def predict_comments(video_id: str, scaler, tokenizer, model, background_tasks: BackgroundTasks):
    try:
        original_comments = await run_in_threadpool(get_video_comments, video_id, background_tasks)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error di thread pool: {str(e)}")
    if not original_comments:
        return {"message": "Tidak ada komentar yang dapat diambil untuk video ini.", "predictions": []}

    # Sisa dari kode ini sama persis seperti sebelumnya
    processed_texts, feature_list = preprocess_text(original_comments)
    features_df = pd.DataFrame(feature_list)
    

    X_features = features_df[feature_cols].values
    X_features_scaled = scaler.transform(X_features)
    sequences = tokenizer.texts_to_sequences(processed_texts)
    X_text = pad_sequences(sequences, maxlen=100, padding='post')
    predictions_prob = model.predict([X_text, X_features_scaled])
    predictions = (predictions_prob > 0.5).astype(int).flatten().tolist()

    
    return {"video_id": video_id, "total":len(original_comments), "predictions": original_comments}