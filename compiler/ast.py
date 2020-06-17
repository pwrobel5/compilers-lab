import abc
import threading

from compiler.errors import *


class Node(object):
    __metaclass__ = abc.ABCMeta

    @property
    def id(self):
        return str(id(self))

    @abc.abstractmethod
    def execute(self, scope, opt):
        pass

    def execute_and_handle_errors(self, scope, opt):
        try:
            return self.execute(scope, opt)
        except BinaryOperationError as err:
            msg, = err.args
            print("Error with binary operation: {}".format(msg))
        except ConditionError as err:
            msg, = err.args
            print("Error with given condition: {}".format(msg))
        except ConversionError as err:
            msg, = err.args
            print("Error with conversion: {}".format(msg))
        except AssignmentError as err:
            msg, = err.args
            print("Error with assignment: {}".format(msg))
        except ValueError as err:
            msg, = err.args
            print("Value Error: {}".format(msg))
        except:
            print("Unrecognized error")

    @staticmethod
    def remove_needless_statements(statement_list, scope):
        needless_statements = []
        unused_names = scope.get_unused_names()
        unused_functions = scope.get_unused_functions()

        for statement in statement_list:
            if isinstance(statement, (Declaration, Assignment)) and statement.name in unused_names.keys():
                needless_statements.append(statement)
            elif isinstance(statement, CustomFunction) and statement.name in unused_functions.keys():
                needless_statements.append(statement)

        return list(filter(lambda x: x not in needless_statements, statement_list))


