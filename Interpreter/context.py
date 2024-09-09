from Interpreter.symboltable import SymbolTable


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.symbol_table = SymbolTable(parent.symbol_table if parent else None)
        self.parent_entry_pos = parent_entry_pos
