from execution.executor import Executor
from execution.filter import FilterExec

class DummyScan:
    def __init__(self, rows):
        self.rows = rows
        self.idx = 0

    def init(self):
        self.idx = 0

    def next(self):
        if self.idx >= len(self.rows):
            return None
        row = self.rows[self.idx]
        self.idx += 1
        return row
    
class CreateTableExec(Executor):
    def __init__(self, catalog, plan):
        self.catalog = catalog
        self.plan = plan
        self.done = False

    def init(self):
        self.done = False

    def next(self):
        if self.done:
            return None

        self.catalog.create_table(
            self.plan.table,
            self.plan.columns,
            getattr(self.plan, "foreign_keys", []),
            getattr(self.plan, "primary_key", None),
            getattr(self.plan, "unique_keys", [])
        )

        self.done = True
        return {"created": self.plan.table}
    

class DeleteExec(Executor):
    def __init__(self, catalog, plan):
        self.catalog = catalog
        self.plan = plan
        self.done = False

    def init(self):
        self.done = False

    def next(self):
        if self.done:
            return None

        table = self.catalog.get_table(self.plan.table)

        before = len(table.rows)

        if self.plan.predicate:
            filtered = FilterExec(DummyScan(table.rows), self.plan.predicate)
            filtered.init()
            to_delete = []
            while True:
                row = filtered.next()
                if row is None:
                    break
                to_delete.append(row)

            table.rows = [r for r in table.rows if r not in to_delete]
        else:
            table.rows = []

        deleted = before - len(table.rows)
        self.done = True
        return {"deleted": deleted}
    
class UpdateExec(Executor):
    def __init__(self, catalog, plan):
        self.catalog = catalog
        self.plan = plan
        self.done = False

    def init(self):
        self.done = False


    def normalize(self, val):
        if isinstance(val, str):
            val = val.strip()   # remove spaces

            if val.startswith("'") and val.endswith("'"):
                return val.strip("'")

            try:
                return int(val)   # safer than isdigit()
            except:
                return val

        return val

    def next(self):
        if self.done:
            return None

        table = self.catalog.get_table(self.plan.table)
        count = 0

        #print("DEBUG → table rows BEFORE:", table.rows)
        #print("DEBUG → predicate:", self.plan.predicate)
        #print("DEBUG → updates:", self.plan.updates)
        for row in table.rows:
            #print("\nDEBUG → checking row:", row)


            if self.plan.predicate:
                scanner = DummyScan([row])   # wrap single row
                filter_exec = FilterExec(scanner, self.plan.predicate)
                filter_exec.init()

                result = filter_exec.next()

                if result is None:
                    continue

            """if self.plan.predicate:
                left_key = self.plan.predicate.left
                right = self.plan.predicate.right

                print("DEBUG → raw left_key:", left_key)
                print("DEBUG → raw right:", right)
                left = self.normalize(row.get(left_key))
                if hasattr(right, "value"):
                    right = right.value
                right = self.normalize(right)

                print("DEBUG → normalized left:", left)
                print("DEBUG → normalized right:", right)
                print("DEBUG → types:", type(left), type(right))
                print("DEBUG → equality check:", left == right)
                if left != right:
                    print("DEBUG → condition failed")
                    continue
                else:
                    print("DEBUG → condition passed")"""

            for col, val in self.plan.updates:
                #row[col] = val.strip("'")
                #print(f"DEBUG → updating {col} from {row.get(col)} to {val}")
                row[col] = self.normalize(val)

            count += 1

        self.done = True
        return {"updated": count}
    
class DropExec(Executor):
    def __init__(self, catalog, plan):
        self.catalog = catalog
        self.plan = plan
        self.done = False

    def init(self):
        self.done = False

    def next(self):
        if self.done:
            return None
        if self.plan.table in self.catalog.tables:
            self.catalog.tables.pop(self.plan.table)
            result = {"dropped": self.plan.table}
        else:
            if getattr(self.plan, "if_exists", False):
                result = {"notice": f"Table '{self.plan.table}' does not exist (ignored)"}
            else:
                raise Exception(f"Table '{self.plan.table}' does not exist.")

        self.done = True
        return result
    
class TruncateExec(Executor):
    def __init__(self, catalog, plan):
        self.catalog = catalog
        self.plan = plan
        self.done = False

    def init(self):
        self.done = False

    def next(self):
        if self.done:
            return None

        table = self.catalog.get_table(self.plan.table)
        table.rows.clear()

        self.done = True
        return {"truncated": self.plan.table}
    
class ShowTablesExec(Executor):
    def __init__(self, catalog):
        self.catalog = catalog
        self.done = False

    def init(self):
        self.done = False

    def next(self):
        if self.done:
            return None

        self.done = True
        return {"tables": list(self.catalog.tables.keys())}
    
class DescTableExec(Executor):
    def __init__(self, catalog, plan):
        self.catalog = catalog
        self.plan = plan
        self.done = False

    def init(self):
        self.done = False

    def next(self):
        if self.done:
            return None

        table = self.catalog.get_table(self.plan.table)

        self.done = True

        return {
            "columns": list(table.columns.keys()),
            "primary_key": table.primary_key,
            "unique": table.unique_keys,
            "foreign_keys": table.foreign_keys
        }