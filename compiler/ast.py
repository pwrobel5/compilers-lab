import abc

from compiler.errors import *


class Node(object):
    __metaclass__ = abc.ABCMeta

    @property
    def id(self):
        return str(hash(self))

    @abc.abstractmethod
    def execute(self, scope):
        pass


class Program(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list

    def execute(self, scope):
        for statement in self._statement_list:
            statement.execute(scope)


class Statement(Node):
    def __init__(self, statement_body):
        self._body = statement_body

    def execute(self, scope):
        return self._body.execute(scope)


class Block(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list

    def execute(self, scope):
        for statement in self._statement_list:
            statement.execute(scope)


class FunctionArgumentList(Node):
    def __init__(self, arguments):
        self._arguments = arguments

    def execute(self, scope):
        result = []
        for argument in self._arguments:
            result += [argument.execute(scope)]
        return result

    def append_argument(self, argument):
        self._arguments.append(argument)


class FunctionArgument(Node):
    def __init__(self, arg_type, arg_name):
        self._name = arg_name
        self._type = arg_type

    def execute(self, scope):
        return self._name, self._type


class CustomFunction(Node):
    def __init__(self, name, arg_list, body, returned_value=None):
        self._name = name
        self._arg_list = arg_list
        self._body = body
        self._returned_value = returned_value

    def execute(self, scope):
        scope.declare_function(self._name, self._arg_list, self._body, self._returned_value)


class Print(Node):
    def __init__(self, expression):
        self._expression = expression

    def execute(self, scope):
        print(self._expression.execute(scope))


class RepeatUntil(Node):
    def __init__(self, block, condition):
        self._block = block
        self._condition = condition

    def execute(self, scope):
        scope.start_new()
        self._block.execute(scope)

        condition = self._condition.execute(scope)
        if not isinstance(condition, bool):
            raise ConditionError("Given repeat-until condition is not bool")

        while not condition:
            self._block.execute(scope)
            condition = self._condition.execute(scope)
        scope.end_current()


class For(Node):
    def __init__(self, initial_assignment, condition, step_assignment, block):
        self._initial_assignment = initial_assignment
        self._condition = condition
        self._step_assignment = step_assignment
        self._block = block

    def execute(self, scope):
        self._initial_assignment.execute(scope)

        condition = self._condition.execute(scope)
        if not isinstance(condition, bool):
            raise ConditionError("Given for condition is not bool")

        scope.start_new()
        while condition:
            self._block.execute(scope)
            self._step_assignment.execute(scope)
            condition = self._condition.execute(scope)
        scope.end_current()


class While(Node):
    def __init__(self, condition, block):
        self._condition = condition
        self._block = block

    def execute(self, scope):
        condition = self._condition.execute(scope)
        if not isinstance(condition, bool):
            raise ConditionError("Given while condition is not bool")

        scope.start_new()
        while condition:
            self._block.execute(scope)
            condition = self._condition.execute(scope)
        scope.end_current()


class ConditionalIfElse(Node):
    def __init__(self, condition, block_if, block_else):
        self._condition = condition
        self._block_if = block_if
        self._block_else = block_else

    def execute(self, scope):
        condition = self._condition.execute(scope)
        if not isinstance(condition, bool):
            raise ConditionError("Given if-else condition is not bool")

        scope.start_new()
        if condition:
            self._block_if.execute(scope)
        else:
            self._block_else.execute(scope)
        scope.end_current()


class ConditionalIf(Node):
    def __init__(self, condition, statement):
        self._condition = condition
        self._statement = statement

    def execute(self, scope):
        condition = self._condition.execute(scope)
        if not isinstance(condition, bool):
            raise ConditionError("Given if condition is not bool")

        if condition:
            scope.start_new()
            self._statement.execute(scope)
            scope.end_current()


class CallArgumentList(Node):
    def __init__(self, arguments):
        self._arguments = arguments

    def execute(self, scope):
        result = []
        for argument in self._arguments:
            result.append(argument.execute(scope))
        return result

    def append_argument(self, argument):
        self._arguments.append(argument)


class Call(Node):
    def __init__(self, function_name, arg_list):
        self._function_name = function_name
        self._arg_list = arg_list

    def execute(self, scope):
        function = scope.read_function(self._function_name)
        call_arguments = self._arg_list.execute(scope)
        function_arguments = function.arg_list.execute(scope)

        if len(call_arguments) != len(function_arguments):
            raise ValueError("Difference in number of arguments for call, expected: {} given: {}"
                             .format(len(function_arguments), len(call_arguments)))

        scope.start_new()
        for i in range(0, len(call_arguments)):
            function_argument = function_arguments[i]
            expected_type = function_argument[1]
            argument_name = function_argument[0]
            call_argument = call_arguments[i]

            # make type conversion if necessary
            if expected_type != type(call_argument):
                call_argument = expected_type(call_argument)

            scope.declare_name(argument_name, expected_type, call_argument)

        function.body.execute(scope)
        result = None

        if function.returned_value:
            result = function.returned_value.execute(scope)

        scope.end_current()
        return result


class PreFixExpression(Node):
    def __init__(self, name, operation):
        self._name = name
        self._operation = operation

    def execute(self, scope):
        value = scope.read_name(self._name)

        if self._operation == "++":
            value += 1
        elif self._operation == "--":
            value -= 1

        scope.assign_name(self._name, value)
        return value


class PostFixExpression(Node):
    def __init__(self, name, operation):
        self._name = name
        self._operation = operation

    def execute(self, scope):
        value = scope.read_name(self._name)

        if self._operation == "++":
            scope.assign_name(self._name, value + 1)
        elif self._operation == "--":
            scope.assign_name(self._name, value - 1)

        return value


class BuiltInFunction(Node):
    def __init__(self, function, arguments):
        self._function = function
        self._arguments = arguments

    def execute(self, scope):
        executed_arguments = self._arguments.execute(scope)
        return self._function(*executed_arguments)


class Assignment(Node):
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def execute(self, scope):
        scope.assign_name(self._name, self._value.execute(scope))


class Minus(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope):
        return (-1) * self._value.execute(scope)


class Declaration(Node):
    def __init__(self, name, value_type, value=None):
        self._name = name
        self._value_type = value_type
        self._value = value

    def execute(self, scope):
        if self._value is not None:
            scope.declare_name(self._name, self._value_type, self._value.execute(scope))
        else:
            scope.declare_name(self._name, self._value_type, None)


class Conversion(Node):
    def __init__(self, type_from, operation, value):
        self._type_from = type_from
        self._operation = operation
        self._value = value

    def execute(self, scope):
        value = self._value.execute(scope)

        if not isinstance(value, self._type_from):
            raise ConversionError("Converted value is in incorrect type, expected {} given {}"
                                  .format(self._type_from.__name__, type(value).__name__))

        return self._operation(value)


class BinaryOperation(Node):
    def __init__(self, left, operation, right):
        self._left = left
        self._operation = operation
        self._right = right

    def execute(self, scope):
        left = self._left.execute(scope)
        right = self._right.execute(scope)

        if type(left) == type(right):
            return self._operation(self._left.execute(scope), self._right.execute(scope))
        else:
            raise BinaryOperationError("Types of arguments do not match! Left is {} while right is {}"
                                       .format(type(left).__name__, type(right).__name__))


class Real(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope):
        return self._value


class Integer(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope):
        return self._value


class Boolean(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope):
        return self._value


class String(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope):
        return self._value


class Name(Node):
    def __init__(self, name):
        self._name = name

    def execute(self, scope):
        return scope.read_name(self._name)
