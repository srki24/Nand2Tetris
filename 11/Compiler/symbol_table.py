from enum import Enum


class SymbolKind(Enum):
    STATIC = 'static'
    FIELD = 'field'
    ARG = 'ARG'
    VAR = 'VAR'


class SymbolTable():

    def __init__(self):
        self.class_symbols = dict()
        self.sub_symbols = dict()

        self.symbols = {
            SymbolKind.STATIC: self.class_symbols, SymbolKind.FIELD: self.class_symbols,
            SymbolKind.ARG: self.sub_symbols, SymbolKind.VAR: self.sub_symbols}

        self.symbol_idx = {
            SymbolKind.STATIC: 0,
            SymbolKind.FIELD: 0,
            SymbolKind.ARG: 0,
            SymbolKind.VAR: 0
        }

    def start_sub(self):
        self.sub_symbols.clear()

    def define(self, name: str, type: str, kind: SymbolKind):
        table = self.symbols[kind]
        table[name] = [type, kind, self.symbol_idx[kind]]
        self.symbol_idx[kind] += 1

    def var_count(self, kind: SymbolKind):
        table = self.symbols[kind]

        print(sum(1 for _, k, _ in table if k == kind))
        print(self.symbol_idx[kind])
        
        return sum(1 for _, k, _ in table if k == kind)

    def type_of(self, name: str):
        type, _, _ = self.lookup(name)
        return type

    def kind_of(self, name: str):
        _, kind, _ = self.lookup(name)
        return kind

    def type_of(self, name: str):
        _, _, idx = self.lookup(name)
        return idx

    def lookup(self, name: str):

        sub_data = self.sub_symbols.get(name, None)
        class_data = self.class_symbols.get(name, None)

        if sub_data:
            return sub_data
        if class_data:
            return class_data
        return [None, None, None]
