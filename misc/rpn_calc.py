import math
import operator

import ply.lex as lex
import ply.yacc as yacc
from scipy.special import jv

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'function': 'CUSTOMFUNC',
    'call': 'CALL'
}

tokens = [
             'REAL', 'NUMBER', 'FUNCTION', 'POWER', 'BESSEL', 'RELATION', 'NAME'
         ] + list(reserved.values())

literals = ['+', '-', '*', '/', '%', '=', ';', '(', ')', '{', '}']

# Tokens
t_BESSEL = r'j'
t_RELATION = r'<|>|<=|>=|==|!='


def t_FUNCTION(t):
    r"""(sin|asin|cos|acos|tan|atan|exp|log|sqrt)"""
    return t


def t_POWER(t):
    r"""\*\*"""
    t.value = '**'
    return t


def t_REAL(t):
    r"""\-?\d+\.\d*|\.\d+"""
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r"""\-?\d+"""
    t.value = int(t.value)
    return t


def t_NAME(t):
    r"""[a-zA-Z_][a-zA-Z0-9_]*"""
    t.type = reserved.get(t.value.lower(), 'NAME')
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
    ('nonassoc', 'IFX'),
    ('nonassoc', 'ELSE'),
    ('left', '+', '-', '*', '/', 'FUNCTION', 'POWER'),
    ('left', ';')
)

names = {}


def p_sequence(p):
    """sequence : statement
                | '{' block '}'
       block : statement %prec IFX
             | statement ';' block """

    statement_list = []
    for statement in p[1:]:
        if statement in literals:
            continue

        statement_list.append(statement)

    p[0] = ("sequence", statement_list)


def p_statement_expr(p):
    """statement : relation
                 | assignment
                 | conditional
                 | while
                 | for
                 | customfunc
                 | call"""
    p[0] = p[1]


def p_statement_print(p):
    """statement : expression"""
    p[0] = ("statement", p[1])


def p_conditional(p):
    """conditional : IF '(' relation ')' sequence %prec IFX """
    p[0] = ("if", p[3], p[5])


def p_conditional_else(p):
    """conditional : IF '(' relation ')' sequence ELSE sequence """
    p[0] = ("if", p[3], p[5], p[7])


def p_while(p):
    """while : WHILE '(' relation ')' sequence """
    p[0] = ("while", p[3], p[5])


def p_for(p):
    """for : FOR '(' assignment ';' relation ';' assignment ')' sequence """
    p[0] = ("for", p[3], p[5], p[7], p[9])


def p_customfunc(p):
    """customfunc : CUSTOMFUNC NAME '(' ')' sequence """
    p[0] = ("customfunc", p[2], p[5])


def p_call(p):
    """call : CALL NAME """
    p[0] = ("call", p[2])


def p_assignment(p):
    """assignment : NAME '=' expression
                  | NAME '=' relation"""
    p[0] = ("assignment", p[1], p[3])


def p_expression(p):
    """expression : number
                  | name
                  | number rpnexpr
                  | name rpnexpr"""

    args = [p[1]]
    if len(p) > 2:
        args += p[2]
    p[0] = ("expression", args)


def p_rpnexpr(p):
    """rpnexpr : rpnexpr number
               | rpnexpr operator
               | rpnexpr function
               | rpnexpr name
               | number
               | operator
               | function
               | name"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_number(p):
    """number : NUMBER
              | REAL"""
    p[0] = ("number", p[1])


def p_name(p):
    """name : NAME"""
    p[0] = ("name", p[1])


def p_operator(p):
    """operator : '+'
                | '-'
                | '*'
                | '/'
                | '%'
                | POWER
                | BESSEL """
    p[0] = ("operator", p[1])


def p_function(p):
    """function : FUNCTION"""
    p[0] = ("function", p[1])


def p_relation(p):
    """relation : expression RELATION expression"""
    p[0] = ("relation", p[2], p[1], p[3])


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


arithmetic_operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '%': operator.mod,
    '**': operator.pow,
    'j': jv
}

relational_operators = {
    '<': operator.lt,
    '>': operator.gt,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}

functions = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'log': math.log10,
    'ln': math.log,
    'exp': math.exp
}

custom_functions = {}


def run(input_string):
    stype = input_string[0]
    sargs = input_string[1:]

    if stype == "sequence":
        for statement in sargs[0]:
            run(statement)

    elif stype == "statement":
        print(run(sargs[0]))

    elif stype == "expression":
        stack = []
        for x in sargs[0]:
            if x[0] == "number":
                stack.append(x[1])
            elif x[0] == "name":
                try:
                    stack.append(names[x[1]])
                except LookupError:
                    print("Incorrect variable name - %s!" % x[1])
                    stack.append(0)
            elif x[0] == "operator":
                second_number = stack.pop()
                first_number = stack.pop()
                result = arithmetic_operators[x[1]](first_number, second_number)
                stack.append(result)
            elif x[0] == "function":
                argument = stack.pop()
                stack.append(functions[x[1]](argument))

        if len(stack) == 0:
            print("Incorrect expression!")
        else:
            return stack.pop()

    elif stype == "number":
        return sargs[0]

    elif stype == "relation":
        left = run(sargs[1])
        right = run(sargs[2])
        return relational_operators[sargs[0]](left, right)

    elif stype == "assignment":
        names[sargs[0]] = run(sargs[1])

    elif stype == "if":
        condition = run(sargs[0])
        if condition:
            run(sargs[1])
        elif len(sargs) == 3:
            run(sargs[2])

    elif stype == "while":
        condition = run(sargs[0])
        while condition:
            run(sargs[1])
            condition = run(sargs[0])

    elif stype == "for":
        run(sargs[0])

        while run(sargs[1]):
            run(sargs[3])
            run(sargs[2])

    elif stype == "customfunc":
        custom_functions[sargs[0]] = sargs[1]

    elif stype == "call":
        try:
            func = custom_functions[sargs[0]]
            run(func)
        except LookupError:
            print("Incorrect function name!")


if __name__ == '__main__':
    lexer = lex.lex()
    parser = yacc.yacc()

    continue_reading = True
    while continue_reading:
        s = None
        try:
            equals_number = 0
            s = input('calc > ')
        except EOFError:
            continue_reading = False
        if not s:
            continue
        elif s.lower() == "exit":
            continue_reading = False

        if continue_reading:
            parsed_input = yacc.parse(s)
            run(parsed_input)
