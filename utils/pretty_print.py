def print_table(columns, rows):
    if not rows:
        print("(no rows)")
        return

    # Convert all values to string
    rows = [[str(val) for val in row] for row in rows]

    # Column widths
    col_widths = []
    for i, col in enumerate(columns):
        max_len = len(col)
        for row in rows:
            max_len = max(max_len, len(row[i]))
        col_widths.append(max_len)

    # Helper to print separator
    def print_separator():
        print("+" + "+".join("-" * (w + 2) for w in col_widths) + "+")

    # Header
    print_separator()
    print("| " + " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns)) + " |")
    print_separator()

    # Rows
    for row in rows:
        print("| " + " | ".join(row[i].ljust(col_widths[i]) for i in range(len(row))) + " |")

    print_separator()


def pretty_output(rows):
    if not rows:
        print("(no rows)")
        return

    # CASE 1: SELECT → multiple columns
    if len(rows[0]) > 1:
        columns = list(rows[0].keys())
        formatted_rows = [[row[col] for col in columns] for row in rows]
        print_table(columns, formatted_rows)

    # CASE 2: DML/DDL → single key (inserted, updated, deleted, etc.)
    else:
        key = list(rows[0].keys())[0]
        value = rows[0][key]

        key = key.lower()

        if key == "inserted":
            print(f"Inserted {value} row{'s' if int(value) != 1 else ''}")
        elif key == "updated":
            print(f"Updated {value} row{'s' if int(value) != 1 else ''}")
        elif key == "deleted":
            print(f"Deleted {value} row{'s' if int(value) != 1 else ''}")
        elif key == "created":
            print(f"Created table {value}")
        elif key == "dropped":
            print(f"Dropped table {value}")
        elif key == "truncated":
            print(f"Truncated table {value}")
        else:
            # fallback
            print(f"{key.capitalize()}: {value}")