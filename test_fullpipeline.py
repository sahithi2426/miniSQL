import os
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from logical.optimizer import LogicalOptimizer
from execution.builder_exec import PhysicalPlanBuilder
from storage.catalog import Catalog
from utils.pretty_print import pretty_output
from utils.relational_algebra import to_relational_algebra,dml_ddl_to_ra

if os.path.exists("minisql_data.db"):
    os.remove("minisql_data.db")

catalog = Catalog()
analyzer = SemanticAnalyzer(catalog)
logical_builder = LogicalPlanBuilder()
optimizer = LogicalOptimizer(catalog)
physical_builder = PhysicalPlanBuilder(catalog)

print("Initial tables:", catalog.tables)
print("Test Catalog ID:", id(catalog))
def test(sql: str):
    print("\n" + "="*30)
    print("INPUT:")
    print(sql)

    try:
        # LEXER + PARSER
        lexer = Lexer(sql)
        #print("Done this 1")
        tokens = lexer.tokenize()
        #print("Done this 2")
        parser = Parser(tokens)
        #print("Done this 3")
        ast = parser.parse()
        #print("Done this 4")

        # SEMANTIC
        analyzer.analyze(ast)
        #print("Done this 5")

        # LOGICAL PLAN
        logical_plan = logical_builder.build(ast)
        print("\n--- RELATIONAL ALGEBRA ---")
        stmt = dml_ddl_to_ra(logical_plan)
        if stmt:
            print(stmt)
        else:
            print(to_relational_algebra(logical_plan,"",True))
        #print("Done this 6")
        # OPTIMIZATION
        logical_plan = optimizer.optimize(logical_plan)
        #print("Done this 7")
        # PHYSICAL PLAN
        physical_plan = physical_builder.build(logical_plan)
        #print("Done this 8")
        # HANDLE DDL (CREATE, DROP, etc.)
        if not physical_plan:
            print("\nSTATUS: Command executed successfully")
            return

        # EXECUTION (SAME AS test_joins)
        print("\n--- OUTPUT ---")
        physical_plan.init()

        rows = []

        while True:
            tup = physical_plan.next()
            if tup is None:
                break
            rows.append(tup)

        pretty_output(rows)
    except Exception as e:
        print("\nERROR:", e)


test("CREATE TABLE Orders (id INT, customer_id INT);")
test("CREATE TABLE Customers (id INT, name TEXT);")

test("INSERT INTO Orders VALUES (1, 101);")
test("INSERT INTO Orders VALUES (2, 101);")
test("INSERT INTO Orders VALUES (3, 102);")
test("INSERT INTO Orders VALUES (4, 103);")

test("INSERT INTO Customers VALUES (101, 'Indu');")
test("INSERT INTO Customers VALUES (102, 'Dhanya');")
test("INSERT INTO Customers VALUES (103, 'Jyothi');")

test("SELECT * FROM Orders WHERE id = 1;")
test("SELECT * FROM Orders WHERE id = 1 AND customer_id = 101;")
test("SELECT * FROM Orders WHERE id = 1 OR id = 3;")
test("SELECT * FROM Orders WHERE NOT id = 1;")
test("SELECT * FROM Orders WHERE id = 1 AND customer_id = 101 OR id = 3;")

test("SELECT o.id, c.name FROM Orders o INNER JOIN Customers c ON o.customer_id = c.id;")
test("SELECT o.id, c.name FROM Orders o INNER JOIN Customers c ON o.customer_id = c.id WHERE c.name = 'Indu';")

test("SELECT customer_id, COUNT(*) FROM Orders GROUP BY customer_id;")
test("SELECT customer_id, COUNT(*) FROM Orders GROUP BY customer_id HAVING COUNT(*) > 1;")
test("SELECT * FROM Orders ORDER BY customer_id DESC;")
test("SELECT * FROM Orders LIMIT 1;")

test("SELECT customer_id, COUNT(*) FROM Orders WHERE id > 1 GROUP BY customer_id HAVING COUNT(*) >= 1 ORDER BY customer_id DESC LIMIT 2;")

# no result
test("SELECT * FROM Orders WHERE id = 999;")
# group by single row
test("SELECT customer_id, COUNT(*) FROM Orders WHERE id = 3 GROUP BY customer_id;")
# having no result

test("SELECT customer_id, COUNT(*) FROM Orders GROUP BY customer_id HAVING COUNT(*) > 1;")

# DELETE tests
test("DELETE FROM Orders WHERE id = 1;")
test("SELECT * FROM Orders;")

test("DELETE FROM Orders WHERE id = 999;")  # no effect
test("SELECT * FROM Orders;")

# UPDATE tests
test("UPDATE Orders SET customer_id = 999 WHERE id = 2;")
test("SELECT * FROM Orders;")

test("UPDATE Orders SET customer_id = 555 WHERE id = 999;")  # no effect
test("SELECT * FROM Orders;")

# UPDATE all rows
test("UPDATE Orders SET customer_id = 111;")
test("SELECT * FROM Orders;")

# Reinsert for further testing
test("INSERT INTO Orders VALUES (5, 101);")
test("INSERT INTO Orders VALUES (6, 102);")

test("SELECT * FROM Orders;")

# JOIN after updates
test("SELECT o.id, c.name FROM Orders o INNER JOIN Customers c ON o.customer_id = c.id;")

# DELETE affecting JOIN
test("DELETE FROM Customers WHERE id = 101;")
test("SELECT o.id, c.name FROM Orders o INNER JOIN Customers c ON o.customer_id = c.id;")

# TRUNCATE test
test("TRUNCATE TABLE Orders;")
test("SELECT * FROM Orders;")

# Reinsert after truncate
test("INSERT INTO Orders VALUES (1, 101);")
test("INSERT INTO Orders VALUES (2, 102);")

test("SELECT * FROM Orders;")

# DROP + error cases
test("DROP TABLE Orders;")
test("SELECT * FROM Orders;")  # should fail

test("DROP TABLE IF EXISTS Orders;")  # safe

# recreate for final check
test("CREATE TABLE Orders (id INT, customer_id INT);")
test("INSERT INTO Orders VALUES (1, 101);")
test("SELECT * FROM Orders;")

# error cases
test("SELECT wrong_col FROM Orders;")
test("SELECT * FROM Unknown;")
test("SELECT * FROM Orders WHERE wrong = 1;")

