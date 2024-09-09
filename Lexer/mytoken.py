import string


class Tokens:
    INT = 'INT'
    BOOL = 'BOOL'
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    INTEGER_DIV = '//'
    MOD = '%'
    OR = '||'
    AND = '&&'
    NOT = '!'
    EQUAL = '=='
    NOT_EQUAL = '!='
    LESS = '<'
    LESS_EQUAL = '<='
    GREATER = '>'
    GREATER_EQUAL = '>='
    LEFT_PAREN = '('
    RIGHT_PAREN = ')'
    LEFT_BRACE = '{'
    RIGHT_BRACE = '}'
    TRUE = 'true'
    FALSE = 'false'
    DIGITS = '0123456789'
    LETTERS = string.ascii_letters
    LETTERS_DIGITS = LETTERS + DIGITS
    ASSIGN = '='
    WHITESPACE = ' \t'
    COMMA = ','
    ARROW = '->'
    EOF = 'EOF'
    NEWLINE = 'NEWLINE'
    FUNCTION = 'function'
    STRING = 'STRING'
    IDENTIFIER = 'IDENTIFIER'
    LAMBDA = 'lambda'
    WHILE = 'while'
    KEYWORD = 'KEYWORD'
    COLON = ':'
    RETURN = 'return'
    BREAK = 'break'
    CONTINUE = 'continue'
    KEYWORDS = [WHILE, FUNCTION, RETURN, BREAK, CONTINUE, LAMBDA]


class Token:
    def __init__(self, type, value=None, position_start=None, position_end=None):
        self.type = type
        self.value = value
        if position_start:
            self.position_start = position_start.copy()
            self.position_end = position_start.copy()
            self.position_end.advance()
        if position_end:
            self.position_end = position_end.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
