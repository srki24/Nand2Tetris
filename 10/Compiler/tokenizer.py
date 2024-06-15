import re
from tokens import Tokens


class JackTokenizer:

    def __init__(self, file):

        with open(file) as f:
            self.file = self.clean_file(f.read())

        self.token = None
        self.value = None

        self.next_token = None
        self.next_value = None
        
        self._set_next_token()


    def _set_next_token(self):
        for token in Tokens:
            if res := re.findall(token.value, self.file):
                self.next_token = token
                self.next_value = res.pop()
                return
        
        self.next_token = None
        self.next_value = None

        # Failed to find token but file is not empty
        if self.file:
            raise ValueError(f"Failed to parse file: {self.file}")


    def has_more_tokens(self):
        return bool(self.next_token)

    def advance(self):
        if self.has_more_tokens:

            self.token = self.next_token
            self.value = self.next_value

            self.file = re.sub(self.token.value, "", self.file)
            self.file = self.file.strip()

            self._set_next_token()


    def clean_file(self, text):
        _eol_comment = r"//.*"
        text = re.sub(_eol_comment, "", text)
        _multiline_comments = r"(?s)/\*.*?\*/"
        text = re.sub(_multiline_comments, "", text)

        _multiple_spaces = r"\s+"
        text = re.sub(_multiple_spaces, " ", text)

        text = text.strip()
        return text
