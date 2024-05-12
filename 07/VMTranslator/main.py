import argparse
import os
import sys
from vm_parser import VMParser
from code_writer import CodeWriter
from command_types import CommandType

def get_filepath():
    argparser = argparse.ArgumentParser(prog="VM translator")
    argparser.add_argument("filename")
    args = argparser.parse_args()

    fp = os.path.join(os.getcwd(), args.filename)
    fp = os.path.normpath(fp)

    return fp



def parse_file(parser: VMParser, code_writer: CodeWriter):

    while parser.has_more_commands():
        parser.advance()

        code_writer.write_command(parser.command)
        if parser.c_type == CommandType.C_ARITHMETICS:
            code_writer.write_arithmetic(parser.command)


        if parser.c_type in [CommandType.C_POP, CommandType.C_PUSH]:
            code_writer.write_push_pop(parser.c_type, parser.arg1(), parser.arg2())
        

        
if __name__ == "__main__":

    fp = get_filepath()
    code_writer = CodeWriter()
    
    if os.path.isfile(fp): # Single file
        if not fp.endswith("vm"):
            raise ValueError("Unknown file type .vm expected")
        
        out_path = fp.replace(".vm", ".asm")
        files = [fp]
            
    else: # Folder
        out_file = os.path.basename(fp) + '.asm' # Single output file based on folder name
        out_path = os.path.join(fp, out_file)
        
        files = [os.path.join(fp,file) for file in os.listdir(fp) if file.endswith('.vm')]
    
    
    if not files:
        raise ValueError("No .vm files found in directory!")
    
    code_writer.set_output_file(out_path)
    
    for file in files:
        parser = VMParser(file)
        code_writer.set_input_file(file)
        
        parse_file(parser, code_writer)

    code_writer.close()