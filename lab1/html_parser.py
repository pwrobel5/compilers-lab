tokens = ('BOLD', 'LISTSINGLE', 'CONTENTS')

def t_BOLD(t):
    r'<b>|<B>|</b>|</B>'
    t.value = '**'
    return t

def t_LISTSINGLE(t):
    r'<li>|</li>|<LI>|</LI>'
    t.value = '* '
    return t

t_CONTENTS = r'[ \t]*[a-zA-Z_ \t][a-zA-Z0-9_ \t]*'

t_ignore = r'<[a-zA-Z_ \t]*>'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

import ply.lex as lex
lexer = lex.lex()

while True:
    try:
        s = input('html > ')
    except EOFError:
        break
    if not s:
        continue

    lexer.input(s)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
# dorobic rozroznianie lsty punktowej i numerowanej, markdown serie 1. 1. 1. ... sobie przerobi na dobre numery