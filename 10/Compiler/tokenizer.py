import re
from typing import Optional
from xml.dom.minidom import Document

from tokens import Tokens


class JackTokenizer:

    def __init__(self, file_name):

        self.file_name = file_name
        with open(file_name) as f:
            self.file_data = self.clean_file(f.read())

        self.token: Optional[Tokens] = None
        self.value = None

        self.next_token = None
        self.next_value = None

        self._set_next_token()
        self._xml_initialize()

    def _xml_initialize(self):
        self.doc = Document()
        self.root = self.doc.createElement("tokens")
        self.doc.appendChild(self.root)

    def _xml_add_element(self):
        element = self.doc.createElement(self.token.name)
        element.appendChild(self.doc.createTextNode(f" {self.value} "))
        self.root.appendChild(element)

    def _xml_write_file(self):

        if not self.root:
            raise ValueError("XML file is not initialized")

        tree = self.root.toprettyxml(indent="")
        with open(self.file_name.replace(".jack", "-test.xml"), "w") as output:
            output.write(tree)

    def _set_next_token(self):
        for token in Tokens:
            if res := re.findall(token.value, self.file_data):
                self.next_token = token
                self.next_value = res.pop()
                return

        self.next_token = None
        self.next_value = None

        # Failed to find token but file is not empty
        if self.file_data:
            raise ValueError(f"Failed to parse file: {self.file_data}")

    def has_more_tokens(self):
        return bool(self.next_token)

    def advance(self):
        if self.has_more_tokens:

            self.token = self.next_token
            self.value = self.next_value

            self._xml_add_element()

            self.file_data = re.sub(self.token.value, "", self.file_data)
            self.file_data = self.file_data.strip()
            self._set_next_token()

    def tokenize(self):
        while self.has_more_tokens():
            self.advance()
        
        self._xml_write_file()

    def clean_file(self, text):
        _eol_comment = r"//.*"
        text = re.sub(_eol_comment, "", text)
        _multiline_comments = r"(?s)/\*.*?\*/"
        text = re.sub(_multiline_comments, "", text)

        _multiple_spaces = r"\s+"
        text = re.sub(_multiple_spaces, " ", text)

        text = text.strip()
        return text
