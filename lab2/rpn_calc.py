tokens = (
    'REAL', 'NUMBER', 'FUNCTION', 'POWER'
)

literals = ['=', '+', '-', '*', '/', '(', ')', ';']

# Tokens

t_FUNCTION = r'(sin|asin|cos|acos|tan|atan|exp|log|sqrt) (?=\d+|\(.*\)) (?i)'

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

    lexer.input(s)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)