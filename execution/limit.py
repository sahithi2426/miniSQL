from execution.executor import Executor

class LimitExec(Executor):
    def __init__(self, child, limit):
        self.child = child
        self.limit = int(limit)
        self.count = 0

    def init(self):
        self.child.init()
        self.count = 0

    def next(self):
        if self.count >= self.limit:
            return None

        val = self.child.next()
        if val is None:
            return None

        self.count += 1
        return val