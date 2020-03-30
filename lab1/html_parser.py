tokens = (
    'BOLD',
    'ORD_LIST',
    'UNORD_LIST',
    'LISTELEMENT',
    'LISTELEMENT_END',
    'CONTENTS'
)

states = (
    ('orderedlist', 'inclusive'),
    ('unorderedlist', 'inclusive')
)

def t_BOLD(t):
    r'(<b>|</b>) (?i)'
    t.value = '**'
    return t

def t_ORD_LIST(t):
    r'<ol>(?i)'
    t.lexer.begin('orderedlist')
    return t

def t_orderedlist_ORD_LIST(t):
    r'</ol>(?i)'
    t.lexer.begin('INITIAL')
    return t

def t_UNORD_LIST(t):
    r'<ul>(?i)'
    t.lexer.begin('unorderedlist')
    return t

def t_unorderedlist_UNORD_LIST(t):
    r'</ul>(?i)'
    t.lexer.begin('INITIAL')
    return t

list_element_state = 0

def t_orderedlist_LISTELEMENT(t):
    r'<li>(?i)'
    t.value = '1 '
    global list_element_state
    if list_element_state == 1:
        print("Incorrect list!")
    else:
        list_element_state = 1
        return t

def t_orderedlist_LISTELEMENT_END(t):
    r'</li>(?i)'
    global list_element_state
    if list_element_state == 0:
        print("Incorrect list!")
    else:
        list_element_state = 0
        return t

def t_unorderedlist_LISTELEMENT(t):
    r'<li>(?i)'
    t.value = '* '
    global list_element_state
    if list_element_state == 1:
        print("Incorrect list!")
    else:
        list_element_state = 1
        return t

def t_unorderedlist_LISTELEMENT_END(t):
    r'</li>(?i)'
    global list_element_state
    if list_element_state == 0:
        print("Incorrect list!")
    else:
        list_element_state = 0
        return t

t_CONTENTS = r'[ \t]*[a-zA-Z_ \t][a-zA-Z0-9_ \t]*'

t_ignore = " \t"

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
    elif s.lower() == "exit":
        break

    lexer.input(s)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)