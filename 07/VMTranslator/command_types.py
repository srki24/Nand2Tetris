from enum import Enum


class CommandType(Enum):

    C_ARITHMETICS = r"^add$|^sub$|^neg$|^eq$|^gt$|^lt$|^and$|^or$|^not$"
    C_PUSH = r"^(?:push)(?:\s\w+){2}$" # Push arg1 arg2
    C_POP = r"^(?:pop)(?:\s\w+){2}$"    # Pop arg1 arg2   # r"^pop$|^pop(?:\s\w+)+"
    C_LABEL = 4
    C_GOTO = 5
    C_IF = 6
    C_FUNCTION = 7
    C_RETURN = 8
    C_CALL = 9
