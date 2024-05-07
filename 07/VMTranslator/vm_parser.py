import re
from command_types import CommandType


class VMParser:

    def __init__(self, file) -> None:
        self.file = open(file)
        self.command = None
        self.c_type = None
        self.pos = -1

    def __del__(self):
        self.file.close()

    def has_more_commands(self) -> bool:
        line = self.file.readline()
        line = self._remove_comment(line)

        if not line:
            pos = self.file.tell()
            if self.pos == pos:
                # EOF
                return False
            # Advancing over non relevant lines
            self.pos = pos
            # Recursive call, trying to find actuall line
            self.has_more_commands()

        # Returning to previous position
        self.file.seek(self.pos)
        return True

    def advance(self):
        if self.has_more_commands():
            line = self.file.readline()
            self.command = self._remove_comment(line)
            self.pos = self.file.tell()
            self.c_type = self.command_type()

    def command_type(self) -> CommandType:

        for command_type in CommandType:
            if re.search(command_type.value, self.command):
                self.c_type = command_type
                return self.c_type
        else:
            raise ValueError(f"Unknown command type: {self.command}")

    def command(self):
        return self.command
    
    def arg1(self):
        if self.c_type == CommandType.C_RETURN:
            return

        if self.c_type == CommandType.C_ARITHMETICS:
            return self.command

        return self.command.split(" ")[1]

    def arg2(self):
        if self.command_type() in [
            CommandType.C_POP,
            CommandType.C_PUSH,
            CommandType.C_FUNCTION,
        ]:
            return self.command.split(" ")[2]

    def _remove_comment(self, line):
        _comments = "//.*"
        line = re.sub(_comments, "", line)
        line = line.strip()
        return line
