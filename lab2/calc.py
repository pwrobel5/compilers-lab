# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
#
# based on https://github.com/dabeaz/ply/blob/master/example/calc/calc.py
# -----------------------------------------------------------------------------

import math

reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'for' : 'FOR',
    'function' : 'CUSTOMFUNC',
    'procedure' : 'PROCEDURE',
    'return' : 'RETURN'
}

tokens = [
    'NAME', 'REAL', 'NUMBER', 'FUNCTION', 'POWER', 'EQUALS', 'EQUALS_IGNORED',
    'RELATIONAL'
] + list(reserved.values())

literals = ['=', '+', '-', '*', '/', '(', ')', ';']

# Tokens

t_FUNCTION = r'(sin|asin|cos|acos|tan|atan|exp|log|sqrt) (?=\d+|\(.*\)) (?i)'
t_RELATIONAL = r'(<|>|<=|>=|!=|==)'

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'NAME')
    return t

def t_EQUALS_IGNORED(t):
    r'=(?!\s*\S+)'
    pass

def t_EQUALS(t):
    r'='
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
    ('nonassoc', 'IFX', 'WHILEX', 'FORX'),
    ('nonassoc', 'ELSE'),
    ('nonassoc', 'RELATIONAL'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('left', 'POWER'),
    ('right', 'FUNCTION'),    
    ('left', ';'),
    ('right', 'UMINUS')
)

# dictionary of names
names = {}

def p_statement_multi(p):
    '''statement : statement ';' statement
                 | empty'''

def p_expression_ignored_eq(p):
    'expression : EQUALS_IGNORED'
    pass

def p_empty(p):
    'empty : '

def p_statement_expr(p):
    '''statement : expression
                 | relation'''
    print(p[1])

def p_statement_other(p):
    '''statement : conditional
                 | loop
                 | assignment'''

def p_statement_assign(p):
    'assignment : NAME EQUALS expression'
    names[p[1]] = p[3]

def p_conditional(p):
    '''conditional : IF '(' relation ')' statement %prec IFX
                   | IF '(' relation ')' statement ELSE statement '''   
    if p[3]:
        p[0] = p[5]
    elif len(p) == 8:
        p[0] = p[7]

def p_while(p):
    '''loop : WHILE '(' relation ')' statement %prec WHILEX '''

def p_for(p):
    '''loop : FOR '(' assignment ';' relation ';' assignment ')' statement %prec FORX '''
    pass

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

def p_expression_power(p):
    'expression : expression POWER expression'
    p[0] = p[1] ** p[3]

def p_expression_function(p):
    'expression : FUNCTION expression'
    p[0] = getattr(math, p[1])(p[2])

def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]

def p_relation(p):
    'relation : expression RELATIONAL expression'
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
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]

def p_expression_real(p):
    "expression : REAL"
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
    '''
    lexer.input(s)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
    '''