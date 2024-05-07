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
        self._pop_sp()              # X
        self._c_command("D", "M")   # D = *X

        self._pop_sp()              # Y
        self._c_command("D", "M-D") # D = *Y - *X

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
        
        self._pop_sp()               # Y
        self._c_command("D", "M")    # D = *Y

        self._dec_sp()               # X
        self._set_sp(f"M{command}D") # *X [+,-,&,|] *Y

    def _unary(self, command):
        self._dec_sp()               # Y
        self._set_sp(f"{command}M")  # [-,&,|,!] *Y

    def write_push_pop(self, command_type: CommandType, segment: str, index: int):
        
        mapping = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
            "constant": "CONST",
            "temp": "TEMP"
            }
        segment = mapping.get(segment, segment)
        
        if command_type == CommandType.C_PUSH:
            self.push(segment, index)

        if command_type == CommandType.C_POP:
            self.pop(segment, index)

    def push(self, segment, index):

        if segment == "CONST":
            self._a_command(index)
            self._c_command("D", "A")   # D = Index
            self._set_sp("D")           # *SP = D (Index)

        if segment == "TEMP":
            
            self._a_command(index)
            self._c_command("D", "A")   # D = Index
            self._a_command("5")        # @5
            self._c_command("A", "D+A") # A = Index + 5
            self._c_command("D", "M")   # D = *Index + 5
            self._set_sp("D")           # *SP = *D (Index+5)


        #TODO: STATIC fille foo.vm push static 5 => creates foo.5 variable 
        #TODO: pointer fixed memory segment, has 0 and 1 => pointer 0 should result in accesing THIS and 1 should result in acessing THAT (changes base address of this or that)
        
        if segment in ["LCL", "ARG", "THIS", "THAT"]:
            self._a_command(index)
            self._c_command("D", "A")   # D = Index
            self._a_command(segment)    # @Segment
            self._c_command("A", "D+M") # A = Index + *Segment
            self._c_command("D", "M")   # D = *(Index + *Segment)
            self._set_sp("D")           # *SP = D (Index + Segment)

    def pop(self, segment, index):
        if segment in ["LCL", "ARG", "THIS", "THAT"]:
            self._a_command(index)       # @Index
            self._c_command("D", "A")    # D = Index

            self._a_command(segment)     # @Segment
            self._c_command("D", "D+M")  # D = Index + *Segment
            
            self._a_command("R14")
            self._c_command("M", "D")    # *R14 = Index + Segment
            
            self._pop_sp()
            self._c_command("D", "M")    # D = *SP
            
            self._a_command("R14")       
            self._c_command("A", "M")    # A = *R14

            self._c_command("M", "D")    # *A = *SP
            
        if segment in ["TEMP"]:
            
            self._a_command(index)       # Index
            self._c_command("D", "A")    # D = Index
            
            self._a_command("5")         # @5 - Temp always start at 5
            self._c_command("D", "A+D")  # D = 5 + Index

            self._a_command("R14")     
            self._c_command("M", "D")    # *R14 = 5 + Index
            
            self._pop_sp()
            self._c_command("D", "M")    # D = *SP
            
            self._a_command("R14")       
            self._c_command("A", "M")    # A = *R14

            self._c_command("M", "D")    # *A = *SP
                   
        

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

    def _pop_sp(self):
        self._dec_sp()
        self._c_command("A", "M")
        # self._load_sp()
        
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


    def write_command(self, command):
        self.file.write(f"\\\\ {command}\n")
        
    def close(self):
        self.__del__()

    def __del__(self):
        self.file.close()
