from logical.logical_plan import *
from execution.seq_scan import SeqScanExec
from execution.filter import FilterExec
from execution.project import ProjectExec
from execution.nested_loop_join import NestedLoopJoinExec
from execution.insert import InsertExec
from execution.ddl_dml_exec import DeleteExec, UpdateExec, TruncateExec, ShowTablesExec, DropExec, CreateTableExec, DescTableExec 
from execution.groupby import GroupByExec
from execution.orderby import OrderByExec
from execution.limit import LimitExec 

class PhysicalPlanBuilder:
    def __init__(self, catalog, analyzer):
        self.catalog = catalog
        self.analyzer = analyzer

    def build(self, plan):

        if isinstance(plan, LogicalScan):
            table = self.catalog.get_table(plan.table)
            return SeqScanExec(table.heap,table_name=plan.table, alias=plan.alias)

        elif isinstance(plan, LogicalFilter):
            child = self.build(plan.child)
            return FilterExec(child, plan.predicate)

        elif isinstance(plan, LogicalProject):
            child = self.build(plan.child)
            return ProjectExec(child, plan.columns)

        elif isinstance(plan, LogicalCreateTable):
            return CreateTableExec(self.catalog, plan)
            
        elif isinstance(plan, LogicalJoin):
            left = self.build(plan.left_child)
            right = self.build(plan.right_child)
            return NestedLoopJoinExec(left, right, plan.join_type, plan.condition)

        elif isinstance(plan, LogicalInsert):
            table = self.catalog.get_table(plan.table)
            return InsertExec(table.heap, plan.values, list(table.columns.keys()),self.analyzer,plan.table)

        elif isinstance(plan, LogicalDelete):
            return DeleteExec(self.catalog, plan)

        elif isinstance(plan, LogicalUpdate):
            return UpdateExec(self.catalog, plan)

        elif isinstance(plan, LogicalDropTable):
            return DropExec(self.catalog, plan)

        elif isinstance(plan, LogicalTruncate):
            return TruncateExec(self.catalog, plan)

        elif isinstance(plan, LogicalShowTables):
            return ShowTablesExec(self.catalog)
        
        elif isinstance(plan, LogicalDescTable):
            return DescTableExec(self.catalog, plan)
        
        elif isinstance(plan, LogicalGroupBy):
            child = self.build(plan.child)
            return GroupByExec(child, plan.group_cols, plan.aggregates)

        elif isinstance(plan, LogicalHaving):
            child = self.build(plan.child)
            return FilterExec(child, plan.predicate)

        elif isinstance(plan, LogicalOrderBy):
            child = self.build(plan.child)
            return OrderByExec(child, plan.column, plan.order_type)

        elif isinstance(plan, LogicalLimit):
            child = self.build(plan.child)
            return LimitExec(child, plan.limit)
        else:
            raise Exception(f"No executor for {type(plan)}")