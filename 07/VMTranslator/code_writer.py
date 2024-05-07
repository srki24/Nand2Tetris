from command_types import CommandType


class CodeWriter:

    def __init__(self, file) -> None:

        self.file = open(file, "w")
        self.label_count = 0

    def write_arithmetic(self, command: str):
        match command:
            case "add":
                self._binary("+")
            case "sub":
                self._binary("-")
            case "neg":
                self._unary("-")
            case "eq":
                self._compare("JEQ")  # true -1 false 0
            case "gt":
                self._compare("JGT")
            case "lt":
                self._compare("JLT")
            case "and":
                self._binary("&")
            case "or":
                self._binary("|")
            case "not":
                self._unary("!")

    def _new_label(self, name):
        label = name + str(self.label_count)
        self.label_count += 1
        return label

    def _compare(self, cond):
        # True -1 False 0

        true_label = self._new_label("TRUE_LABEL")
        cont_label = self._new_label(("CONT_LABEL"))

        # Loading data
        self._dec_sp()
        self._load_sp()
        self._c_command("D", "M")

        self._dec_sp()
        self._load_sp()
        self._c_command("D", "M-D")  # D = Y - X

        # JMP to true
        self._a_command(true_label)
        self._c_command(comp="D", jmp=cond)

        # Else jmp to continue
        self._set_sp("0") # False
        self._a_command(cont_label)
        self._c_command(comp=0, jmp="JMP")

        # True
        self._l_command(true_label)
        self._set_sp("-1") # True

        # Continue
        self._l_command(cont_label)

    def _binary(self, command):
        self._dec_sp()  # y

        self._load_sp()
        self._c_command("D", "M")

        self._dec_sp()  # x
        self._set_sp(f"M{command}D")

    def _unary(self, command):
        self._dec_sp()  # y
        self._set_sp(f"{command}M")

    def write_push_pop(self, command_type: CommandType, segment: str, index: int):
        if command_type == CommandType.C_PUSH:
            self._push(segment, index)

        if command_type == CommandType.C_POP:
            self._pop(segment, index)

    def _push(self, segment, index):

        self._a_command(index)
        self._c_command("D", "A")  # index into D

        #TODO: TEMP base address is always 5
        #TODO: STATIC fille foo.vm push static 5 => creates foo.5 variable 
        #TODO: pointer fixed memory segment, has 0 and 1 => pointer 0 should result in accesing THIS and 1 should result in acessing THAT (changes base address of this or that)
        
        if segment != "constant": #TODO this works for lcl arg this that
            self._a_command(segment)  # Get segtment addr
            self._c_command("A", "D+A")  # Add index and get new addres
            self._c_command("D", "M")  # Get data into D

        self._set_sp("D")

    def _pop(self, segment, index):

        self._a_command(index)
        self._c_command("D", "A")  # index into D

        self._a_command(segment)
        self._c_command("D", "D+A")  # Address set to segment + idx

        self._dec_sp()
        self._load_sp()

        self._c_command("D", "M")  # Data in D

    def _dec_sp(self):
        self._a_command("SP")
        self._c_command("M", "M-1")

    def _inc_sp(self):
        self._a_command("SP")
        self._c_command("M", "M+1")

    def _load_sp(self):
        self._a_command("SP")
        self._c_command("A", "M")
        
    def _set_sp(self, val):
        self._load_sp()
        self._c_command("M", val)
        self._inc_sp()

    def _a_command(self, segment):
        cmd = f"@{str(segment)}\n"
        self.file.write(cmd)

    def _c_command(self, dest="", comp="", jmp=""):

        dest = f"{dest}=" if dest else ""
        comp = str(comp)
        jmp = f";{jmp}" if jmp else ""
        cmd = dest + comp + jmp + "\n"
        self.file.write(cmd)

    def _l_command(self, label):
        cmd = f"({label})\n"
        self.file.write(cmd)

    def close(self):
        self.__del__()

    def __del__(self):
        self.file.close()
