#!/usr/bin/env python3

import bella_lexer as lexer
import bella_parser as parser
import bella_memory_verifier as memory_verifier
import json
# program = "a     =   (5 + 3.0) * 2e-2;"

program_file = open("bella_program.bla", "r")
program = program_file.read()

lexer = lexer.Lexer(program)
tokens = lexer.tokenize()
# for token in tokens:
#     print(f"{{{token.type}, {token.value}}}", end=" ")
# print()
# print(tokens)

parser = parser.Parser(tokens)
ast = parser.parse()
print(ast)
memory_verifier.MemoryVerifier.verify_allocation(ast)
