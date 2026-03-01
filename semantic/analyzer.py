from parser.ast import CreateTable, Insert, Select

class SemanticAnalyzer:
    def __init__(self, catalog):
        self.catalog = catalog

    def analyze(self, ast):
        if isinstance(ast, CreateTable):
            self._analyze_create(ast)
        elif isinstance(ast, Insert):
            self._analyze_insert(ast)
        elif isinstance(ast, Select):
            self._analyze_select(ast)
        else:
            raise Exception("Unknown AST node")

    def _analyze_create(self, node):
        self.catalog.create_table(node.name, node.columns)

    def _analyze_insert(self, node):
        table = self.catalog.get_table(node.table)

        if len(node.values) != len(table.columns):
            raise Exception("Column count does not match value count")

    def _analyze_select(self, node):
        table = self.catalog.get_table(node.table)

        for col in node.columns:
            if col != "*" and col not in table.columns:
                raise Exception(f"Column '{col}' does not exist in '{table.name}'")

        if node.where:
            if node.where.column not in table.columns:
                raise Exception(
                    f"Column '{node.where.column}' does not exist in '{table.name}'"
                )
