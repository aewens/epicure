from helpers.encode import jsto
from database.sqlite import SQLite
from database.schemas import Schemas

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse

from typing import Any, Dict, List
from enum import Enum

KeyedDict = Dict[str, Any]
app = FastAPI()
db = SQLite("x.db")
schemas = Schemas()

schemas.create_tables(db)
models = schemas.generate_models()

# DEBUG
#for name, model in models.items():
#    print(name)
#    for field_name, field_type in model.__annotations__.items():
#        print("\t", field_name, field_type, model.__fields__.get(field_name))

#SchemaName = Enum("SchemaName", {key: key for key in models.keys()})

class Entry(BaseModel):
    table: str

class GetEntry(Entry):
    table: str
    select: List[str]

class PutEntry(Entry):
    table: str
    value: KeyedDict

@app.get("/api")
async def welcome():
    return {"welcome": "Hello, world!"}

@app.get("/api/")
async def directory():
    return {"db": "/api/db", "notes": "/api/notes"}

@app.get("/api/schema/{schema_name}")
async def get_schema(schema_name: str):
    res = dict()

    schema_model = models.get(schema_name)
    if schema_model is None:
        res["status"] = "unknown"
        return res

    return jsto(schema_model.schema_json())

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
