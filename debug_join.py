import os, sys
sys.stdout.reconfigure(encoding='utf-8')

if os.path.exists('minisql_data.db'):
    os.remove('minisql_data.db')
if os.path.exists('catalog.json'):
    os.remove('catalog.json')

from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from logical.builder import LogicalPlanBuilder
from logical.optimizer import LogicalOptimizer
from execution.builder_exec import PhysicalPlanBuilder
from storage.catalog import Catalog

catalog = Catalog()
analyzer = SemanticAnalyzer(catalog)
lb = LogicalPlanBuilder()
opt = LogicalOptimizer(catalog)
pb = PhysicalPlanBuilder(catalog, analyzer)

def run(sql):
    tokens = Lexer(sql).tokenize()
    ast = Parser(tokens).parse()
    analyzer.analyze(ast)
    lp = lb.build(ast)
    lp = opt.optimize(lp)
    pp = pb.build(lp)
    if not pp:
        print(f"OK: {sql}")
        return []
    pp.init()
    rows = []
    while True:
        t = pp.next()
        if t is None:
            break
        rows.append(t)
    print(f"QUERY: {sql}")
    print(f"  -> {len(rows)} rows")
    for r in rows:
        print(f"     {r}")
    return rows

run("CREATE TABLE Orders (id INT, customer_id INT);")
run("CREATE TABLE Customers (id INT, name TEXT);")
run("INSERT INTO Orders VALUES (1, 101);")
run("INSERT INTO Orders VALUES (2, 101);")
run("INSERT INTO Orders VALUES (3, 102);")
run("INSERT INTO Customers VALUES (101, 'Indu');")
run("INSERT INTO Customers VALUES (102, 'Dhanya');")

print("\n=== SELECT * FROM Orders ===")
run("SELECT * FROM Orders;")

print("\n=== SELECT * FROM Customers ===")
run("SELECT * FROM Customers;")

print("\n=== JOIN TEST ===")
rows = run("SELECT o.id, c.name FROM Orders o INNER JOIN Customers c ON o.customer_id = c.id;")
if not rows:
    print("  *** NO ROWS RETURNED - investigating ***")
