from helpers.encode import jsto
from database.sqlite import SQLite
from database.schemas import Schemas

from fastapi import FastAPI
from pydantic import BaseModel, create_model
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

# Inject dynamic models in as variables
dynamic_fields = dict()
for name, model in models.items():
    model_name = model.__name__
    globals()[model_name] = model
    dynamic_fields[name] = (model, None)

DynamicEntry = create_model("DynamicEntry", **dynamic_fields)

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

@app.get("/api/schema")
async def get_all_schemas():
    return list(models.keys())

@app.get("/api/schema/dynamic")
async def get_dynamic_schema():
    res = dict()
    res["status"] = "success"
    res["data"] = jsto(DynamicEntry.schema_json())
    return res

@app.get("/api/schema/{schema_name}")
async def get_schema(schema_name: str):
    res = dict()

    model = models.get(schema_name)
    if model is None:
        res["status"] = "unknown"
        return res

    schema_model = jsto(model.schema_json()) 

    res["status"] = "success"
    res["data"] = schema_model
    return res

@app.get("/api/db")
async def get_all_dbs():
    res = dict()
    res["status"] = "success"
    res["data"] = db.get_all_tables()
    return res

@app.get("/api/db/{db_name}")
async def get_db_entries(db_name: str):
    res = dict()
    res["status"] = "error"
    if db_name not in db.get_all_tables():
        res["error"] = f"'{db_name}' is not a valid database, see /api/db"
        return res

    model = models.get(db_name)
    if model is None:
        res["status"] = "unknown"
        return res

    entries = db.lookup_all(db_name)
    schema_model = jsto(model.schema_json())

    res["status"] = "success"
    res["data"] = dict()
    res["data"]["entries"] = entries
    res["data"]["schema"] = schema_model
    return res

@app.post("/api/db/{db_name}/get")
async def get_db(db_name: str, entry: Entry):
    return entry.table

@app.post("/api/db/put")
async def put_db(entry: DynamicEntry):
    db_res = dict()
    fields = entry.__fields__
    for name in fields.keys():
        entry_fields = getattr(entry, name, None)
        if entry_fields is None:
            continue

        meta_fields = getattr(entry_fields, "__fields__", None)
        if meta_fields is None:
            continue

        db_fields = dict()
        for field_name in meta_fields.keys():
            field_data = getattr(entry_fields, field_name, None)
            if field_data is not None:
                db_fields[field_name] = field_data

        with db.transaction():        
            db_res[name] = db.insert(name, db_fields)

    res = dict()
    res["status"] = "unknown"
    res["data"] = db_res
    return res

@app.delete("/api/db/drop")
async def drop_db(entry: Entry):
    res = dict()
    with db.transaction():
        res["success"] = "success"
        res["data"] = db.drop_table(entry.table)
        return res

@app.get("/api/notes")
async def get_notes():
    messages = list()
    #with db.transaction():

    return messages
