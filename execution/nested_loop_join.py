"""
Reference: Database Management Systems (Ramakrishnan & Gehrke) - Chapter 14
Executes a Block Nested Loop Join evaluating the cross-product against a predicate.
"""
from execution.executor import Executor

class NestedLoopJoinExec(Executor):
    def __init__(self, left_child: Executor, right_child: Executor, join_type: str, condition):
        self.left_child = left_child
        self.right_child = right_child
        self.join_type = join_type.upper()   # INNER, LEFT, RIGHT, FULL
        self.condition = condition

        self.left_tuple = None
        self.left_matched = False

        # Cache right side exactly once
        self.right_tuples = []
        self.right_index = 0
        self.matched_right_indices = set()

        # Phase control for RIGHT/FULL unmatched rows
        self.output_unmatched_right = False
        self.unmatched_right_index = 0

    def init(self):
        print("JOIN EXECUTOR INIT CALLED")
        self.left_child.init()
        self.right_child.init()

        self.left_tuple = self.left_child.next()
        self.left_matched = False

        self.right_tuples = []
        while True:
            tup = self.right_child.next()
            if tup is None:
                break
            self.right_tuples.append(tup)

        self.right_index = 0
        self.matched_right_indices = set()
        self.output_unmatched_right = False
        self.unmatched_right_index = 0

    def next(self):
        # Phase 2: emit unmatched right rows for RIGHT/FULL joins
        if self.output_unmatched_right:
            while self.unmatched_right_index < len(self.right_tuples):
                idx = self.unmatched_right_index
                self.unmatched_right_index += 1
                if idx not in self.matched_right_indices:
                    return self._combine(None, self.right_tuples[idx])
            return None

        # Phase 1: normal nested-loop join
        while self.left_tuple is not None:
            while self.right_index < len(self.right_tuples):
                idx = self.right_index
                right_tuple = self.right_tuples[idx]
                self.right_index += 1

                combined = self._combine(self.left_tuple, right_tuple)
                if self._evaluate_condition(combined):
                    self.left_matched = True
                    self.matched_right_indices.add(idx)
                    return combined

            # finished scanning right side for current left tuple
            old_left = self.left_tuple
            had_match = self.left_matched

            self.left_tuple = self.left_child.next()
            self.left_matched = False
            self.right_index = 0

            if not had_match and self.join_type in ("LEFT", "FULL"):
                return self._combine(old_left, None)

        # left side exhausted
        if self.join_type in ("RIGHT", "FULL"):
            self.output_unmatched_right = True
            self.unmatched_right_index = 0
            return self.next()

        return None

    def _combine(self, t1, t2):
        res = {}
        if t1:
            res.update(t1)
        if t2:
            res.update(t2)
        return res

    def _evaluate_condition(self, tup):
        if not self.condition:
            return True

        op = getattr(self.condition, 'op', None)
        if not op:
            return True

        left_col = getattr(self.condition, 'left', None)
        right_col = getattr(self.condition, 'right', None)

        left_val = tup.get(left_col, None)

        # right side can be another column or a literal
        right_val = tup.get(right_col, None)
        if right_val is None and isinstance(right_col, str):
            if right_col.startswith("'") and right_col.endswith("'"):
                right_val = right_col.strip("'")
            elif right_col.isdigit():
                right_val = right_col

        if left_val is None or right_val is None:
            return False

        if op in ('=', '=='):
            return str(left_val) == str(right_val)
        elif op == '!=' or op == '<>':
            return str(left_val) != str(right_val)
        elif op == '<':
            try:
                return float(left_val) < float(right_val)
            except:
                return str(left_val) < str(right_val)
        elif op == '>':
            try:
                return float(left_val) > float(right_val)
            except:
                return str(left_val) > str(right_val)

        return False