from execution.executor import Executor
from storage.table_heap import TableHeap

class InsertExec(Executor):
    def __init__(self, table_heap: TableHeap, values: list, column_names: list, analyzer, table_name):
        self.table_heap = table_heap
        self.values = values # A single row representing values, e.g. [1, 'Bob']
        self.column_names = column_names
        self.inserted = False
        self.analyzer = analyzer
        self.table_name = table_name

    def init(self):
        self.inserted = False

    def next(self):
        if self.inserted:
            return None
            
        row_dict = dict(zip(self.column_names, self.values))
        # Strip quotes if they somehow were passed down from parser AST as string expressions
        for k, v in row_dict.items():
            if v == "NULL":
                row_dict[k] = None
            elif isinstance(v, str) and v.startswith("'") and v.endswith("'"):
                row_dict[k] = v[1:-1]
            elif isinstance(v, str) and v.isdigit():
                row_dict[k] = int(v)
                
        table = self.analyzer.catalog.get_table(self.table_name)
            
        # simulate row like analyzer does
        for pk in [table.primary_key] if table.primary_key else []:
            val = row_dict[pk]
            if val is None:
                raise Exception(f"PRIMARY KEY '{pk}' cannot be NULL")
            for r in table.rows:
                if r[pk] == val:
                    raise Exception(f"Duplicate PRIMARY KEY value '{val}'")

        for uk in table.unique_keys:
            val = row_dict[uk]
            for r in table.rows:
                if r[uk] == val:
                    raise Exception(f"Duplicate UNIQUE value '{val}' for column '{uk}'")

        # Step 4: ACTUAL INSERT
        self.table_heap.insert_tuple(row_dict)

        self.inserted = True
        return {"inserted": 1}