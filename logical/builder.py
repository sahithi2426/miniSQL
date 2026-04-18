from parser.ast import Select, Insert, CreateTable, DropTable, Delete, Update, Alter, Truncate, ShowTables, DescTable
from logical.logical_plan import (
    LogicalScan,
    LogicalFilter,
    LogicalProject,
    LogicalInsert,
    LogicalCreateTable,
    LogicalJoin,
    LogicalDropTable,
    LogicalDelete,
    LogicalUpdate,
    LogicalAlter, 
    LogicalTruncate, 
    LogicalShowTables,
    LogicalDescTable,
    LogicalGroupBy,
    LogicalHaving,
    LogicalLimit,
    LogicalOrderBy,
    LogicalPlan
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
        if isinstance(ast, DropTable):
            return LogicalDropTable(ast.table)
        if isinstance(ast, Delete):
            return LogicalDelete(ast.table, ast.where)
        if isinstance(ast, Update):
            return LogicalUpdate(ast.table, ast.updates, ast.where)
        if isinstance(ast, Alter):
            return LogicalAlter(ast.table, ast.action, ast.details)
        if isinstance(ast, Truncate):
            return LogicalTruncate(ast.table)
        if isinstance(ast, ShowTables):
            return LogicalShowTables()
        if isinstance(ast, DescTable):
            return LogicalDescTable(ast.table)
        raise NotImplementedError(
            f"Logical plan not implemented for {type(ast)}"
        )

    def _build_select(self, node):
        plan = LogicalScan(node.table, alias=node.alias)

        if hasattr(node, 'joins') and node.joins:
            for j in node.joins:
                right_plan = LogicalScan(j.table, alias=j.alias)
                plan = LogicalJoin(j.join_type, plan, right_plan, j.condition)

        if node.where:
            plan = LogicalFilter(node.where, plan)
        # GROUP BY + AGGREGATES
        if node.group_by:
            plan = LogicalGroupBy(node.group_by, node.columns, plan)

        # HAVING
        if node.having:
            plan = LogicalHaving(node.having, plan)

        # PROJECT
        plan = LogicalProject(node.columns, plan)

        # ORDER BY
        if node.order_by:
            plan = LogicalOrderBy(node.order_by, node.order_type, plan)

        # LIMIT
        if node.limit:
            plan = LogicalLimit(node.limit, plan)
            
        return plan