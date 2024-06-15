from typing import Generator
from tokens import Tokens
from tokenizer import JackTokenizer

class JackCompiler:

    def __init__(self, file):
        self.file = file
        self.tokenizer = JackTokenizer(file)

        self.tokenizer.tokenize()

    # def consume(self) -> JackTokenizer:
    #     return next(self.tokens)
    
    # def compile_class(self):
        
    #     tok = self.consume()

    