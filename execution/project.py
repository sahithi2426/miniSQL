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
        
        if self.columns == ['*']:
            return tup
            
        proj = {}
        for col in self.columns:
            if col in tup:
                proj[col] = tup[col]
        return proj
