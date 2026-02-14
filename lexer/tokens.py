from enum import Enum, auto

class TokenType(Enum):
    CREATE = auto()
    TABLE = auto()

    INSERT = auto()
    INTO = auto()  
    VALUES = auto()

    SELECT = auto()
    FROM = auto()
    WHERE = auto()
    ORDER =auto()
    BY =auto()
    LIMIT =auto()
    GROUP =auto()
    HAVING =auto()

    IDENT = auto()
    INT = auto()
    TEXT = auto()
    NUMBER = auto()
    STRING = auto()
    
    AND = auto()
    OR = auto()
    NOT = auto()

    COUNT = auto()
    SUM = auto()
    AVG = auto()
    MIN = auto()
    MAX = auto()

    ASC = auto()
    DESC = auto()

    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEMICOLON = auto()

    GT = auto()
    LT = auto()
    EQ = auto()
    NOT_EQ = auto()
    GTE = auto()        
    LTE = auto()        
    STAR = auto()       
    MINUS = auto()

    EOF = auto()


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type.name}({self.value})"
