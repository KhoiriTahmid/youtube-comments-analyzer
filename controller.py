from collections import defaultdict
from fastapi import BackgroundTasks, HTTPException

from scrap import get_comments
from db_services import add_comments_bulk
from services import predict_judol_comments, predict_spam_comments, predict_sentimen_comments
from preprocess import preprocess_text

async def get_comments_and_process(video_id: str, background_tasks: BackgroundTasks):
    try:
        
        output_data = get_comments(video_id)
        
        # Start background job for all predictions
        background_tasks.add_task(process_predictions_in_bg, output_data)

        # run dan tunggu ampe kelar
        await add_comments_bulk(output_data)

        # Periksa jika worker mengembalikan pesan error
        if isinstance(output_data, dict) and 'error' in output_data:
            raise HTTPException(status_code=500, detail=f"error: {output_data['error']}")

        print("first push to DB")
        return {"success":True}

    except Exception as e:
        # Untuk error lainnya
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")


async def process_predictions_in_bg(output_data: list):

    comments = []
    cids = []
    spamDict = defaultdict(list)

    for row in output_data:
        comments.append(row['text'])
        cids.append(row['cid'])
        spamDict[row['author']].append({"cid": row["cid"], "text": row["text"]})

    processed_texts, feature_list = preprocess_text(comments)

    await predict_judol_comments(cids, processed_texts, feature_list)
    await predict_spam_comments(spamDict)
    await predict_sentimen_comments(cids, processed_texts)
    print("last push to DB")
