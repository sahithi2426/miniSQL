"""
Reference: Database Management Systems (Ramakrishnan & Gehrke) - Chapter 14
Executes a Block Nested Loop Join evaluating the cross-product against a predicate.
"""
from execution.executor import Executor

class NestedLoopJoinExec(Executor):
    def __init__(self, left_child: Executor, right_child: Executor, join_type: str, condition, left_table,right_table):
        self.left_child = left_child
        self.right_child = right_child
        self.join_type = join_type.upper()   # INNER, LEFT, RIGHT, FULL
        self.condition = condition

        self.left_tuple = None
        self.left_matched = False
        self.left_table = left_table
        self.right_table = right_table
        # Cache right side exactly once
        self.right_tuples = []
        self.right_index = 0
        self.matched_right_indices = set()

        # Phase control for RIGHT/FULL unmatched rows
        self.output_unmatched_right = False
        self.unmatched_right_index = 0

    def init(self):
        #print("JOIN EXECUTOR INIT CALLED")
        self.left_child.init()
        self.right_child.init()

        self.left_tuple = self.left_child.next()
        self.left_columns = list(self.left_tuple.keys()) if self.left_tuple else []
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
        # left table
        if t1:
            for k, v in t1.items():
                res[k] = v
                res[f"{self.left_table}.{k}"] = v
                #res[k] = v   # optional (helps SELECT *)
        else:
            for k in self.left_columns:
                res[f"left.{k}"] = None
        # right table
        if t2:
            for k, v in t2.items():
                res[k] = v
                res[f"{self.right_table}.{k}"] = v
        else:
        # CRITICAL FIX: add NULLs for right columns
            if self.right_tuples:
                sample = self.right_tuples[0]
                for k in sample.keys():
                    res[f"right.{k}"] = None

        return res

    """def _get_value(self, col, tup):
        if col is None or tup is None:
            return None
        if col in tup:
            return tup[col]

        short = col.split('.')[-1]

        for k in tup:
            if k.endswith("." + short):
                return tup[k]

        return None"""
    def _get_value(self, col, tup):
        if col is None or tup is None:
            return None

        # direct match
        if col in tup:
            return tup[col]

        parts = col.split('.')

        # CASE 1: table.column OR alias.column
        if len(parts) == 2:
            alias_or_table, column = parts

            # try exact match first
            key1 = f"{alias_or_table}.{column}"
            if key1 in tup:
                return tup[key1]

            # fallback: match column name safely
            for k in tup:
                if k.endswith("." + column):
                    return tup[k]

        # CASE 2: only column name
        if len(parts) == 1:
            column = parts[0]

            matches = [tup[k] for k in tup if k.endswith("." + column)]

            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                # ambiguous column (real SQL would throw error)
                return matches[0]

        return None


    def _normalize(self, val):
        if isinstance(val, str):
            if val.isdigit():
                return int(val)
        return val

    def _evaluate_condition(self, tup):
        if not self.condition:
            return True

        op = getattr(self.condition, 'op', None)
        if not op:
            return True

        left_col = getattr(self.condition, 'left', None)
        right_col = getattr(self.condition, 'right', None)

        left_val = self._get_value(left_col, tup)

        # right side can be another column or a literal
        right_val = self._get_value(right_col, tup)
        if right_val is None and isinstance(right_col, str):
            if right_col.startswith("'") and right_col.endswith("'"):
                right_val = right_col.strip("'")
            elif right_col.isdigit():
                right_val = right_col

        if left_val is None or right_val is None:
            return False

        left_val = self._normalize(left_val)
        right_val = self._normalize(right_val)

        if op in ('=', '=='):
            return left_val == right_val
        elif op == '!=' or op == '<>':
            return left_val != right_val
        elif op == '<':
            try:
                return left_val < right_val
            except:
                return left_val < right_val
        elif op == '>':
            try:
                return left_val > right_val
            except:
                return left_val > right_val

        return False