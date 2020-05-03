from compiler import ast


def add_to_class(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class TreePrinter:
    @add_to_class(ast.Node)
    def print_tree(self, graph):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @add_to_class(ast.Program)
    def print_tree(self, graph):
        graph.node(self.id, "Program")
        for statement in self._statement_list:
            graph.edge(self.id, statement.print_tree(graph))
        return self.id

    @add_to_class(ast.Statement)
    def print_tree(self, graph):
        graph.node(self.id, "Statement")
        graph.edge(self.id, self._body.print_tree(graph))
        return self.id

    @add_to_class(ast.Block)
    def print_tree(self, graph):
        graph.node(self.id, "Block")
        for statement in self._statement_list:
            graph.edge(self.id, statement.print_tree(graph))
        return self.id

    @add_to_class(ast.Print)
    def print_tree(self, graph):
        graph.node(self.id, "Print")
        graph.edge(self.id, self._expression.print_tree(graph), "Expression")
        return self.id

    @add_to_class(ast.RepeatUntil)
    def print_tree(self, graph):
        graph.node(self.id, "Repeat")
        graph.edge(self.id, self._block.print_tree(graph), "Block")
        graph.edge(self.id, self._condition.print_tree(graph), "Until")
        return self.id

    @add_to_class(ast.For)
    def print_tree(self, graph):
        graph.node(self.id, "For")
        graph.edge(self.id, self._initial_assignment.print_tree(graph), "Initial")
        graph.edge(self.id, self._condition.print_tree(graph), "Condition")
        graph.edge(self.id, self._step_assignment.print_tree(graph), "Step")
        graph.edge(self.id, self._block.print_tree(graph), "Block")
        return self.id

    @add_to_class(ast.While)
    def print_tree(self, graph):
        graph.node(self.id, "While")
        graph.edge(self.id, self._condition.print_tree(graph), "Condition")
        graph.edge(self.id, self._block.print_tree(graph), "Block")
        return self.id

    @add_to_class(ast.ConditionalIfElse)
    def print_tree(self, graph):
        graph.node(self.id, "IfElse")
        graph.edge(self.id, self._condition.print_tree(graph), "Condition")
        graph.edge(self.id, self._block_if.print_tree(graph), "If")
        graph.edge(self.id, self._block_else.print_tree(graph), "Else")
        return self.id

    @add_to_class(ast.ConditionalIf)
    def print_tree(self, graph):
        graph.node(self.id, "If")
        graph.edge(self.id, self._condition.print_tree(graph), "Condition")
        graph.edge(self.id, self._statement.print_tree(graph), "Instructions")
        return self.id

    @add_to_class(ast.PreFixExpression)
    def print_tree(self, graph):
        graph.node(self.id, "Prefix expression: " + self._operation)
        return self.id

    @add_to_class(ast.PostFixExpression)
    def print_tree(self, graph):
        graph.node(self.id, "Postfix expression: " + self._operation)
        return self.id

    @add_to_class(ast.BuiltInFunction)
    def print_tree(self, graph):
        graph.node(self.id, "Built-in function: " + self._function.__name__)
        for element in self._arguments:
            graph.edge(self.id, element.print_tree(graph), "Argument")
        return self.id

    @add_to_class(ast.Assignment)
    def print_tree(self, graph):
        graph.node(self.id, "Assignment to " + self._name)
        graph.edge(self.id, self._value.print_tree(graph), "Equals")
        return self.id

    @add_to_class(ast.Minus)
    def print_tree(self, graph):
        graph.node(self.id, "Minus")
        graph.edge(self.id, self._value.print_tree(graph))
        return self.id

    @add_to_class(ast.Declaration)
    def print_tree(self, graph):
        graph.node(self.id, "DeclareVariable: " + self._name + ", type: " + self._value_type)
        if self._value is not None:
            graph.edge(self.id, self._value.print_tree(graph), "Assign")
        return self.id

    @add_to_class(ast.Conversion)
    def print_tree(self, graph):
        graph.node(self.id, "Conversion from {} to {}".format(self._type_from.__name__, self._operation.__name__))
        graph.edge(self.id, self._value.print_tree(graph), "Value")
        return self.id

    @add_to_class(ast.BinaryOperation)
    def print_tree(self, graph):
        graph.node(self.id, "BinaryOperation: " + self._operation.__name__)
        graph.edge(self.id, self._left.print_tree(graph), "Left")
        graph.edge(self.id, self._right.print_tree(graph), "Right")
        return self.id

    @add_to_class(ast.Real)
    def print_tree(self, graph):
        graph.node(self.id, "Real: " + str(self._value))
        return self.id

    @add_to_class(ast.Integer)
    def print_tree(self, graph):
        graph.node(self.id, "Integer: " + str(self._value))
        return self.id

    @add_to_class(ast.Boolean)
    def print_tree(self, graph):
        graph.node(self.id, "Boolean: " + str(self._value))
        return self.id

    @add_to_class(ast.String)
    def print_tree(self, graph):
        graph.node(self.id, "String: " + self._value)
        return self.id

    @add_to_class(ast.Name)
    def print_tree(self, graph):
        graph.node(self.id, "VariableName: " + self._name)
        return self.id
