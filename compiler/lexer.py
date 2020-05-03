import ply.lex as lex


class Lexer:
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'repeat': 'REPEAT',
        'until': 'UNTIL',
        'function': 'CUSTOMFUNC',
        'procedure': 'PROCEDURE',
        'return': 'RETURN',
        'print': 'PRINT',
        'inttostr': 'INTTOSTR',
        'inttoreal': 'INTTOREAL',
        'inttoboolean': 'INTTOBOOLEAN',
        'realtostr': 'REALTOSTR',
        'realtoint': 'REALTOINT',
        'realtoboolean': 'REALTOBOOLEAN',
        'booleantostr': 'BOOLEANTOSTR',
        'booleantoint': 'BOOLEANTOINT',
        'booleantoreal': 'BOOLEANTOREAL',
        'strtoint': 'STRTOINT',
        'strtoreal': 'STRTOREAL',
        'strtoboolean': 'STRTOBOOLEAN'
    }
    tokens = ['INCR', 'DECR', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD',
              'POW', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE',
              'ASSIGN', 'TYPE', 'FUNCTION', 'NAME', 'REAL', 'INTEGER',
              'BOOLEAN', 'STRING'
              ] + list(reserved.values())

    literals = ['(', ')', ';', ',', '{', '}']

    # Tokens
    t_INCR = r'\+\+'
    t_DECR = r'--'
    t_ADD = r'\+'
    t_SUB = r'-'
    t_MUL = r'\*'
    t_DIV = r'/'
    t_MOD = r'%'
    t_POW = r'\*\*'
    t_EQ = r'=='
    t_NEQ = r'!='
    t_LT = r'<'
    t_LE = r'<='
    t_GT = r'>'
    t_GE = r'>='
    t_ASSIGN = r':='

    def __init__(self):
        self._lexer = None

    @property
    def lexer(self):
        return self._lexer

    def t_TYPE(self, t):
        r"""\b(int|real|boolean|string)\b"""
        return t

    def t_FUNCTION(self, t):
        r"""(sin|asin|cos|acos|tan|atan|exp|log|sqrt|j) (?=\d+|\(.*\)) (?i)"""
        return t

    def t_REAL(self, t):
        r"""\d+\.\d*|\.\d+"""
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t):
        r"""\d+"""
        t.value = int(t.value)
        return t

    def t_BOOLEAN(self, t):
        r"""true|false"""
        t.value = t.value.lower()
        if t.value == "true":
            t.value = True
        elif t.value == "false":
            t.value = False
        return t

    def t_STRING(self, t):
        r"""'[^\']*'|\"[^\"]*\""""
        t.value = t.value[1:-1]
        return t

    def t_NAME(self, t):
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        t.type = self.reserved.get(t.value.lower(), 'NAME')
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r"""\n+"""
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def build(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)
