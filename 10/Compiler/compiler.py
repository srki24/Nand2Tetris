from typing import List, Optional
from xml.dom.minidom import Document, Node

from constants import Keywords, Symbols, Constant
from tokens import Tokens

from tokenizer import JackTokenizer


class JackCompiler:

    def __init__(self, file):
        self.file = file
        self.tokenizer = JackTokenizer(file)
        self.doc = Document()

    def _xml_add_element(self, parent: Node, tag: str, value: Optional[str] = None):
        element = self.doc.createElement(tag)

        if value:
            val = self.doc.createTextNode(f" {value} ")
            element.appendChild(val)

        parent.appendChild(element)
        return element

    def consume(
        self,
        parent,
        token: Optional[Tokens] = None,
        const: Optional[Constant] | Optional[list[Constant]] = None
    ):
        tok_check = self.is_next(token=token, const=const)
        self.tokenizer.advance()

        actual_tok = self.tokenizer.token.name
        actual_val = self.tokenizer.value

        if not tok_check:
            raise TypeError(
                f"Expected token: {token}; constants: {const}",
                f"Got token: {actual_tok}; constant: {actual_val}"
            )

        self._xml_add_element(parent=parent, tag=actual_tok, value=actual_val)
        print(actual_tok, actual_val)

    def compile_class(self):
        CLASS = self._xml_add_element(self.doc, "class")

        self.consume(parent=CLASS, const=Keywords.CLASS)

        self.consume(parent=CLASS, token=Tokens.identifier)

        self.consume(parent=CLASS, const=Symbols.OPEN_CURLY)

        while self.is_next(const=[Keywords.STATIC, Keywords.FIELD]):
            self.compile_class_var_dec(parent=CLASS)

        while self.is_next(const=[Keywords.CONSTRUCTOR, Keywords.FUNCTION, Keywords.METHOD]):
            self.compile_subroutine_dec(parent=CLASS)

        self.consume(parent=CLASS, const=Symbols.CLOSE_CURLY)

    def compile_class_var_dec(self, parent: Node):

        CLASS_VAR_DEC = self._xml_add_element(parent=parent, tag="classVarDec")

        self.consume(parent=CLASS_VAR_DEC, const=[Keywords.STATIC,
                                                        Keywords.FIELD])

        self.compile_type(CLASS_VAR_DEC)

        self.consume(parent=CLASS_VAR_DEC, token=Tokens.identifier)

        while self.is_next(const=Symbols.COMMA):
            self.consume(parent=CLASS_VAR_DEC, const=Symbols.COMMA)
            self.consume(parent=CLASS_VAR_DEC, token=Tokens.identifier)

    def compile_type(self, parent: Node):

        const = [Keywords.INT, Keywords.CHAR, Keywords.BOOL]
        tok = Tokens.identifier

        if self.is_next(const=const):
            tok = None
        elif self.is_next(token=Tokens.identifier):
            const = None
        else:
            raise TypeError(
                f"Failed to compile TYPE. ",
                f"Expect either Symbol[INT, CHAR, BOOL] or Class Identifier got ",
                f"token: {self.tokenizer.next_token.name}, constant: '{self.tokenizer.next_value}'"
            )

        self.consume(parent=parent, token=tok, const=const)

    def compile_subroutine_dec(self, parent: Node):

        SUB_DEC = self._xml_add_element(parent=parent, tag="subroutineDec")

        self.consume(parent=SUB_DEC, const=[Keywords.CONSTRUCTOR,
                                                  Keywords.FUNCTION,
                                                  Keywords.METHOD])

        if self.is_next(const=Keywords.VOID):
            self.consume(parent=SUB_DEC, const=Keywords.VOID)
        else:
            self.compile_type(parent=SUB_DEC)

        self.consume(parent=SUB_DEC, token=Tokens.identifier)

        self.consume(parent=SUB_DEC, const=Symbols.OPEN_REG)

        self.compile_parameter_list(parent=SUB_DEC)

        self.consume(parent=SUB_DEC, const=Symbols.CLOSE_REG)

        self.compile_subroutine_body(parent=SUB_DEC)

    def compile_parameter_list(self, parent: Node):
        PARAM_LIST = self._xml_add_element(parent=parent,
                                           tag="parameterList")

        const = [Keywords.INT, Keywords.CHAR, Keywords.BOOL]
        tok = Tokens.identifier

        if (self.is_next(const=const) or self.is_next(token=tok)):

            self.compile_type(parent=PARAM_LIST)

            self.consume(parent=PARAM_LIST, token=Tokens.identifier)

            while self.is_next(const=[Symbols.COMMA]):

                self.consume(parent=PARAM_LIST, const=Symbols.COMMA)
                self.compile_type(parent=PARAM_LIST)
                self.consume(parent=PARAM_LIST, token=Tokens.identifier)

    def compile_subroutine_body(self, parent: Node):
        SUB_BODY = self._xml_add_element(parent=parent, tag="subroutineBody")

        self.consume(parent=SUB_BODY, const=Symbols.OPEN_CURLY)

        if self.is_next(const=Keywords.VAR):
            self.compile_var_dec(parent=SUB_BODY)

        self.compile_statements(SUB_BODY)

        self.consume(parent=SUB_BODY, const=Symbols.CLOSE_CURLY)

    def compile_var_dec(self, parent: Node):
        VAR_DEC = self._xml_add_element(parent=parent,
                                        tag="varDec")

        self.consume(parent=VAR_DEC, const=Keywords.VAR)
        self.compile_type(VAR_DEC)
        self.consume(parent=VAR_DEC, token=Tokens.identifier)

        while self.is_next(const=Symbols.COMMA):

            self.consume(parent=VAR_DEC, const=Symbols.COMMA)
            self.consume(parent=VAR_DEC, token=Tokens.identifier)

        self.consume(parent=VAR_DEC, const=Symbols.SEMICOLON)

        if self.is_next(const=Keywords.VAR):
            self.compile_var_dec(parent=parent)

    def compile_statements(self, parent: Node):
        STATEMENTS = self._xml_add_element(parent=parent, tag="statements")
        while self.is_next(
            const=[Keywords.LET,
                   Keywords.IF,
                   Keywords.WHILE,
                   Keywords.DO,
                   Keywords.RETURN]):
            self.compile_statement(parent=STATEMENTS)

    def compile_statement(self, parent: Node):

        if self.is_next(const=Keywords.LET):
            self.compile_let_statement(parent=parent)
        if self.is_next(const=Keywords.IF):
            ...
        if self.is_next(const=Keywords.WHILE):
            ...
        if self.is_next(const=Keywords.DO):
            ...
        if self.is_next(const=Keywords.RETURN):
            ...

        raise TypeError("Unknown statement!")

    def compile_let_statement(self, parent: Node):
        LET_STATEMENT = self._xml_add_element(parent=parent,
                                              tag="letStatement")

        self.consume(parent=LET_STATEMENT, const=Keywords.LET)
        self.consume(parent=LET_STATEMENT, token=Tokens.identifier)
        self.consume(parent=LET_STATEMENT, const=Keywords.LET)

    def is_next(self,
                token: Optional[Tokens] | Optional[List[Tokens]] = None,
                const: Optional[List[Constant]] = []
                ) -> bool:

        return self._is_token(
            which='next',
            expected_token=token,
            expected_constants=const)

    def _is_token(self,
                  which: Optional[str] = 'this',
                  expected_token: Optional[Tokens] | Optional[List[Tokens]] = None,
                  expected_constants: Optional[List[Constant]] = []
                  ) -> bool:

        if which == 'this':
            tok = self.tokenizer.token
            val = self.tokenizer.value

        if which == 'next':
            tok = self.tokenizer.next_token
            val = self.tokenizer.next_value

        if (not tok) or (not val):
            return False

        if expected_token:
            if not isinstance(expected_token, list):
                expected_token = [expected_token]

            if tok not in expected_token:
                return False

        if expected_constants:
            const_val = None

            if not isinstance(expected_constants, list):
                expected_constants = [expected_constants]

            for const_class in set(const.__class__ for const in expected_constants):
                # Can add multiple types here
                try:
                    const_val = const_class(val)
                except:
                    continue

                if const_val not in expected_constants:
                    return False

            if not const_val:
                return False  # Failed to transform

        return True
