# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
#
# based on https://github.com/dabeaz/ply/blob/master/example/calc/calc.py
# -----------------------------------------------------------------------------

import sys
sys.path.insert(0, "../..")

states = (
    ('text','inclusive'),
)

tokens = (
    'NAME', 'REAL', 'NUMBER', 'FUNCTION', 'POWER', 'EQUALS', 'EQUALS_IGNORED',
    'TEXT', 'TEXT_BEGIN', 'TEXT_END', 'EQUATION'
)

literals = ['=', '+', '-', '*', '/', '(', ')']
equals_number = 0

# Tokens

t_FUNCTION = r'(sin|asin|cos|acos|tan|atan|exp|log|sqrt) (?=\d+|\(.*\)) (?i)'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

t_text_EQUATION = r'\$ .* \$'
t_text_TEXT = r'\w+'

def t_TEXT_BEGIN(t):
    r'\\text'
    t.lexer.begin('text')

def t_text_TEXT_END(t):
    r'\\text_end'
    t.lexer.begin('INITIAL')

def t_EQUALS_IGNORED(t):
    r'=(?!\s*\S+)'
    pass

def t_EQUALS(t):
    r'='
    global equals_number
    equals_number += 1
    if equals_number > 1:
        print("Too many equals signs! Expected 1 got %d" % equals_number)
        t.lexer.skip(1)
    else:
        return t

def t_POWER(t):
    r'\*\*'
    t.value = '^'
    return t

def t_REAL(t):
    r'\d+\.\d*|\.\d+'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)

# dictionary of names
names = {}

def p_statement_assign(p):
    'statement : NAME "=" expression'
    names[p[1]] = p[3]


def p_statement_expr(p):
    'statement : expression'
    print(p[1])


def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]


def p_expression_name(p):
    "expression : NAME"
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

import ply.yacc as yacc
parser = yacc.yacc()

while True:
    try:
        equals_number = 0
        s = input('calc > ')
    except EOFError:
        break
    if not s:
        continue
    elif s.lower() == "exit":
        break

    yacc.parse(s)