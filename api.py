from helpers.encode import jsto
from database.sqlite import SQLite
from database.schemas import Schemas

from fastapi import FastAPI
from pydantic import BaseModel, create_model
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from typing import Any, Dict, List, Tuple, Union, Optional
from enum import Enum

KeyedDict = Dict[str, Any]
DataType = Tuple[Union[str, int, float, bool]]
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
async def get_db_entries(db_name: str, where_query: Optional[str] = None,
    limit: Optional[int] = None):
    res = dict()
    res["status"] = "error"
    if db_name not in db.get_all_tables():
        res["error"] = f"'{db_name}' is not a valid database, see /api/db"
        return res

    model = models.get(db_name)
    if model is None:
        res["status"] = "unknown"
        return res

    fields = list(model.__fields__.keys())
    schema_model = jsto(model.schema_json())

    where = None
    if where_query is not None:
        where = where_query, tuple()

    entries = db.lookup(db_name, fields, where=where, limit=limit)

    res["status"] = "success"
    res["data"] = dict()
    res["data"]["entries"] = entries
    res["data"]["schema"] = schema_model
    return res

@app.post("/api/db/{db_name}/get")
async def get_db(db_name: str, where_query: str,
    where_values: Optional[DataType] = None, limit: Optional[int] = None):
    res = dict()
    res["status"] = "error"
    if db_name not in db.get_all_tables():
        res["error"] = f"'{db_name}' is not a valid database, see /api/db"
        return res

    model = models.get(db_name)
    if model is None:
        res["status"] = "unknown"
        return res

    fields = list(model.__fields__.keys())
    schema_model = jsto(model.schema_json())

    where = None
    if where_query is not None:
        where = where_query, where_values
        if where_values is None:
            where = where_query, tuple()

    entries = db.lookup(db_name, fields, where=where, limit=limit)

    res["status"] = "success"
    res["data"] = dict()
    res["data"]["entries"] = entries
    res["data"]["schema"] = schema_model
    return res

def is_valid(db_name: str, data: KeyedDict) -> int:
    res = dict()
    res["status"] = "error"
    if db_name not in db.get_all_tables():
        res["data"] = f"'{db_name}' is not a valid database, see /api/db"
        return 1, res

    model = models.get(db_name)
    if model is None:
        res["status"] = "unknown"
        res["data"] = None
        return 2, res

    schema_model = jsto(model.schema_json())
    try:
        validate(instance=data, schema=schema_model)
        return 0, res

    except ValidationError as e:
        res["data"] = str(e)
        return 3, res

@app.post("/api/db/{db_name}/put")
async def put_db(db_name: str, data: KeyedDict):
    valid_state, res = is_valid(db_name, data)
    if valid_state != 0:
        return res

    with db.transaction():
        res["status"] = "success"
        res["data"] = db.insert(db_name, data)

    return res

@app.put("/api/db/{db_name}/fix")
async def fix_db(db_name: str, data: KeyedDict, where_query: str,
    where_values: Optional[DataType] = None):
    valid_state, res = is_valid(db_name, data)
    if valid_state != 0:
        return res

    if where_values is None:
        where_values = tuple()

    with db.transaction():
        res["status"] = "success"
        res["data"] = db.update(db_name, data, (where_query, where_values))

    return res

@app.delete("/api/db/{db_name}/pop")
async def pop_db(db_name: str, entry_id: int):
    res = dict()
    with db.transaction():
        res["success"] = "success"
        res["data"] = db.delete(db_name, ("id = ?", (entry_id,)))

    return res

@app.post("/api/db/put")
async def put_any_db(entry: DynamicEntry):
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
