#!/usr/bin/env python3

import lexer

program = "a     =   (5 + 3.0) * 2e-2;"
program_file = open("program.bla", "r")
program = program_file.read()

lexer = lexer.Lexer(program)
tokens = lexer.tokenize()

for token in tokens:
    print(f'{token.type}: {token.value}')
