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

    def parse_element(
        self,
        parent,
        expected_token: Optional[Tokens] = None,
        expected_constants: Optional[Constant] | Optional[list[Constant]] = None
    ):
        self.tokenizer.advance()

        tok_check = self._is_token(which='this',
                                   expected_token=expected_token,
                                   expected_constants=expected_constants)

        if not tok_check:
            raise TypeError(f"Expected token: {expected_token}; constants: {expected_constants}",
                            f"Got token: {self.tokenizer.token.name}; constant: {self.tokenizer.value}")

        print(self.tokenizer.value)
        self._xml_add_element(parent=parent,
                              tag=self.tokenizer.token.name,
                              value=self.tokenizer.value)

    def compile_class(self):
        CLASS = self._xml_add_element(self.doc, "class")

        self.parse_element(parent=CLASS,
                           expected_constants=Keywords.CLASS)

        self.parse_element(parent=CLASS,
                           expected_token=Tokens.identifier)

        self.parse_element(parent=CLASS,
                           expected_constants=Symbols.OPEN_CURLY_BRACKET)

        while self._is_token(which='next',
                             expected_constants=[Keywords.STATIC,
                                                 Keywords.FIELD]):
            self.compile_class_var_dec(parent=CLASS)

        while self._is_token(which='next',
                             expected_constants=[Keywords.CONSTRUCTOR,
                                                 Keywords.FUNCTION,
                                                 Keywords.METHOD]):
            self.compile_subroutine_dec(parent=CLASS)

        self.parse_element(
            parent=CLASS,
            expected_constants=Symbols.CLOSE_CURLY_BRACKET)

    def compile_class_var_dec(self, parent: Node):

        CLASS_VAR_DEC = self._xml_add_element(parent=parent, tag="classVarDec")

        self.parse_element(parent=CLASS_VAR_DEC,
                           expected_constants=[Keywords.STATIC,
                                               Keywords.FIELD])

        self.parse_type(CLASS_VAR_DEC)

        self.parse_element(
            parent=CLASS_VAR_DEC,
            expected_token=Tokens.identifier
        )

        while self._is_token(which='next',
                             expected_constants=Symbols.COMMA):

            self.parse_element(parent=CLASS_VAR_DEC,
                               expected_constants=Symbols.COMMA)

            self.parse_element(parent=CLASS_VAR_DEC,
                               expected_token=Tokens.identifier)

    def parse_type(self, parent: Node):

        if self._is_token(which='next',
                          expected_constants=[Keywords.INT,
                                              Keywords.CHAR,
                                              Keywords.BOOLEAN]
                          ):
            expected_token = None
            expected_constants = [Keywords.INT,
                                  Keywords.CHAR,
                                  Keywords.BOOLEAN]

        elif self._is_token(which='next',
                            expected_token=Tokens.identifier):
            expected_token = Tokens.identifier
            expected_constants = None

        else:
            raise TypeError(f"Failed to compile TYPE. ",
                            f"Expect Symbol[INT, CHAR, BOOL] or Identifier got ",
                            f"token: {self.tokenizer.next_token.name}, constant: '{self.tokenizer.next_value}'")

        self.parse_element(parent=parent,
                           expected_token=expected_token,
                           expected_constants=expected_constants)

    def compile_subroutine_dec(self, parent: Node):

        SUBROUTINE_DEC = self._xml_add_element(parent=parent,
                                               tag="subroutineDec")

        self.parse_element(parent=SUBROUTINE_DEC,
                           expected_constants=[Keywords.CONSTRUCTOR,
                                               Keywords.FUNCTION,
                                               Keywords.METHOD])

        if self._is_token(which='next',
                          expected_constants=Keywords.VOID):

            self.parse_element(parent=SUBROUTINE_DEC,
                               expected_constants=Keywords.VOID)

        else:
            self.parse_type(parent=SUBROUTINE_DEC)

        self.parse_element(parent=SUBROUTINE_DEC,
                           expected_token=Tokens.identifier)

        self.parse_element(parent=SUBROUTINE_DEC,
                           expected_constants=Symbols.OPEN_BRACKET)

        self.compile_parameter_list(parent=SUBROUTINE_DEC)

        self.parse_element(parent=SUBROUTINE_DEC,
                           expected_constants=Symbols.CLOSE_BRACKET)

        self.compile_subroutine_body(parent=SUBROUTINE_DEC)

    def compile_parameter_list(self, parent: Node):
        PARAMETER_LIST = self._xml_add_element(parent=parent,
                                               tag="parameterList")

        if self._is_token(which='next',
                          expected_token=[Tokens.keyword, Tokens.identifier],
                          expected_constants=[Keywords.INT,
                                              Keywords.CHAR,
                                              Keywords.BOOLEAN]):

            self.parse_type(parent=PARAMETER_LIST)

            self.parse_element(parent=PARAMETER_LIST,
                               expected_token=Tokens.identifier)

            while self._is_token(which='next',
                                 expected_token=Tokens.symbol,
                                 expected_constants=[Symbols.COMMA]):

                self.parse_element(parent=PARAMETER_LIST,
                                   expected_constants=Symbols.COMMA)

                self.parse_type(parent=PARAMETER_LIST)

                self.parse_element(parent=PARAMETER_LIST,
                                   expected_token=Tokens.identifier)

    def compile_subroutine_body(self, parent: Node):
        SUBROUTINE_BODY = self._xml_add_element(parent=parent,
                                                tag="subroutineBody")

        self.parse_element(parent=SUBROUTINE_BODY,
                           expected_constants=Symbols.OPEN_CURLY_BRACKET)

        if self._is_token(which='next',
                          expected_constants=Keywords.VAR):
            self.compile_var_dec(parent=SUBROUTINE_BODY)

        self.compile_statements(SUBROUTINE_BODY)

        self.parse_element(parent=SUBROUTINE_BODY,
                           expected_constants=Symbols.CLOSE_CURLY_BRACKET)

    def compile_var_dec(self, parent: Node):
        VAR_DEC = self._xml_add_element(parent=parent,
                                        tag="varDec")

        self.parse_element(parent=VAR_DEC,
                           expected_constants=Keywords.VAR)

        self.parse_type(VAR_DEC)

        self.parse_element(parent=VAR_DEC,
                           expected_token=Tokens.identifier)

        while self._is_token(which='next',
                             expected_constants=Symbols.COMMA):

            self.parse_element(parent=VAR_DEC,
                               expected_constants=Symbols.COMMA)

            self.parse_element(parent=VAR_DEC,
                               expected_token=Tokens.identifier)

        self.parse_element(parent=VAR_DEC,
                           expected_constants=Symbols.SEMICOLON)

        if self._is_token(which='next',
                          expected_constants=Keywords.VAR):
            self.compile_var_dec(parent=parent)

    def compile_statements(self, parent: Node):
        STATEMENTS = self._xml_add_element(parent=parent, tag="statements")
        while self._is_token(which='next',
                             expected_constants=[Keywords.LET,
                                                 Keywords.IF,
                                                 Keywords.WHILE,
                                                 Keywords.DO,
                                                 Keywords.RETURN]):
            self.parse_statements(parent=STATEMENTS)

    def parse_statements(self, parent: Node):

        if self._is_token(which='next', expected_constants=Keywords.LET):
            self.compile_let_statement(parent=parent)
        if self._is_token(which='next', expected_constants=Keywords.IF):
            ...
        if self._is_token(which='next', expected_constants=Keywords.WHILE):
            ...
        if self._is_token(which='next', expected_constants=Keywords.DO):
            ...
        if self._is_token(which='next', expected_constants=Keywords.RETURN):
            ...

    def compile_let_statement(self, parent: Node):

        LET_STATEMENT = self._xml_add_element(parent=parent,
                                              tag="letStatement")

        self.parse_element(parent=LET_STATEMENT,
                           expected_constants=Keywords.LET)

        self.parse_element(parent=LET_STATEMENT,
                           expected_token=Tokens.identifier)

        self.parse_element(parent=LET_STATEMENT,
                           expected_constants=Keywords.LET)

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
