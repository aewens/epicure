from helpers.general import eprint

from os import stat, remove
from os.path import dirname, basename, isfile, isdir, join as path_join
from shutil import copyfile
from time import strftime
from operator import itemgetter
from contextlib import closing, contextmanager
from threading import Lock
from sqlite3 import connect, register_converter, PARSE_DECLTYPES, PARSE_COLNAMES
from sqlite3 import IntegrityError, ProgrammingError, Error as SQLiteError
from traceback import format_exc

register_converter("BOOLEAN", lambda value: bool(int(value)))

class SQLite:
    def __init__(self, db_file, debug=False, lock=Lock()):
        self.db_file = db_file
        self.path = dirname(self.db_file)
        self.filename = basename(self.db_file)

        self.debug = debug

        self.connection = None
        self.cursor = None
        self.memory = False
        self.lock = lock
        self._load()

    def _load(self):
        settings = dict()
        settings["check_same_thread"] = False
        settings["isolation_level"] = "DEFERRED"
        settings["detect_types"] = PARSE_DECLTYPES | PARSE_COLNAMES
        try:
            self.connection = connect(self.db_file, **settings)
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA foreign_keys = ON")
        except SQLiteError as e:
            eprint(format_exc() if self.debug else str(e))
            self.connection = connect(":memory:")
            self.memory = True
        # self.cursor = self.connection.cursor()

    def _unload(self):
        self.connection.close()

    # Must be called from `backup`
    def _remove_old_backups(self, backup_dir, backups):
        contents = listdir(backup_dir)
        files = [(f, stat(f).st_mtime) for f in contents if isfile(f)]
        # Sort by mtime
        files.sort(key=itemgetter(1))
        remove_files = files[:-backups]
        for rfile in remove_files:
            remove(rfile)

    def _convert(self, values):
        convert = lambda value: value if not None else "NULL"
        return (convert(value) for value in values)

    def stop(self):
        self._unload()

    def backup(self, backup_dir=None, backups=1):
        if backup_dir is None:
            backup_dir = self.path

        if not isdir(backup_dir):
            eprint("ERROR: Backup directory does not exist")
            return None

        suffix = strftime("-%Y%m%d-%H%M%S")
        backup_name = f"{self.filename} {suffix}"
        backup_file = path_join(backup_dir, backup_name)
        # Lock database
        with closing(self.connection.cursor()) as cursor:
            cursor.execute("begin immediate")
            copyfile(self.db_file, backup_file)
        # Unlock database
        self.conenction.rollback()
        self._remove_old_backups(backup_dir, backups)

    def execute(self, executor, values=tuple(), fetch=False, commit=False):
        try:
            with closing(self.connection.cursor()) as cursor:
                args = (executor, values) if "?" in executor else (executor,)
                if commit:
                    with self.transaction():
                        result = cursor.execute(*args)

                else:
                    result = cursor.execute(*args)

                if not fetch:
                    return True

                return cursor.fetchall()

        except (ProgrammingError, IntegrityError) as e:
            eprint(format_exc() if self.debug else str(e))
            return False

    def fetch(self, executor, values=tuple(), commit=False):
        return self.execute(executor, values, fetch=True, commit=commit)

    """
    e.g. create_table("test", ["value TEXT"])
    """
    def create_table(self, name, fields, commit=False):
        pkey = False
        for field in fields:
            if "PRIMARY KEY" in field:
                pkey = True
                break

        # A table without a primary key is a table without legs, useless
        if not pkey:
            fields.insert(0, "id INTEGER NOT NULL PRIMARY KEY")

        fields_string = ",".join(fields)
        executor = f"CREATE TABLE {name} ({fields_string})"
        return self.execute(executor, commit=commit)

    """
    e.g. insert("test", {"value": "abc"})
    """
    def insert(self, table, insertion, commit=False):
        assert isinstance(insertion, dict), "Expected dict"
        keys = ",".join(insertion.keys())
        places = ",".join(["?"] * len(insertion))
        values = tuple(self._convert(insertion.values()))
        executor = f"INSERT INTO {table} ({keys}) VALUES({places})"
        return self.execute(executor, values, commit=commit)

    def update(self, table, modification, where, commit=False):
        assert isinstance(modification, dict), "Expected dict"
        assert isinstance(where, tuple), "Expected tuple"
        assert len(where) == 2, "Expected length of '2'"
        assert isinstance(where[0], str), "Expected str"
        assert isinstance(where[1], tuple), "Expected tuple"
        keys = ",".join(f"{key} = ?" for key in modification.keys())
        mod_values = tuple(self._convert(modification.values()))
        where_query = where[0]
        where_values = where[1]
        values = mod_values + where_values
        executor = f"UPDATE {table} SET {keys} WHERE {where_query}"
        return self.execute(executor, values, commit=commit)

    def delete(self, table, where, commit=False):
        assert isinstance(where, tuple), "Expected tuple"
        assert len(where) == 2, "Expected length of '2'"
        assert isinstance(where[0], str), "Expected str"
        assert isinstance(where[1], tuple), "Expected tuple"
        where_query = where[0]
        where_values = where[1]
        values = where_values
        executor = f"DELETE FROM {table} WHERE {where_query}"
        return self.execute(executor, values, commit=commit)

    def lookup(self, table, search, where=None):
        if type(search) != list:
            search = [search]
        keys = ",".join(search)
        executor = f"SELECT {keys} FROM {table}"
        if where:
            assert isinstance(where, tuple), "Expected tuple"
            assert len(where) == 2, "Expected length of '2'"
            assert isinstance(where[0], str), "Expected str"
            assert isinstance(where[1], tuple), "Expected tuple"
            where_query = where[0]
            where_values = where[1]
            executor = f"{executor} WHERE {where_query}"
            results = self.fetch(executor, where_values)

        else:
            results = self.fetch(executor)

        #found = list()
        #for result in results:
        #    remap = dict()
        #    for index, term in enumerate(search):
        #        remap[term] = result[index]

        #    found.append(remap)

        #return found
        return results

    def lookup_one(self, table, search, where=None):
        result = self.lookup(table, search, where)
        return result[0] if len(result) > 0 else None

    def lookup_all(self, table, where=None):
        return self.lookup(table, ["*"], where)

    def get_all_tables(self):
        executor = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = self.fetch(executor)
        return (table[0] for table in tables)

    def drop_table(self, name, commit=False):
        executor = f"DROP TABLE IF EXISTS {name}"
        return self.execute(executor, commit=commit)

    @contextmanager
    def transaction(self):
        with self.lock:
            try:
                yield
                self.connection.commit()
            except:
                self.connection.rollback()
                raise
