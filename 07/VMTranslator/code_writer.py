import os
import re
from command_types import CommandType


class CodeWriter:

    def __init__(self) -> None:
        self.curr_file = None    
        self.output_file = None
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

    def _get_seg_addr(self, segment):
        #TODO create constants
        mapping = {
            "local":    "LCL",
            "argument": "ARG",
            "this":     "THIS",
            "that":     "THAT",
            "temp":     "5"    # Temp has always address of 5
            }
        segment = mapping.get(segment, segment)
        return segment

    def write_push(self, segment, index):
        seg_addr = self._get_seg_addr(segment)
        
        if segment == "constant":
            self._a_command(index)
            self._c_command("D", "A")       # D = Index
            self._set_sp("D")               # *SP = D (Index)

        if segment in ["local", "argument", "this", "that", "temp"]:
            self._a_command(index)
            self._c_command("D", "A")       # D = Index
            self._a_command(seg_addr)       # @Segment
            
            if segment == "temp":           # Address itself
                self._c_command("A", "D+A") # A = Index + Address
            else:                           # Load address
                self._c_command("A", "D+M") # A = Index + *Segment
            
            self._c_command("D", "M")       # D = *(Index + *Segment)
            self._set_sp("D")               # *SP = D (Index + Segment)
            
        if segment == "pointer":
            point_mapping = {
                "0": "THIS",
                "1": "THAT"
            }
            target = point_mapping[index]
            
            self._a_command(target)         # @Target
            self._c_command("D", "M")       # D = M
            self._set_sp("D")               # *SP = *Target
        
        if segment == "static":
            if not self.curr_file:
                raise ValueError("Current file not set")
            
            target = f"{self.curr_file}.{index}"
            self._a_command(target)         # @ Target
            self._c_command("D", "M")       # D = M
            self._set_sp("D")               # *SP = *Target
        
    def write_pop(self, segment, index):
        seg_addr = self._get_seg_addr(segment)
        
        if segment in ["local", "argument", "this", "that", "temp"]:
            self._a_command(index)          # @Index
            self._c_command("D", "A")       # D = Index

            self._a_command(seg_addr)       # @Segment
            
            if segment == "temp":           # Address itself
                self._c_command("D", "D+A") # D = Index + Address
            else:                           # Load address
                self._c_command("D", "D+M") # D = Index + *Segment
            
            self._a_command("R14")
            self._c_command("M", "D")       # *R14 = Index + Segment
            
            self._pop_sp()
            self._c_command("D", "M")       # D = *SP
            
            self._a_command("R14")       
            self._c_command("A", "M")       # A = *R14

            self._c_command("M", "D")       # *A = *SP
            
        if segment == "pointer":
            point_mapping = {
                "0": "THIS",
                "1": "THAT"
            }
            target = point_mapping[index]
            
            self._pop_sp()               # @SP--
            self._c_command("D", "M")    # D = *SP
            
            self._a_command(target)      # @Target
            self._c_command("M", "D")    # *Target = *(--sp)

        if segment == "static":
            target = f"{self.curr_file}.{index}"
            
            self._pop_sp()               # @SP--
            self._c_command("D", "M")    # D = *SP
            
            self._a_command(target)      # @Target
            self._c_command("M", "D")    # *Target = *(--sp)

    def write_label(self, label):
        ...
        
    def write_goto(self, dest):
        ...
        
    def write_if(self, dest):
        ...
        
    def write_call(self, name, args):
        ...
        
    def write_return(self, addr):
        ...
        
    def write_function(self, name, args):
        ...
        
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
        self._write_to_file(cmd)

    def _c_command(self, dest="", comp="", jmp=""):
        dest = f"{dest}=" if dest else ""
        comp = str(comp)
        jmp = f";{jmp}" if jmp else ""
        cmd = dest + comp + jmp + "\n"
        self._write_to_file(cmd)

    def _l_command(self, label: str):
        if label[0].isnumeric():
            raise ValueError(f"Label name cannot start with a digit! Labem: {label}")
        cmd = f"({label})\n"
        self._write_to_file(cmd)

    def write_command(self, command: str):
        self._write_to_file(f"// {command}\n")
       
    def _write_to_file(self, cmd):
        if not self.output_file:
            raise ValueError("Output file must be set!")
        self.output_file.write(cmd)
        
    def close(self):
        self.__del__()

    def set_output_file(self, file):
        self.output_file = open(file, "w")

    def set_input_file(self, file_path):
        curr_file = os.path.basename(file_path)
        self.curr_file = re.sub(r"\.vm$", "", curr_file)
        
    def __del__(self):
        if self.output_file:
            self.output_file.close()
