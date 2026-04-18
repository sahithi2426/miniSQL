import json
import os

class TableIterator:
    def __init__(self, rows):
        self.rows = rows
        self.idx = 0

    def get_next(self):
        if self.idx >= len(self.rows):
            return None
        val = self.rows[self.idx]
        self.idx += 1
        return val
    
class Table:
    def __init__(self, name, columns,catalog, foreign_keys=None, primary_key=None, unique_keys=None):
        self.name = name
        self.columns = {col[0]: col[1] for col in columns}
        self.rows = []
        self.heap = self
        self.catalog = catalog
        self.foreign_keys = foreign_keys or []
        self.primary_key = primary_key
        self.unique_keys = unique_keys or []

     # REQUIRED FOR InsertExec
    def insert_tuple(self, row):
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, str) and v.startswith("'") and v.endswith("'"):
                clean_row[k] = v.strip("'")
            else:
                clean_row[k] = v

        self.rows.append(clean_row)

        # correct persistence call
        self.catalog._save()

    # REQUIRED FOR SeqScanExec
    def iterator(self):
        return TableIterator(self.rows)

class Catalog:
    def __init__(self):
        self.tables = {}
        self._load()

    def create_table(self, name, columns, foreign_keys=None, primary_key=None, unique_keys=None):
        if name in self.tables:
            raise Exception(f"Table '{name}' already exists.")
        self.tables[name] = Table(name, columns,self, foreign_keys, primary_key, unique_keys)
        self._save()

    def get_table(self, name):
        if name not in self.tables:
            raise Exception(f"Table '{name}' does not exist.")
        return self.tables[name]

    def _save(self):
        data = {}
        for name, table in self.tables.items():
            data[name] = {
                "columns": {k: str(v) for k, v in table.columns.items()},  # 🔥 FIX
                "rows": table.rows,
                "primary_key": table.primary_key,
                "unique_keys": table.unique_keys
            }

        with open("catalog_temp.json", "w") as f:
            json.dump(data, f)

        os.replace("catalog_temp.json", "catalog.json")


    def _load(self):
        if not os.path.exists("catalog.json"):
            return
        
        try:
            with open("catalog.json", "r") as f:
                data = json.load(f)

        except Exception:
            print("Corrupted catalog.json — resetting")
            self.tables = {}
            return

        for name, t in data.items():
            table = Table(name, [(k, v) for k, v in t["columns"].items()], self)
            table.rows = t["rows"]
            table.primary_key = t["primary_key"]
            table.unique_keys = t["unique_keys"]
            self.tables[name] = table