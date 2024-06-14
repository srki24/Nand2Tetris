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


    def has_more_tokens(self):
       
        # Already checked
        if self.next_token:
            return True
        
        self.file = self.file.strip()
        # Checking...
        for token in Tokens:
            if res:= re.findall(token.value, self.file):
                self.next_token = token
                self.next_value = res.pop()
                return True
        
        # No more files
        if self.file:
            raise ValueError(f"Failed to parse file: {self.file}")
        return False
        
    def advance(self):
        if self.has_more_tokens:
            
            self.token = self.next_token
            self.next_token = None
            
            self.value = self.next_value
            self.next_value = None
            
            self.file = re.sub(self.token.value, "", self.file)
            self.file = self.file.strip()
            

    def clean_file(self, text):
        _eol_comment = r"//.*"
        text = re.sub(_eol_comment, "", text)
        _multiline_comments = r"(?s)/\*.*?\*/"
        text = re.sub(_multiline_comments, "", text)

        _multiple_spaces = r"\s+"
        text = re.sub(_multiple_spaces, " ", text)

        text = text.strip()
        return text
