class LogicalPlan:
    def pretty_print(self, indent=""):
        pass

class LogicalCreateTable(LogicalPlan):
    def __init__(self, table, columns):
        self.table = table
        self.columns = columns  # list of (name, type)

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalCreateTable")
        print(f"{indent}├── Table: {self.table}")
        print(f"{indent}└── Columns:")
        for name, dtype in self.columns:
            print(f"{indent}    ├── {name} {dtype}")

class LogicalScan(LogicalPlan):
    def __init__(self, table):
        self.table = table

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalScan")
        print(f"{indent}└── Table: {self.table}")


class LogicalFilter(LogicalPlan):
    def __init__(self, predicate, child):
        self.predicate = predicate
        self.child = child

    def pretty_print(self, indent=""):
        print(f"{indent}LogicalFilter")
        print(f"{indent}├── Predicate: {self.predicate.column} {self.predicate.op} {self.predicate.value}")
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