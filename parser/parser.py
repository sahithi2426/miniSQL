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
            stmt = self.parse_create()
        elif self.current().type == TokenType.INSERT:
            stmt = self.parse_insert()
        elif self.current().type == TokenType.SELECT:
            stmt = self.parse_select()
        elif self.current().type == TokenType.DROP:
            stmt = self.parse_drop()
        elif self.current().type == TokenType.DELETE:
            stmt = self.parse_delete()
        elif self.current().type == TokenType.UPDATE:
            stmt = self.parse_update()
        elif self.current().type == TokenType.ALTER:
            stmt = self.parse_alter()
        elif self.current().type == TokenType.TRUNCATE:
            stmt = self.parse_truncate()
        elif self.current().type == TokenType.SHOW:
            stmt = self.parse_show()
        elif self.current().type == TokenType.DESC:
            stmt = self.parse_desc()
        else:
            raise SyntaxError("Unknown statement")

        # Optional trailing semicolon at top level
        if self.current().type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)

        if self.current().type != TokenType.EOF:
            raise SyntaxError(f"Unexpected token '{self.current().value}'")

        return stmt


    def parse_expression(self):
        return self.parse_or()
    
    def parse_create(self):
        self.eat(TokenType.CREATE)
        self.eat(TokenType.TABLE)
        if_not_exists = False

        if self.current().type == TokenType.IF:
            self.eat(TokenType.IF)
            self.eat(TokenType.NOT)
            self.eat(TokenType.EXISTS)
            if_not_exists = True

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

                # Support inline PRIMARY KEY / UNIQUE after type
                if self.current().type == TokenType.PRIMARY:
                    self.eat(TokenType.PRIMARY)
                    self.eat(TokenType.KEY)
                    primary_key = col_name
                elif self.current().type == TokenType.UNIQUE:
                    self.eat(TokenType.UNIQUE)
                    unique_keys.append(col_name)

                # Support NOT NULL (ignore constraint, just consume)
                if self.current().type == TokenType.NOT:
                    self.eat(TokenType.NOT)
                    self.eat(TokenType.NULL)

                columns.append((col_name, col_type))

            if self.current().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)

        self.eat(TokenType.RPAREN)
        # semicolon consumed by top-level parse()
        return CreateTable(name, columns, foreign_keys, primary_key, unique_keys, if_not_exists)
    
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
        # semicolon consumed by top-level parse()
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
                """columns.append(self.current().value)
                self.eat(TokenType.IDENT)
                    # check for table.column
                if self.current().type == TokenType.DOT:
                    self.eat(TokenType.DOT)
                    col = self.current().value
                    self.eat(TokenType.IDENT)
                    columns.append(f"{table}.{col}")
                else:
                    columns.append(table)"""
                col = self.parse_identifier()
                if col.upper() not in [c for c in columns] and col.upper() not in ["*"]:
                    columns.append(col)

            else:
                raise SyntaxError("Invalid column in SELECT")

            if self.current().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            else:
                break

        self.eat(TokenType.FROM)
        table = self.current().value
        self.eat(TokenType.IDENT)
        # CRITICAL FIX
        
        alias = None
        if self.current().type == TokenType.IDENT:
            
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_token and next_token.type  == TokenType.DOT:
                pass
            else:
                alias = self.current().value
                self.eat(TokenType.IDENT)

        valid_next = {TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.FULL, TokenType.JOIN,
        TokenType.WHERE, TokenType.GROUP, TokenType.ORDER, TokenType.LIMIT,
        TokenType.SEMICOLON, TokenType.EOF}

        if self.current().type not in valid_next:
            raise SyntaxError(f"Unexpected token '{self.current().value}' after table")
        joins = []
        while self.current().type in (TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.FULL, TokenType.JOIN):
            join_type = "INNER"
            if self.current().type in (TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.FULL):
                join_type = self.current().type.name
                self.eat(self.current().type)
                if self.current().type == TokenType.OUTER:
                    self.eat(TokenType.OUTER)
            
            self.eat(TokenType.JOIN)
            join_table = self.current().value
            self.eat(TokenType.IDENT)
            join_alias = None
            if self.current().type == TokenType.IDENT:
                join_alias = self.current().value
                self.eat(TokenType.IDENT)
            
            self.eat(TokenType.ON)
            condition = self.parse_or()
            joins.append(Join(join_type, join_table, condition, join_alias))

        where = None
        if self.current().type == TokenType.WHERE:
            where = self.parse_where()

    # GROUP BY
        group_by = None
        if self.current().type == TokenType.GROUP:
            self.eat(TokenType.GROUP)
            self.eat(TokenType.BY)
            group_by = [self.current().value]
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

        # semicolon consumed by top-level parse()
        return Select(columns, table, alias, where, group_by, having, order_by, order_type, limit, joins)
    
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
            condition = self.parse_not() 
            return Where(condition, "NOT", None)

        return self.parse_comparison()
    

    def parse_identifier(self):
        name = self.current().value
        self.eat(TokenType.IDENT)

        if self.current().type == TokenType.DOT:
            self.eat(TokenType.DOT)
            col = self.current().value
            self.eat(TokenType.IDENT)
            return f"{name}.{col}"

        return name

    def parse_primary(self):
        token = self.current()

        # NUMBER
        if token.type == TokenType.NUMBER:
            val = int(token.value)
            self.eat(TokenType.NUMBER)
            return Literal(val)

        # STRING
        if token.type == TokenType.STRING:
            val = token.value.strip("'")
            self.eat(TokenType.STRING)
            return Literal(val)

        # IDENTIFIER (column)
        if token.type == TokenType.IDENT:
            return self.parse_identifier()

        # Parenthesis
        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            expr = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return expr

        # NULL
        if token.type == TokenType.NULL:
            self.eat(TokenType.NULL)
            return None

        raise SyntaxError(f"Unexpected token {token}")
    
    """def parse_comparison(self):
        col = self.parse_identifier()

        op = self.current().value
        self.eat(self.current().type)

        if self.current().type == TokenType.NUMBER:
            val = self.current().value
            self.eat(TokenType.NUMBER)
        elif self.current().type == TokenType.STRING:
            val = self.current().value
            self.eat(TokenType.STRING)
        elif self.current().type == TokenType.IDENT:
            val = self.parse_identifier()
        else:
            raise SyntaxError("Invalid Comparision Value")
        print("LEFT:", col, "OP:", op, "RIGHT:", val)
        return Where(col, op, val)"""
    """def parse_comparison(self):
        # 1. Parse Left Side
        left = self.parse_identifier()

        # 2. Parse Operator
        op = self.current().value
        # Ensure we only eat if it's actually a comparison operator
        if op in ('=', '>', '<', '!=', '<=', '>='):
            self.eat(self.current().type)
        else:
            return left # Just a literal/identifier

        # 3. Parse Right Side
        if self.current().type == TokenType.IDENT:
            right = self.parse_identifier()
        else:
            right = self.current().value
            self.eat(self.current().type)

        #print(f"DEBUG PARSER -> LEFT: {left} OP: {op} RIGHT: {right}")
        return Where(left, op, right)"""
    def parse_comparison(self):
        left = self.parse_term()

        #  BETWEEN
        if self.current().type == TokenType.BETWEEN:
            self.eat(TokenType.BETWEEN)
            low = self.parse_term()
            self.eat(TokenType.AND)
            high = self.parse_term()

            return BinaryOp(
                BinaryOp(left, ">=", low),
                "AND",
                BinaryOp(left, "<=", high)
            )

        # LIKE
        if self.current().type == TokenType.LIKE:
            self.eat(TokenType.LIKE)
            pattern = self.current().value
            self.eat(TokenType.STRING)
            return BinaryOp(left, "LIKE", pattern)

        # IS NULL
        if self.current().type == TokenType.IS:
            self.eat(TokenType.IS)
            if self.current().type == TokenType.NULL:
                self.eat(TokenType.NULL)
                return BinaryOp(left, "IS NULL", None)

        # NORMAL COMPARISON
        if self.current().type in (
            TokenType.EQ, TokenType.GT, TokenType.LT,
            TokenType.GTE, TokenType.LTE, TokenType.NOT_EQ
        ):
            op = self.current().value
            self.eat(self.current().type)
            right = self.parse_term()
            return BinaryOp(left, op, right)

        return left

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
    
    def parse_drop(self):
        self.eat(TokenType.DROP)
        self.eat(TokenType.TABLE)
        if_exists = False
        if self.current().type == TokenType.IF:
            self.eat(TokenType.IF)
            self.eat(TokenType.EXISTS)
            if_exists = True

        table = self.current().value
        self.eat(TokenType.IDENT)
        # semicolon consumed by top-level parse()
        return DropTable(table, if_exists)

    def parse_delete(self):
        self.eat(TokenType.DELETE)
        self.eat(TokenType.FROM)

        table = self.current().value
        self.eat(TokenType.IDENT)

        where = None
        if self.current().type == TokenType.WHERE:
            where = self.parse_where()

        # semicolon consumed by top-level parse()
        return Delete(table, where)

    def parse_update(self):
        self.eat(TokenType.UPDATE)

        table = self.current().value
        self.eat(TokenType.IDENT)

        self.eat(TokenType.SET)

        updates = []
        while True:
            col = self.current().value
            self.eat(TokenType.IDENT)

            self.eat(TokenType.EQ)

            val = self.current().value
            self.eat(self.current().type)

            updates.append((col, val))

            if self.current().type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            else:
                break

        where = None
        if self.current().type == TokenType.WHERE:
            where = self.parse_where()

        # semicolon consumed by top-level parse()
        return Update(table, updates, where)

    def parse_alter(self):
        self.eat(TokenType.ALTER)
        self.eat(TokenType.TABLE)

        table = self.current().value
        self.eat(TokenType.IDENT)

        if self.current().type == TokenType.ADD:
            self.eat(TokenType.ADD)
            col = self.current().value
            self.eat(TokenType.IDENT)
            col_type = self.current().type
            self.eat(col_type)
            action = "ADD"
            details = (col, col_type)

        elif self.current().type == TokenType.CHANGE:
            self.eat(TokenType.CHANGE)
            old = self.current().value
            self.eat(TokenType.IDENT)
            new = self.current().value
            self.eat(TokenType.IDENT)
            col_type = self.current().type
            self.eat(col_type)
            action = "CHANGE"
            details = (old, new, col_type)

        elif self.current().type == TokenType.MODIFY:
            self.eat(TokenType.MODIFY)
            col = self.current().value
            self.eat(TokenType.IDENT)
            col_type = self.current().type
            self.eat(col_type)
            action = "MODIFY"
            details = (col, col_type)

        else:
            raise SyntaxError("Invalid ALTER")

        # semicolon consumed by top-level parse()
        return Alter(table, action, details)

    def parse_truncate(self):
        self.eat(TokenType.TRUNCATE)
        self.eat(TokenType.TABLE)

        table = self.current().value
        self.eat(TokenType.IDENT)

        # semicolon consumed by top-level parse()
        return Truncate(table)

    def parse_show(self):
        self.eat(TokenType.SHOW)
        self.eat(TokenType.TABLES)
        # semicolon consumed by top-level parse()
        return ShowTables()
    
    def parse_desc(self):
        self.eat(TokenType.DESC)
        self.eat(TokenType.TABLE)

        table = self.current().value
        self.eat(TokenType.IDENT)

        # semicolon consumed by top-level parse()
        return DescTable(table)
    def parse_term(self):
        node = self.parse_factor()

        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current().value
            self.eat(self.current().type)
            right = self.parse_factor()
            node = BinaryOp(node, op, right)

        return node
    def parse_factor(self):
        node = self.parse_primary()

        while self.current().type in (TokenType.STAR, TokenType.DIV, TokenType.MOD):
            op = self.current().value
            self.eat(self.current().type)
            right = self.parse_primary()
            node = BinaryOp(node, op, right)

        return node