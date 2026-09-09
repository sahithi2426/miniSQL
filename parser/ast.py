class DescTable:
    def __init__(self, table):
        self.table = table

class CreateTable:
    def __init__(self, name, columns,foreign_keys=None,primary_key=None,unique_keys=None, if_not_exists=False):
        self.name = name
        self.columns = columns
        self.foreign_keys=foreign_keys or []
        self.primary_key = primary_key
        self.unique_keys = unique_keys or []
        self.if_not_exists = if_not_exists

    def pretty_print(self):
        print("CREATE TABLE")
        print("├── Name:", self.name)
        print("└── Columns")
        for i, (col_name, col_type) in enumerate(self.columns):
            connector = "└──" if i == len(self.columns) - 1 else "├──"
            print(f"    {connector} {col_name} ({col_type.name})")


class Insert:
    def __init__(self, table, values):
        self.table = table
        self.values = values

    def pretty_print(self):
        print("INSERT")
        print("├── Table:", self.table)
        print("└── Values")
        for i, val in enumerate(self.values):
            connector = "└──" if i == len(self.values) - 1 else "├──"
            print(f"    {connector} {val}")


class Select:
    def __init__(self, columns, table,alias, where=None,
                 group_by=None, having=None, order_by=None,
                 order_type=None, limit=None, joins=None):
        self.columns = columns
        self.table = table
        self.alias = alias
        self.joins = joins or []
        self.where = where
        self.group_by = group_by
        self.having = having
        self.order_by = order_by
        self.order_type = order_type
        self.limit = limit

    def pretty_print(self):
        print("SELECT")
        print("├── Columns:", ", ".join(self.columns))
        print("├── Table:", self.table)

        if self.where:
            print("├── WHERE")
            self.where.pretty_print("│   ")

        if self.group_by:
            print("├── GROUP BY:", self.group_by)
            
        if self.having:
            print("├── HAVING")
            self.having.pretty_print("│   ")

        if self.order_by:
            print("├── ORDER BY:", self.order_by,
                  self.order_type if self.order_type else "")

        if self.limit:
            print("└── LIMIT:", self.limit)
            
        if self.joins:
            print("└── JOINS")
            for join in self.joins:
                join.pretty_print("    ")

class Join:
    def __init__(self, join_type, table, condition, alias=None):
        self.join_type = join_type
        self.table = table
        self.condition = condition
        self.alias = alias

    def pretty_print(self, indent=""):
        print(f"{indent}├── {self.join_type} JOIN {self.table} ON")
        if self.condition:
            self.condition.pretty_print(indent + "│   ")
        else:
            print(f"{indent}│   (no condition)")

class Where:
    def __init__(self, left, op=None, right=None):
        self.left = left
        self.op = op
        self.right = right

    def pretty_print(self, indent=""):
        if isinstance(self.left, Where):
            self.left.pretty_print(indent + "  ")
        else:
            print(f"{indent}├── {self.left}")

        if self.op:
            print(f"{indent}├── {self.op}")

        if isinstance(self.right, Where):
            self.right.pretty_print(indent + "  ")
        elif self.right is not None:
            print(f"{indent}└── {self.right}")

    def __str__(self):
        if self.op:
            return f"({self.left} {self.op} {self.right})"
        return str(self.left)

class DropTable:
    def __init__(self, table, if_exists=False):
        self.table = table
        self.if_exists = if_exists

class Delete:
    def __init__(self, table, where=None):
        self.table = table
        self.where = where

class Update:
    def __init__(self, table, updates, where=None):
        self.table = table
        self.updates = updates  # list of (col, val)
        self.where = where

class Alter:
    def __init__(self, table, action, details):
        self.table = table
        self.action = action  # ADD / CHANGE / MODIFY
        self.details = details

class Truncate:
    def __init__(self, table):
        self.table = table

class ShowTables:
    pass

class Expr:
    pass

class BinaryOp(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

    def __repr__(self):
        return self.__str__()

    def pretty_print(self, indent=""):
        # Left child
        if hasattr(self.left, 'pretty_print'):
            self.left.pretty_print(indent + "  ")
        else:
            print(f"{indent}\u251c\u2500\u2500 {self.left}")
        # Operator
        print(f"{indent}\u251c\u2500\u2500 {self.op}")
        # Right child
        if hasattr(self.right, 'pretty_print'):
            self.right.pretty_print(indent + "  ")
        else:
            print(f"{indent}\u2514\u2500\u2500 {self.right}")

class UnaryOp(Expr):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __str__(self):
        return f"({self.op} {self.operand})"

    def __repr__(self):
        return self.__str__()

    def pretty_print(self, indent=""):
        print(f"{indent}\u251c\u2500\u2500 {self.op}")
        if hasattr(self.operand, 'pretty_print'):
            self.operand.pretty_print(indent + "  ")
        else:
            print(f"{indent}\u2514\u2500\u2500 {self.operand}")

class Literal(Expr):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def pretty_print(self, indent=""):
        print(f"{indent}\u2514\u2500\u2500 {self.value}")

class Column(Expr):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def pretty_print(self, indent=""):
        print(f"{indent}\u251c\u2500\u2500 {self.name}")