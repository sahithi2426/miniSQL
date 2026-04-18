from execution.executor import Executor

class OrderByExec(Executor):
    def __init__(self, child, col, order_type):
        self.child = child
        self.col = col
        self.order_type = order_type

    def init(self):
        self.child.init()
        self.rows = []

        while True:
            row = self.child.next()
            if row is None:
                break
            self.rows.append(row)

        reverse = self.order_type == "DESC"
        self.rows.sort(key=lambda x: x.get(self.col), reverse=reverse)

        self.idx = 0

    def next(self):
        if self.idx >= len(self.rows):
            return None
        val = self.rows[self.idx]
        self.idx += 1
        return val