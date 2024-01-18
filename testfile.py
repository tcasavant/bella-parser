#!/usr/bin/env python3

class SymbolTable:
    def __init__(self):
        self.table = {}

    def add(self, identifier, type, initialized=False):
        if identifier in self.table:
            raise Exception(f"Identifier \"{identifier}\" declared more than once")

        self.table[identifier] = {"type": type, "initialized": initialized}

    def is_initialized(self, identifier):
       return self.table[identifier]["initialized"]

    def set_initialized(self, identifier):
        if identifier not in self.table:
            raise Exception(f"Identifier \"{identifier}\" not declared")

        self.table[identifier]["initialized"] = True

    def lookup(self, identifier):
        if identifier not in self.table:
            raise Exception(f"Identifier \"{identifier}\" not declared")

        return self.table[identifier]["type"]

    def update(self, identifier, newType):
        if identifier not in self.table:
            raise Exception(f"Identifier \"{identifier}\" not declared")

        self.table[identifier]["type"] = newType

root_table = SymbolTable()
extra_table = SymbolTable()
extra_table.table["new"] = "new"
root_table.table["one"] = 1
cur_table = root_table
root_table.table["two"] = 2
cur_table.table["one"] = "one"
cur_table.table["three"] = "three"

print(root_table.table["one"])
print(cur_table.table["one"])
print(root_table.table["two"])
print(cur_table.table["two"])
print(root_table.table["three"])
print(cur_table.table["three"])

cur_table = extra_table
print(root_table.table["one"])
print(root_table.table["two"])
print(root_table.table["three"])
print(cur_table.table["new"])
