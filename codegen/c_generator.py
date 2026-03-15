from logical.logical_plan import (
    LogicalCreateTable,
    LogicalInsert,
    LogicalScan,
    LogicalFilter,
    LogicalProject
)

from codegen.templates import *

class CCodeGenerator:
    def __init__(self):
        self.tables = {}
        self.inserts = {}
        self.code = ""

    def generate(self, logical_plan):

        self.code = ""
        self.code += C_HEADER

        if hasattr(self, "catalog"):
            self.tables = {}
            for tname, table in self.catalog.tables.items():
                cols = []
                for cname, ctype in table.columns.items():
                    cols.append((cname, ctype))
                self.tables[tname] = cols

        if isinstance(logical_plan, LogicalCreateTable):
            self._generate_create(logical_plan)

        elif isinstance(logical_plan, LogicalInsert):
            self._generate_insert(logical_plan)

        elif isinstance(logical_plan, LogicalProject):
            self._generate_select(logical_plan)

        return self.code

    def _generate_create(self, node):
        self.tables[node.table] = node.columns

        fields = []

        for col, dtype in node.columns:

            if dtype.name == "INT":
                fields.append(f"    int {col};")
            else:
                fields.append(f"    char {col}[100];")

        fields = "\n".join(fields)

        struct_code = TABLE_STRUCT_TEMPLATE.format(
            table_name=node.table,
            fields=fields
        )

        self.code += struct_code

        if node.table not in self.inserts:
            self.inserts[node.table] = []

    def _generate_insert(self, node):

        values = []

        for v in node.values:
            if isinstance(v, str) and v.startswith("'"):
                values.append(v.replace("'", '"'))
            else:
                values.append(str(v))

        row = ROW_TEMPLATE.format(values=", ".join(values))

        if node.table not in self.inserts:
            self.inserts[node.table] = []

        self.inserts[node.table].append(row)

        rows = ",\n".join(self.inserts[node.table])

        table_data = TABLE_DATA_TEMPLATE.format(
            table_name=node.table,
            rows=rows
        )

        row_count = ROW_COUNT_TEMPLATE.format(
            table_name=node.table
        )

        self.code += table_data
        self.code += row_count

    def _generate_condition(self, where_node, table):
        if where_node.op in ("AND", "OR"):
            left_code = self._generate_condition(where_node.left, table)
            right_code = self._generate_condition(where_node.right, table)
            op_c = "&&" if where_node.op == "AND" else "||"
            return f"({left_code} {op_c} {right_code})"
        elif where_node.op == "NOT":
            right_code = self._generate_condition(where_node.right, table)
            return f"(!{right_code})"
        else:
            column = where_node.left
            op = where_node.op
            value = where_node.right

            if op == "=":
                op = "=="

            dtype_name = ""
            for c, t in self.tables[table]:
                if c == column:
                    dtype_name = t.name

            if dtype_name == "TEXT":
                c_val = value.replace("'", '"')
                if op == "==":
                    return f'(strcmp({table}_data[i].{column}, {c_val}) == 0)'
                elif op == "!=" or op == "<>":
                    return f'(strcmp({table}_data[i].{column}, {c_val}) != 0)'
                else:
                    raise Exception(f"Unsupported string operator {op}")
            else:
                return f"({table}_data[i].{column} {op} {value})"

    def _generate_select(self, node):

        child = node.child

        if child.__class__.__name__ == "LogicalFilter":
            table = child.child.table
        else:
            table = child.table

        fields = []
        for col, dtype in self.tables[table]:
            if dtype.name == "INT":
                fields.append(f"    int {col};")
            else:
                fields.append(f"    char {col}[100];")

        struct_code = TABLE_STRUCT_TEMPLATE.format(
            table_name=table,
            fields="\n".join(fields)
        )

        self.code += struct_code

        rows = []
        if table in self.inserts:
            rows = self.inserts[table]

        rows_str = ",\n".join(rows)

        table_data = TABLE_DATA_TEMPLATE.format(
            table_name=table,
            rows=rows_str
        )

        row_count = ROW_COUNT_TEMPLATE.format(
            table_name=table
        )

        self.code += table_data
        self.code += row_count

        self.code += MAIN_START

        self.code += SCAN_LOOP_START.format(
            table_name=table
        )

        if child.__class__.__name__ == "LogicalFilter":

            cond_code = self._generate_condition(child.predicate, table)

            self.code += FILTER_TEMPLATE.format(
                condition=cond_code
            )

            self._generate_projection(node.columns, table)

            self.code += FILTER_END

        else:
            self._generate_projection(node.columns, table)

        self.code += SCAN_LOOP_END

        self.code += MAIN_END

    def _generate_projection(self, columns, table):

        for col in columns:

            if col == "*":

                for c, dtype in self.tables[table]:

                    if dtype.name == "INT":
                        self.code += PRINT_INT_TEMPLATE.format(
                            table_name=table,
                            column=c
                        )

                    else:
                        self.code += PRINT_TEXT_TEMPLATE.format(
                            table_name=table,
                            column=c
                        )

            else:

                for c, dtype in self.tables[table]:

                    if c == col:

                        if dtype.name == "INT":
                            self.code += PRINT_INT_TEMPLATE.format(
                                table_name=table,
                                column=c
                            )

                        else:
                            self.code += PRINT_TEXT_TEMPLATE.format(
                                table_name=table,
                                column=c
                            )

        self.code += PRINT_NEWLINE