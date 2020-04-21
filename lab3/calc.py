# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
#
# based on https://github.com/dabeaz/ply/blob/master/example/calc/calc.py
# -----------------------------------------------------------------------------

import math

import ply.lex as lex
import ply.yacc as yacc
from scipy.special import jv

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'function': 'CUSTOMFUNC',
    'procedure': 'PROCEDURE',
    'return': 'RETURN',
    'end': 'END',
    'print': 'PRINT'
}

tokens = [
             'NAME', 'REAL', 'NUMBER', 'FUNCTION', 'POWER', 'EQUALS',
             'RELATIONAL', 'INCR', 'DECR', 'BESSEL'
         ] + list(reserved.values())

literals = ['=', '+', '-', '*', '/', '(', ')', ';', ',', '%']

# Tokens

t_RELATIONAL = r'(<|>|<=|>=|!=|==)'
t_INCR = r'\+\+'
t_DECR = r'--'


def t_FUNCTION(t):
    r"""(sin|asin|cos|acos|tan|atan|exp|log|sqrt) (?=\d+|\(.*\)) (?i)"""
    return t


def t_BESSEL(t):
    r"""j (?i) (?=\d+|\(.*\))"""
    return t


def t_NAME(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    t.type = reserved.get(t.value.lower(), 'NAME')
    return t


def t_EQUALS(t):
    r"""="""
    return t


def t_POWER(t):
    r"""\*\*"""
    t.value = '^'
    return t


def t_REAL(t):
    r"""\d+\.\d*|\.\d+"""
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


t_ignore = " \t"


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Parsing rules
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


def p_statement_multi(p):
    """statement : statement ';' statement
                 | empty"""


def p_empty(p):
    """empty : """


def p_statement_expr(p):
    """statement : expression
                 | relation"""
    print(p[1])


def p_statement_other(p):
    """statement : conditional
                 | loop
                 | assignment
                 | customfunc
                 | procedure
                 | print"""


def p_print(p):
    """print : PRINT '(' NAME ')' """
    try:
        print(names[p[3]])
    except LookupError:
        print("Incorrect identifier!")


def p_statement_assign(p):
    """assignment : NAME EQUALS expression"""
    names[p[1]] = p[3]


def p_conditional(p):
    """conditional : IF '(' relation ')' statement %prec IFX
                   | IF '(' relation ')' statement ELSE statement """
    if p[3]:
        p[0] = p[5]
    elif len(p) == 8:
        p[0] = p[7]


def p_while(p):
    """loop : WHILE '(' relation ')' statement %prec WHILEX """


def p_for(p):
    """loop : FOR '(' assignment ';' relation ';' assignment ')' statement %prec FORX"""


def p_customfunc(p):
    """customfunc : CUSTOMFUNC NAME '(' arglist ')' statement RETURN NAME %prec CUSTOMFUNCX
                  | CUSTOMFUNC NAME '(' ')' statement RETURN NAME %prec CUSTOMFUNCX"""


def p_procedure(p):
    """procedure : PROCEDURE NAME '(' arglist ')' statement END %prec PROCX
                 | PROCEDURE NAME '(' ')' statement END %prec PROCX"""


def p_arglist(p):
    """arglist : NAME
               | NAME ',' arglist  """


def p_expression_binop(p):
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


def p_expression_prefix(p):
    """expression : INCR NAME
                  | DECR NAME"""
    try:
        if p[1] == '++':
            names[p[2]] += 1
        elif p[1] == '--':
            names[p[2]] -= 1

        p[0] = names[p[2]]
    except LookupError:
        print("Incorrect identifier!")
        p[0] = 0


def p_expression_postfix(p):
    """expression : NAME INCR
                  | NAME DECR"""
    try:
        p[0] = names[p[1]]
        if p[2] == '++':
            names[p[1]] += 1
        elif p[2] == '--':
            names[p[1]] -= 1
    except LookupError:
        print("Incorrect identifier!")
        p[0] = 0


def p_expression_power(p):
    """expression : expression POWER expression"""
    p[0] = p[1] ** p[3]


def p_expression_function(p):
    """expression : FUNCTION expression"""
    p[0] = getattr(math, p[1])(p[2])


def p_expression_bessel(p):
    """expression : BESSEL '(' NUMBER ',' expression ')' """
    p[0] = jv(p[3], p[5])


def p_expression_uminus(p):
    """expression : '-' expression %prec UMINUS"""
    p[0] = -p[2]


def p_relation(p):
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


def p_expression_group(p):
    """expression : '(' expression ')'"""
    p[0] = p[2]


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = p[1]


def p_expression_real(p):
    """expression : REAL"""
    p[0] = p[1]


def p_expression_name(p):
    """expression : NAME"""
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


lexer = lex.lex()
parser = yacc.yacc()
equals_number = 0


def main():
    while True:
        try:
            s = input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        elif s.lower() == "exit":
            break

        yacc.parse(s)


if __name__ == '__main__':
    main()