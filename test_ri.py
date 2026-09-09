from lexer.lexer import Lexer
from parser.parser import Parser
from parser.ast import *
from semantic.analyzer import SemanticAnalyzer

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
        analyzer.analyze(ast)

        print("\nAST OUTPUT:")
        ast.pretty_print()

        print("\nSemantic Analysis: SUCCESS")

    except Exception as e:
        print("\nERROR:", e)

test("CREATE TABLE users (id INT);")
test("CREATE TABLE orders(order_id INT, user_id INT, FOREIGN KEY(user_id) REFERENCES users(id));") 
test("INSERT INTO users VALUES (1);")
test("INSERT INTO orders VALUES (101, 1);")
test("INSERT INTO orders VALUES (102, 999);")
test("INSERT INTO orders VALUES (200, 5);")   
test("INSERT INTO users VALUES (5);")        
test("INSERT INTO orders VALUES (200, 5);") 