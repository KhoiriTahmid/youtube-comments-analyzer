from databases import Database
from sqlalchemy import create_engine
from dotenv import load_dotenv
from typing import Literal
import os

from model import comment, metadata

load_dotenv()  # baca .env di folder yg sama

db_url = os.getenv("DATABASE_URL")
database = Database(db_url)
engine = create_engine(db_url)
metadata.create_all(engine)  # untuk buat tabel jika belum ada

async def db_connect():
    await database.connect()

async def db_disconnect():
    await database.disconnect()

async def add_comments_bulk(comments):
    try:
        query = comment.insert()
        await database.execute_many(query=query, values=comments)
        print(f"Added {len(comments)} new data.")
    except Exception as e:
        print("DB insert failed:", e)

async def update_bulk(col: Literal["is_judol", "is_spam", "sentimen"], cids: list[str], predictions: list[str]):
    try:
        where_tuples=[]
        case_stmt = "CASE "
        for cid, pred in zip(cids, predictions):
            where_tuples.append(f"'{cid}'")
            case_stmt += (f"WHEN cid = '{cid}' THEN '{pred}' ")
                
        case_stmt += (f"ELSE {col} END")

        where_tuples = ", ".join(where_tuples)

        query = (f"""
        UPDATE comments
        SET {col} = {case_stmt}
        WHERE cid IN ({where_tuples})
        """)

        await database.execute(query=query)
        print(f"{col} Updated {len(cids)} new data.")
    except Exception as e:
        raise e


