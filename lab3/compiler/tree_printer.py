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

    @add_to_class(ast.Name)
    def print_tree(self, graph):
        graph.node(self.id, "VariableName: " + self._name)
        return self.id

    @add_to_class(ast.Declaration)
    def print_tree(self, graph):
        graph.node(self.id, "DeclareVariable: " + self._name + ", type: " + self._value_type)
        if self._value is not None:
            graph.edge(self.id, self._value.print_tree(graph), "Assign")

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
