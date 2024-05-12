from enum import Enum


class CommandType(Enum):

    C_ARITHMETICS = r"^add$|^sub$|^neg$|^eq$|^gt$|^lt$|^and$|^or$|^not$"
    C_PUSH = r"^(?:push)(?:\s\w+){2}$"         # Push arg1 arg2
    C_POP = r"^(?:pop)(?:\s\w+){2}$"           # Pop arg1 arg2 
    C_LABEL = r"^(?:label)(?:\s\w+){1}$"       # label label_name
    C_GOTO = r"^(?:goto)(?:\s\w+){1}$"         # goto label
    C_IF = r"^(?:if-goto)(?:\s\w+){1}$"        # if-goto label
    C_FUNCTION = r"^(?:function)(?:\s\S+){2}$" # function fn.name nr of args
    C_RETURN = r"^(?:return)$"                 # return
    C_CALL = r"^(?:call)(?:\s\S+){2}$"         # call fn.name nr of args
