from execution.executor import Executor
from parser.ast import Where
from parser.ast import BinaryOp, UnaryOp, Literal, Column

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

        # 2. Handle alias.column → column
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
        if val is None:
            return None

        if isinstance(val, str):
            if val.startswith("'") and val.endswith("'"):
                val = val.strip("'")

            try:
                return int(val)
            except:
                try:
                    return float(val)
                except:
                    return val

        return val

    def _eval_node(self, node, tup):
        #print("ENTERING EVAL NODE")
        if node is None:
            return True
        if isinstance(node, Literal):
            return node.value
        #op = getattr(node, 'op', None)
        if isinstance(node, str):
            if node.startswith("'") and node.endswith("'"):
                return node.strip("'")
            return self._resolve(node, tup)
        #  NEW EXPRESSION HANDLING
        #print("DEBUG:", op, node.left, node.right)
        if isinstance(node, BinaryOp):
            left = self._eval_node(node.left, tup)
            right = self._eval_node(node.right, tup)

            left = self._normalize(left)
            right = self._normalize(right)

            if node.op == '+': return left + right
            if node.op == '-': return left - right
            if node.op == '*': return left * right
            if node.op == '/':
                if right == 0:
                    raise Exception("Division by zero")
                return left / right
            if node.op == '%': return left % right

            if left is None or right is None:
                return False
            if node.op == '=': return left == right
            if node.op == '!=': return left != right
            if node.op == '>': return left > right
            if node.op == '<': return left < right
            if node.op == '>=': return left >= right
            if node.op == '<=': return left <= right

            if node.op == 'AND':
                return bool(left) and bool(right)

            if node.op == 'OR':
                return bool(left) or bool(right)

            if node.op == 'LIKE':
                pattern = right
                value = left

                if pattern is None or value is None:
                    return False

                pattern = str(pattern)
                value = str(value)

                if pattern.startswith('%') and pattern.endswith('%'):
                    return pattern[1:-1] in value
                elif pattern.endswith('%'):
                    return value.startswith(pattern[:-1])
                elif pattern.startswith('%'):
                    return value.endswith(pattern[1:])
                else:
                    return value == pattern

            if node.op == "IS NULL":
                return left is None

            if node.op == "IS NOT NULL":
                return left is not None

            return False
        # Unary (NOT)
        if isinstance(node, UnaryOp):
            val = self._eval_node(node.operand, tup)
            return not val

        if not hasattr(node, "op"):
            return node

        op = node.op
        # 1. Handle Logical Operators (AND, OR, NOT)
        if op == "AND":
            return self._eval_node(node.left, tup) and self._eval_node(node.right, tup)

        if op == "OR":
            return self._eval_node(node.left, tup) or self._eval_node(node.right, tup)

        if op == "NOT":
            # NOT usually wraps the condition in 'left'
            target = node.left if node.left is not None else node.right
            return not self._eval_node(target, tup)

        # 2. Handle Comparisons (Basic Predicates)
        # We check if 'op' is a comparison operator
        if op in ('=', '==', '>', '<', '!=', '<>', '>=', '<='):
            left_val = self._eval_node(node.left, tup) if isinstance(node.left, Where) else self._resolve(node.left, tup)

            if left_val is None and not isinstance(node.left, Where):
                left_val = node.left # Fallback to literal if not a column

            # Resolve Right side
            right_val = self._eval_node(node.right, tup) if isinstance(node.right, Where) else self._resolve(node.right, tup)
            if right_val is None and not isinstance(node.right, Where):
                right_val = node.right

            # Normalize both sides (handle types like '1' vs 1)
            left_val = self._normalize(left_val)
            right_val = self._normalize(right_val)

            if left_val is None or right_val is None:
                return False
            # Perform comparison
            if op in ('=', '=='):
                if left_val is None or right_val is None:
                    return False
                return left_val == right_val
            elif op == '>':
                if left_val is None or right_val is None:
                    return False
                return left_val > right_val
            elif op == '<':
                if left_val is None or right_val is None:
                    return False
                return left_val < right_val
            elif op in ('!=', '<>'):
                if left_val is None or right_val is None:
                    return False
                return left_val != right_val
            elif op == '>=':
                if left_val is None or right_val is None:
                    return False
                return left_val >= right_val
            elif op == '<=':
                if left_val is None or right_val is None:
                    return False
                return left_val <= right_val

        # Fallback for unexpected node structures
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


