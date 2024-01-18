#!/usr/bin/env python3

from bella_token import Token
from bella_node import Node
from bella_type_checker import TypeChecker
from bella_symbol_table import SymbolTable

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.root_symbol_table = SymbolTable()
        self.root_symbol_table.add("alloc", "INTEGER")
        self.root_symbol_table.add("free", "VOID")
        self.cur_symbol_table = self.root_symbol_table

    # Read the current token and ensure it is of the expected type, moving the position to the next token
    def consume(self, expected_type = None):
        token = self.tokens[self.position]
        if (token.type != expected_type):
            raise Exception(f"Syntax error")
        self.position += 1
        return Token(token.type, token.value)


    # Return the current token without consuming it
    def peek(self):
        if self.position >= len(self.tokens):
            raise Exception("Syntax error: unexpected end of input")
        return self.tokens[self.position]

    # To construct the root of the Abstract Syntax Tree (AST) and iteratively parse each statement in the token list
    def parse(self):
        ast = Node("Program", "program", [])

        while (self.position != len(self.tokens)):
            statement = self.parse_statement()
            if statement != None:
                ast.children.append(statement)

        return ast

    # To parse a block of statements enclosed by curly braces
    def parse_block(self):
        self.consume("CURLY_BRACE")
        block = Node("Block", "block", [])
        block_symbol_table = SymbolTable(self.cur_symbol_table)
        self.cur_symbol_table = block_symbol_table

        while (self.position != len(self.tokens) and self.peek().type != "CURLY_BRACE"):
            block.children.append(self.parse_statement())

        self.consume("CURLY_BRACE")
        self.cur_symbol_table = self.cur_symbol_table.parent

        return block

    # To determine the type of the current statement and delegate to the corresponding parse function
    def parse_statement(self):
        token = self.peek()

        # Consume comments and do not add to AST
        if token.type == "COMMENT":
            self.consume("COMMENT")
            return

        match (token.value):
            case "let":
                declaration = self.parse_declaration()
                if self.peek().type != "SEMICOLON":
                    raise Exception("Syntax error: unexpected end of input")
                self.consume("SEMICOLON")
                return declaration
            case "function":
                self.consume("KEYWORD")
                fun = Node("Id", self.consume("ID").value, [])

                # Create symbol table for function parameters to be used in function
                function_symbol_table = SymbolTable(self.cur_symbol_table)
                self.cur_symbol_table = function_symbol_table

                self.consume("PARENTHESIS")

                params = self.parse_params()
                self.consume("PARENTHESIS")

                fun.children.append(params)
                rhs = self.parse_assignment()
                rhs.children.insert(0, fun)
                if self.peek().type != "SEMICOLON":
                    raise Exception("Syntax error: unexpected end of input")
                self.consume("SEMICOLON")

                self.cur_symbol_table = self.cur_symbol_table.parent

                self.cur_symbol_table.add(fun.value, "ANY")

                return rhs
            case "while":
                while_node = Node("While", self.consume("KEYWORD").value, [])
                # self.consume("PARENTHESIS")
                while_node.children.append(self.parse_expression())
                # self.consume("PARENTHESIS")
                while_node.children.append(self.parse_block())
                return while_node
            case "if":
                self.consume("KEYWORD")
                branch_node = Node("Branch", "branch", [])
                cond = self.parse_expression()
                if_block = self.parse_block()
                branch_node.children.append(cond)
                branch_node.children.append(if_block)
                if self.position < len(self.tokens) and self.peek().value == "else":
                    self.consume("KEYWORD")
                    else_block = self.parse_block()
                    branch_node.children.append(else_block)
                return branch_node
            case "print":
                print_node = Node("Print", self.consume("BUILTIN_FUNCTION").value, [])
                print_node.children.append(self.parse_expression())
                self.consume("SEMICOLON")
                return print_node
            case "free":
                free_node = Node("Free", self.consume("BUILTIN_FUNCTION").value, [])
                self.consume("PARENTHESIS")
                free_var = Node("Id", self.consume("ID").value, [])
                free_node.children.append(free_var)
                self.consume("PARENTHESIS")
                self.consume("SEMICOLON")
                return free_node
            case _:
                raise Exception("Syntax error: unexpected input")

    # To parser declaration statements
    def parse_declaration(self):
        var_type = self.consume("KEYWORD")
        lhs = Node("Id", self.consume("ID").value, [])
        # Declarations must include assignment in Bella
        rhs = self.parse_assignment()
        rhs.value = "Declaration"
        rhs.children.insert(0, lhs)

        match (rhs.children[1].type):
            case "Int":
                self.cur_symbol_table.add(lhs.value, "INTEGER")
            case "Float":
                self.cur_symbol_table.add(lhs.value, "FLOAT")
            case "Keyword":
                self.cur_symbol_table.add(lhs.value, "BOOLEAN")
            case "Id":
                rhs_type = self.cur_symbol_table.lookup(rhs.children[1].value)
                self.cur_symbol_table.add(lhs.value, rhs_type)
            case "Operator":
                if rhs.children[1].value == "?":
                    self.cur_symbol_table.add(lhs.value, "ANY")
                else:
                    rhs_type = TypeChecker.result_type_of_expression(rhs.children[1], self.cur_symbol_table)
                    self.cur_symbol_table.add(lhs.value, rhs_type)
            case _:
                raise Exception("Unkown code in declaration")

        return rhs

    # To parse assignment statements
    def parse_assignment(self):
        assign = Node("Assign", self.consume("ASSIGN").value, [])
        assign.children.append(self.parse_expression())

        return assign

    # To parse list of parameters
    def parse_params(self):
        params = Node("Parameters", "", [])
        while self.peek().value != ")":
            param = self.consume("ID")
            params.children.append(Node("Id", param.value, []))

            self.cur_symbol_table.add(param.value, "ANY")
            if self.peek().value != ")":
                self.consume("COMMA")

        return params

    # To parse a list of arguments for a function call
    def parse_args(self):
        args = Node("Parameters", "", [])
        while self.peek().value != ")":
            args.children.append(self.parse_expression())
            if self.peek().value != ")":
                self.consume("COMMA")

        return args

    # To parse an expression
    def parse_expression(self):
        if self.peek().value == "-":
            exp = Node("Operator", self.consume("OPERATOR4").value, [])
            rhs = self.parse_expression7()
            exp.children.append(rhs)
            return exp
        elif self.peek().value == "!":
            exp = Node("Operator", self.consume("NOT_OPERATOR").value, [])
            rhs = self.parse_expression7()
            exp.children.append(rhs)
            return exp

        lhs = self.parse_expression1()

        # Check the types of the expression to ensure they are valid
        if lhs.type == "Operator":
            result_type = TypeChecker.result_type_of_expression(lhs, self.cur_symbol_table)


        # Parse ternary expression if it exists
        if self.peek().value == "?":
            exp = Node("Operator", self.consume("OPERATOR").value, [])
            first_exp = self.parse_expression1()
            if self.peek().value != ":":
                raise Exception("Syntax error: Expected \":\"")
            self.consume("OPERATOR")
            second_exp = self.parse_expression1()
            exp.children = [lhs, first_exp, second_exp]
            lhs = exp
        return lhs

    def parse_expression1(self):
        lhs = self.parse_expression2()
        while self.peek().type == "OPERATOR1":
            exp = Node("Operator", self.consume("OPERATOR1").value, [lhs])
            rhs = self.parse_expression2()
            exp.children.append(rhs)

            lhs = exp
        return lhs

    def parse_expression2(self):
        lhs = self.parse_expression3()
        while self.peek().type == "OPERATOR2":
            exp = Node("Operator", self.consume("OPERATOR2").value, [lhs])
            rhs = self.parse_expression3()
            exp.children.append(rhs)

            lhs = exp
        return lhs

    def parse_expression3(self):
        lhs = self.parse_expression4()
        while self.peek().type == "OPERATOR3":
            exp = Node("Operator", self.consume("OPERATOR3").value, [lhs])
            rhs = self.parse_expression4()
            exp.children.append(rhs)

            lhs = exp
        return lhs

    def parse_expression4(self):
        lhs = self.parse_expression5()
        while self.peek().type == "OPERATOR4":
            exp = Node("Operator", self.consume("OPERATOR4").value, [lhs])
            rhs = self.parse_expression5()
            exp.children.append(rhs)

            lhs = exp
        return lhs

    def parse_expression5(self):
        lhs = self.parse_expression6()
        while self.peek().type == "OPERATOR5":
            exp = Node("Operator", self.consume("OPERATOR5").value, [lhs])
            rhs = self.parse_expression6()
            exp.children.append(rhs)

            lhs = exp
        return lhs

    def parse_expression6(self):
        lhs = self.parse_expression7()
        while self.peek().type == "OPERATOR6":
            exp = Node("Operator", self.consume("OPERATOR6").value, [lhs])
            rhs = self.parse_expression7()
            exp.children.append(rhs)

            lhs = exp
        return lhs

    # To parse individual terms in an expression
    def parse_expression7(self):
        term = self.peek()
        if term.value == "(":
            self.consume("PARENTHESIS")
            exp = self.parse_expression()
            self.consume("PARENTHESIS")
            return exp
        elif term.type == "INT":
            return Node("Int", self.consume("INT").value, [])
        elif term.type == "FLOAT":
            return Node("Float", self.consume("FLOAT").value, [])
        elif term.type == "ID":
            identifier = Node("Id", self.consume("ID").value, [])
            if self.peek().value == "(":
                self.consume("PARENTHESIS")
                args = self.parse_args()
                identifier.children.append(args)
                self.consume("PARENTHESIS")
            return identifier
        elif term.type == "KEYWORD":
            if term.value != "true" and term.value != "false":
                raise Exception("Syntax error")
            return Node("Keyword", self.consume("KEYWORD").value, [])
        else:
            raise Exception("Syntax error")
