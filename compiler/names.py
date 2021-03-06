import threading

import numpy as np

from compiler.errors import AssignmentError, ExpressionResultSavingError


class DeclaredName:
    def __init__(self, value_type, value):
        self._type = value_type
        self._value = value
        self._changes = 0
        self._used = False

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value, self._changes

    @property
    def used(self):
        return self._used

    def mark_as_used(self):
        self._used = True

    @value.setter
    def value(self, value):
        self._value = value
        self._changes += 1


class NamesDict:
    defaults = {
        "int": 0,
        "float": 0.0,
        "bool": False,
        "str": ""
    }

    np_types = {
        "int": np.int,
        "float": np.float,
        "bool": np.bool,
        "str": np.str
    }

    def __init__(self):
        self._dict = {}

    @property
    def dict(self):
        return self._dict

    def declare(self, name, value_type, value, array_size=None):
        if value is None:
            value = self.defaults[value_type.__name__]

        if name in self._dict:
            raise ValueError("Variable is already declared!")

        # using isinstance fails when trying to assign bool to int
        if value_type != type(value):
            raise AssignmentError("Value of wrong type assigned to {}. Expected {} given {}"
                                  .format(name, value_type.__name__, type(value).__name__))

        if array_size is None:
            declared_name = DeclaredName(value_type, value)
        else:
            value = np.zeros(array_size, dtype=self.np_types[value_type.__name__])
            declared_name = DeclaredName(value_type, value)
        self._dict[name] = declared_name

    def assign(self, name, value, array_index=None):
        if name not in self._dict:
            raise ValueError("Variable not defined!")

        expected_type = self._dict[name].type
        if expected_type != type(value):
            raise AssignmentError("Value of wrong type assigned to {}. Expected {} given {}"
                                  .format(name, expected_type.__name__, type(value).__name__))

        if array_index is None:
            self._dict[name].value = value
        else:
            array, _ = self._dict[name].value
            shape = array.shape
            if len(array_index) != len(shape):
                raise ValueError("Given indices number does not match dimension of an array")

            flattened_index = np.ravel_multi_index(array_index, shape)
            np.put(array, flattened_index, value)

    def read(self, name, array_index=None):
        if name not in self._dict:
            raise ValueError("Variable not defined!")

        self._dict[name].mark_as_used()

        result, changes = self._dict[name].value
        if array_index is None:
            return result, changes
        else:
            for index in array_index:
                result = result[index]
            return result, changes

    def contains(self, name):
        return name in self._dict


class DeclaredFunction:
    def __init__(self, arg_list, body, returned_value=None):
        self._arg_list = arg_list
        self._body = body
        self._returned_value = returned_value
        self._used = False

    @property
    def arg_list(self):
        return self._arg_list

    @property
    def body(self):
        return self._body

    @property
    def returned_value(self):
        return self._returned_value

    @property
    def used(self):
        return self._used

    def mark_as_used(self):
        self._used = True


class FunctionsDict:
    def __init__(self):
        self._dict = {}

    @property
    def dict(self):
        return self._dict

    def declare(self, name, arg_list, body, returned_value):
        if name in self._dict:
            raise ValueError("Function {} is already declared!".format(name))

        declared_function = DeclaredFunction(arg_list, body, returned_value)
        self._dict[name] = declared_function

    def read(self, name):
        if name not in self._dict:
            raise ValueError("Function not declared")

        self._dict[name].mark_as_used()
        return self._dict[name]

    def contains(self, name):
        return name in self._dict


class ExpressionSet:
    def __init__(self):
        self._set = []

    @property
    def set(self):
        return self._set

    def add(self, expression):
        self._set.append([expression, 0])

    def __get_element_index(self, expression):
        for index, element in enumerate(self._set):
            if element[0] == expression:
                return index

        return -1

    def get_if_declared(self, expression):
        index = self.__get_element_index(expression)
        if index != -1:
            element = self._set[index]
            self._set[index] = [element[0], element[1] + 1]
            return element[0]

        return None

    def get_occurrences(self, expression):
        for expr, counter in self._set:
            if expr == expression:
                return counter
        return 0

    def save_result(self, expression, result):
        for index, element in enumerate(self._set):
            if element[0] == expression:
                if len(element) == 3:
                    raise ExpressionResultSavingError("Result for this expression has been already saved")
                self._set[index] = [element[0], element[1], result]
                return

        raise ExpressionResultSavingError("Statement with given result has not been placed in expression set before")

    def get_result(self, expression):
        for element in self._set:
            if element[0] == expression:
                if len(element) == 3:
                    return element[2]
                else:
                    return None
        return None


class Scope:
    def __init__(self):
        self._functions = [FunctionsDict()]
        self._names = [NamesDict()]
        self._expressions = ExpressionSet()
        self._lock = threading.RLock()

    def start_new(self):
        with self._lock:
            self._functions.append(FunctionsDict())
            self._names.append(NamesDict())

    def end_current(self):
        with self._lock:
            self._functions.pop()
            self._names.pop()

    def declare_function(self, name, arg_list, body, returned_value):
        with self._lock:
            self._functions[-1].declare(name, arg_list, body, returned_value)

    def read_function(self, name):
        with self._lock:
            for functions_dict in reversed(self._functions):
                if functions_dict.contains(name):
                    return functions_dict.read(name)

            raise ValueError("Function {} not declared in any scope".format(name))

    def get_unused_functions(self):
        with self._lock:
            function_scope = self._functions[-1].dict
            return {k: v for k, v in function_scope.items() if not v.used}

    def declare_name(self, name, value_type, value=None, array_size=None):
        with self._lock:
            self._names[-1].declare(name, value_type, value, array_size)

    def get_dict_index_for_name(self, name):
        with self._lock:
            for names_dict in reversed(self._names):
                if names_dict.contains(name):
                    return self._names.index(names_dict)

            raise ValueError("Name {} not declared in any scope".format(name))

    def assign_name(self, name, value, array_index=None):
        with self._lock:
            index = self.get_dict_index_for_name(name)
            self._names[index].assign(name, value, array_index)

    def read_name(self, name, array_index=None):
        with self._lock:
            index = self.get_dict_index_for_name(name)
            return self._names[index].read(name, array_index)

    def get_unused_names(self):
        with self._lock:
            name_scope = self._names[-1].dict
            return {k: v for k, v in name_scope.items() if not v.used}

    def add_expression(self, expression):
        with self._lock:
            self._expressions.add(expression)

    def get_expression(self, expression):
        with self._lock:
            return self._expressions.get_if_declared(expression)

    def get_expression_occurrence(self, expression):
        with self._lock:
            return self._expressions.get_occurrences(expression)

    def save_expression_result(self, expression, result):
        with self._lock:
            self._expressions.save_result(expression, result)

    def get_expression_result(self, expression):
        with self._lock:
            return self._expressions.get_result(expression)
