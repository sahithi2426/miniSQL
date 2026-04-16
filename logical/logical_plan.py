class LogicalPlan:
    def pretty_print(self, indent=""):
        pass

class LogicalCreateTable(LogicalPlan):
    def __init__(self, table, columns, foreign_keys=None, primary_key=None, unique_keys=None):
        self.table = table
        self.columns = columns
        self.foreign_keys = foreign_keys or []
        self.primary_key = primary_key
        self.unique_keys = unique_keys or []

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalCreateTable")
        print(f"{indent}├── Table: {self.table}")
        print(f"{indent}├── Columns: {self.columns}")

        if self.primary_key:
            print(f"{indent}├── PRIMARY KEY: {self.primary_key}")

        if self.unique_keys:
            print(f"{indent}├── UNIQUE: {self.unique_keys}")

        if self.foreign_keys:
            print(f"{indent}└── FOREIGN KEYS: {self.foreign_keys}")

        """if self.predicate.op:
            print(f"{indent}├── Predicate: {self.predicate.left} {self.predicate.op} {self.predicate.right}")
        else:
            print(f"{indent}├── Predicate: {self.predicate.left}")

        print(f"{indent}└── Child:")
        self.child.pretty_print(indent + "    ")"""

class LogicalScan(LogicalPlan):
    def __init__(self, table):
        self.table = table

    def pretty_print(self, indent=""):
        print(f"{indent}└── Table: {self.table}")

class LogicalJoin(LogicalPlan):
    def __init__(self, join_type, left_child, right_child, condition):
        self.join_type = join_type
        self.left_child = left_child
        self.right_child = right_child
        self.condition = condition

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalJoin ({self.join_type})")
        print(f"{indent}├── Condition:")
        if self.condition:
            self.condition.pretty_print(indent + "│   ")
        print(f"{indent}├── Left Child:")
        self.left_child.pretty_print(indent + "│   ")
        print(f"{indent}└── Right Child:")
        self.right_child.pretty_print(indent + "    ")


# class LogicalFilter(LogicalPlan):
#     def __init__(self, predicate, child):
#         self.predicate = predicate
#         self.child = child

#     def pretty_print(self, indent=""):
#         print(f"{indent}LogicalFilter")
#         print(f"{indent}├── Predicate: {self.predicate.column} {self.predicate.op} {self.predicate.value}")
#         print(f"{indent}└── Child:")
#         self.child.pretty_print(indent + "    ")

class LogicalFilter(LogicalPlan):
    def __init__(self, predicate, child):
        self.predicate = predicate
        self.child = child

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalFilter")
        print(f"{indent}├── Predicate:")
        self.predicate.pretty_print(indent + "│   ")
        print(f"{indent}└── Child:")
        self.child.pretty_print(indent + "    ")


class LogicalProject(LogicalPlan):
    def __init__(self, columns, child, required=None):
        self.columns = columns
        self.required = required or set(columns)
        self.child = child

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalProject")
        print(f"{indent}├── Columns: {', '.join(self.columns)}")
        print(f"{indent}└── Child:")
        self.child.pretty_print(indent + "    ")


class LogicalInsert(LogicalPlan):
    def __init__(self, table, values):
        self.table = table
        self.values = values

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalInsert")
        print(f"{indent}├── Table: {self.table}")
        print(f"{indent}└── Values: {self.values}")