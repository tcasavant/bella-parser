class MemoryVerifier:
    @staticmethod
    def verify_allocation(ast, allocation_table = None):
        if allocation_table == None:
            allocation_table = AllocationTable()
        for child in ast.children:
            try:
                if child.children[1].value == "alloc":
                    id = child.children[0].value
                    # Attempt to allocate the variable, fail if it already is allocated in the current scope
                    allocation_table.allocate(id)
                    # Continue to the next child node (statement or portion of expression)
                    continue
            except:
                pass
            if child.value == "free":
                id = child.children[0].value
                # Attempt to free the variable in the closest scope possible, fail if it is not allocated
                allocation_table.free(id)
                # Continue to the next child node (statement or portion of expression)
                continue
            if child.type == "Branch" or child.type == "While":
                # Use DFS to confirm that the condition expression does not contain a null reference
                condition = child.children[1]
                MemoryVerifier.check_expression_for_null_reference(condition, allocation_table)

                # Recursively check for memory errors in the block
                MemoryVerifier.verify_allocation(child.children[1], AllocationTable(allocation_table))
            if child.value == "Declaration":
                # Use DFS to confirm that the expression being assigned does not contain a null reference
                exp = child.children[1]
                # If the expression is a ternary operator, check each expression separately
                if exp.value == "?":
                    MemoryVerifier.check_expression_for_null_reference(exp.children[0], allocation_table)
                    MemoryVerifier.check_expression_for_null_reference(exp.children[1], allocation_table)
                    MemoryVerifier.check_expression_for_null_reference(exp.children[2], allocation_table)
                else:
                    MemoryVerifier.check_expression_for_null_reference(exp, allocation_table)
            if child.type == "print":
                exp = child.children[0]
                MemoryVerifier.check_expression_for_null_reference(exp, allocation_table)

        if not allocation_table.isEmpty():
            raise Exception("Memory leak: not all allocated variables are freed")

        return

    @staticmethod
    def check_expression_for_null_reference(exp, allocation_table):
        nodes = []
        nodes.append(exp)
        while len(nodes) != 0:
            node = nodes.pop()

            # If the node is an identifier, check if it is a null reference
            if node.type == "Id":
                if allocation_table.isNull(node.value):
                    raise Exception(f"Null pointer reference: Identifier \"{node.value}\" has already been freed")
            for child in node.children:
                nodes.append(child)


class AllocationTable:
    def __init__(self, parent = None):
        self.table = {}
        self.parent = parent

    def allocate(self, identifier):
        if identifier in self.table and self.table[identifier] != None:
            raise Exception(f"Variable \"{identifier}\" already allocated in current scope")

        self.table[identifier] = True

    def isAllocated(self, identifier):
        if identifier in self.table and self.table[identifier] != None:
            return True
        cur_table = self.parent
        while cur_table != None:
            if identifier in cur_table.table and cur_table.table[identifier] == True:
                return True
            cur_table = cur_table.parent

        return False

    # If identifier was freed and there is not a separate object with the same name allocated in a parent scope, return True to indicate a reference to that identifier is a null pointer reference
    def isNull(self, identifier):
        if identifier in self.table and self.table[identifier] == None:
            return True
        cur_table = self.parent
        while cur_table != None:
            if identifier in cur_table.table and cur_table.table[identifier] == None and not cur_table.parent.isAllocated(identifier):
                return True
            cur_table = cur_table.parent

        return False

    def free(self, identifier):
        if not self.isAllocated(identifier):
            raise Exception(f"Variable \"{identifier}\" never allocated")

        cur_table = self
        while cur_table != None:
            if identifier in cur_table.table and cur_table.table[identifier] != None:
                # Set value to None to indicate null pointer
                cur_table.table[identifier] = None
                return
            cur_table = cur_table.parent

    # Return True if the table does not contain any allocated variables
    def isEmpty(self):
        for id, status in self.table.items():
            if status != None:
                return False
        return True
