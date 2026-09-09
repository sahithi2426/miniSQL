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

test("CREATE TABLE students (id INT, name TEXT);")
test("INSERT INTO students VALUES (1, 'A');")
test("INSERT INTO students VALUES (2, 'B');")
test("SELECT * FROM students;")
test("DESC TABLE students;")
test("DELETE FROM students WHERE id = 1;")
test("DELETE FROM students WHERE id = 999;")
test("DELETE FROM students;")
test("SELECT * FROM students;")
test("INSERT INTO students VALUES (3, 'C');")
test("UPDATE students SET name = 'Indu' WHERE id = 3;")
test("UPDATE students SET name = 'X' WHERE id = 999;")
test("UPDATE students SET name = 'ALL';")
test("SELECT * FROM students;")
test("CREATE TABLE users (id INT, name TEXT, PRIMARY KEY(id));")
test("INSERT INTO users VALUES (1, 'A');")
test("INSERT INTO users VALUES (1, 'B');")
test("CREATE TABLE IF NOT EXISTS students (id INT, name TEXT);")
test("DROP TABLE IF EXISTS random_table;")
test("SELECT * FROM unknown;")
test("SELECT age FROM students;")
test("INSERT INTO students VALUES ();")
test("INSERT INTO students VALUES (10, 'Z');")
test("SELECT * FROM students;")
test("TRUNCATE TABLE students;")
test("SELECT * FROM students;")
test("DROP TABLE students;")
test("SELECT * FROM students;")  
test("TRUNCATE TABLE students;")
test("SELECT * FROM students;")
test("SHOW TABLES;")