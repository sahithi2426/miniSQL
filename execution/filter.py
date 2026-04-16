from execution.executor import Executor

class FilterExec(Executor):
    def __init__(self, child: Executor, predicate):
        self.child = child
        self.predicate = predicate

    def init(self):
        self.child.init()

    def next(self):
        while True:
            tup = self.child.next()
            if tup is None:
                return None
            
            if self._evaluate_predicate(tup):
                return tup

    def _evaluate_predicate(self, tup):
        if not self.predicate:
            return True
            
        op = getattr(self.predicate, 'op', None)
        if not op:
            return True
            
        left_col = getattr(self.predicate, 'left', None)
        right_val = getattr(self.predicate, 'right', None)
        
        if left_col not in tup:
            return False
            
        left_val = tup[left_col]
        
        # Strip quotes for string comparison
        if isinstance(right_val, str) and right_val.startswith("'"):
            right_val = right_val.strip("'")
            
        if op == '=' or op == '==':
            return str(left_val) == str(right_val)
        elif op == '>':
            return float(left_val) > float(right_val)
        elif op == '<':
            return float(left_val) < float(right_val)
        elif op == '!=' or op == '<>':
            return str(left_val) != str(right_val)
            
        return False
