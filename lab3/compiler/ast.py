import compiler.names
import abc


class Node(object):
    __metaclass__ = abc.ABCMeta

    @property
    def id(self):
        return str(hash(self))

    @abc.abstractmethod
    def execute(self, names):
        pass


class Block(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list

    def execute(self, names):
        result = None
        for statement in self._statement_list:
            result = statement.execute(names)

        return result


class Statement(Node):
    def __init__(self, statement_body):
        self._body = statement_body

    def execute(self, names):
        return self._body.execute(names)


class RepeatUntil(Node):
    def __init__(self, block, condition):
        self._block = block
        self._condition = condition

    def execute(self, names):
        self._block.execute(names)
        while not self._condition.execute(names):
            self._block.execute(names)


class For(Node):
    def __init__(self, initial_assignment, condition, step_assignment, block):
        self._initial_assignment = initial_assignment
        self._condition = condition
        self._step_assignment = step_assignment
        self._block = block

    def execute(self, names):
        self._initial_assignment.execute(names)
        while self._condition.execute(names):
            self._block.execute(names)
            self._step_assignment.execute(names)


class While(Node):
    def __init__(self, condition, block):
        self._condition = condition
        self._block = block

    def execute(self, names):
        while self._condition.execute(names):
            self._block.execute(names)


class ConditionalIfElse(Node):
    def __init__(self, condition, block_if, block_else):
        self._condition = condition
        self._block_if = block_if
        self._block_else = block_else

    def execute(self, names):
        if self._condition.execute(names):
            self._block_if.execute(names)
        else:
            self._block_else.execute(names)


class ConditionalIf(Node):
    def __init__(self, condition, statement):
        self._condition = condition
        self._statement = statement

    def execute(self, names):
        if self._condition.execute(names):
            self._statement.execute(names)


class PreFixExpression(Node):
    def __init__(self, name, operation):
        self._name = name
        self._operation = operation

    def execute(self, names):
        value = names.read(self._name)

        if self._operation == "++":
            value += 1
        elif self._operation == "--":
            value -= 1

        names.assign(self._name, value)
        return value


class PostFixExpression(Node):
    def __init__(self, name, operation):
        self._name = name
        self._operation = operation

    def execute(self, names):
        value = names.read(self._name)

        if self._operation == "++":
            names.assign(self._name, value + 1)
        elif self._operation == "--":
            names.assign(self._name, value - 1)

        return value


class BuiltInFunction(Node):
    def __init__(self, function, arguments):
        self._function = function
        self._arguments = arguments

    def execute(self, names):
        return self._function(*map(lambda arg: arg.execute(names), self._arguments))


class Assignment(Node):
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def execute(self, names):
        names.assign(self._name, self._value.execute(names))


class Minus(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, names):
        return (-1) * self._value.execute(names)


class Declaration(Node):
    def __init__(self, name, value_type, value=None):
        self._name = name
        self._value_type = value_type
        self._value = value

    def execute(self, names):
        if self._value is not None:
            names.declare(self._name, self._value_type, self._value.execute(names))
        else:
            names.declare(self._name, self._value_type, None)


class BinaryOperation(Node):
    def __init__(self, left, operation, right):
        self._left = left
        self._operation = operation
        self._right = right

    def execute(self, names):
        return self._operation(self._left.execute(names), self._right.execute(names))


class Real(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, names):
        return self._value


class Integer(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, names):
        return self._value


class Boolean(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, names):
        return self._value


class String(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, names):
        return self._value


class Name(Node):
    def __init__(self, name):
        self._name = name

    def execute(self, names):
        return names.read(self._name)
