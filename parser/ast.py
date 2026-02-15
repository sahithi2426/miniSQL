class CreateTable:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns

    def __repr__(self):
        return f"CreateTable({self.name}, {self.columns})"

class Insert:
    def __init__(self, table, values):
        self.table = table
        self.values = values

    def __repr__(self):
        return f"Insert({self.table}, {self.values})"

class Select:
    def __init__(self, columns, table, where):
        self.columns = columns
        self.table = table
        self.where = where

    def __repr__(self):
        return f"Select({self.columns}, {self.table}, {self.where})"

class Where:
    def __init__(self, column, op, value):
        self.column = column
        self.op = op
        self.value = value

    def __repr__(self):
        return f"Where({self.column} {self.op} {self.value})"
