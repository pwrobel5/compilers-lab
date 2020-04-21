import ply.lex as lex


class Lexer:
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'function': 'CUSTOMFUNC',
        'procedure': 'PROCEDURE',
        'return': 'RETURN',
        'end': 'END',
        'print': 'PRINT'
    }
    tokens = ['NAME', 'REAL', 'NUMBER', 'FUNCTION', 'POWER', 'EQUALS',
              'RELATIONAL', 'INCR', 'DECR', 'BESSEL'
              ] + list(reserved.values())

    literals = ['=', '+', '-', '*', '/', '(', ')', ';', ',', '%']

    # Tokens
    t_RELATIONAL = r'(<|>|<=|>=|!=|==)'
    t_INCR = r'\+\+'
    t_DECR = r'--'

    def __init__(self):
        self._lexer = None

    @property
    def lexer(self):
        return self._lexer

    def t_FUNCTION(self, t):
        r"""(sin|asin|cos|acos|tan|atan|exp|log|sqrt) (?=\d+|\(.*\)) (?i)"""
        return t

    def t_BESSEL(self, t):
        r"""j (?i) (?=\d+|\(.*\))"""
        return t

    def t_NAME(self, t):
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        t.type = self.reserved.get(t.value.lower(), 'NAME')
        return t

    def t_EQUALS(self, t):
        r"""="""
        return t

    def t_POWER(self, t):
        r"""\*\*"""
        t.value = '^'
        return t

    def t_REAL(self, t):
        r"""\d+\.\d*|\.\d+"""
        t.value = float(t.value)
        return t

    def t_NUMBER(self, t):
        r"""\d+"""
        t.value = int(t.value)
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
