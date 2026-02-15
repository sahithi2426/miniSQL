import re
from lexer.tokens import Token, TokenType

KEYWORDS = {
    "CREATE": TokenType.CREATE,
    "TABLE": TokenType.TABLE,
    "INSERT": TokenType.INSERT,
    "INTO": TokenType.INTO,
    "VALUES": TokenType.VALUES,
    "SELECT": TokenType.SELECT,
    "FROM": TokenType.FROM,
    "WHERE": TokenType.WHERE,
    "ORDER": TokenType.ORDER,
    "BY": TokenType.BY,
    "LIMIT": TokenType.LIMIT,
    "GROUP": TokenType.GROUP,
    "HAVING": TokenType.HAVING,
    "INT": TokenType.INT,
    "TEXT": TokenType.TEXT,
    "AND": TokenType.AND,
    "OR": TokenType.OR,
    "NOT": TokenType.NOT,
    "COUNT": TokenType.COUNT,
    "SUM": TokenType.SUM,
    "AVG": TokenType.AVG,
    "MIN": TokenType.MIN,
    "MAX": TokenType.MAX,
    "ASC": TokenType.ASC,
    "DESC": TokenType.DESC,
}

TOKEN_SPEC = [
    ("NUMBER", r"\d+"),
    ("STRING", r"'[^']*'"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("COMMENT", r"--.*"), 
    ("COMMA", r","),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("SEMICOLON", r";"),
    ("NOT_EQ", r"<>|!="),
    ("GTE", r">="),
    ("LTE", r"<="),
    ("GT", r">"),
    ("LT", r"<"),
    ("EQ", r"="),
    ("STAR", r"\*"),
    ("SKIP", r"[ \t\n]+"),
]

class Lexer:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        tokens = []
        pos = 0
        line = 1

        while pos < len(self.text):
            match = None
            for tok_type, pattern in TOKEN_SPEC:
                regex = re.compile(pattern)
                match = regex.match(self.text, pos)
                if match:
                    value = match.group(0)
                    if tok_type == "SKIP" or tok_type=="COMMENT":
                        pass
                    elif tok_type == "IDENT":
                        upper = value.upper()
                        token_type = KEYWORDS.get(upper, TokenType.IDENT)
                        tokens.append(Token(token_type, value))
                    else:
                        tokens.append(Token(TokenType[tok_type], value))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Unexpected character '{self.text[pos]}' at line {line}")
        tokens.append(Token(TokenType.EOF))
        return tokens
