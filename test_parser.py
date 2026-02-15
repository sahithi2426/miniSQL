from lexer.lexer import Lexer
from parser.parser import Parser

def test(sql):
    print("\nINPUT:")
    print(sql)

    lexer = Lexer(sql)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    print("\nAST OUTPUT:")
    print(ast)

test("CREATE TABLE users (id INT, name TEXT);")
test("INSERT INTO users VALUES (1, 'Alice');")
test("SELECT name FROM users;")
test("SELECT * FROM users;")
test("SELECT name FROM users WHERE age > 25;")