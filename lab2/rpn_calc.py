tokens = (
    'REAL', 'NUMBER', 'FUNCTION', 'POWER'
)

literals = ['+', '-', '*', '/', ';']

# Tokens

t_FUNCTION = r'(sin|asin|cos|acos|tan|atan|exp|log|sqrt)(?i)'

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
import math

precedence = (
    ('left', '+', '-', '*', '/', 'FUNCTION', 'POWER'),
    ('left', 'UMINUS'),
    ('left', ';')
)

def p_statement_multi(p):
    '''statement : statement ';' statement'''

def p_statement_expr(p):
    'statement : expression'
    print(p[1])

def p_binary_op(p):
    '''expression : expression expression '+'
                  | expression expression '-'
                  | expression expression '*'
                  | expression expression '/'
                  '''
    if p[3] == '+':
        p[0] = p[1] + p[2]
    elif p[3] == '-':
        p[0] = p[1] - p[2]
    elif p[3] == '*':
        p[0] = p[1] * p[2]
    elif p[3] == '/':
        p[0] = p[1] / p[2]

def p_expression_power(p):
    'expression : expression expression POWER'
    p[0] = p[1] ** p[2]

def p_expression_function(p):
    'expression : expression FUNCTION'
    p[0] = getattr(math, p[2])(p[1])

def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]

def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]

def p_expression_real(p):
    "expression : REAL"
    p[0] = p[1]

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