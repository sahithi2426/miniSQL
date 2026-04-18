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
    def __init__(self, name, columns, foreign_keys=None, primary_key=None, unique_keys=None):
        self.name = name
        self.columns = {col[0]: col[1] for col in columns}
        self.rows = []
        self.heap = self
        self.foreign_keys = foreign_keys or []
        self.primary_key = primary_key
        self.unique_keys = unique_keys or []

     # REQUIRED FOR InsertExec
    def insert_tuple(self, row):
        # remove quotes if present
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, str) and v.startswith("'") and v.endswith("'"):
                clean_row[k] = v.strip("'")
            else:
                clean_row[k] = v

        self.rows.append(clean_row)

    # REQUIRED FOR SeqScanExec
    def iterator(self):
        return TableIterator(self.rows)

class Catalog:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns, foreign_keys=None, primary_key=None, unique_keys=None):
        if name in self.tables:
            raise Exception(f"Table '{name}' already exists.")
        self.tables[name] = Table(name, columns, foreign_keys, primary_key, unique_keys)

    def get_table(self, name):
        if name not in self.tables:
            raise Exception(f"Table '{name}' does not exist.")
        return self.tables[name]