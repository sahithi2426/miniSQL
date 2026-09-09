from execution.executor import Executor
from parser.ast import Where

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

    def _resolve(self, col, row):
        #print("DEBUG RESOLVE TYPE:", type(col), col)
        if col is None:
            return None

        if not isinstance(col, str):
            return col

        # 1. Exact match
        if col in row:
            return row[col]

        # 2. Handle alias.column -> column
        short = col.split('.')[-1]

        if short in row:
            return row[short]

        # 3. Handle full names like Orders.customer_id
        for k in row:
            if k.endswith("." + short):
                return row[k]

        return None
    
    def _evaluate_predicate(self, tup):
        if not self.predicate:
            return True

        return self._eval_node(self.predicate, tup)
    
    def _normalize(self, val):
        if isinstance(val, str) and val.startswith("'"):
            return val.strip("'")
        try:
            return int(val)
        except:
            try:
                return float(val)
            except:
                return val

    def _eval_node(self, node, tup):
        if node is None:
            return True

        # Handle Literal values directly
        from parser.ast import Literal, BinaryOp
        if isinstance(node, Literal):
            return node.value

        # Duck-type: any node with .op, .left, .right (Where or BinaryOp)
        if not hasattr(node, 'op'):
            # Plain string/int — treat as literal
            return node

        op = node.op
        left = node.left
        right = node.right

        # 1. Logical Operators
        if op == "AND":
            return self._eval_node(left, tup) and self._eval_node(right, tup)
        if op == "OR":
            return self._eval_node(left, tup) or self._eval_node(right, tup)
        if op == "NOT":
            target = left if left is not None else right
            return not self._eval_node(target, tup)

        # 2. Comparison Operators
        if op in ('=', '==', '>', '<', '!=', '<>', '>=', '<=', 'LIKE', 'IS NULL'):
            # Resolve left side
            if hasattr(left, 'op') or isinstance(left, Literal):
                left_val = self._eval_node(left, tup)
            else:
                left_val = self._resolve(left, tup)
                if left_val is None:
                    left_val = left  # fallback to literal

            # Resolve right side
            if hasattr(right, 'op') or isinstance(right, Literal):
                right_val = self._eval_node(right, tup)
            else:
                right_val = self._resolve(right, tup)
                if right_val is None:
                    right_val = right  # fallback to literal

            # Normalize types
            left_val = self._normalize(left_val)
            right_val = self._normalize(right_val)

            if op == 'IS NULL':
                return left_val is None
            if left_val is None or right_val is None:
                return False

            if op in ('=', '=='):
                return left_val == right_val
            elif op == '>':
                return left_val > right_val
            elif op == '<':
                return left_val < right_val
            elif op in ('!=', '<>'):
                return left_val != right_val
            elif op == '>=':
                return left_val >= right_val
            elif op == '<=':
                return left_val <= right_val
            elif op == 'LIKE':
                import re
                pattern = str(right_val).replace('%', '.*').replace('_', '.')
                return bool(re.fullmatch(pattern, str(left_val), re.IGNORECASE))

        return False
    """def _eval_node(self, node, tup):
            if node is None:
                return True

            op = getattr(node, 'op', None)

            print("DEBUG:", op, node.left, node.right)

            # -------------------------
            # LOGICAL OPERATORS
            # -------------------------
            if op == "AND":
                return self._eval_node(node.left, tup) and self._eval_node(node.right, tup)

            if op == "OR":
                return self._eval_node(node.left, tup) or self._eval_node(node.right, tup)

            if op == "NOT":
                return not self._eval_node(node.left, tup)

            # -------------------------
            # BASE COMPARISON
            # -------------------------
            if isinstance(node.left, str):

                left_col = node.left
                right_val = node.right

                left_val = self._resolve(left_col, tup)

                # column vs literal
                if isinstance(right_val, str) and not right_val.startswith("'") and not right_val.isdigit():
                    right_val_final = self._resolve(right_val, tup)
                else:
                    right_val_final = right_val

                left_val = self._normalize(left_val)
                right_val_final = self._normalize(right_val_final)

                if left_val is None:
                    return False

                # 🔥 IMPORTANT: RETURN VALUES HERE
                if op in ('=', '=='):
                    return left_val == right_val_final

                elif op == '>':
                    return left_val > right_val_final

                elif op == '<':
                    return left_val < right_val_final

                elif op in ('!=', '<>'):
                    return left_val != right_val_final

            # ❗ fallback
            return False"""


