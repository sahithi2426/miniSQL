from lexer.lexer import Lexer
from parser.parser import Parser
from logical.builder import LogicalPlanBuilder

def test(sql):
    print("\n=========================")
    print("INPUT:", sql)

    lexer = Lexer(sql)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    builder = LogicalPlanBuilder()
    plan = builder.build(ast)

    if plan:
        print("\nLogical Plan:\n")
        plan.pretty_print()
    else:
        print("\nNo logical plan generated (DDL statement)")



test("SELECT name FROM users WHERE age > 18;")
test("CREATE TABLE users (id INT, name TEXT);")
test("INSERT INTO users VALUES (1, 'Alice');")
test("SELECT name FROM users;")
test("SELECT * FROM users;")
test("select name from users where id > 18;")  