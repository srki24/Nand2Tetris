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

    return fp



def parse_file(fp):
    if not fp.endswith(".vm"):
        raise ValueError("Unknown file type .vm expected")

    parser = VMParser(fp)
    
    out_fp = fp.replace('.vm', '.asm')
    code_writer = CodeWriter(out_fp)
    
    while parser.has_more_commands():
        parser.advance()

        if parser.c_type == CommandType.C_ARITHMETICS:
            code_writer.write_arithmetic(parser.command)


        if parser.c_type in [CommandType.C_POP, CommandType.C_PUSH]:
            code_writer.write_push_pop(parser.c_type, parser.arg1(), parser.arg2())

        
if __name__ == "__main__":

    fp = get_filepath()
    
    # Single file
    if os.path.isfile(fp):
        parse_file(fp)
        sys.exit()
    
    # Folder
    files = [file for file in os.listdir(fp) if file.endswith('.vm')]
    if not files:
        raise ValueError("No .vm files found in directory!")
    for file in files:
        parse_file(os.path.join(fp, file))
