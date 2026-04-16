"""
Reference: Architecture of a Database System (Hellerstein et al.)
Physical Planner module. Transmutes logical operations into executable Volcano Nodes.
"""
import hashlib
from logical.logical_plan import LogicalScan, LogicalFilter, LogicalProject, LogicalInsert, LogicalCreateTable, LogicalJoin
from execution.seq_scan import SeqScanExec
from execution.filter import FilterExec
from execution.project import ProjectExec
from execution.insert import InsertExec
from execution.nested_loop_join import NestedLoopJoinExec
from storage.buffer_pool import BufferPoolManager
from storage.table_heap import TableHeap

class PhysicalPlanBuilder:
    def __init__(self, catalog, buffer_pool: BufferPoolManager):
        self.catalog = catalog
        self.buffer_pool = buffer_pool
        self.tables_heaps = {}

    def get_or_create_heap(self, table_name: str) -> TableHeap:
        if table_name in self.tables_heaps:
            return self.tables_heaps[table_name]

    # Assign unique page ids sequentially
        root_page_id = len(self.tables_heaps) * 1000 + 1

        heap = TableHeap(self.buffer_pool, first_page_id=root_page_id)
        self.tables_heaps[table_name] = heap
        return heap

    def build(self, logical_plan):
        if logical_plan is None:
            return None

        if isinstance(logical_plan, LogicalCreateTable):
            # DDL is usually executed directly, but we can treat as a pass-through
            return None

        if isinstance(logical_plan, LogicalInsert):
            table = self.catalog.get_table(logical_plan.table)
            heap = self.get_or_create_heap(logical_plan.table)
            return InsertExec(heap, logical_plan.values, list(table.columns.keys()))

        if isinstance(logical_plan, LogicalProject):
            child_exec = self.build(logical_plan.child)
            return ProjectExec(child_exec, logical_plan.columns)

        if isinstance(logical_plan, LogicalFilter):
            child_exec = self.build(logical_plan.child)
            return FilterExec(child_exec, logical_plan.predicate)

        if isinstance(logical_plan, LogicalScan):
            heap = self.get_or_create_heap(logical_plan.table)
            return SeqScanExec(heap)

        if isinstance(logical_plan, LogicalJoin):
            left_exec = self.build(logical_plan.left_child)
            right_exec = self.build(logical_plan.right_child)
            return NestedLoopJoinExec(left_exec, right_exec, logical_plan.join_type, logical_plan.condition)

        raise NotImplementedError(f"Physical plan not implemented for {type(logical_plan)}")
