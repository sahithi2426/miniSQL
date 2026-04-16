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
        self.catalog.create_table(node.name, node.columns,node.foreign_keys,node.primary_key,node.unique_keys)

    def _analyze_insert(self, node):
        table = self.catalog.get_table(node.table)

        if len(node.values) != len(table.columns):
            raise Exception("Column count does not match value count")

        # Map column -> value
        col_names = list(table.columns.keys())
        row = dict(zip(col_names, node.values))

        # 🔹 ENTITY INTEGRITY (PRIMARY KEY)
        if table.primary_key:
            pk = table.primary_key
            value = row[pk]

            # NOT NULL check
            if value is None or value == "NULL":
                raise Exception(f"PRIMARY KEY '{pk}' cannot be NULL")

            # UNIQUE check
            for r in table.rows:
                if r[pk] == value:
                    raise Exception(f"Duplicate PRIMARY KEY value '{value}'")
        # 🔹 KEY INTEGRITY (UNIQUE)
        for uk in table.unique_keys:
            value = row[uk]

            for r in table.rows:
                if r[uk] == value:
                    raise Exception(f"Duplicate UNIQUE value '{value}' for column '{uk}'")

        # 🔥 Referential integrity check
        for fk_col, ref_table_name, ref_col in table.foreign_keys:

            ref_table = self.catalog.get_table(ref_table_name)
            value = row[fk_col]
            exists = any(r[ref_col] == value for r in ref_table.rows)

            if not exists:
                raise Exception(
                    f"Referential integrity violation: {fk_col}={value} "
                    f"does not exist in {ref_table_name}.{ref_col}"
                )
        print("DEBUG → inserting row:", row)
        print("DEBUG → table rows:", table.rows)
        table.rows.append(row)

    # def _analyze_select(self, node):
    #     table = self.catalog.get_table(node.table)

    #     for col in node.columns:
    #         if col != "*" and col not in table.columns:
    #             raise Exception(f"Column '{col}' does not exist in '{table.name}'")

    #     if node.where:
    #         if node.where.column not in table.columns:
    #             raise Exception(
    #                 f"Column '{node.where.column}' does not exist in '{table.name}'"
    #             )
    # Replace the _analyze_select function in semantic/analyzer.py with this version

    def _analyze_select(self, node):

        tables = [self.catalog.get_table(node.table)]
        if hasattr(node, 'joins') and node.joins:
            for j in node.joins:
                tables.append(self.catalog.get_table(j.table))
                
        all_cols = set()
        for t in tables:
            all_cols.update(t.columns.keys())

        if node.columns != ["*"]:
            for col in node.columns:
                c = col.split('(')[1].strip(')') if '(' in col else col
                if c != "*" and c not in all_cols:
                    raise Exception(f"Column '{c}' does not exist in any selected tables")

        if node.where:
            self._check_where(node.where, all_cols)

    def _check_where(self, where_node, all_cols):
        if where_node.op in ("AND", "OR"):
            self._check_where(where_node.left, all_cols)
            self._check_where(where_node.right, all_cols)

        elif where_node.left == "NOT":
            self._check_where(where_node.right, all_cols)

        else:
            column = where_node.left
            if column not in all_cols:
                raise Exception(f"Column '{column}' does not exist in selected tables")