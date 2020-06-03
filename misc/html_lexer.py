import ply.lex as lex

tokens = (
    'HTML',
    'BODY',
    'BOLD',
    'ITALIC',
    'UNDERLINE',
    'PARAGRAPH',
    'NEWLINE',
    'ORD_LIST',
    'HEADER1',
    'HEADER2',
    'HEADER3',
    'UNORD_LIST',
    'LISTELEMENT',
    'LISTELEMENT_END',
    'CONTENTS'
)

states = (
    ('orderedlist', 'inclusive'),
    ('unorderedlist', 'inclusive')
)

t_HTML = r"""(<html>|</html>)"""
t_BODY = r"""(<body>|</body>)"""
t_BOLD = r"""(<b>|</b>) (?i)"""
t_ITALIC = r"""(<i>|</i>)"""
t_UNDERLINE = r"""(<u>|</u>)"""
t_PARAGRAPH = r"""(<p>|</p>)"""
t_NEWLINE = r"""(<br>|<br />)"""


def t_ORD_LIST(t):
    r"""<ol>(?i)"""
    t.lexer.begin('orderedlist')
    return t


def t_orderedlist_ORD_LIST(t):
    r"""</ol>(?i)"""
    t.lexer.begin('INITIAL')
    return t


t_HEADER1 = r"""(<h1>|</h1>)"""
t_HEADER2 = r"""(<h2>|</h2>)"""
t_HEADER3 = r"""(<h3>|</h3>)"""


def t_UNORD_LIST(t):
    r"""<ul>(?i)"""
    t.lexer.begin('unorderedlist')
    return t


def t_unorderedlist_UNORD_LIST(t):
    r"""</ul>(?i)"""
    t.lexer.begin('INITIAL')
    return t


list_element_state = 0


def t_orderedlist_LISTELEMENT(t):
    r"""<li>(?i)"""
    global list_element_state
    if list_element_state == 1:
        print("Incorrect list!")
    else:
        list_element_state = 1
        return t


def t_orderedlist_LISTELEMENT_END(t):
    r"""</li>(?i)"""
    global list_element_state
    if list_element_state == 0:
        print("Incorrect list!")
    else:
        list_element_state = 0
        return t


def t_unorderedlist_LISTELEMENT(t):
    r"""<li>(?i)"""
    global list_element_state
    if list_element_state == 1:
        print("Incorrect list!")
    else:
        list_element_state = 1
        return t


def t_unorderedlist_LISTELEMENT_END(t):
    r"""</li>(?i)"""
    global list_element_state
    if list_element_state == 0:
        print("Incorrect list!")
    else:
        list_element_state = 0
        return t


t_CONTENTS = r'[ \t]*[a-zA-Z_ \t][a-zA-Z0-9_ \t]*'
t_ignore = " \t"


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


if __name__ == '__main__':
    lexer = lex.lex()

    input_file = open("data.html", "r")
    data = input_file.read()
    input_file.close()

    lexer.input(data)

    token = lexer.token()
    while token:
        print(token)
        token = lexer.token()
