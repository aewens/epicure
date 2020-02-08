from database.sqlite import SQLite
from database.schemas import Schemas

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse

from typing import Any, Dict

KeyedDict = Dict[str, Any]
app = FastAPI()
db = SQLite("x.db")
schemas = Schemas()

tables = schemas.sql
schemas.create_tables(db)

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
