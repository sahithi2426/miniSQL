from execution.executor import Executor

class ProjectExec(Executor):
    def __init__(self, child: Executor, columns: list):
        self.child = child
        self.columns = columns

    def init(self):
        self.child.init()


    def _resolve(self, col, tup):
        # direct match (BEST case)
        if col in tup:
            return tup[col]

        short = col.split('.')[-1]

        # find matching column
        matches = [tup[k] for k in tup if k.endswith("." + short)]

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            # ambiguous (for now pick first)
            return matches[0]

        return None
    def next(self):
        tup = self.child.next()
        if tup is None:
            return None

        if self.columns == ["*"]:
            return tup

        proj = {}

        for col in self.columns:
            if not isinstance(col, str):
                continue

            val = self._resolve(col, tup)

            # keep original column name (o.id, c.name)
            proj[col] = val

        return proj