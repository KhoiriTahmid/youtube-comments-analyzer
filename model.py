from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData
from sqlalchemy.sql import expression

metadata = MetaData()

comment = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("video_id", String(100)),
    Column("cid", String(100)),
    Column("text", String),
    Column("author", String(100)),
    Column("is_judol", Boolean, nullable=True, default=None),
    Column("is_spam", Boolean, nullable=False, server_default=expression.false()),
    Column("sentimen", Integer, nullable=True, default=None),
    Column("is_delete", Boolean, nullable=False, server_default=expression.true()),
)
