class SymbolTable:
    def __init__(self, parent=None):
        self.table = {}
        self.parent = parent

    def add(self, identifier, type, initialized=False):
        if identifier in self.table:
            if self.lookup(identifier) != type and self.lookup(identifier) != "ANY" and type != "ANY":
                raise Exception(f"Identifier \"{identifier}\" reassigned to different type")

        self.table[identifier] = {"type": type, "initialized": initialized}

    def is_initialized(self, identifier):
       return self.table[identifier]["initialized"]

    def set_initialized(self, identifier):
        if identifier not in self.table:
            raise Exception(f"Identifier \"{identifier}\" not declared")

        self.table[identifier]["initialized"] = True

    def lookup(self, identifier):
        if identifier in self.table:
            return self.table[identifier]["type"]
        cur_table = self.parent
        while cur_table != None:
            if identifier in cur_table.table:
                return cur_table.table[identifier]["type"]
            cur_table = cur_table.parent

        raise Exception(f"Identifier \"{identifier}\" not declared")


    def update(self, identifier, newType):
        if identifier not in self.table:
            raise Exception(f"Identifier \"{identifier}\" not declared")

        self.table[identifier]["type"] = newType
