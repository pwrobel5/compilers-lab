from compiler.lexer import Lexer
from compiler.parser import Parser
from graphviz import Digraph
from compiler.names import NamesTable

import compiler.tree_printer


def main():
    lexer = Lexer()
    lexer.build()
    parser = Parser(lexer.tokens)
    parser.build()
    names = NamesTable()

    while True:
        graph = Digraph(format='png')
        try:
            s = input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        elif s.lower() == "exit":
            break

        res = parser.parse(lexer, s)
        print(res.execute(names))
        res.print_tree(graph)
        graph.render('ast')
        '''
        lexer.lexer.input(s)
        while True:
            tok = lexer.lexer.token()
            if not tok:
                break
            print(tok)
        '''


if __name__ == '__main__':
    main()
