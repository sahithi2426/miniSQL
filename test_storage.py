import os
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from logical.optimizer import LogicalOptimizer
from execution.builder_exec import PhysicalPlanBuilder
from storage.catalog import Catalog

#if os.path.exists("catalog.json"):
#    os.remove("catalog.json")

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
        print("Done this 1")
        tokens = lexer.tokenize()
        print("Done this 2")
        parser = Parser(tokens)
        print("Done this 3")
        ast = parser.parse()
        print("Done this 4")

        # SEMANTIC
        analyzer.analyze(ast)
        print("Done this 5")

        # LOGICAL PLAN
        logical_plan = logical_builder.build(ast)
        print("Done this 6")
        # OPTIMIZATION
        logical_plan = optimizer.optimize(logical_plan)
        print("Done this 7")
        # PHYSICAL PLAN
        physical_plan = physical_builder.build(logical_plan)
        print("Done this 8")
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

"""test("CREATE TABLE test (id INT, name TEXT);")
test("INSERT INTO test VALUES (1, 'A');")
test("INSERT INTO test VALUES (2, 'B');")"""
test("SELECT * FROM test;")
test("CREATE TABLE test (id INT, name TEXT);")
test("INSERT INTO test VALUES (3, 'C');")
test("SELECT * FROM test;")