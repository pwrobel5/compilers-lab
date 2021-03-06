import math
import operator

import ply.yacc as yacc
from scipy.special import jv

from compiler import ast


class Parser:
    precedence = (
        ('right', 'IFX'),  # to avoid shift/reduce conflicts with conditionals
        ('left', 'OR', 'AND', 'XOR'),
        ('left', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV', 'MOD'),
        ('right', 'UMINUS'),
        ('right', 'POW'),
        ('nonassoc', 'INCR', 'DECR')
    )

    # bool value in tuple - determines if operation is reversible
    operations = {
        "+": (operator.add, True),
        "-": (operator.sub, False),
        "*": (operator.mul, True),
        "/": (operator.truediv, False),
        "%": (operator.mod, False),
        "**": (operator.pow, False),
        "==": (operator.eq, True),
        "!=": (operator.ne, True),
        "<": (operator.lt, False),
        "<=": (operator.le, False),
        ">": (operator.gt, False),
        ">=": (operator.ge, False),
        "&": (operator.and_, True),
        "|": (operator.or_, True),
        "^": (operator.xor, True)
    }

    built_in_functions = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "exp": math.exp,
        "log": math.log,
        "sqrt": math.sqrt,
        "j": jv
    }

    types = {
        "int": int,
        "real": float,
        "boolean": bool,
        "string": str
    }

    python_types_to_ast = {
        int: ast.Integer,
        float: ast.Real,
        bool: ast.Boolean,
        str: ast.String
    }

    conversions = {
        "inttostr": (int, str),
        "inttoreal": (int, float),
        "inttoboolean": (int, bool),
        "realtostr": (float, str),
        "realtoint": (float, int),
        "realtoboolean": (float, bool),
        "booleantostr": (bool, str),
        "booleantoint": (bool, int),
        "booleantoreal": (bool, float),
        "strtoint": (str, int),
        "strtoreal": (str, float),
        "strtoboolean": (str, bool)
    }

    def __init__(self, tokens):
        self._yacc = None
        self.tokens = tokens

    @staticmethod
    def is_number(element):
        return isinstance(element, (ast.Integer, ast.Real))

    @staticmethod
    def is_simple_value(element):
        return isinstance(element, (ast.Integer, ast.Real, ast.String, ast.Boolean))

    @property
    def yacc(self):
        return self._yacc

    def p_program(self, p):
        """program : statement_set"""
        p[0] = ast.Program(p[1])

    def p_statement(self, p):
        """statement : expression
                     | conditional
                     | loop
                     | declaration
                     | assignment
                     | customfunc
                     | procedure
                     | print
                     | parallel"""
        p[0] = p[1]

    def p_block(self, p):
        """block : '{' statement_set '}'"""
        p[0] = ast.Block(p[2])

    def p_statement_set(self, p):
        """statement_set : statement ';' statement_set
                         | statement ';'"""
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_arglist(self, p):
        """arglist : func_arg
                   | func_arg ',' arglist
                   |"""
        if len(p) == 2:
            p[0] = ast.FunctionArgumentList([p[1]])
        elif len(p) == 1:
            p[0] = ast.FunctionArgumentList([])
        else:
            p[3].append_argument(p[1])
            p[0] = p[3]

    def p_func_arg(self, p):
        """func_arg : TYPE NAME"""
        p[0] = ast.FunctionArgument(self.types[p[1]], p[2])

    def p_procedure(self, p):
        """procedure : PROCEDURE NAME '(' arglist ')' block"""
        p[0] = ast.CustomFunction(p[2], p[4], p[6])

    def p_customfunc(self, p):
        """customfunc : CUSTOMFUNC NAME '(' arglist ')' block RETURN expression"""
        p[0] = ast.CustomFunction(p[2], p[4], p[6], p[8])

    def p_print(self, p):
        """print : PRINT '(' expression ')' """
        p[0] = ast.Print(p[3])

    def p_parallel(self, p):
        """parallel : PARALLEL '(' statement_set ')'"""
        p[0] = ast.Parallel(p[3])

    def p_repeat_until(self, p):
        """loop : REPEAT statement UNTIL '(' expression ')'
                | REPEAT block UNTIL '(' expression ')'"""
        p[0] = ast.RepeatUntil(p[2], p[5])

    def p_for(self, p):
        """loop : FOR '(' assignment ';' expression ';' assignment ')' statement
                | FOR '(' assignment ';' expression ';' assignment ')' block"""
        p[0] = ast.For(p[3], p[5], p[7], p[9])

    def p_while(self, p):
        """loop : WHILE '(' expression ')' statement
                | WHILE '(' expression ')' block"""
        p[0] = ast.While(p[3], p[5])

    def p_if_else_conditional(self, p):
        """conditional : IF '(' expression ')' block ELSE block"""
        p[0] = ast.ConditionalIfElse(p[3], p[5], p[7])

    def p_if_conditional(self, p):
        """conditional : IF '(' expression ')' block %prec IFX"""
        p[0] = ast.ConditionalIf(p[3], p[5])

    def p_call_args(self, p):
        """call_args : expression
                     | expression ',' call_args
                     |"""
        if len(p) == 1:
            p[0] = ast.CallArgumentList([])
        elif len(p) == 2:
            p[0] = ast.CallArgumentList([p[1]])
        else:
            p[3].append_argument(p[1])
            p[0] = p[3]

    def p_expression_call(self, p):
        """expression : NAME '(' call_args ')'"""
        p[0] = ast.Call(p[1], p[3])

    def p_expression_prefix(self, p):
        """expression : INCR NAME
                      | DECR NAME"""
        p[0] = ast.PreFixExpression(p[2], p[1])

    def p_expression_postfix(self, p):
        """expression : NAME INCR
                      | NAME DECR"""
        p[0] = ast.PostFixExpression(p[1], p[2])

    def p_expression_function(self, p):
        """expression : FUNCTION '(' call_args ')'"""
        p[0] = ast.BuiltInFunction(self.built_in_functions[p[1]], p[3])

    def p_assignment(self, p):
        """assignment : NAME ASSIGN expression
                      | NAME array_size ASSIGN expression"""
        if len(p) == 4:
            p[0] = ast.Assignment(p[1], p[3])
        elif len(p) == 5:
            p[0] = ast.Assignment(p[1], p[4], index=p[2])

    def p_expression_uminus(self, p):
        """expression : SUB expression %prec UMINUS"""
        p[0] = ast.Minus(p[2])

    def p_expression_group(self, p):
        """expression : '(' expression ')'"""
        p[0] = p[2]

    def p_declaration(self, p):
        """declaration : TYPE NAME
                       | TYPE NAME array_size
                       | TYPE NAME ASSIGN expression"""
        if len(p) == 3:
            p[0] = ast.Declaration(p[2], self.types[p[1]])
        elif len(p) == 4:
            p[0] = ast.Declaration(p[2], self.types[p[1]], array_size=p[3])
        elif len(p) == 5:
            p[0] = ast.Declaration(p[2], self.types[p[1]], p[4])

    def p_array_size(self, p):
        """array_size : '[' expression ']'
                      | '[' expression ']' array_size"""
        if len(p) == 4:
            p[0] = [p[2]]
        elif len(p) == 5:
            p[0] = [p[2]] + p[4]

    def p_expression_conversion(self, p):
        """expression : INTTOSTR '(' expression ')'
                      | INTTOREAL '(' expression ')'
                      | INTTOBOOLEAN '(' expression ')'
                      | REALTOSTR '(' expression ')'
                      | REALTOINT '(' expression ')'
                      | REALTOBOOLEAN '(' expression ')'
                      | BOOLEANTOSTR '(' expression ')'
                      | BOOLEANTOINT '(' expression ')'
                      | BOOLEANTOREAL '(' expression ')'
                      | STRTOINT '(' expression ')'
                      | STRTOREAL '(' expression ')'
                      | STRTOBOOLEAN '(' expression ')'"""
        conversion = self.conversions[p[1]]
        p[0] = ast.Conversion(conversion[0], conversion[1], p[3])

    def p_expression_binop(self, p):
        """expression : expression ADD expression
                      | expression SUB expression
                      | expression MUL expression
                      | expression DIV expression
                      | expression MOD expression
                      | expression POW expression
                      | expression EQ expression
                      | expression NEQ expression
                      | expression LT expression
                      | expression LE expression
                      | expression GT expression
                      | expression GE expression
                      | expression AND expression
                      | expression OR expression
                      | expression XOR expression"""
        left = p[1]
        right = p[3]

        # operation between two constants
        if Parser.is_simple_value(left) and Parser.is_simple_value(right) and type(left) == type(right):
            if isinstance(left, ast.Boolean):
                if p[2] == "+":
                    p[2] = "|"
                elif p[2] == "*":
                    p[2] = "&"

            result = self.operations[p[2]][0](left.value, right.value)
            result_type = self.python_types_to_ast[type(result)]
            p[0] = result_type(result)
            return

        elif p[2] == "+" or p[2] == "-":
            # 0 + x = x or 0 - x = -x
            if Parser.is_number(left) and left.value == 0:
                p[0] = right if p[2] == "+" else ast.Minus(right)
                return
            # x +/- 0 = x
            elif Parser.is_number(right) and right.value == 0:
                p[0] = left
                return

        elif p[2] == "*":
            # 1 * x = x
            if Parser.is_number(left) and left.value == 1:
                p[0] = right
                return
            # x * 1 = x
            elif Parser.is_number(right) and right.value == 1:
                p[0] = left
                return
            # x * 0 = 0 * x = 0
            elif (Parser.is_number(left) and left.value == 0) or (Parser.is_number(right) and right.value == 0):
                p[0] = ast.Integer(0)
                return
            # x * 2 = x + x
            elif Parser.is_number(right) and right.value == 2:
                p[0] = ast.BinaryOperation(left, self.operations["+"], left)
                return
            # 2 * x = x + x
            elif Parser.is_number(left) and left.value == 2:
                p[0] = ast.BinaryOperation(right, self.operations["+"], right)
                return

        elif p[2] == "/":
            # x / 1 = x
            if Parser.is_number(right) and right.value == 1:
                p[0] = left
                return
            # x / 2 = 0.5 * x
            elif Parser.is_number(right) and right.value == 2:
                p[0] = ast.BinaryOperation(left, self.operations["*"], ast.Real(0.5))
                return

        elif p[2] == "**":
            # x ** 2 = x * x
            if Parser.is_number(right) and right.value == 2:
                p[0] = ast.BinaryOperation(left, self.operations["*"], left)
                return

        p[0] = ast.BinaryOperation(left, self.operations[p[2]], right)

    def p_expression_real(self, p):
        """expression : REAL"""
        p[0] = ast.Real(p[1])

    def p_expression_integer(self, p):
        """expression : INTEGER"""
        p[0] = ast.Integer(p[1])

    def p_expression_boolean(self, p):
        """expression : BOOLEAN"""
        p[0] = ast.Boolean(p[1])

    def p_expression_string(self, p):
        """expression : STRING"""
        p[0] = ast.String(p[1])

    def p_expression_name(self, p):
        """expression : NAME
                      | NAME array_size"""
        if len(p) == 2:
            p[0] = ast.Name(p[1])
        elif len(p) == 3:
            p[0] = ast.Name(p[1], p[2])

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    def build(self, **kwargs):
        self._yacc = yacc.yacc(module=self, **kwargs)

    def parse(self, lexer, text):
        return self._yacc.parse(text, lexer=lexer.lexer)
