#!/usr/bin/env python3

import bella_token
import re

class Lexer:
    token_type_patterns = {
        "WHITESPACE":"^[\\s\\t\\n\\r]",
        "COMMENT":"^\\/\\/.*;",
        "KEYWORD":"^(let|function|while|true|false|if|else)",
        "BUILTIN_FUNCTION":"^(print|free)",
        "PARENTHESIS":"^(\\(|\\))",
        "CURLY_BRACE":"^(\\{|\\})",
        "SEMICOLON":"^;",
        "COMMA":"^,",
        "FLOAT":"^\\-?\\d+((\\.\\d+)((E|e)(\\+|\\-)?\\d+)?)",
        "INT":"^\\d+",
        "ID":"^[a-zA-Z]([a-zA-Z0-9]|\\_)*",
        "OPERATOR":"^(\\?|\\:)",
        "OPERATOR1":"^(\\|\\|)",
        "OPERATOR2":"^(\\&\\&)",
        "OPERATOR3":"^(\\<\\=|\\<|\\=\\=|\\!\\=|\\>\\=|\\>)",
        "OPERATOR4":"^(\\+|\\-)",
        "OPERATOR6":"^(\\*\\*)",
        "OPERATOR5":"^(\\*|\\/|\\%)",
        "NOT_OPERATOR":"^\\!",
        "ASSIGN":"^(\\=)",
    }

    def __init__(self, input):
        self.input = input
        self.position = 0
        self.tokens = []

    # Convert the input string into a list of token objects
    def tokenize(self):
        while self.position < len(self.input):
            remaining_input = self.input[self.position:]
            valid_token = False

            # Find the first token type regex that matches from the start of the string
            for token_type, regex in self.token_type_patterns.items():
                match = re.search(regex, remaining_input)
                if match:
                    token = bella_token.Token(token_type, match.group())
                    if token.type == "INTEGER":
                        token.value = int(token.value)
                    if token.type == "FLOAT":
                        token.value = float(token.value)
                    if token.type != "WHITESPACE":
                        self.tokens.append(token)
                    self.position += len(match.group())
                    valid_token = True
                    break
            if not valid_token:
                raise Exception("Lexer error")


        return self.tokens
