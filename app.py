from database.sqlite import SQLite

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse

from typing import Any, Dict

KeyedDict = Dict[str, Any]
app = FastAPI()
db = SQLite("x.db")

tables = dict()
tables["tags"] = [
    "tag VARCHAR(64)",
    "UNIQUE (tag)"
]
tables["notes"] = [
    "title VARCHAR(256)",
    "contents TEXT NOT NULL",
    "created_at TIMESTAMP NOT NULL",
    "last_updated_at TIMESTAMP NOT NULL",
    "UNIQUE (title)"
]
tables["data"] = [
    "parent_id INTEGER REFERENCES data(id)",
    "raw_data TEXT NOT NULL",
    "CONSTRAINT fk_parent_menu FOREIGN KEY (parent_id) REFERENCES raw_data (id) ON DELETE CASCADE",
    "UNIQUE (raw_data)"
]
tables["tagmap"] = [
    "id INTEGER",
    "note_id INTEGER",
    "data_id INTEGER",
    "tag_id INTEGER",
    "PRIMARY KEY (note_id, data_id)",
    "FOREIGN KEY (note_id) REFERENCES notes (id)",
    "FOREIGN KEY (data_id) REFERENCES data (id)",
    "FOREIGN KEY (tag_id) REFERENCES tags (id)"
]

all_tables = db.get_all_tables()
for name, fields in tables.items():
    if name not in all_tables:
        db.create_table(name, fields)

class Entry(BaseModel):
    table: str

class PutEntry(Entry):
    table: str
    value: KeyedDict

@app.get("/api")
async def welcome():
    return {"welcome": "Hello, world!"}

@app.get("/api/")
async def directory():
    return {"db": "/api/db", "notes": "/api/notes"}

@app.get("/api/db")
async def get_db():
    return db.get_all_tables()

@app.post("/api/db/get")
async def get_db(entry: Entry):
    return entry.table

@app.post("/api/db/put")
async def put_db(entry: PutEntry):
    return {entry.table: entry.value}

@app.delete("/api/db/drop")
async def drop_db(entry: Entry):
    with db.transaction():
        return db.drop_table(entry.table)

@app.get("/api/notes")
async def get_notes():
    messages = list()
    #with db.transaction():

    return messages
