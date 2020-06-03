# based on https://github.com/StevenChangZH/Markdown_python_compiler/blob/master/codes/plyLex.py

import ply.lex as lex

states = (
    ('equation', 'exclusive'),
)

tokens = (
    'SEPARATOR',
    'LISTNUMBER',
    'LISTSINGLE',
    'LISTDOUBLE',

    'TAB',

    'POUNDSIGN',
    'EXCLAMATION',
    'DOLLAR',
    'CODEFIELD',
    'NEWLINE',
    'CODE',
    'BOLD',
    'LATICS',

    'LANGLE',
    'RANGLE',
    'LBRACKET',
    'RBRACKET',
    'LPAREN',
    'RPAREN',

    'CONTENTS',

    'EQUATION',
    'EQUATION_END',
    'NAME',
    'REAL',
    'NUMBER',
    'FUNCTION',
    'POWER',

    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'MOD',
    'EQ',
    'NEQ',
    'LT',
    'LE',
    'GT',
    'GE'
)

t_equation_FUNCTION = r'(sin|asin|cos|acos|tan|atan|exp|log|sqrt) (?=\d+|\(.*\)) (?i)'
t_equation_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

t_equation_ADD = r'\+'
t_equation_SUB = r'-'
t_equation_MUL = r'\*'
t_equation_DIV = r'/'
t_equation_MOD = r'%'
t_equation_EQ = r'='
t_equation_NEQ = r'!='
t_equation_LT = r'<'
t_equation_LE = r'<='
t_equation_GT = r'>'
t_equation_GE = r'>='
t_equation_LPAREN = r'\('
t_equation_RPAREN = r'\)'
t_equation_RBRACKET = r'\['
t_equation_LBRACKET = r'\]'


def t_EQUATION(t):
    r"""\$"""
    t.lexer.begin('equation')
    return t


def t_equation_EQUATION_END(t):
    r"""\$"""
    t.lexer.begin('INITIAL')
    return t


def t_equation_POWER(t):
    r"""\*\*"""
    t.value = '^'
    return t


def t_equation_REAL(t):
    r"""\d+\.\d*|\.\d+"""
    t.value = float(t.value)
    return t


def t_equation_NUMBER(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


t_equation_ignore = " \t"


def t_equation_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count("\n")


def t_equation_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def t_SEPARATOR(t):
    r"""[\n\r]{1}[ ]{0,1}[*\-=]([ ]{0,1}[*\-=]){2,}[ ]{0,}"""
    return t


def t_LISTNUMBER(t):
    r"""[\n\r]{1}[ \t]*[0-9]+[.]{1}[ ]{1}"""
    t.value = t.value[1:-2]
    return t


def t_LISTSINGLE(t):
    r"""[\n\r]{1}[ \t]*[\*\-\+]{1}[ ]{1}"""
    t.value = t.value[1:-1]
    return t


def t_LISTDOUBLE(t):
    r"""[\n\r]{1}[ \t]*[\*\-\+]{2}[ ]{1}"""
    t.value = t.value[1:-2]
    return t


def t_TAB(t):
    r"""[\t]{1}"""
    return t


def t_POUNDSIGN(t):
    r"""[ ]{0,1}[#]{1,6}"""
    t.value = str(len(t.value))
    return t


def t_EXCLAMATION(t):
    r"""[ ]{0,1}[!]{1}"""
    return t


def t_DOLLAR(t):
    r"""[$]{1}"""
    return t


def t_CODEFIELD(t):
    """[\n\r]{1}[ ]{0,1}[`]{3}[ ]{0,}"""
    return t


def t_NEWLINE(t):
    r"""[\r\n]"""
    t.value = len(t.value)
    return t


def t_CODE(t):
    r"""[`]{1}"""
    return t


def t_BOLD(t):
    r"""[*_]{2}"""
    return t


def t_LATICS(t):
    r"""[*_]{1}"""
    return t


def t_LANGLE(t):
    r"""[<]{1}"""
    return t


def t_RANGLE(t):
    r"""[>]{1}"""
    return t


def t_LBRACKET(t):
    r"""[\[]{1}"""
    return t


def t_RBRACKET(t):
    r"""[\]]{1}"""
    return t


def t_LPAREN(t):
    r"""[(]{1}"""
    return t


def t_RPAREN(t):
    r"""[)]{1}"""
    return t


def t_CONTENTS(t):
    r"""([0-9a-zA-Z]|[., :;/\'’?{}"\\+^#|=%&])+"""
    return t


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


if __name__ == '__main__':
    lexer = lex.lex()

    input_file = open("data.md", "r")
    data = input_file.read()
    input_file.close()

    lexer.input(data)

    token = lexer.token()
    while token:
        print(token)
        token = lexer.token()
