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
        print("\n--- RELATIONAL ALGEBRA AFTER OPTIMIZATION ---")
        stmt = dml_ddl_to_ra(logical_plan)
        if stmt:
            print(stmt)
        else:
            print(to_relational_algebra(logical_plan,"",True))
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

test("CREATE TABLE students (id INT,name TEXT,student_dept_id INT,PRIMARY KEY(id));");
test("CREATE TABLE departments (dept_id INT,dept_name TEXT,PRIMARY KEY(dept_id));");
test("CREATE TABLE courses (course_id INT,course_dept_id INT,course_name TEXT,PRIMARY KEY(course_id));");

test("INSERT INTO students VALUES (1, 'Alice',10);")
test("INSERT INTO students VALUES (2, 'Bob',20);")
test("INSERT INTO students VALUES (3, 'Charlie',30);")
test("INSERT INTO students VALUES (4, 'David',NULL);")

test("INSERT INTO departments VALUES (10,'CSE');")
test("INSERT INTO departments VALUES (20,'ECE');")
test("INSERT INTO departments VALUES (40,'MECH');")

test("INSERT INTO courses VALUES (101, 10, 'DSA');")
test("INSERT INTO courses VALUES (102, 20, 'Circuits');")
test("INSERT INTO courses VALUES (103, 10, 'OS');")
test("INSERT INTO courses VALUES (104, 50, 'Thermodynamics');")

"""print("\nINNER JOIN TEST")
test("SELECT * FROM students INNER JOIN departments ON student_dept_id = dept_id;")

print("\nLEFT JOIN TEST")
test("SELECT * FROM students LEFT JOIN departments ON student_dept_id = dept_id;")
test("SELECT * FROM courses LEFT JOIN departments ON course_dept_id = dept_id;")
print("\nRIGHT JOIN TEST")
test("SELECT * FROM students RIGHT JOIN departments ON student_dept_id = dept_id;")

print("\nFULL JOIN TEST")
test("SELECT * FROM students FULL JOIN departments ON student_dept_id = dept_id;")"""


test("SELECT * FROM courses INNER JOIN departments ON course_dept_id = dept_id WHERE dept_name = 'CSE';")
test("SELECT * FROM students WHERE student_dept_id > 10 AND id < 3;")
test("SELECT * FROM students INNER JOIN departments ON student_dept_id = dept_id WHERE student_dept_id > 10 AND dept_name = 'ECE';")
# Final Cleanup
#buffer_pool.flush_all_pages()
#disk_manager.close()