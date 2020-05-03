import abc

from compiler.errors import *


class Node(object):
    __metaclass__ = abc.ABCMeta

    @property
    def id(self):
        return str(hash(self))

    @abc.abstractmethod
    def execute(self, names):
        pass


class Program(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list

    def execute(self, names):
        for statement in self._statement_list:
            statement.execute(names)


class Statement(Node):
    def __init__(self, statement_body):
        self._body = statement_body

    def execute(self, names):
        return self._body.execute(names)


class Block(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list

    def execute(self, names):
        for statement in self._statement_list:
            statement.execute(names)


class Print(Node):
    def __init__(self, expression):
        self._expression = expression

    def execute(self, names):
        print(self._expression.execute(names))


class RepeatUntil(Node):
    def __init__(self, block, condition):
        self._block = block
        self._condition = condition

    def execute(self, names):
        self._block.execute(names)

        condition = self._condition.execute(names)
        if not isinstance(condition, bool):
            raise ConditionError("Given repeat-until condition is not bool")

        while not condition:
            self._block.execute(names)
            condition = self._condition.execute(names)


class For(Node):
    def __init__(self, initial_assignment, condition, step_assignment, block):
        self._initial_assignment = initial_assignment
        self._condition = condition
        self._step_assignment = step_assignment
        self._block = block

    def execute(self, names):
        self._initial_assignment.execute(names)

        condition = self._condition.execute(names)
        if not isinstance(condition, bool):
            raise ConditionError("Given for condition is not bool")

        while condition:
            self._block.execute(names)
            self._step_assignment.execute(names)
            condition = self._condition.execute(names)


class While(Node):
    def __init__(self, condition, block):
        self._condition = condition
        self._block = block

    def execute(self, names):
        condition = self._condition.execute(names)
        if not isinstance(condition, bool):
            raise ConditionError("Given while condition is not bool")

        while condition:
            self._block.execute(names)
            condition = self._condition.execute(names)


class ConditionalIfElse(Node):
    def __init__(self, condition, block_if, block_else):
        self._condition = condition
        self._block_if = block_if
        self._block_else = block_else

    def execute(self, names):
        condition = self._condition.execute(names)
        if not isinstance(condition, bool):
            raise ConditionError("Given if-else condition is not bool")

        if condition:
            self._block_if.execute(names)
        else:
            self._block_else.execute(names)


class ConditionalIf(Node):
    def __init__(self, condition, statement):
        self._condition = condition
        self._statement = statement

    def execute(self, names):
        condition = self._condition.execute(names)
        if not isinstance(condition, bool):
            raise ConditionError("Given if condition is not bool")

        if condition:
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


class Conversion(Node):
    def __init__(self, type_from, operation, value):
        self._type_from = type_from
        self._operation = operation
        self._value = value

    def execute(self, names):
        value = self._value.execute(names)

        if not isinstance(value, self._type_from):
            raise ConversionError("Converted value is in incorrect type, expected {} given {}"
                                  .format(self._type_from.__name__, type(value).__name__))

        return self._operation(value)


class BinaryOperation(Node):
    def __init__(self, left, operation, right):
        self._left = left
        self._operation = operation
        self._right = right

    def execute(self, names):
        left = self._left.execute(names)
        right = self._right.execute(names)

        if type(left) == type(right):
            return self._operation(self._left.execute(names), self._right.execute(names))
        else:
            raise BinaryOperationError("Types of arguments do not match! Left is {} while right is {}"
                                       .format(type(left).__name__, type(right).__name__))


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
