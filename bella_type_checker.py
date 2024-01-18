class TypeChecker:
    @staticmethod
    def check_assignment(target_type, value_type):
        return target_type == value_type or target_type == "ANY" or value_type == "ANY"

    @staticmethod
    def result_type_of_op(left_type, op, right_type):
        """
        Determines the resulting type of a binary operation given the types of its
        operands.
        Args:
        left_type (str): The type of the left operand.
        op (str): The operator being applied.
        right_type (str): The type of the right operand.
        Returns:
        str: The resulting type of the operation.
        """
        arithmetic_ops = ['+', '-', '*', '/', '**', '%']
        boolean_ops = ['>', '<','>=', '<=', '==', '!=', '&&', '||']
        if left_type == "ANY":
            return right_type
        if right_type == "ANY":
            return left_type
        if left_type == right_type:
            if op in arithmetic_ops:
                return left_type
            if op in boolean_ops:
                return "BOOLEAN"
            raise Exception("Unknown operator")
        else:
            raise TypeError(f"Incompatible types for operation: {left_type} {op} {right_type}")

    @staticmethod
    def check_op(left_type, op, right_type):
        return left_type == right_type or left_type == "ANY" or right_type == "ANY"

    @staticmethod
    def result_type_of_expression(exp, symbol_table):
        if exp.type != "Operator":
            # The expression is just a value, so return its type
            return exp.type
        left_term = exp.children[0]
        left_term_type = None

        try:
            right_term = exp.children[1]
        except:
            right_term = None
        right_term_type = None

        op = exp.value

        match (left_term.type):
            case "Operator":
                left_term_type = TypeChecker.result_type_of_expression(left_term, symbol_table)
            case "Id":
                left_term_type = symbol_table.lookup(left_term.value)
            case "Int":
                left_term_type = "INTEGER"
            case "Float":
                left_term_type = "FLOAT"
            case "Keyword":
                if left_term.value == "true" or left_term.value == "false":
                    left_term_type = "BOOLEAN"


        if right_term == None:
            return left_term_type
        match (right_term.type):
            case "Operator":
                right_term_type = TypeChecker.result_type_of_expression(right_term, symbol_table)
            case "Id":
                right_term_type = symbol_table.lookup(right_term.value)
            case "Int":
                right_term_type = "INTEGER"
            case "Float":
                right_term_type = "FLOAT"
            case "Keyword":
                if right_term.value == "true" or right_term.value == "false":
                    right_term_type = "BOOLEAN"

        return TypeChecker.result_type_of_op(left_term_type, op, right_term_type)
