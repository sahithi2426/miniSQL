from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from codegen.c_generator import CCodeGenerator
from codegen.emitter import CodeEmitter

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
builder = LogicalPlanBuilder()
codegen = CCodeGenerator()
codegen.catalog = catalog
emitter = CodeEmitter()

def test_codegen(sql):
    print("\n======")
    print("===== INPUT: =====")
    print(sql)

    try:
        lexer = Lexer(sql)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        analyzer.analyze(ast)

        plan = builder.build(ast)

        c_code = codegen.generate(plan)

        c_path = emitter.write_c_file(c_code)

        print("\nGENERATED C CODE:\n")
        print(c_code)

        print("\nC file written to:", c_path)

    except Exception as e:
        print("\nERROR:", e)

test_codegen("CREATE TABLE users (id INT, name TEXT);")
test_codegen("INSERT INTO users VALUES (1, 'Alice');")
test_codegen("INSERT INTO users VALUES (2, 'Alice');")
test_codegen("INSERT INTO users VALUES (3, 'Alice');")
test_codegen("SELECT name FROM users WHERE id = 1;")
test_codegen("SELECT * FROM users WHERE id > 0 AND name = 'Alice';")