from enum import Enum


class CommandType(Enum):
    A_COMMAND = r"^@.+"          # starts with @
    C_COMMAND = r"[=;,+\-\!|&]"  # has some of: =;,+\-\!|&
    L_COMMAND = r"^[\(].+[\)]$"  # words in brackets
