from lexer.lexer import Lexer
from parser.parser import Parser
from parser.ast import *
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from logical.optimizer import LogicalOptimizer   

class Table:
    def __init__(self, name, columns, foreign_keys=None,primary_key=None, unique_keys=None):
        self.name = name
        self.columns = {c: t for c, t in columns}
        self.foreign_keys = foreign_keys or []
        self.primary_key = primary_key
        self.unique_keys = unique_keys or []
        self.rows = []
        self.estimated_rows = 1000

class Catalog:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns, foreign_keys=None, primary_key=None, unique_keys=None):
        if name in self.tables:
            raise Exception(f"Table '{name}' already exists")

        t = Table(name, columns, foreign_keys, primary_key, unique_keys)
        self.tables[name] = t
        
        if name == "orders": t.estimated_rows = 1 
        if name == "users": t.estimated_rows = 1

    def get_table(self, name):
        if name not in self.tables:
            raise Exception(f"Table '{name}' does not exist")

        return self.tables[name]

catalog = Catalog()
analyzer = SemanticAnalyzer(catalog)


import traceback

def test(sql):
    print("\n==============================")
    print("INPUT:")
    print(sql)

    try:
        lexer = Lexer(sql)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()
        #print(type(ast))
        analyzer.analyze(ast)

        print("\nAST OUTPUT:")
        ast.pretty_print()

        builder = LogicalPlanBuilder()
        plan = builder.build(ast)

        print("\nLOGICAL PLAN:")
        plan.pretty_print()

        if isinstance(ast, Select):
            optimizer = LogicalOptimizer(catalog)
            optimized_plan = optimizer.optimize(plan)

            print("\nOPTIMIZED PLAN:")
            optimized_plan.pretty_print()

        print("\nSemantic Analysis: SUCCESS")
    except Exception as e:
        print("\nERROR:", e)
        traceback.print_exc()

test("CREATE TABLE users (user_id INT,email TEXT,PRIMARY KEY(id),UNIQUE(email));")
test("CREATE TABLE orders(order_id INT, order_user_id INT, amount INT);")
test("INSERT INTO users VALUES(1,'a@gmail.com');")
test("INSERT INTO users VALUES(2,'b@gmail.com');")
test("INSERT INTO users VALUES(15,'d@gmail.com');")
test("INSERT INTO users VALUES(25,'c@gmail.com');")
test("INSERT INTO orders VALUES(101,1,500);")
test("INSERT INTO orders VALUES(102,2,700);")
test("INSERT INTO orders VALUES(103,15,300);")

test("SELECT email FROM users WHERE user_id > 10;")
test("SELECT email FROM users WHERE user_id > 10 AND email = 'a@gmail.com';")
test("SELECT email FROM users WHERE user_id > 10 OR user_id < 5;")
test("SELECT email FROM users;")
test("SELECT * FROM users WHERE user_id > 10;")
test("SELECT email FROM users WHERE NOT user_id > 10;")
test("SELECT email FROM users WHERE user_id > 10 AND user_id < 20;")

test("SELECT * FROM orders INNER JOIN users ON order_user_id = user_id;")

test("SELECT * FROM users INNER JOIN orders ON user_id = order_user_id WHERE email = 'a@gmail.com';")