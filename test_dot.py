import os
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from logical.optimizer import LogicalOptimizer
from execution.builder_exec import PhysicalPlanBuilder
from storage.catalog import Catalog

if os.path.exists("minisql_data.db"):
    os.remove("minisql_data.db")

catalog = Catalog()
analyzer = SemanticAnalyzer(catalog)
logical_builder = LogicalPlanBuilder()
optimizer = LogicalOptimizer(catalog)
physical_builder = PhysicalPlanBuilder(catalog, analyzer)

print("Initial tables:", catalog.tables)
print("Test Catalog ID:", id(catalog))
def test(sql: str):
    print("\n" + "="*30)
    print("INPUT:")
    print(sql)

    try:
        # LEXER + PARSER
        lexer = Lexer(sql)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # SEMANTIC
        analyzer.analyze(ast)

        # LOGICAL PLAN
        logical_plan = logical_builder.build(ast)

        # OPTIMIZATION
        logical_plan = optimizer.optimize(logical_plan)

        # PHYSICAL PLAN
        physical_plan = physical_builder.build(logical_plan)

        # HANDLE DDL (CREATE, DROP, etc.)
        if not physical_plan:
            print("\nSTATUS: Command executed successfully")
            return

        # EXECUTION (SAME AS test_joins)
        print("\n--- OUTPUT ---")
        physical_plan.init()

        count = 0
        while True:
            tup = physical_plan.next()
            if tup is None:
                break
            print(tup)
            count += 1

        if count == 0:
            print("(no rows)")

    except Exception as e:
        print("\nERROR:", e)

test("CREATE TABLE Orders (id INT, customer_id INT);")
test("CREATE TABLE Customers (id INT, name TEXT);")

test("INSERT INTO Orders VALUES (1, 101);")
test("INSERT INTO Customers VALUES (101, 'Indu');")

test("SELECT o.id, c.name FROM Orders o INNER JOIN Customers c ON o.customer_id = c.id;")