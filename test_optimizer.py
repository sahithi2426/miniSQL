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


class Catalog:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns, foreign_keys=None, primary_key=None, unique_keys=None):
        if name in self.tables:
            raise Exception(f"Table '{name}' already exists")

        self.tables[name] = Table(name, columns, foreign_keys, primary_key, unique_keys)

    def get_table(self, name):
        if name not in self.tables:
            raise Exception(f"Table '{name}' does not exist")

        return self.tables[name]

catalog = Catalog()
analyzer = SemanticAnalyzer(catalog)


def test(sql):
    print("\n==============================")
    print("INPUT:")
    print(sql)

    try:
        lexer = Lexer(sql)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()
        print(type(ast))
        analyzer.analyze(ast)

        print("\nAST OUTPUT:")
        ast.pretty_print()

        builder = LogicalPlanBuilder()
        plan = builder.build(ast)

        print("\nLOGICAL PLAN:")
        plan.pretty_print()

        if isinstance(ast, Select):
            optimizer = LogicalOptimizer()
            optimized_plan = optimizer.optimize(plan)

            print("\nOPTIMIZED PLAN:")
            optimized_plan.pretty_print()

        print("\nSemantic Analysis: SUCCESS")

    except Exception as e:
        print("\nERROR:", e)

test("CREATE TABLE users (id INT,email TEXT,PRIMARY KEY(id),UNIQUE(email));")
test("SELECT email FROM users WHERE id > 10;")
test("SELECT email FROM users WHERE id > 10 AND email = 'a@gmail.com';")
test("SELECT email FROM users WHERE id > 10 OR id < 5;")
test("SELECT email FROM users;")
test("SELECT * FROM users WHERE id > 10;")
test("SELECT email FROM users WHERE NOT id > 10;")
test("SELECT email FROM users WHERE id > 10 AND id < 20;")