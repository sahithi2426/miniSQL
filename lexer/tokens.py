from enum import Enum, auto

class TokenType(Enum):
    CREATE = auto()
    DROP = auto()
    DELETE = auto()
    UPDATE = auto()
    SET = auto()
    TABLE = auto()

    SHOW = auto()
    TABLES = auto()
    
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

    FOREIGN = auto()
    KEY = auto()
    REFERENCES = auto()
    PRIMARY = auto()
    UNIQUE = auto()
    
    JOIN = auto()
    INNER = auto()
    LEFT = auto()
    RIGHT = auto()
    FULL = auto()
    OUTER = auto()
    ON = auto()

    ALTER = auto()
    ADD = auto()
    CHANGE = auto()
    MODIFY = auto()
    TRUNCATE = auto()

    IF = auto()
    EXISTS = auto()
    DESC_TABLE = auto() 
    DOT = auto()

    PLUS = auto()
    DIV = auto()
    MOD = auto()

    BETWEEN = auto()
    LIKE = auto()
    IS = auto()
    NULL = auto()
        
    EOF = auto()


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type.name}({self.value})"
