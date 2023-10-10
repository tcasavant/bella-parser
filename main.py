#!/usr/bin/env python3

import bella_lexer

# program = "a     =   (5 + 3.0) * 2e-2;"
program_file = open("bella_program.bla", "r")
program = program_file.read()

lexer = bella_lexer.Lexer(program)
tokens = lexer.tokenize()

if tokens != None:
    for token in tokens:
        print(f'{token.type}: {token.value}')
