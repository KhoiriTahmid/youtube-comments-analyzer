from databases import Database
from sqlalchemy import create_engine
from dotenv import load_dotenv
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
        print("Keys in first comment:", comments[0].keys())
        query = comment.insert()
        await database.execute_many(query=query, values=comments)
        print(f"{len(comments)} comments inserted.")
    except Exception as e:
        print("DB insert failed:", e)



async def update_judol_bulk(updates: list[dict]):
    # Build CASE WHEN string
    case_stmt = "CASE "
    for u in updates:
        case_stmt += (
            f"WHEN cid = '{u['cid']}' AND author = '{u['author']}' "
            f"THEN '{u['is_judol']}' "
        )
    case_stmt += "ELSE is_judol END"

    # Build WHERE clause tuples for filtering
    where_tuples = ", ".join(
        [f"('{u['cid']}', '{u['author']}')" for u in updates]
    )

    query = f"""
    UPDATE comments
    SET is_judol = {case_stmt}
    WHERE (cid, author) IN ({where_tuples})
    """

    await database.execute(query=query)
    return {"updated": len(updates)}
