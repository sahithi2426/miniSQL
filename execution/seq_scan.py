from execution.executor import Executor
from storage.table_heap import TableHeap

class SeqScanExec(Executor):
    def __init__(self, table_heap: TableHeap,table_name=None, alias=None):
        self.table_heap = table_heap
        self.table_name = table_name
        self.alias = alias

        self.rows = []
        self.index = 0
        self.loaded = False

    def init(self):
        if not self.loaded:   
            self.rows = []
            iterator = self.table_heap.iterator()

            seen = set()  

            while True:
                tup = iterator.get_next()
                if tup is None:
                    break

                key = tuple(sorted(tup.items()))
                if key not in seen:
                    seen.add(key)
                    self.rows.append(dict(tup))

            self.loaded = True

        self.index = 0

    """def next(self):
        if self.index >= len(self.rows):
            return None

        tup = self.rows[self.index]
        self.index += 1
        table_name = self.table_heap.name

        qualified = {}
        for k, v in tup.items():
            qualified[k] = v
            qualified[f"{table_name}.{k}"] = v

        return qualified"""
    def next(self):
        if self.index >= len(self.rows):
            return None

        tup = self.rows[self.index]
        self.index += 1
        result = {}

        table_name = self.table_name
        alias = self.alias if self.alias else table_name

        for k, v in tup.items():
            # plain column
            result[k] = v

            # table.column
            #result[f"{table_name}.{k}"] = v

            # alias.column
            #result[f"{alias}.{k}"] = v

        return result