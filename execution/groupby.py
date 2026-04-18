from execution.executor import Executor

class GroupByExec(Executor):
    def __init__(self, child, group_cols, aggregates):
        self.child = child
        self.group_cols = group_cols
        self.aggregates = aggregates

    def _resolve(self, col, row):
        if col in row:
            return row[col]
        short = col.split('.')[-1]
        return row.get(short, None)
    
    def init(self):
        self.child.init()
        self.groups = {}

        while True:
            row = self.child.next()
            if row is None:
                break

            key = tuple(self._resolve(col, row) for col in self.group_cols)

            if key not in self.groups:
                self.groups[key] = []

            self.groups[key].append(row)

        self.result = []
        for key, rows in self.groups.items():
            agg_row = dict(zip(self.group_cols, key))

            for col in self.aggregates:
                if col.startswith("COUNT("):
                    agg_row[col] = len(rows)

            self.result.append(agg_row)

        self.idx = 0

    def next(self):
        if self.idx >= len(self.result):
            return None
        val = self.result[self.idx]
        self.idx += 1
        return val