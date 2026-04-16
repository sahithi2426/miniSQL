import os
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from logical.optimizer import LogicalOptimizer
from storage.disk_manager import DiskManager
from storage.buffer_pool import BufferPoolManager
from planner.physical_plan_builder import PhysicalPlanBuilder

DB_FILE = "minisql_data.db"

class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = {c: t for c, t in columns}
        self.primary_key = None
        self.unique_keys = []
        self.foreign_keys = []
        self.rows = []
        self.estimated_rows = 1000  

class Catalog:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns, foreign_keys=None, primary_key=None, unique_keys=None):
        t = Table(name, columns)
        if primary_key: t.primary_key = primary_key
        if unique_keys: t.unique_keys = unique_keys
        if foreign_keys: t.foreign_keys = foreign_keys
        self.tables[name] = t
        
        if name == "orders": t.estimated_rows = 50000 
        if name == "users": t.estimated_rows = 1000

    def get_table(self, name):
        if name not in self.tables:
            raise Exception(f"Table '{name}' does not exist.")
        return self.tables[name]

catalog = Catalog()
analyzer = SemanticAnalyzer(catalog)
logical_builder = LogicalPlanBuilder()
optimizer = LogicalOptimizer(catalog)
disk_manager = DiskManager(DB_FILE)
buffer_pool = BufferPoolManager(disk_manager, pool_size=10)
physical_builder = PhysicalPlanBuilder(catalog, buffer_pool)

def test(sql: str):
    """Refined execution pipeline for testing SQL queries"""
    print("\n" + "="*30)
    print("INPUT:")
    print(sql)

    try:
        lexer = Lexer(sql)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        analyzer.analyze(ast)
        logical_plan = logical_builder.build(ast)
        logical_plan = optimizer.optimize(logical_plan)
        physical_plan = physical_builder.build(logical_plan)
        
        if not physical_plan:
            print("\nSTATUS: DDL/DML Logic Executed (Metadata Updated)")
            return

        print("\n--- RESULTS ---")
        physical_plan.init()
        while True:
            tup = physical_plan.next()
            if tup is None:
                break
            print(tup)

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

print("\nINNER JOIN TEST")
test("SELECT * FROM students INNER JOIN departments ON student_dept_id = dept_id;")

print("\nLEFT JOIN TEST")
test("SELECT * FROM students LEFT JOIN departments ON student_dept_id = dept_id;")
test("SELECT * FROM courses LEFT JOIN departments ON course_dept_id = dept_id;");
print("\nRIGHT JOIN TEST")
test("SELECT * FROM students RIGHT JOIN departments ON student_dept_id = dept_id;")

print("\nFULL JOIN TEST")
test("SELECT * FROM students FULL JOIN departments ON student_dept_id = dept_id;")
test("SELECT * FROM courses INNER JOIN departments ON course_dept_id = dept_id WHERE dept_name = 'CSE';")
test("SELECT * FROM courses LEFT JOIN departments ON course_dept_id = dept_id;")

# Final Cleanup
buffer_pool.flush_all_pages()
disk_manager.close()