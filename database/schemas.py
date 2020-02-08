from helpers.datetime import now
from helpers.encode import jots, jsto
from helpers.general import generator, trap, eprint

from pydantic import BaseModel

import typing
from pathlib import Path
from datetime import datetime
from copy import deepcopy
from collections import defaultdict

"""
_id = "id INTEGER NOT NULL PRIMARY KEY"

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
    "CONSTRAINT fk_parent_menu FOREIGN KEY (parent_id) REFERENCES data(id) ON DELETE CASCADE",
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
"""

class Schemas:
    def __init__(self, debug=False):
        self.debug = debug

        current_path = Path(__file__).parent.absolute()
        schema_path = current_path / ".." / "schemas"
        self.path = schema_path.resolve()

        self.raw = dict()
        self.model = defaultdict(dict)
        self.sql = defaultdict(list)
        self.sql_meta = defaultdict(list)

        self.graph = defaultdict(list)

        self.sql_map = dict()
        self.sql_map["integer"] = int
        self.sql_map["varchar"] = str
        self.sql_map["text"] = str
        self.sql_map["timestamp"] = datetime

        self.parse()

    def create_tables(self, db):
        all_tables = db.get_all_tables()
        for name, fields in self.sql.items():
            meta_fields = self.sql_meta[name]
            fields.extend(meta_fields)

            if name not in all_tables:
                db.create_table(name, fields)

    def parse(self):
        sql = self._parse_sql()
        model = self._parse_model()

        for schema_file in self.path.glob("*.json"):
            schema_name = schema_file.name.replace(".json", "")
            schema_data = jsto(schema_file.read_text())
            if schema_data is None:
                continue

            self.raw[schema_name] = schema_data

            for key, value in schema_data.items():
                entry = schema_name, key, value
                sql.send(entry)
                model.send(entry)

        if self.debug:
            print("Graph", self.graph)
            for table, entries in self.sql.items():
                print("SQL", table)
                for entry in entries:
                    print("\t", entry)

                meta_entries = self.sql_meta[table]
                if len(meta_entries) > 0:
                    for m_entry in meta_entries:
                        print("\t", m_entry)

                print()

    @trap(eprint)
    @generator
    def _parse_sql_meta(self):
        name, key, value = (yield)

        entry = None
        if key == "unique" and isinstance(value, list):
            ukeys = ", ".join(value)
            entry = f"{key.upper()} ({ukeys})"

        elif key == "primary_key" and isinstance(value, list):
            pkeys = ", ".join(value)
            entry = f"PRIMARY KEY ({pkeys})"

        elif key == "foreign_key" and isinstance(value, dict):
            entry = list()
            prefix = "FOREIGN KEY"
            for fkey, parameters in value.items():
                item = f"{prefix} ({fkey})"
                references = parameters.get("references")
                if isinstance(references, dict):
                    table = references.get("table", name)
                    field = references.get("field")
                    item = f"{item} REFERENCES {table}({field})"

                on = parameters.get("on")
                if isinstance(on, dict):
                    for method, effect in on.items():
                        item = f"{item} ON {method.upper()} {effect.upper()}"

                entry.append(item)
                
        if entry is not None:
            if isinstance(entry, list):
                self.sql_meta[name].extend(entry)

            else:
                self.sql_meta[name].append(entry)

    @trap(eprint)
    @generator
    def _parse_sql(self):
        name, key, value = (yield)

        if key == "_needs" and isinstance(value, list):
            self.graph[name].extend(value)
            return

        elif key == "_sql" and isinstance(value, dict):
            meta = self._parse_sql_meta()
            for k, v in value.items():
                item = name, k, v
                meta.send(item)

            return

        assert isinstance(value, dict), f"Expected dict: {value}"

        value_type = value.get("type")
        if value_type is None:
            return

        entry = f"{key} {value_type.upper()}"
        if value_type == "varchar":
            value_length = value.get("max_length")
            entry = f"{entry}({value_length})"

        required = value.get("required", True)
        if required:
            entry = f"{entry} NOT NULL"

        primary_key = value.get("primary_key", False)
        if primary_key:
            entry = f"{entry} PRIMARY KEY"

        references = value.get("references")
        if isinstance(references, dict):
            table = references.get("table", name)
            field = references.get("field")
            entry = f"{entry} REFERENCES {table}({field})"

        self.sql[name].append(entry)

    @trap(eprint)
    @generator
    def _parse_model(self):
        name, key, value = (yield)

        if key.startswith("_"):
            return

        value_type = value.get("type")
        if value_type is not None:
            pass

    def _schema_factory(self, name, data):
        inherits = (BaseModel,)
        variables = dict()
        annotations = variables["__annotations__"] = dict()
        for key, value in data.items():
            resolver = None
            if isinstance(value, str):
                # Check if value is a built-in type
                resolver = __builtin__.__dict__.get(value)

                # Check if value is a type from the typing module
                if resolver is None:
                    resolver = getattr(typing, value, None)

                # Check if value is a type from the loaded modules
                if resolve is None:
                    resolver = globals().get(value)

            if resolve is not None:
                annotations[key] = resolver

        model = type(name, inherits, variables)

