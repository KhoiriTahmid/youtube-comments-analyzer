from fastapi import FastAPI, BackgroundTasks
import nltk
nltk.download('punkt_tab')
from youtube_comment_downloader import *

from services import add_lexicon
from db_services import db_connect, db_disconnect
from preprocess import add_slangwords
from controller import get_comments_and_process
from ngrok import run_ngrok

# Inisialisasi FastAPI App
app = FastAPI(
    title="S moni com",
    description="API untuk comments analisis",
)

@app.on_event("startup")
async def startup():
    add_lexicon()
    add_slangwords()
    await db_connect()

@app.on_event("shutdown")
async def shutdown():
    await db_disconnect()

@app.post("/predict_comments/")
async def predict_comments(video_id: str, background_tasks: BackgroundTasks):
    return await get_comments_and_process(video_id, background_tasks)

run_ngrok(app)