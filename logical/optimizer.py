from logical.logical_plan import (
    LogicalScan,
    LogicalFilter,
    LogicalProject,
)

class LogicalOptimizer:
    def optimize(self, plan):
        if not isinstance(plan, (LogicalProject, LogicalFilter, LogicalScan)):
            return plan
        return self._optimize_node(plan)

    def _optimize_node(self, node):
        # Recursively optimize tree

        if isinstance(node, LogicalFilter):
            node.child = self._optimize_node(node.child)
            return node

        if isinstance(node, LogicalProject):
            node.child = self._optimize_node(node.child)
            return self._safe_pushdown(node)

        return node

    # 🔥 Extract all columns used in WHERE condition
    def _extract_columns(self, where_node):
        cols = set()

        if where_node is None:
            return cols

        # Handle AND / OR
        if where_node.op in ("AND", "OR"):
            cols |= self._extract_columns(where_node.left)
            cols |= self._extract_columns(where_node.right)

        # Handle NOT
        elif where_node.op == "NOT":
            cols |= self._extract_columns(where_node.right)

        # Leaf condition (column op value)
        else:
            # left is column name
            if isinstance(where_node.left, str):
                cols.add(where_node.left)

        return cols

    # 🔥 Projection Pushdown Optimization
    def _safe_pushdown(self, project):
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