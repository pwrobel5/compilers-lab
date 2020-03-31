tokens = (
    'REAL', 'NUMBER', 'FUNCTION', 'POWER', 'BESSEL'
)

literals = ['+', '-', '*', '/', '%', ';']

# Tokens

t_FUNCTION = r'(sin|asin|cos|acos|tan|atan|exp|log|sqrt)(?i)'
t_BESSEL = r'j'

def t_POWER(t):
    r'\*\*'
    t.value = '**'
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
    ('left', '+', '-', '*', '/', 'FUNCTION', 'POWER'),
    ('left', 'UMINUS'),
    ('left', ';')
)

def p_statement_multi(p):
    '''statement : statement ';' statement'''

def p_statement_expr(p):
    'statement : expression'
    print(p[1])
    p[0] = p[1]

def p_binary_op(p):
    '''expression : expression expression '+'
                  | expression expression '-'
                  | expression expression '*'
                  | expression expression '/'
                  | expression expression '%'
                  | expression expression POWER
                  | expression expression BESSEL
                  '''
    p[0] = ("binary_op", p[1], p[2], ("operator", p[3]))

def p_expression_function(p):
    'expression : expression FUNCTION'
    p[0] = ("function", p[2], p[1])

def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]

def p_expression_number(p):
    '''expression : NUMBER
                  | REAL'''
    p[0] = ("number", p[1])

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

import ply.yacc as yacc
parser = yacc.yacc()

import operator
from scipy.special import jv
operators = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,
    '%' : operator.mod,
    '**' : operator.pow,
    'j' : jv
}

import math
functions = {
    'sin' : math.sin,
    'cos' : math.cos,
    'tan' : math.tan,
    'asin' : math.asin,
    'acos' : math.acos,
    'atan' : math.atan,
    'log' : math.log10,
    'ln' : math.log,
    'exp' : math.exp
}

def run(s):
    stype = s[0]
    sargs = s[1:]

    if stype == "binary_op":
        stack = []
        for x in sargs:
            if x[0] == "number":
                stack.append(x[1])
            elif x[0] == "binary_op":
                stack.append(run(x))
            elif x[0] == "operator":
                second_number = stack.pop()
                first_number = stack.pop()
                result = operators[x[1]](first_number, second_number)
                stack.append(result)
        
        if len(stack) != 1:
            print("Incorrect expression!")
        else:
            return stack[0]
    elif stype == "function":
        return functions[sargs[0]](run(sargs[1]))
    elif stype == "number":
        return sargs[0]
            


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

    p = yacc.parse(s)
    print(p)
    print(run(p))