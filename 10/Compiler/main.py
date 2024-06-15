import argparse
import os
from xml.dom.minidom import Document
from compiler import JackCompiler
from tokenizer import JackTokenizer


def get_filepath():
    argparser = argparse.ArgumentParser(prog="VM translator")
    argparser.add_argument("filename")
    args = argparser.parse_args()

    fp = os.path.join(os.getcwd(), args.filename)
    fp = os.path.normpath(fp)

    return fp


def tokenize(file):
    tokenizer = JackTokenizer(file=file)
    while tokenizer.has_more_tokens():
        tokenizer.advance()
        yield tokenizer


def _generate_tokens(file):

    doc = Document()
    root = doc.createElement("tokens")
    doc.appendChild(root)
    for tok in tokenize(file):

        element = doc.createElement(tok.token.name)
        element.appendChild(doc.createTextNode(f" {tok.value} "))
        root.appendChild(element)

    tree = root.toprettyxml(indent="")
    with open(file.replace(".jack", "-test.xml"), "w") as output:
        output.write(tree)


if __name__ == "__main__":

    fp = get_filepath()

    # Single file
    if os.path.isfile(fp):
        if not fp.endswith(".jack"):
            raise ValueError("Unknow file type .jack expected")

        files = [fp]

    # Directory
    else:
        files = [
            os.path.join(fp, file) for file in os.listdir(fp) if file.endswith(".jack")
        ]

    if not files:
        raise ValueError("No .jack files found!")

    for file in files:
        _generate_tokens(file)
