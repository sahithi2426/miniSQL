from parser.ast import Select, Insert, CreateTable
from logical.logical_plan import (
    LogicalScan,
    LogicalFilter,
    LogicalProject,
    LogicalInsert,
    LogicalCreateTable,
    LogicalJoin
)

class LogicalPlanBuilder:
    def build(self, ast):

        if ast is None:
            return None

        if isinstance(ast, Select):
            return self._build_select(ast)

        if isinstance(ast, Insert):
            return LogicalInsert(ast.table, ast.values)

        if isinstance(ast, CreateTable):
            return LogicalCreateTable(ast.name, ast.columns,getattr(ast, "foreign_keys", []),getattr(ast, "primary_key", None),getattr(ast, "unique_keys", []))
        
        raise NotImplementedError(
            f"Logical plan not implemented for {type(ast)}"
        )

    def _build_select(self, node):
        plan = LogicalScan(node.table)

        if hasattr(node, 'joins') and node.joins:
            for j in node.joins:
                right_plan = LogicalScan(j.table)
                plan = LogicalJoin(j.join_type, plan, right_plan, j.condition)

        if node.where:
            plan = LogicalFilter(node.where, plan)

        plan = LogicalProject(node.columns, plan)
        return plan