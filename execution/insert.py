from execution.executor import Executor
from storage.table_heap import TableHeap

class InsertExec(Executor):
    def __init__(self, table_heap: TableHeap, values: list, column_names: list):
        self.table_heap = table_heap
        self.values = values # A single row representing values, e.g. [1, 'Bob']
        self.column_names = column_names
        self.inserted = False

    def init(self):
        self.inserted = False

    def next(self):
        if self.inserted:
            return None
            
        row_dict = dict(zip(self.column_names, self.values))
        # Strip quotes if they somehow were passed down from parser AST as string expressions
        for k, v in row_dict.items():
            if isinstance(v, str) and v.startswith("'"):
                row_dict[k] = v.strip("'")
                
        self.table_heap.insert_tuple(row_dict)
            
        self.inserted = True
        return {"inserted": 1}
