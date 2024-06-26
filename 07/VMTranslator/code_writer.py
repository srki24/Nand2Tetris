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
            
            self._pop_reg("SP")               # D = *Y

            self._dec_reg("SP")               # X
            self._push_sp(f"M{cmd}D")         # *X [+,-,&,|] *Y
            
        if command in ["neg", "not"]:
            self._dec_reg("SP")               # Y
            self._push_sp(f"{cmd}M")          # [-,&,|,!] *Y
            
        if command in ["eq", "gt", "lt"]:
            #TODO add constants
            true_label = self._create_label("TRUE_LABEL") 
            cont_label = self._create_label("CONT_LABEL")
            self.label_count +=1

            self._pop_reg("SP")                # D = *X

            self._dec_reg("SP")                # Y
            self._c_command("A", "M")
            self._c_command("D", "M-D")        # D = *Y - *X

            self._a_command(true_label)        
            self._c_command(comp="D", jmp=cmd) # Compare & JMP to true

            self._push_sp("0")                 # False
            self._a_command(cont_label)         
            self._c_command(comp=0, jmp="JMP") # Continue

            self._l_command(true_label)        # True
            self._push_sp("-1")

            self._l_command(cont_label)        # Continue

    def _create_label(self, label):
        label = f"{label}${str(self.label_count)}"
        self.label_count +=1
        return label
    
    def _get_seg_addr(self, segment):
        #TODO create constants
        mapping = {
            "local":    "LCL",
            "argument": "ARG",
            "this":     "THIS",
            "that":     "THAT",
            "temp":     "5" 
            }
        segment = mapping.get(segment, segment)
        return segment

    def write_push(self, segment, index):
        seg_addr = self._get_seg_addr(segment)
        
        if segment == "constant":
            self._load_addr(index)          # D = @Index
            self._push_sp("D")              # *SP = D (Index)

        if segment in ["local", "argument", "this", "that", "temp"]:
            
            self._load_addr(index)          # D = @Index
            self._a_command(seg_addr)       # @Segment
            
            if segment == "temp":           # Address itself
                self._c_command("A", "D+A") # A = Index + Address
            else:                           # Load address
                self._c_command("A", "D+M") # A = Index + *Segment
            
            self._c_command("D", "M")       # D = *(Index + *Segment)
            self._push_sp("D")              # *SP = D (Index + Segment)
            
        if segment == "pointer":
            point_mapping = {
                "0": "THIS",
                "1": "THAT"
            }
            target = point_mapping[index]
            
            self._load_reg(target)          # D = @Target
            self._push_sp("D")              # *SP = *Target
        
        if segment == "static":
            if not self.curr_file:
                raise ValueError("Current file not set")
            
            target = f"{self.curr_file}.{index}"
            self._load_reg(target)          # @ Target
            self._push_sp("D")              # *SP = *Target
        
    def write_pop(self, segment, index):
        seg_addr = self._get_seg_addr(segment)
        temp_pop = self._create_label("TEMP_POP")
        if segment in ["local", "argument", "this", "that", "temp"]:
            self._load_addr(index)          # D = @Index

            self._a_command(seg_addr)       # @Segment
            
            if segment == "temp":           # Address itself
                self._c_command("D", "D+A") # D = Index + Address
            else:                           # Load address
                self._c_command("D", "D+M") # D = Index + *Segment
           
            self._set_reg("R14", "D")       # *R14 = Index + Segment
            
            self._pop_reg("SP")             # D = *SP
            
            self._a_command("R14")       
            self._c_command("A", "M")       # A = *R14

            self._c_command("M", "D")       # *A = *SP
            
        if segment == "pointer":
            point_mapping = {
                "0": "THIS",
                "1": "THAT"
            }
            target = point_mapping[index]
            
            self._pop_reg("SP")              # D = *SP
            self._set_reg(target, "D")       # Target = *SP

        if segment == "static":
            target = f"{self.curr_file}.{index}"
            self._pop_reg("SP")              # D = *SP
            self._set_reg(target, "D")            # Target = *SP

    def write_label(self, label):
        self._l_command(label)               # (Label)
        
    def write_goto(self, dest):
        self._a_command(dest)                # @Dest 
        self._c_command(comp=0, jmp="JMP")   # JMP
        
    def write_if(self, dest):
        self._pop_reg("SP")                  # D = *SP
        self._a_command(dest)                # @Dest
        self._c_command(comp="D", jmp="JNE") # *SP != 0; JMP
       
    def write_init(self):
        self._load_addr("256")
        self._set_reg("SP", "D")
        self.write_call("Sys.init", 0)
            
    def write_call(self, name, args):
        #TODO: ADD CONSTANT
        ret = self._create_label(f"RETURN_{name}")
        
        # Ret
        self._load_addr(ret)     # D = @RET
        self._push_sp("D")       # SP = @RET
        
        # LCL
        self._load_reg("LCL")    # D = *LCL
        self._push_sp("D")       # SP = *LC
        
        # ARG
        self._load_reg("ARG")     # D = *ARG
        self._push_sp("D")        # SP = *ARG
          
        # THIS
        self._load_reg("THIS")    # D = *THIS
        self._push_sp("D")        # SP = *THAT
        
        # THAT
        self._load_reg("THAT")    # D = *THAT
        self._push_sp("D")        # SP = *THAT
      
        # LCL = *SP
        self._load_reg("SP")      # D = *SP
        self._set_reg("LCL", "D") # LCL = *SP 
        
        # ARG
        self._load_reg("SP")          # D = *SP
        self._a_command(5+int(args))  # A = 5 + args
        self._c_command("D", "D-A")   # D = *SP - A
        self._set_reg("ARG", "D")     # ARG = *SP - args - 5
        
        # JMP to function
        self.write_goto(name)
        
        # (Ret)
        self._l_command(ret)
        
    def write_return(self):
        
        # FRAME
        self._load_reg("LCL")              # D = *LCL
        self._set_reg("R14", "D")          # R14 = *LCL
      
        # Return address 
        self._load_reg("LCL")               # @LCL
        self._a_command("5")
        self._c_command("A", "D-A")         # A = *LCL - 5
        self._c_command("D", "M")           # D = *(*LCL-5)
        self._set_reg("R15", "D")
       
        # Updating SP
        self._pop_reg("SP")                 # D = *SP
        self._a_command("ARG")              # @ARG
        self._c_command("A", "M")           # A = *ARG
        self._c_command("M", "D")           # *A = *SP
        self._c_command("D", "A+1")         # D = A+1
        self._set_reg("SP", "D")            # SP = *ARG + 1

        # THAT
        self._pop_reg("R14")                # D = *R14 -1
        self._set_reg("THAT", "D")          # *THAT = *(*FRAME - 1)
        
        # THIS
        self._pop_reg("R14")                # D = *R14-1
        self._set_reg("THIS", "D")          # *THIS = *FRAME - 2
        
        # ARG
        self._pop_reg("R14")                # D = *R14-1
        self._set_reg("ARG", "D")           # *ARG = *FRAME - 3
        
        # LCL
        self._pop_reg("R14")                # D = *R14-1
        self._set_reg("LCL", "D")           # *LCL = *FRAME - 4
       
        # Return address (PC)
        self._load_reg("R15")
        self._c_command("A", "M")
        self._c_command(comp=0, jmp="JMP")
        
    def write_function(self, name, args):
        self._l_command(name) 
        for _ in range(int(args)):
            self._push_sp("0")
        
    def _dec_reg(self, reg):
        self._set_reg(reg, "M-1")
    
    def _set_reg(self, reg, val):
        self._a_command(reg)
        self._c_command("M", val)
   
    def _load_reg(self, reg):
        self._a_command(reg)
        self._c_command("D", "M")
    
    def _load_addr(self, reg):
        self._a_command(reg)
        self._c_command("D", "A")
       
    def _push_sp(self, val):
        self._a_command("SP")
        self._c_command("M", "M+1")
        self._c_command("A", "M-1")
        self._c_command("M", val)

    def _pop_reg(self, reg):
        self._dec_reg(reg)
        self._c_command("A", "M")
        self._c_command("D", "M")
        
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
            raise ValueError(f"Label name cannot start with a digit! Label: {label}")
        cmd = f"({label})\n"
        self._write_to_file(cmd)

    def write_comment(self, comment: str):
        self._write_to_file(f"// {comment}\n")
       
    def _write_to_file(self, cmd):
        if not self.output_file:
            raise ValueError("Output file must be set!")
        self.output_file.write(cmd)
        
    def set_output_file(self, file):
        self.output_file = open(file, "w")

    def set_input_file(self, file_path):
        curr_file = os.path.basename(file_path)
        self.curr_file = re.sub(r"\.vm$", "", curr_file)
        
    def __del__(self):
        if self.output_file:
            self.output_file.close()
