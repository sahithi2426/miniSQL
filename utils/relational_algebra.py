def predicate_to_string(pred):
    if pred is None:
        return ""

    # -------------------------
    # NOT
    # -------------------------
    if hasattr(pred, "op") and pred.op == "NOT":
        return f"NOT ({predicate_to_string(pred.left)})"

    # -------------------------
    # AND / OR (recursive case)
    # -------------------------
    if hasattr(pred, "left") and hasattr(pred, "op") and hasattr(pred, "right"):
        left = pred.left
        right = pred.right

        # If nested condition -> recurse
        if hasattr(left, "op"):
            left = predicate_to_string(left)
        if hasattr(right, "op"):
            right = predicate_to_string(right)

        return f"({left} {pred.op} {right})"

    # -------------------------
    # Base case (simple condition)
    # -------------------------
    if hasattr(pred, "left") and hasattr(pred, "op") and hasattr(pred, "right"):
        return f"{pred.left} {pred.op} {pred.right}"

    return str(pred)

def dml_ddl_to_ra(plan):
    node = plan.__class__.__name__

    # -------------------------
    # CREATE TABLE
    # -------------------------
    if node == "LogicalCreateTable":
        cols = ", ".join([c[0] if isinstance(c, (list, tuple)) else str(c)
                          for c in plan.columns])
        return f"{plan.table}({cols})"

    # -------------------------
    # INSERT
    # -------------------------
    elif node == "LogicalInsert":
        # values like [(3, 102)] or [3, 102]
        vals = plan.values
        if isinstance(vals, list) and vals and not isinstance(vals[0], (list, tuple)):
            vals = [vals]

        tuples = ", ".join("(" + ", ".join(map(str, v)) + ")" for v in vals)
        return f"{plan.table} ← {plan.table} ∪ {{{tuples}}}"

    # -------------------------
    # DELETE
    # -------------------------
    elif node == "LogicalDelete":
        pred = predicate_to_string(plan.predicate)
        return f"{plan.table} ← {plan.table} − σ({pred})({plan.table})"

    # -------------------------
    # UPDATE
    # -------------------------
    elif node == "LogicalUpdate":
        pred = predicate_to_string(plan.predicate)
        # simple rendering (don’t overcomplicate)
        updates = ", ".join(f"{k}={v}" for k, v in plan.updates)
        return (f"{plan.table} ← ({plan.table} − σ({pred})({plan.table})) "
                f"∪ {{ updated({updates}) }}")

    elif node == "LogicalTruncate":
        return f"{plan.table} ← ∅_{plan.table}"

    return None

def to_relational_algebra(plan, indent="", is_last=True):
    prefix = indent + ("└── " if is_last else "├── ")
    next_indent = indent + ("    " if is_last else "│   ")

    node_type = plan.__class__.__name__

    if node_type == "LogicalScan":
        print(prefix + plan.table)
    elif node_type == "LogicalFilter":
        predicate = predicate_to_string(plan.predicate)
        print(prefix + f"σ({predicate})")
        to_relational_algebra(plan.child, next_indent, True)
    elif node_type == "LogicalProject":
        cols = ", ".join(plan.columns)
        print(prefix + f"π({cols})")
        to_relational_algebra(plan.child, next_indent, True)
    elif node_type == "LogicalJoin":
        condition = predicate_to_string(plan.condition)
        print(prefix + f"⨝({condition})")
        to_relational_algebra(plan.left_child, next_indent, False)
        to_relational_algebra(plan.right_child, next_indent, True)
    elif node_type == "LogicalGroupBy":
        group_cols = ", ".join(plan.group_cols)
        if hasattr(plan, "aggregates") and plan.aggregates:
            aggs = ", ".join(plan.aggregates)
            print(prefix + f"γ({group_cols}; {aggs})")
        else:
            print(prefix + f"γ({group_cols})")
        to_relational_algebra(plan.child, next_indent, True)
    elif node_type == "LogicalHaving":
        predicate = predicate_to_string(plan.predicate)
        print(prefix + f"σ({predicate})")
        to_relational_algebra(plan.child, next_indent, True)
    elif node_type == "LogicalOrderBy":
        print(prefix + f"τ({plan.column} {plan.order_type})")
        to_relational_algebra(plan.child, next_indent, True)
    elif node_type == "LogicalLimit":
        print(prefix + f"LIMIT({plan.limit})")
        to_relational_algebra(plan.child, next_indent, True)
    else:
        print(prefix + f"[Unsupported: {node_type}]")


def _select_ra_lines(plan, lines, indent="", is_last=True):
    """Recursively build RA expression lines as strings for SELECT plans."""
    prefix = indent + ("└── " if is_last else "├── ")
    next_indent = indent + ("    " if is_last else "│   ")
    node_type = plan.__class__.__name__

    if node_type == "LogicalScan":
        lines.append(prefix + plan.table)

    elif node_type == "LogicalFilter":
        predicate = predicate_to_string(plan.predicate)
        lines.append(prefix + f"σ({predicate})")
        _select_ra_lines(plan.child, lines, next_indent, True)

    elif node_type == "LogicalProject":
        cols = ", ".join(plan.columns)
        lines.append(prefix + f"π({cols})")
        _select_ra_lines(plan.child, lines, next_indent, True)

    elif node_type == "LogicalJoin":
        condition = predicate_to_string(plan.condition)
        lines.append(prefix + f"⨝({condition})")
        _select_ra_lines(plan.left_child, lines, next_indent, False)
        _select_ra_lines(plan.right_child, lines, next_indent, True)

    elif node_type == "LogicalGroupBy":
        group_cols = ", ".join(plan.group_cols)
        if hasattr(plan, "aggregates") and plan.aggregates:
            aggs = ", ".join(plan.aggregates)
            lines.append(prefix + f"γ({group_cols}; {aggs})")
        else:
            lines.append(prefix + f"γ({group_cols})")
        _select_ra_lines(plan.child, lines, next_indent, True)

    elif node_type == "LogicalHaving":
        predicate = predicate_to_string(plan.predicate)
        lines.append(prefix + f"σ({predicate})")
        _select_ra_lines(plan.child, lines, next_indent, True)

    elif node_type == "LogicalOrderBy":
        lines.append(prefix + f"τ({plan.column} {plan.order_type})")
        _select_ra_lines(plan.child, lines, next_indent, True)

    elif node_type == "LogicalLimit":
        lines.append(prefix + f"LIMIT({plan.limit})")
        _select_ra_lines(plan.child, lines, next_indent, True)

    else:
        lines.append(prefix + f"[{node_type}]")


def select_to_ra_string(plan) -> str:
    """Return the relational algebra tree for a SELECT plan as a string."""
    lines = []
    _select_ra_lines(plan, lines)
    return "\n".join(lines)


def plan_to_ra_string(plan) -> str:
    """Single entry point: returns RA string for any plan (SELECT or DML/DDL)."""
    # Try DML/DDL first
    result = dml_ddl_to_ra(plan)
    if result is not None:
        return result
    # Fall back to SELECT tree rendering
    return select_to_ra_string(plan)