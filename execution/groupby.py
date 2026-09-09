from execution.executor import Executor

class GroupByExec(Executor):
    def __init__(self, child, group_cols, aggregates):
        self.child = child
        self.group_cols = group_cols      # may be [] for global aggregates
        self.aggregates = aggregates      # list of column names like ["COUNT(*)", "SUM(age)"]

    def _resolve(self, col, row):
        if col in row:
            return row[col]
        short = col.split('.')[-1]
        return row.get(short, None)

    def _get_agg_col(self, agg_expr):
        """Extract the column name inside an aggregate function, e.g. 'age' from 'SUM(age)'."""
        if '(' in agg_expr:
            inner = agg_expr[agg_expr.index('(')+1 : agg_expr.rindex(')')]
            return inner.strip()
        return agg_expr

    def init(self):
        self.child.init()
        self.groups = {}

        while True:
            row = self.child.next()
            if row is None:
                break

            if self.group_cols:
                key = tuple(self._resolve(col, row) for col in self.group_cols)
            else:
                key = ()   # single global group

            if key not in self.groups:
                self.groups[key] = []
            self.groups[key].append(row)

        self.result = []
        for key, rows in self.groups.items():
            agg_row = dict(zip(self.group_cols, key)) if self.group_cols else {}

            for col in self.aggregates:
                col_upper = col.upper()
                if col_upper.startswith("COUNT("):
                    inner = self._get_agg_col(col)
                    if inner == '*':
                        agg_row[col] = len(rows)
                    else:
                        agg_row[col] = sum(1 for r in rows if self._resolve(inner, r) is not None)
                elif col_upper.startswith("SUM("):
                    inner = self._get_agg_col(col)
                    vals = [self._resolve(inner, r) for r in rows if self._resolve(inner, r) is not None]
                    agg_row[col] = sum(float(v) for v in vals) if vals else None
                elif col_upper.startswith("AVG("):
                    inner = self._get_agg_col(col)
                    vals = [self._resolve(inner, r) for r in rows if self._resolve(inner, r) is not None]
                    agg_row[col] = (sum(float(v) for v in vals) / len(vals)) if vals else None
                elif col_upper.startswith("MIN("):
                    inner = self._get_agg_col(col)
                    vals = [self._resolve(inner, r) for r in rows if self._resolve(inner, r) is not None]
                    agg_row[col] = min(vals) if vals else None
                elif col_upper.startswith("MAX("):
                    inner = self._get_agg_col(col)
                    vals = [self._resolve(inner, r) for r in rows if self._resolve(inner, r) is not None]
                    agg_row[col] = max(vals) if vals else None
                else:
                    # non-aggregate column in group result
                    agg_row[col] = self._resolve(col, rows[0]) if rows else None

            self.result.append(agg_row)

        # If no rows at all but aggregates requested, emit one null row
        if not self.result and not self.group_cols:
            agg_row = {}
            for col in self.aggregates:
                col_upper = col.upper()
                if col_upper.startswith("COUNT("):
                    agg_row[col] = 0
                else:
                    agg_row[col] = None
            self.result.append(agg_row)

        self.idx = 0

    def next(self):
        if self.idx >= len(self.result):
            return None
        val = self.result[self.idx]
        self.idx += 1
        return val