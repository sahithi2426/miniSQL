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
physical_builder = PhysicalPlanBuilder(catalog, analyzer)

print("Initial tables:", catalog.tables)
print("Test Catalog ID:", id(catalog))

def clean_query(sql: str):
    lines = sql.split('\n')
    cleaned = []

    for line in lines:
        line = line.strip()

        # skip full-line comments
        if line.startswith("--") or line == "":
            continue

        # remove inline comments
        if "--" in line:
            line = line.split("--")[0].strip()

        if line:
            cleaned.append(line)

    return " ".join(cleaned)

def test(sql: str):
    print("\n" + "="*30)
    print("INPUT:")
    print(sql)

    try:
        sql = clean_query(sql)

        if not sql:
            print("(comment / empty query skipped)")
            return
        
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

test("CREATE TABLE users (id INT, name TEXT);")
test("INSERT INTO users VALUES (1, 'Alice');")
test("INSERT INTO users VALUES (2, 'Bob');")
test("INSERT INTO users VALUES (3, 'Anu');")
test("SELECT * FROM users WHERE id + 1 > 2;")
test("SELECT * FROM users WHERE id > 1 AND name = 'Bob';")
test("SELECT * FROM users WHERE id = 1 OR id = 3;")
test("SELECT * FROM users WHERE NOT id = 1;")
test("SELECT * FROM users WHERE id = 1 OR id = 2 AND id = 3;")
test("SELECT * FROM users WHERE name LIKE 'A%';")
test("SELECT * FROM users WHERE name LIKE '%b';")
test("SELECT * FROM users WHERE id BETWEEN 1 AND 2;")
test("INSERT INTO users VALUES (4, NULL);")
test("SELECT * FROM users WHERE name IS NULL;")
test("SELECT * FROM users WHERE id / 0 > 1;")