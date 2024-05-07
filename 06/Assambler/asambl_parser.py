from command_types import CommandType
import re


class ASAMBLParser:

    def __init__(self, file: str):
        self.file = open(file)
        self.command = None
        self.pos = -1
        self.c_type = None

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
            # Recursive call, trying to find actuall data
            self.has_more_commands()

        # Returning to previous position
        self.file.seek(self.pos)
        return True

    def advance(self):
        if self.has_more_commands:
            line = self.file.readline()
            self.command = self._remove_comment(line)
            self.pos = self.file.tell()
            self.c_type = None

    def command_type(self) -> CommandType:
        if self.c_type:
            return self.c_type

        for command_type in CommandType:
            if re.search(command_type.value, self.command):
                self.c_type = command_type
                return self.c_type
        else:
            raise ValueError(f"Unknown command type: {self.command}")


    def symbol(self):

        if self.command_type() == CommandType.C_COMMAND:
            return

        if self.command_type() == CommandType.A_COMMAND:
            _pattern = r"[^@]{1}.*"

        if self.command_type() == CommandType.L_COMMAND:
            _pattern = r"[^(]{1}.*[^)]{1}"

        symbol = re.search(_pattern, self.command)
        return symbol.group(0) if symbol else None

    def dest(self):
        if self.command_type() != CommandType.C_COMMAND or ";" in self.command:
            return ""

        if "=" in self.command:
            return self.command.split("=")[0]

        raise ValueError(f"Failed to parse dest for command: {self.command}")

    def comp(self):
        if self.command_type() != CommandType.C_COMMAND:
            return

        if ";" in self.command:
            return self.command.split(";")[0]

        if "=" in self.command:
            return self.command.split("=")[1]

        raise ValueError(f"Failed to parse comp for command: {self.command}")

    def jump(self):

        if self.command_type() != CommandType.C_COMMAND or "=" in self.command:
            return

        if ";" in self.command:
            return self.command.split(";")[1]

        raise ValueError(f"Failed to parse jump for command: {self.command}")

    def _remove_comment(self, line):
        _comments = "//.*"
        line = re.sub(_comments, "", line)
        line = line.strip()
        return line
