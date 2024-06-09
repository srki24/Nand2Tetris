from enum import Enum


class Tokens(Enum):

    KEYWORD = r"^class|^constructor|^function|^method|^field|^static|^var|^int|^char|^boolean|^void|^true|^false|^null|^this|^let|^do|^if|^else|^while|^return"
    SYMBOL = r"^\{|^\}|^\(|^\)|^\[|^\]|^\.|^\,|^\;|^\+|^\-|^\*|^\/|^\&|^\||^\<|^\>|^\=|^\~" 
    INTEGER = r"^[0-9]+"
    STRING = r"^\".*?\""
    IDENTIFIER = r"^[A-z][\w]*"
    
    
