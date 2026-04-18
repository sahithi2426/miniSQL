from lexer.lexer import Lexer
from parser.parser import Parser
from parser.ast import *

def test(sql):
    print("\nINPUT:")
    print(sql)

    lexer = Lexer(sql)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    print("\nAST OUTPUT:")
    if ast is None:
        print("(No statement)")
    else:
        ast.pretty_print()

test("CREATE TABLE users (id INT, name TEXT, age INT);")
test("INSERT INTO users VALUES (1, 'Alice', 32);")
test("SELECT name FROM users;")
test("SELECT * FROM users;")
test("select name from users where age > 18;")
test("SELECT department, COUNT(*) FROM employees GROUP BY department;")
test("SELECT department, COUNT(*) FROM employees GROUP BY department HAVING COUNT(*) > 5;")
test("SELECT department, COUNT(*), SUM(salary), AVG(age) FROM employees GROUP BY department;")
test("SELECT department, COUNT(*) FROM employees GROUP BY department HAVING COUNT(*) >= 10;")
test("SELECT department, COUNT(*) FROM employees WHERE age > 25 GROUP BY department HAVING COUNT(*) > 5;")
test("SELECT name FROM employees WHERE department = 'HR';")
test("SELECT name FROM employees WHERE age < 20 OR age > 60;")
test("SELECT   name    FROM    employees   ;")
test("SELECT department FROM employees HAVING COUNT(*) > 5;")
test("SELECT name FROM employees WHERE age > 18 AND NOT salary > 50000;")
test("SELECT name FROM employees WHERE age > 18 AND salary > 50000 OR department = 'IT';")
test("SELECT name FROM employees")#error
test("SELECT FROM employees;")#error
test("SELECT department FROM employees GROUP BY;")#error
test("SELECT COUNT(*) FROM employees;")
test("SELECT name FROM employees LIMIT 3;")
test("SELECT name FROM employees WHERE age > 25 AND salary > 50000 OR department = 'HR';")
test("-- this is a comment")
test("SELECT name,,age FROM employees;")#error
test("SELECT name FROM employees WHERE age > 18 AND NOT salary > 50000;")
test("SELECT name FROM employees WHERE age > 18 AND salary > 50000 OR department = 'IT';")
