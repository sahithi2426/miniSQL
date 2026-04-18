from execution.executor import Executor

class ProjectExec(Executor):
    def __init__(self, child: Executor, columns: list):
        self.child = child
        self.columns = columns

    def init(self):
        self.child.init()

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

            # HANDLE alias.column
            if "." in col:
                alias, field = col.split(".", 1)

                if alias == "o":
                    key = f"left.{field}"
                    if key in tup:
                        proj[field] = tup[key]

                elif alias == "c":
                    key = f"right.{field}"
                    if key in tup:
                        proj[field] = tup[key]

            # fallback (no alias)
            elif col in tup:
                proj[col] = tup[col]
            else:
                short = col.split('.')[-1]
                for k in tup:
                    if k.endswith("." + short):
                        proj[short] = tup[k]

        return proj