import os
import re
from command_types import CommandType


class CodeWriter:

    def __init__(self, file) -> None:

        file_name = os.path.basename(file)
        self.file_name = re.sub(r"\.vm$", "", file_name)
        self.file = open(file, "w")
        self.label_count = 0
            
    def write_arithmetic(self, command: str):
        command_mappings = {
             "add": "+",
             "sub":"-", 
             "neg":"-", 
             "eq":"JEQ",
             "gt":"JGT",
             "lt":"JLT",
             "and":"&", 
             "or":"|", 
             "not":"!"
             }
        cmd = command_mappings[command]
        if command in ["add", "sub", "and", "or"]:
            
            self._pop_sp()                    # Y
            self._c_command("D", "M")         # D = *Y

            self._dec_sp()                    # X
            self._set_sp(f"M{cmd}D")          # *X [+,-,&,|] *Y
            
        if command in ["neg", "not"]:
            self._dec_sp()                    # Y
            self._set_sp(f"{cmd}M")           # [-,&,|,!] *Y
            
        if command in ["eq", "gt", "lt"]:
            #TODO add constants
            true_label = "TRUE_LABEL" + str(self.label_count)
            cont_label = "CONT_LABEL" + str(self.label_count)
            self.label_count +=1

            self._pop_sp()                     # X
            self._c_command("D", "M")          # D = *X

            self._pop_sp()                     # Y
            self._c_command("D", "M-D")        # D = *Y - *X

            self._a_command(true_label)        
            self._c_command(comp="D", jmp=cmd) # Compare & JMP to true

            self._set_sp("0")                   # False
            self._a_command(cont_label)         
            self._c_command(comp=0, jmp="JMP")  # Continue

            self._l_command(true_label)  # True
            self._set_sp("-1")

            self._l_command(cont_label)  # Continue

    def write_push_pop(self, command_type: CommandType, segment: str, index: int):
        #TODO create constants
        mapping = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
            "constant": "CONST",
            "temp": "TEMP",
            "pointer": "POINT",
            "static": "STATIC"
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
        
        if segment in ["LCL", "ARG", "THIS", "THAT"]:
            self._a_command(index)
            self._c_command("D", "A")   # D = Index
            self._a_command(segment)    # @Segment
            self._c_command("A", "D+M") # A = Index + *Segment
            self._c_command("D", "M")   # D = *(Index + *Segment)
            self._set_sp("D")           # *SP = D (Index + Segment)
            
        if segment == "POINT":
            point_mapping = {
                "0": "THIS",
                "1": "THAT"
            }
            target = point_mapping[index]
            
            self._a_command(target)     # @Target
            self._c_command("D", "M")   # D = M
            self._set_sp("D")           # *SP = *Target
        
        if segment == "STATIC":
            target = f"{self.file_name}.{index}"
            self._a_command(target)          # @ Target
            self._c_command("D", "M")        # D = M
            self._set_sp("D")                # *SP = *Target
        
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
            
        if segment == "TEMP":
            
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
            
        if segment == "POINT":
            point_mapping = {
                "0": "THIS",
                "1": "THAT"
            }
            target = point_mapping[index]
            
            self._pop_sp()               # @SP--
            self._c_command("D", "M")    # D = *SP
            
            self._a_command(target)      # @Target
            self._c_command("M", "D")    # *Target = *(--sp)

        if segment == "STATIC":
            target = f"{self.file_name}.{index}"
            self._pop_sp()               # @SP--
            self._c_command("D", "M")    # D = *SP
            
            self._a_command(target)      # @Target
            self._c_command("M", "D")    # *Target = *(--sp)

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
        
    def _a_command(self, segment):
        cmd = f"@{str(segment)}\n"
        self.file.write(cmd)

    def _c_command(self, dest="", comp="", jmp=""):
        dest = f"{dest}=" if dest else ""
        comp = str(comp)
        jmp = f";{jmp}" if jmp else ""
        cmd = dest + comp + jmp + "\n"
        self.file.write(cmd)

    def _l_command(self, label: str):
        if label[0].isnumeric():
            raise ValueError(f"Label name cannot start with a digit! Labem: {label}")
        cmd = f"({label})\n"
        self.file.write(cmd)

    def write_command(self, command: str):
        self.file.write(f"// {command}\n")
        
    def close(self):
        self.__del__()

    def __del__(self):
        self.file.close()