class Program(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list
        self._repl_mode = False

    def execute(self, scope, opt):
        for statement in self._statement_list:
            result = statement.execute_and_handle_errors(scope, opt)

            if self._repl_mode and result is not None:
                print(result)

        if opt:
            self._statement_list = Node.remove_needless_statements(self._statement_list, scope)

    @property
    def statement_list(self):
        return self._statement_list

    def activate_repl_mode(self):
        self._repl_mode = True


class Block(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list

    def execute(self, scope, opt):
        for statement in self._statement_list:
            statement.execute(scope, opt)

        if opt:
            self._statement_list = Node.remove_needless_statements(self._statement_list, scope)


class FunctionArgumentList(Node):
    def __init__(self, arguments):
        self._arguments = arguments

    def execute(self, scope, opt):
        result = []
        for argument in self._arguments:
            result += [argument.execute(scope, opt)]
        return result

    def append_argument(self, argument):
        self._arguments.append(argument)


class FunctionArgument(Node):
    def __init__(self, arg_type, arg_name):
        self._name = arg_name
        self._type = arg_type

    def execute(self, scope, opt):
        return self._name, self._type


class CustomFunction(Node):
    def __init__(self, name, arg_list, body, returned_value=None):
        self._name = name
        self._arg_list = arg_list
        self._body = body
        self._returned_value = returned_value

    def execute(self, scope, opt):
        scope.declare_function(self._name, self._arg_list, self._body, self._returned_value)

    @property
    def name(self):
        return self._name


class Print(Node):
    def __init__(self, expression):
        self._expression = expression

    def execute(self, scope, opt):
        result = self._expression.execute(scope, opt)

        if opt:
            saved_expression = scope.get_expression(self._expression)
            if saved_expression is not None:
                self._expression = saved_expression

        print(result)

    @property
    def expression(self):
        return self._expression

    def __eq__(self, other):
        return isinstance(other, Print) and \
               self.expression == other.expression


class Parallel(Node):
    def __init__(self, statement_list):
        self._statement_list = statement_list

    def execute(self, scope, opt):
        thread_list = []
        for statement in self._statement_list:
            statement_thread = threading.Thread(target=statement.execute_and_handle_errors, args=(scope, opt))
            statement_thread.start()
            thread_list.append(statement_thread)

        for statement_thread in thread_list:
            statement_thread.join()


class RepeatUntil(Node):
    def __init__(self, block, condition):
        self._block = block
        self._condition = condition

    def execute(self, scope, opt):
        scope.start_new()
        self._block.execute(scope, opt)

        condition = self._condition.execute(scope, opt)
        if not isinstance(condition, bool):
            raise ConditionError("Given repeat-until condition is not bool")

        while not condition:
            self._block.execute(scope, opt)
            condition = self._condition.execute(scope, opt)
        scope.end_current()


class For(Node):
    def __init__(self, initial_assignment, condition, step_assignment, block):
        self._initial_assignment = initial_assignment
        self._condition = condition
        self._step_assignment = step_assignment
        self._block = block

    def execute(self, scope, opt):
        self._initial_assignment.execute(scope, opt)

        condition = self._condition.execute(scope, opt)
        if not isinstance(condition, bool):
            raise ConditionError("Given for condition is not bool")

        scope.start_new()
        while condition:
            self._block.execute(scope, opt)
            self._step_assignment.execute(scope, opt)
            condition = self._condition.execute(scope, opt)
        scope.end_current()


class While(Node):
    def __init__(self, condition, block):
        self._condition = condition
        self._block = block

    def execute(self, scope, opt):
        condition = self._condition.execute(scope, opt)
        if not isinstance(condition, bool):
            raise ConditionError("Given while condition is not bool")

        scope.start_new()
        while condition:
            self._block.execute(scope, opt)
            condition = self._condition.execute(scope, opt)
        scope.end_current()


class ConditionalIfElse(Node):
    def __init__(self, condition, block_if, block_else):
        self._condition = condition
        self._block_if = block_if
        self._block_else = block_else

    def execute(self, scope, opt):
        condition = self._condition.execute(scope, opt)
        if not isinstance(condition, bool):
            raise ConditionError("Given if-else condition is not bool")

        scope.start_new()
        if condition:
            self._block_if.execute(scope, opt)
        else:
            self._block_else.execute(scope, opt)
        scope.end_current()


class ConditionalIf(Node):
    def __init__(self, condition, statement):
        self._condition = condition
        self._statement = statement

    def execute(self, scope, opt):
        condition = self._condition.execute(scope, opt)
        if not isinstance(condition, bool):
            raise ConditionError("Given if condition is not bool")

        if condition:
            scope.start_new()
            self._statement.execute(scope, opt)
            scope.end_current()


class CallArgumentList(Node):
    def __init__(self, arguments):
        self._arguments = arguments

    def execute(self, scope, opt):
        result = []
        for index, argument in enumerate(self._arguments):
            result.append(argument.execute(scope, opt))

            if opt:
                saved_argument = scope.get_expression(argument)
                if saved_argument is not None:
                    self._arguments[index] = saved_argument

        return result

    def append_argument(self, argument):
        self._arguments.append(argument)


class Call(Node):
    def __init__(self, function_name, arg_list):
        self._function_name = function_name
        self._arg_list = arg_list

    def execute(self, scope, opt):
        function = scope.read_function(self._function_name)
        call_arguments = self._arg_list.execute(scope, opt)
        function_arguments = function.arg_list.execute(scope, opt)

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

        function.body.execute(scope, opt)
        result = None

        if function.returned_value:
            result = function.returned_value.execute(scope, opt)

        scope.end_current()
        return result


class PreFixExpression(Node):
    def __init__(self, name, operation):
        self._name = name
        self._operation = operation

    def execute(self, scope, opt):
        value, _ = scope.read_name(self._name)

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

    def execute(self, scope, opt):
        value, _ = scope.read_name(self._name)

        if self._operation == "++":
            scope.assign_name(self._name, value + 1)
        elif self._operation == "--":
            scope.assign_name(self._name, value - 1)

        return value


class BuiltInFunction(Node):
    def __init__(self, function, arguments):
        self._function = function
        self._arguments = arguments

    def execute(self, scope, opt):
        executed_arguments = self._arguments.execute(scope, opt)
        return self._function(*executed_arguments)


class Assignment(Node):
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def execute(self, scope, opt):
        executed_value = self._value.execute(scope, opt)

        if opt:
            saved_value = scope.get_expression(self._value)
            if saved_value is not None:
                self._value = saved_value

        scope.assign_name(self._name, executed_value)

    @property
    def name(self):
        return self._name


class Minus(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope, opt):
        executed_value = self._value.execute(scope, opt)

        if opt:
            saved_value = scope.get_expression(self._value)
            if saved_value is not None:
                self._value = saved_value

        return (-1) * executed_value


class Declaration(Node):
    def __init__(self, name, value_type, value=None):
        self._name = name
        self._value_type = value_type
        self._value = value

    def execute(self, scope, opt):
        if self._value is not None:
            executed_value = self._value.execute(scope, opt)

            if opt:
                saved_value = scope.get_expression(self._value)
                if saved_value is not None:
                    self._value = saved_value

            scope.declare_name(self._name, self._value_type, executed_value)
        else:
            scope.declare_name(self._name, self._value_type, None)

    @property
    def name(self):
        return self._name


class Conversion(Node):
    def __init__(self, type_from, operation, value):
        self._type_from = type_from
        self._operation = operation
        self._value = value

    def execute(self, scope, opt):
        value = self._value.execute(scope, opt)

        if not isinstance(value, self._type_from):
            raise ConversionError("Converted value is in incorrect type, expected {} given {}"
                                  .format(self._type_from.__name__, type(value).__name__))

        if opt:
            saved_value = scope.get_expression(self._value)
            if saved_value is not None:
                self._value = saved_value

        return self._operation(value)


class BinaryOperation(Node):
    def __init__(self, left, operation, right):
        self._left = left
        self._operation, self._is_reversible = operation
        self._right = right

    def execute(self, scope, opt):
        left = self._left.execute(scope, opt)
        right = self._right.execute(scope, opt)

        if scope.get_expression(self) is None:
            scope.add_expression(self)

        result = scope.get_expression_result(self)
        if result is not None:
            return result

        if type(left) == type(right):
            result = self._operation(left, right)
            scope.save_expression_result(self, result)
            return result
        else:
            raise BinaryOperationError("Types of arguments do not match! Left is {} while right is {}"
                                       .format(type(left).__name__, type(right).__name__))

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def operation(self):
        return self._operation

    def __eq__(self, other):
        common_condition = isinstance(other, BinaryOperation) and self.operation == other.operation

        if self._is_reversible:
            return common_condition and \
                   ((self.left == other.left and self.right == other.right) or
                    (self.left == other.right and self.right == other.left))
        else:
            return common_condition and \
                   self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self._left, self._right, self._operation))


class Real(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope, opt):
        return self._value

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return isinstance(other, Real) and \
               self._value == other.value

    def __hash__(self):
        return hash(self._value)


class Integer(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope, opt):
        return self._value

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return isinstance(other, Integer) and \
               self.value == other.value

    def __hash__(self):
        return hash(self._value)


class Boolean(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope, opt):
        return self._value

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return isinstance(other, Boolean) and \
               self.value == other.value


class String(Node):
    def __init__(self, value):
        self._value = value

    def execute(self, scope, opt):
        return self._value

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return isinstance(other, String) and \
               self.value == other.value

    def __hash__(self):
        return hash(self._value)


class Name(Node):
    def __init__(self, name):
        self._name = name
        self._changes = None  # to not include name in common subexpressions after variable modification

    def execute(self, scope, opt):
        value, changes = scope.read_name(self._name)
        self._changes = changes
        return value

    @property
    def name(self):
        return self._name

    @property
    def changes(self):
        return self._changes

    def __eq__(self, other):
        return isinstance(other, Name) and \
               self.name == other.name and \
               self.changes == other.changes

    def __hash__(self):
        return hash((self._name, self._changes))
