import compiler.names


class Node(object):
    @property
    def id(self):
        return str(hash(self))


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


class Name(Node):
    def __init__(self, name):
        self._name = name

    def execute(self, names):
        return names.read(self._name)


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
