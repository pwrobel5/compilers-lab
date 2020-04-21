import math

import ply.yacc as yacc
from scipy.special import jv


class Parser:
    precedence = (
        ('nonassoc', 'IFX', 'WHILEX', 'FORX', 'CUSTOMFUNCX', 'PROCX'),
        ('nonassoc', 'ELSE'),
        ('nonassoc', 'RELATIONAL'),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        ('left', 'POWER'),
        ('right', 'FUNCTION'),
        ('left', ';'),
        ('right', 'UMINUS'),
        ('nonassoc', 'INCR', 'DECR')
    )

    # dictionary of names
    names = {}

    def __init__(self, tokens):
        self._yacc = None
        self.tokens = tokens

    @property
    def yacc(self):
        return self._yacc

    def p_statement_multi(self, p):
        """statement : statement ';' statement
                     | empty"""

    def p_empty(self, p):
        """empty : """

    def p_statement_expr(self, p):
        """statement : expression
                     | relation"""
        print(p[1])

    def p_statement_other(self, p):
        """statement : conditional
                     | loop
                     | assignment
                     | customfunc
                     | procedure
                     | print"""

    def p_print(self, p):
        """print : PRINT '(' NAME ')' """
        try:
            print(self.names[p[3]])
        except LookupError:
            print("Incorrect identifier!")

    def p_statement_assign(self, p):
        """assignment : NAME EQUALS expression"""
        self.names[p[1]] = p[3]

    def p_conditional(self, p):
        """conditional : IF '(' relation ')' statement %prec IFX
                       | IF '(' relation ')' statement ELSE statement """
        if p[3]:
            p[0] = p[5]
        elif len(p) == 8:
            p[0] = p[7]

    def p_while(self, p):
        """loop : WHILE '(' relation ')' statement %prec WHILEX """

    def p_for(self, p):
        """loop : FOR '(' assignment ';' relation ';' assignment ')' statement %prec FORX"""

    def p_customfunc(self, p):
        """customfunc : CUSTOMFUNC NAME '(' arglist ')' statement RETURN NAME %prec CUSTOMFUNCX
                      | CUSTOMFUNC NAME '(' ')' statement RETURN NAME %prec CUSTOMFUNCX"""

    def p_procedure(self, p):
        """procedure : PROCEDURE NAME '(' arglist ')' statement END %prec PROCX
                     | PROCEDURE NAME '(' ')' statement END %prec PROCX"""

    def p_arglist(self, p):
        """arglist : NAME
                   | NAME ',' arglist  """

    def p_expression_binop(self, p):
        """expression : expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression '/' expression
                      | expression '%' expression"""
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '%':
            p[0] = p[1] % p[3]

    def p_expression_prefix(self, p):
        """expression : INCR NAME
                      | DECR NAME"""
        try:
            if p[1] == '++':
                self.names[p[2]] += 1
            elif p[1] == '--':
                self.names[p[2]] -= 1

            p[0] = self.names[p[2]]
        except LookupError:
            print("Incorrect identifier!")
            p[0] = 0

    def p_expression_postfix(self, p):
        """expression : NAME INCR
                      | NAME DECR"""
        try:
            p[0] = self.names[p[1]]
            if p[2] == '++':
                self.names[p[1]] += 1
            elif p[2] == '--':
                self.names[p[1]] -= 1
        except LookupError:
            print("Incorrect identifier!")
            p[0] = 0

    def p_expression_power(self, p):
        """expression : expression POWER expression"""
        p[0] = p[1] ** p[3]

    def p_expression_function(self, p):
        """expression : FUNCTION expression"""
        p[0] = getattr(math, p[1])(p[2])

    def p_expression_bessel(self, p):
        """expression : BESSEL '(' NUMBER ',' expression ')' """
        p[0] = jv(p[3], p[5])

    def p_expression_uminus(self, p):
        """expression : '-' expression %prec UMINUS"""
        p[0] = -p[2]

    def p_relation(self, p):
        """relation : expression RELATIONAL expression"""
        if p[2] == '==':
            p[0] = p[1] == p[3]
        elif p[2] == "!=":
            p[0] = p[1] != p[3]
        elif p[2] == ">":
            p[0] = p[1] > p[3]
        elif p[2] == ">=":
            p[0] = p[1] >= p[3]
        elif p[2] == "<":
            p[0] = p[1] < p[3]
        elif p[2] == "<=":
            p[0] = p[1] <= p[3]

    def p_expression_group(self, p):
        """expression : '(' expression ')'"""
        p[0] = p[2]

    def p_expression_number(self, p):
        """expression : NUMBER"""
        p[0] = p[1]

    def p_expression_real(self, p):
        """expression : REAL"""
        p[0] = p[1]

    def p_expression_name(self, p):
        """expression : NAME"""
        try:
            p[0] = self.names[p[1]]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    def build(self, **kwargs):
        self._yacc = yacc.yacc(module=self, **kwargs)

    def parse(self, lexer, text):
        self._yacc.parse(text, lexer=lexer.lexer)
