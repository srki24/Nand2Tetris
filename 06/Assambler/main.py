import argparse
import os

from asambl_parser import ASAMBLParser
from command_types import CommandType
from translator import Translator
from symbols_table import Symbols


def pass1(fp: str, symbols: Symbols):
    parser = ASAMBLParser(fp)

    counter = 0

    while parser.has_more_commands():
        parser.advance()
        s = parser.symbol()

        if parser.command_type() == CommandType.L_COMMAND:
            symbols.add_entry(symbol=s, address=counter)
            continue

        counter += 1


def pass2(fp: str, symbols: Symbols):
    code = Translator()
    parser = ASAMBLParser(fp)

    f = open(fp.replace(".asm", ".hack"), mode="w")

    while parser.has_more_commands():
        parser.advance()

        cmd = None
        address = None
        if parser.command_type() == CommandType.A_COMMAND:
            sym = parser.symbol()

            if sym.isnumeric():
                address = sym
            if symbols.contains(sym):
                address = symbols.get_address(sym)
            if address is None:
                address = symbols.EMPTY_SLOT
                symbols.add_entry(sym, address)
                # This is an error, might overwrite existing address
                symbols.EMPTY_SLOT += 1

            cmd = code.addr(address)
        if parser.command_type() == CommandType.C_COMMAND:
            cmd = (
                "111"
                + code.comp(parser.comp())
                + code.dest(parser.dest())
                + code.jump(parser.jump())
            )

        if parser.command_type() == CommandType.L_COMMAND:
            continue

        if not cmd:
            raise ValueError(f"Unknown command type. Failed to parse {parser.command}")
        f.write(cmd + "\n")

    f.close()


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(prog="Assambler")

    argparser.add_argument("filename")
    args = argparser.parse_args()
    fp = os.path.join(os.getcwd(), args.filename)

    symbols_table = Symbols()
    pass1(fp, symbols_table)
    pass2(fp, symbols_table)
