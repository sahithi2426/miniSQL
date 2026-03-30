from lexer.tokens import TokenType
from parser.ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def eat(self, token_type):
        if self.current().type == token_type:
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current()}")

    def parse(self):
        if self.current().type == TokenType.EOF:
            return None
        if self.current().type == TokenType.CREATE:
            return self.parse_create()
        if self.current().type == TokenType.INSERT:
            return self.parse_insert()
        if self.current().type == TokenType.SELECT:
            return self.parse_select()
        raise SyntaxError("Unknown statement")

    def parse_create(self):
        self.eat(TokenType.CREATE)
        self.eat(TokenType.TABLE)
        name = self.current().value
        self.eat(TokenType.IDENT)

        self.eat(TokenType.LPAREN)

        columns = []
        foreign_keys = []
        primary_key=None
        unique_keys=[]

        while self.current().type != TokenType.RPAREN:

        # FOREIGN KEY parsing
            if self.current().type == TokenType.FOREIGN:
                self.eat(TokenType.FOREIGN)
                self.eat(TokenType.KEY)

                self.eat(TokenType.LPAREN)
                fk_col = self.current().value
                self.eat(TokenType.IDENT)
                self.eat(TokenType.RPAREN)

                self.eat(TokenType.REFERENCES)

                ref_table = self.current().value
                self.eat(TokenType.IDENT)

                self.eat(TokenType.LPAREN)
                ref_col = self.current().value
                self.eat(TokenType.IDENT)
                self.eat(TokenType.RPAREN)

                foreign_keys.append((fk_col, ref_table, ref_col))
            elif self.current().type == TokenType.PRIMARY:
                self.eat(TokenType.PRIMARY)
                self.eat(TokenType.KEY)

                self.eat(TokenType.LPAREN)
                pk_col = self.current().value
                self.eat(TokenType.IDENT)
                self.eat(TokenType.RPAREN)

                primary_key = pk_col
            
            elif self.current().type == TokenType.UNIQUE:
                self.eat(TokenType.UNIQUE)

                self.eat(TokenType.LPAREN)
                uk_col = self.current().value
                self.eat(TokenType.IDENT)
                self.eat(TokenType.RPAREN)

                unique_keys.append(uk_col)

            else:
                col_name = self.current().value
                self.eat(TokenType.IDENT)
                col_type = self.current().type
                self.eat(col_type)
                columns.append((col_name, col_type))

            if self.current().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)

        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)

        return CreateTable(name, columns, foreign_keys,primary_key,unique_keys)
    
    def parse_insert(self):
        self.eat(TokenType.INSERT)
        self.eat(TokenType.INTO)

        table = self.current().value
        self.eat(TokenType.IDENT)

        self.eat(TokenType.VALUES)
        self.eat(TokenType.LPAREN)

        values = []
        while self.current().type != TokenType.RPAREN:
            values.append(self.current().value)
            self.eat(self.current().type)
            if self.current().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)

        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)

        return Insert(table, values)

    def parse_select(self):
        self.eat(TokenType.SELECT)
        columns = []

    # Columns (support aggregates)
        while True:
            if self.current().type == TokenType.STAR:
                columns.append("*")
                self.eat(TokenType.STAR)

            elif self.current().type in (
                TokenType.COUNT,
                TokenType.SUM,
                TokenType.AVG,
                TokenType.MIN,
                TokenType.MAX,
            ):
                func = self.current().type.name
                self.eat(self.current().type)
                self.eat(TokenType.LPAREN)
                if self.current().type==TokenType.STAR:
                    col="*"
                    self.eat(TokenType.STAR)
                elif self.current().type==TokenType.IDENT:
                    col=self.current().value
                    self.eat(TokenType.IDENT)
                else:
                    raise SyntaxError("Expected column name or * inside aggregate")
                self.eat(TokenType.RPAREN)
                columns.append(f"{func}({col})")

            elif self.current().type == TokenType.IDENT:
                columns.append(self.current().value)
                self.eat(TokenType.IDENT)

            else:
                raise SyntaxError("Invalid column in SELECT")

            if self.current().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            else:
                break

        self.eat(TokenType.FROM)
        table = self.current().value
        self.eat(TokenType.IDENT)

        where = None
        if self.current().type == TokenType.WHERE:
            where = self.parse_where()

    # GROUP BY
        group_by = None
        if self.current().type == TokenType.GROUP:
            self.eat(TokenType.GROUP)
            self.eat(TokenType.BY)
            group_by = self.current().value
            self.eat(TokenType.IDENT)

        # HAVING
        having = None
        if self.current().type == TokenType.HAVING:
            self.eat(TokenType.HAVING)
            having = self.parse_having()

    # ORDER BY
        order_by = None
        order_type = None
        if self.current().type == TokenType.ORDER:
            self.eat(TokenType.ORDER)
            self.eat(TokenType.BY)
            order_by = self.current().value
            self.eat(TokenType.IDENT)

            if self.current().type in (TokenType.ASC, TokenType.DESC):
                order_type = self.current().type.name
                self.eat(self.current().type)

    # LIMIT
        limit = None
        if self.current().type == TokenType.LIMIT:
            self.eat(TokenType.LIMIT)
            limit = self.current().value
            self.eat(TokenType.NUMBER)

        self.eat(TokenType.SEMICOLON)
        return Select(columns, table, where, group_by, having, order_by, order_type, limit)
    
    def parse_where(self):
        self.eat(TokenType.WHERE)
        return self.parse_or()
    
    def parse_or(self):
        left = self.parse_and()

        while self.current().type == TokenType.OR:
            self.eat(TokenType.OR)
            right = self.parse_and()
            left = Where(left, "OR", right)

        return left
    
    def parse_and(self):
        left = self.parse_not()

        while self.current().type == TokenType.AND:
            self.eat(TokenType.AND)
            right = self.parse_not()
            left = Where(left, "AND", right)

        return left

    def parse_not(self):
        if self.current().type == TokenType.NOT:
            self.eat(TokenType.NOT)
            condition = self.parse_comparison()
            return Where("NOT", None, condition)

        return self.parse_comparison()
    
    def parse_comparison(self):
        col = self.current().value
        self.eat(TokenType.IDENT)

        op = self.current().value
        self.eat(self.current().type)

        if self.current().type == TokenType.NUMBER:
            val = self.current().value
            self.eat(TokenType.NUMBER)
        elif self.current().type == TokenType.STRING:
            val = self.current().value
            self.eat(TokenType.STRING)
        else:
            raise SyntaxError("Expected NUMBER or STRING in WHERE")

        return Where(col, op, val)

    def parse_having(self):
    # Support aggregate like COUNT(*)
        if self.current().type in (
            TokenType.COUNT,
            TokenType.SUM,
            TokenType.AVG,
            TokenType.MIN,
            TokenType.MAX,
        ):
            func = self.current().type.name
            self.eat(self.current().type)
            self.eat(TokenType.LPAREN)

            if self.current().type == TokenType.STAR:
                col = "*"
                self.eat(TokenType.STAR)
            else:
                col = self.current().value
                self.eat(TokenType.IDENT)

            self.eat(TokenType.RPAREN)

            left = f"{func}({col})"

        else:
            raise SyntaxError("Expected aggregate function in HAVING")

        op = self.current().value
        self.eat(self.current().type)

        if self.current().type == TokenType.NUMBER:
            val = self.current().value
            self.eat(TokenType.NUMBER)
        else:
            raise SyntaxError("Expected number in HAVING condition")

        return Where(left, op, val)