class DeclaredName:
    def __init__(self, value_type, value):
        self._type = value_type
        self._value = value

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class NamesTable:
    defaults = {
        "int": 0,
        "real": 0.0,
        "boolean": False,
        "string": ""
    }

    def __init__(self):
        self._table = {}

    @property
    def table(self):
        return self._table

    def declare(self, name, value_type, value):
        if value is None:
            value = self.defaults[value_type]

        if name in self._table:
            raise ValueError("Variable is already declared!")

        declared_name = DeclaredName(value_type, value)
        self.table[name] = declared_name

    def assign(self, name, value):
        if name not in self._table:
            raise ValueError("Variable not defined!")

        self._table[name].value = value

    def read(self, name):
        if name not in self._table:
            raise ValueError("Variable not defined!")

        return self._table[name].value
