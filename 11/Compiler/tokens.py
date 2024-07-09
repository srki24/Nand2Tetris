from enum import Enum
from constants import Keywords, Symbols

class Tokens(Enum):

    keyword = '|'.join('^'+ x.value for x in Keywords)
    symbol = '|'.join('^\\'+ x.value for x in Symbols)
    integerConstant = r"^[0-9]+"
    stringConstant = r"^(?:\")(.*?)(?:\")"
    identifier = r"^[A-z][\w]*"
    
    
