import math
from compiler import ast
import operator

import ply.yacc as yacc


# from scipy.special import jv


class Parser:
    precedence = (
        ('nonassoc', 'IFX', 'WHILEX', 'FORX', 'CUSTOMFUNCX', 'PROCX'),
        ('nonassoc', 'ELSE'),
        ('left', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV', 'MOD'),
        ('right', 'UMINUS'),
        ('right', 'POW'),
        ('nonassoc', 'INCR', 'DECR')
    )

    operations = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "%": operator.mod,
        "**": operator.pow,
        "==": operator.eq,
        "!=": operator.ne,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge
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
        # "j": jv
    }

    # dictionary of names
    names = {}

    def __init__(self, tokens):
        self._yacc = None
        self.tokens = tokens

    @property
    def yacc(self):
        return self._yacc

    def p_statement(self, p):
        """statement : expression
                     | conditional
                     | loop
                     | declaration
                     | assignment
                     | customfunc
                     | procedure
                     | print"""
        p[0] = ast.Statement(p[1])

    def p_print(self, p):
        """print : PRINT '(' NAME ')' """
        try:
            print(self.names[p[3]])
        except LookupError:
            print("Incorrect identifier!")

    def p_while(self, p):
        """loop : WHILE '(' expression ')' statement %prec WHILEX """

    def p_for(self, p):
        """loop : FOR '(' assignment ';' expression ';' assignment ')' statement %prec FORX"""

    def p_customfunc(self, p):
        """customfunc : CUSTOMFUNC NAME '(' arglist ')' statement RETURN NAME %prec CUSTOMFUNCX
                      | CUSTOMFUNC NAME '(' ')' statement RETURN NAME %prec CUSTOMFUNCX"""

    def p_procedure(self, p):
        """procedure : PROCEDURE NAME '(' arglist ')' statement END %prec PROCX
                     | PROCEDURE NAME '(' ')' statement END %prec PROCX"""

    def p_arglist(self, p):
        """arglist : NAME
                   | NAME ',' arglist  """

    def p_if_conditional(self, p):
        """conditional : IF '(' expression ')' statement %prec IFX"""
        p[0] = ast.ConditionalIf(p[3], p[5])

    def p_expression_prefix(self, p):
        """expression : INCR NAME
                      | DECR NAME"""
        p[0] = ast.PreFixExpression(p[2], p[1])

    def p_expression_postfix(self, p):
        """expression : NAME INCR
                      | NAME DECR"""
        p[0] = ast.PostFixExpression(p[1], p[2])

    def p_expression_function(self, p):
        """expression : FUNCTION '(' expression ')'"""
        p[0] = ast.BuiltInFunction(self.built_in_functions[p[1]], [p[3]])

    def p_assignment(self, p):
        """assignment : NAME ASSIGN expression"""
        p[0] = ast.Assignment(p[1], p[3])

    def p_expression_uminus(self, p):
        """expression : SUB expression %prec UMINUS"""
        p[0] = ast.Minus(p[2])

    def p_expression_group(self, p):
        """expression : '(' expression ')'"""
        p[0] = p[2]

    def p_expression_name(self, p):
        """expression : NAME"""
        p[0] = ast.Name(p[1])

    def p_declaration(self, p):
        """declaration : TYPE NAME
                       | TYPE NAME ASSIGN expression"""
        if len(p) == 3:
            p[0] = ast.Declaration(p[2], p[1])
        elif len(p) == 5:
            p[0] = ast.Declaration(p[2], p[1], p[4])

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
                      | expression GE expression"""
        left = p[1]
        right = p[3]
        p[0] = ast.BinaryOperation(left, self.operations[p[2]], right)

    def p_expression_real(self, p):
        """expression : REAL"""
        p[0] = ast.Real(p[1])

    def p_expression_integer(self, p):
        """expression : INTEGER"""
        p[0] = ast.Integer(p[1])

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    def build(self, **kwargs):
        self._yacc = yacc.yacc(module=self, **kwargs)

    def parse(self, lexer, text):
        return self._yacc.parse(text, lexer=lexer.lexer)
