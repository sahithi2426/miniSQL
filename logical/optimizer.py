from logical.logical_plan import (
    LogicalScan,
    LogicalFilter,
    LogicalProject,
    LogicalJoin
)

class LogicalOptimizer:
    def __init__(self, catalog=None):
        self.catalog = catalog

    def optimize(self, plan):
        if not isinstance(plan, (LogicalProject, LogicalFilter, LogicalScan, LogicalJoin)):
            return plan
        return self._optimize_node(plan)

    def _optimize_node(self, node):
        # Recursively optimize tree
        if isinstance(node, LogicalFilter):
            node.child = self._optimize_node(node.child)
            return self._predicate_pushdown(node)

        if isinstance(node, LogicalProject):
            node.child = self._optimize_node(node.child)
            return self._safe_pushdown(node)
            
        if isinstance(node, LogicalJoin):
            node.left_child = self._optimize_node(node.left_child)
            node.right_child = self._optimize_node(node.right_child)
            return self._reorder_join(node)

        return node

    # Cost-Based Optimization: Join Reordering
    def _reorder_join(self, join_node):
        """
        Simple CBO: Reorders join sides based on estimated cardinality.
        Nested Loop Join performs better if the smaller table is the outer (left) loop.
        """
        if not self.catalog:
            return join_node
            
        left_cost = self._estimate_cost(join_node.left_child)
        right_cost = self._estimate_cost(join_node.right_child)
        
        # If right side is smaller and we are doing an INNER join, swap them!
        # Note: We must restrict to INNER joins. Left/Right joins have semantic ordering.
        if join_node.join_type == "INNER" and right_cost < left_cost:
            # Swap left and right
            join_node.left_child, join_node.right_child = join_node.right_child, join_node.left_child
            
        return join_node

    def _estimate_cost(self, node):
        """ Estimates the number of rows a plan node will produce. """
        if isinstance(node, LogicalScan):
            try:
                table = self.catalog.get_table(node.table)
                # Read dummy statistics
                return getattr(table, "estimated_rows", 1000)
            except Exception:
                return 1000
        elif isinstance(node, LogicalFilter):
            # Filtering reduces cardinality (e.g., 33% selectivity assumption)
            return max(1, self._estimate_cost(node.child) // 3)
        elif isinstance(node, LogicalProject):
            return self._estimate_cost(node.child)
        elif isinstance(node, LogicalJoin):
            # Worst case cross product, realistically maybe inner join is smaller
            return self._estimate_cost(node.left_child) * self._estimate_cost(node.right_child) // 10
        return 1000

    # Predicate Pushdown (Rule-Based Optimization)
    def _predicate_pushdown(self, filter_node):
        """ Pushes a filter past a Join to the base tables if possible. """
        child = filter_node.child
        if isinstance(child, LogicalJoin) and child.join_type == "INNER":
            predicate_cols = self._extract_columns(filter_node.predicate)
            
            # Check which tables the predicate columns belong to
            left_tables = self._extract_tables(child.left_child)
            right_tables = self._extract_tables(child.right_child)
            
            # Assuming simple predicates. A full implementation would parse columns like `table.col`
            # Here we do a simplified check: do all predicate columns belong to just ONE side?
            # For MiniSQL, we check table schemas:
            if self.catalog:
                left_has_all = True
                right_has_all = True
                for col in predicate_cols:
                    if not self._column_in_plan(col, child.left_child):
                        left_has_all = False
                    if not self._column_in_plan(col, child.right_child):
                        right_has_all = False
                        
                if left_has_all and not right_has_all:
                    # Push filter to the left child
                    new_filter = LogicalFilter(filter_node.predicate, child.left_child)
                    child.left_child = new_filter
                    return child # Replaced Filter(Join(L, R)) with Join(Filter(L), R)
                    
                if right_has_all and not left_has_all:
                    # Push filter to the right child
                    new_filter = LogicalFilter(filter_node.predicate, child.right_child)
                    child.right_child = new_filter
                    return child
                    
        return filter_node
        
    def _extract_tables(self, plan):
        """ Recursively find all base tables in a logical plan. """
        if isinstance(plan, LogicalScan):
            return {plan.table}
        elif isinstance(plan, (LogicalFilter, LogicalProject)):
            return self._extract_tables(plan.child)
        elif isinstance(plan, LogicalJoin):
            return self._extract_tables(plan.left_child) | self._extract_tables(plan.right_child)
        return set()

    def _column_in_plan(self, col_name, plan):
        """ Checks if a column is available in the schema of a logical plan using the catalog. """
        if not self.catalog: return False
        tables = self._extract_tables(plan)
        for t_name in tables:
            try:
                table = self.catalog.get_table(t_name)
                if col_name in table.columns:
                    return True
            except Exception:
                pass
        return False

    # Extract all columns used in WHERE condition
    def _extract_columns(self, where_node):
        cols = set()

        if where_node is None:
            return cols

        # Handle AND / OR
        if getattr(where_node, "op", None) in ("AND", "OR"):
            cols |= self._extract_columns(where_node.left)
            cols |= self._extract_columns(where_node.right)

        # Handle NOT
        elif getattr(where_node, "op", None) == "NOT":
            cols |= self._extract_columns(where_node.left)

        # Leaf condition (column op value)
        else:
            # left is column name
            if hasattr(where_node, "left") and isinstance(where_node.left, str):
                cols.add(where_node.left)

        return cols

    # Projection Pushdown Optimization
    def _safe_pushdown(self, project):
        if project.columns == ["*"]:
            return project

        if isinstance(project.child, LogicalFilter):
            filter_node = project.child

            # Extract columns needed for filter
            predicate_cols = self._extract_columns(filter_node.predicate)

            # Combine SELECT columns + WHERE columns
            required = set(project.columns) | predicate_cols

            # Create new Project below Filter
            new_project = LogicalProject(
                columns=list(required),
                child=filter_node.child,
            )

            # Return reordered plan: Filter → Project
            return LogicalFilter(filter_node.predicate, new_project)

        return project