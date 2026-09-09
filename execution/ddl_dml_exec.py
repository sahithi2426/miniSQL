from execution.executor import Executor

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

    def _matches(self, row, predicate):
        from execution.filter import FilterExec
        dummy = FilterExec(None, predicate)
        return dummy._evaluate_predicate(row)

    def next(self):
        if self.done:
            return None

        table = self.catalog.get_table(self.plan.table)
        before = len(table.rows)

        if self.plan.predicate:
            table.rows = [
                r for r in table.rows
                if not self._matches(r, self.plan.predicate)
            ]
        else:
            table.rows = []

        deleted = before - len(table.rows)
        self.catalog._save()
        self.done = True
        return {"deleted": deleted}

class UpdateExec(Executor):
    def __init__(self, catalog, plan):
        self.catalog = catalog
        self.plan = plan
        self.done = False

    def init(self):
        self.done = False

    def _matches(self, row, predicate):
        from execution.filter import FilterExec
        dummy = FilterExec(None, predicate)
        return dummy._evaluate_predicate(row)

    def next(self):
        if self.done:
            return None

        table = self.catalog.get_table(self.plan.table)
        count = 0

        for row in table.rows:
            if self.plan.predicate:
                if not self._matches(row, self.plan.predicate):
                    continue

            for col, val in self.plan.updates:
                if isinstance(val, str) and val.startswith("'") and val.endswith("'"):
                    row[col] = val.strip("'")
                else:
                    try:
                        row[col] = int(val)
                    except (ValueError, TypeError):
                        try:
                            row[col] = float(val)
                        except (ValueError, TypeError):
                            row[col] = val

            count += 1

        self.catalog._save()
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
            self.catalog._save()
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

        self.catalog._save()
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