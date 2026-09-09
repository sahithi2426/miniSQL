from parser.ast import CreateTable, Insert, Select, DropTable, Delete, Update, Alter, Truncate, ShowTables, DescTable

class SemanticAnalyzer:
    def __init__(self, catalog):
        self.catalog = catalog

    def _clean(self, val):
        if val == "NULL":
            return None
        if isinstance(val, str):
            if val.startswith("'") and val.endswith("'"):
                return val[1:-1]
            if val.isdigit():
                return int(val)
        return val

    def analyze(self, ast):
        if isinstance(ast, CreateTable):
            self._analyze_create(ast)
        elif isinstance(ast, Insert):
            self._analyze_insert(ast)
        elif isinstance(ast, Select):
            self._analyze_select(ast)
        elif isinstance(ast, DropTable):
            self._analyze_drop(ast)
        elif isinstance(ast, Delete):
            self._analyze_delete(ast)
        elif isinstance(ast, Update):
            self._analyze_update(ast)
        elif isinstance(ast, Alter):
            self._analyze_alter(ast)
        elif isinstance(ast, Truncate):
            self._analyze_truncate(ast)
        elif isinstance(ast, DescTable):
            self.catalog.get_table(ast.table)
        elif isinstance(ast, ShowTables):
            pass 
        else:
            raise Exception("Unknown AST node")

    def _analyze_create(self, node):
        print("Semantic Catalog ID:", id(self.catalog))
        if node.name in self.catalog.tables:
            if getattr(node,"if_not_exists",False):
                return
            raise Exception(f"Table '{node.name}' already exists.")
        #self.catalog.create_table(node.name, node.columns,node.foreign_keys,node.primary_key,node.unique_keys)

    def _analyze_insert(self, node):
        table = self.catalog.get_table(node.table)

        if len(node.values) != len(table.columns):
            raise Exception("Column count does not match value count")

        # Map column -> value
        col_names = list(table.columns.keys())
        row = {k: self._clean(v) for k, v in zip(col_names, node.values)}

        # ENTITY INTEGRITY (PRIMARY KEY)
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
        # KEY INTEGRITY (UNIQUE)
        for uk in table.unique_keys:
            value = row[uk]

            for r in table.rows:
                if self._clean(r[uk]) == self._clean(value):
                    raise Exception(f"Duplicate UNIQUE value '{value}' for column '{uk}'")

        # Referential integrity check
        for fk_col, ref_table_name, ref_col in table.foreign_keys:

            ref_table = self.catalog.get_table(ref_table_name)
            value = row[fk_col]
            exists = any(r[ref_col] == value for r in ref_table.rows)

            if not exists:
                raise Exception(
                    f"Referential integrity violation: {fk_col}={value} "
                    f"does not exist in {ref_table_name}.{ref_col}"
                )
        print("DEBUG -> inserting row:", row)
        print("DEBUG -> table rows:", table.rows)
        #table.rows.append(row)
        pass

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
                base_col = c.split('.')[-1]
                if c != "*" and base_col not in all_cols:
                    raise Exception(f"Column '{c}' does not exist in any selected tables")

        if node.where:
            self._check_where(node.where, all_cols)

    def _check_where(self, where_node, all_cols):
        if where_node is None:
            return
        if where_node.op in ("AND", "OR"):
            self._check_where(where_node.left, all_cols)
            self._check_where(where_node.right, all_cols)

        elif where_node.op == "NOT":
            self._check_where(where_node.left, all_cols)

        else:
            if isinstance(where_node.left, str):
                column = where_node.left
                base_col = column.split('.')[-1]
                if base_col not in all_cols:
                    raise Exception(f"Column '{column}' does not exist in selected tables")
            
        # also check right side if it's a column
        if isinstance(where_node.right, str):
            right = where_node.right
            base_right = right.split('.')[-1]

            # ignore literals like 'A' or numbers
            if not right.startswith("'") and not right.isdigit():
                if base_right not in all_cols:
                    raise Exception(f"Column '{right}' does not exist in selected tables")
            
    def _analyze_drop(self, node):
         if node.table not in self.catalog.tables:
            if getattr(node, "if_exists", False):
                return
            raise Exception(f"Table '{node.table}' does not exist.")
        #self.catalog.get_table(node.table)

    def _analyze_delete(self, node):
        table = self.catalog.get_table(node.table)
        if node.where:
            self._check_where(node.where, table.columns.keys())

    def _analyze_update(self, node):
        table = self.catalog.get_table(node.table)

        for col, _ in node.updates:
            if col not in table.columns:
                raise Exception(f"Column '{col}' does not exist")

        if node.where:
            self._check_where(node.where, table.columns.keys())

    def _analyze_alter(self, node):
        table = self.catalog.get_table(node.table)

        if node.action == "ADD":
            col, _ = node.details
            if col in table.columns:
                raise Exception(f"Column '{col}' already exists")

        elif node.action == "CHANGE":
            old, new, _ = node.details
            if old not in table.columns:
                raise Exception(f"Column '{old}' does not exist")

        elif node.action == "MODIFY":
            col, _ = node.details
            if col not in table.columns:
                raise Exception(f"Column '{col}' does not exist")

    def _analyze_truncate(self, node):
        self.catalog.get_table(node.table)