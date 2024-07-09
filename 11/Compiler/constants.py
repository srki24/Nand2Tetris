from enum import Enum

class Constant(Enum):
    ...

class Keywords(Constant):

    CLASS = "class"
    CONSTRUCTOR = "constructor"
    FUNCTION = "function"
    METHOD = "method"
    FIELD = "field"
    STATIC = "static"
    VAR = "var"
    INT = "int"
    CHAR = "char"
    BOOL = "boolean"
    VOID = "void"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    THIS = "this"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"


class Symbols(Constant):

    OPEN_CURLY = "{"
    CLOSE_CURLY = "}"
    OPEN_REG = "("
    CLOSE_REG = ")"
    OPEN_SQUARE = "["
    CLOSE_SQUARE = "]"
    DOT = "."
    COMMA = ","
    SEMICOLON = ";"
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    AND = "&"
    OR = "|"
    LT = "<"
    GT = ">"
    EQ = "="
    NOT = "~"
