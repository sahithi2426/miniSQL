from lexer.lexer import Lexer   # adjust if your structure differs

def test(input_sql):
    print("\nINPUT:")
    print(input_sql)
    print("\nTOKENS:")
    lexer = Lexer(input_sql)
    tokens = lexer.tokenize()
    for t in tokens:
        print(t)

# Test cases
test("SELECT * FROM users;")
test("SELECT name FROM users WHERE age >= 18;")
test("INSERT INTO users VALUES ('Alice');")
test("SELECT * FROM users WHERE age != 20;")
test("SELECT * FROM users; -- this is a comment")
test("SELECT * FROM users WHERE age <= 30;")
test("SELECT age>=18 FROM users;")
test("SELECT age<=30 FROM users;")
test("SELECT age<>25 FROM users;")
test("SELECT age!=25 FROM users;")
