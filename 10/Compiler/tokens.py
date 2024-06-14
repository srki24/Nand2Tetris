from enum import Enum


class Tokens(Enum):

    keyword = r"^class|^constructor|^function|^method|^field|^static|^var|^int|^char|^boolean|^void|^true|^false|^null|^this|^let|^do|^if|^else|^while|^return"
    symbol = r"^\{|^\}|^\(|^\)|^\[|^\]|^\.|^\,|^\;|^\+|^\-|^\*|^\/|^\&|^\||^\<|^\>|^\=|^\~" 
    integerConstant = r"^[0-9]+"
    stringConstant = r"^(?:\")(.*?)(?:\")"
    identifier = r"^[A-z][\w]*"
    
    
