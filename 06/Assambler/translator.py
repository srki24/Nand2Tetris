class Translator:

    def addr(self, a:str="")->str:
        return self._to_bin(a).zfill(16)
    
    def dest(self, d: str = "") -> str:
        mapping = {"M": 1, "D": 2, "A": 4, "": 0}

        try:
            s = sum(mapping[val.upper()] for val in d if d)
        except SyntaxError as err:
            raise (f"Unknown dest: {d}. Must be one of {','.join(mapping.keys())}")
        return self._to_bin(s).zfill(3)

    def comp(self, c: str):
        mappings = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "M": "1110000",
            "!D": "0001111",
            "!A": "0110001",
            "!M": "1110001",
            "-D": "0001111",
            "-A": "0110011",
            "-M": "1110011",
            "D+1": "0011111",
            "1+D": "0011111",
            "A+1": "0110111",
            "1+A": "0110111",
            "M+1": "1110111",
            "1+M": "1110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "M-1": "1110010",
            "D+A": "0000010",
            "A+D": "0000010",
            "D+M": "1000010",
            "M+D": "1000010",
            "D-A": "0010011",
            "D-M": "1010011",
            "A-D": "0000111",
            "M-D": "1000111",
            "D&A": "0000000",
            "A&D": "0000000",
            "M&D": "1000000",
            "D&M": "1000000",
            "D|A": "0010101",
            "A|D": "0010101",
            "D|M": "1010101",
            "M|D": "1010101",
        }
        return mappings[c]

    def jump(self, j: str):
        # returns 3 bits
        mappings = {
            "JGT": "001",
            "JEQ": "010",
            "JLE": "100",
            "JGE": "011",
            "JLE": "110",
            "JNE": "101",
            "JMP": "111",
        }
        if j:
            j = j.upper()
        return mappings.get(j, "000")

    def _to_bin(self, nr):
        return bin(int(nr)).replace("0b", "")
