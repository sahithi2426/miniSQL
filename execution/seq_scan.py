from execution.executor import Executor
from storage.table_heap import TableHeap

class SeqScanExec(Executor):
    def __init__(self, table_heap: TableHeap):
        self.table_heap = table_heap
        self.rows = []
        self.index = 0
        self.loaded = False

    def init(self):
        if not self.loaded:   # 🔥 IMPORTANT
            self.rows = []
            iterator = self.table_heap.iterator()

            seen = set()  # 🔥 avoid duplicates

            while True:
                tup = iterator.get_next()
                if tup is None:
                    break

                key = tuple(sorted(tup.items()))
                if key not in seen:
                    seen.add(key)
                    self.rows.append(tup)

            self.loaded = True

        self.index = 0

    def next(self):
        if self.index >= len(self.rows):
            return None

        tup = self.rows[self.index]
        self.index += 1
        return tup