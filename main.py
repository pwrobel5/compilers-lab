import argparse

from graphviz import Digraph

import compiler.tree_printer
from compiler.lexer import Lexer
from compiler.names import Scope
from compiler.parser import Parser

lexer = Lexer()
lexer.build()
parser = Parser(lexer.tokens)
parser.build()
scope = Scope()


def print_tokens(code):
    lexer.lexer.input(code)
    tok = lexer.lexer.token()
    while tok:
        print(tok)
        tok = lexer.lexer.token()


def run(code, opt, ast_file_name=None, repl_mode=False):
    if repl_mode and code[-1] != ";":
        code += ";"

    res = parser.parse(lexer, code)

    if res is not None:
        if repl_mode:
            res.activate_repl_mode()

        res.execute(scope, opt)

        if ast_file_name:
            graph = Digraph(format="png")
            res.print_tree(graph)
            graph.render(ast_file_name)


def interpret_file(file_name, ast_file_name, opt):
    with open(file_name, "r") as input_file:
        code = input_file.read()
        run(code, opt, ast_file_name)


def run_interactive_console(ast_file_name, print_tokens_mode):
    run_console = True
    while run_console:
        s = None
        try:
            s = input('calc > ')
        except (EOFError, KeyboardInterrupt):
            run_console = False
        if not s:
            continue
        elif s.lower() == "exit":
            run_console = False

        if run_console:
            if print_tokens_mode:
                print_tokens(s)
            else:
                run(s, ast_file_name, repl_mode=True)


def main():
    argparser = argparse.ArgumentParser(description="Compiler")
    argparser.add_argument("input_file", nargs="?", type=str, help="Path to file with code")
    argparser.add_argument("-ast", type=str, help="Draw AST to given filename")
    argparser.add_argument("-opt", action="store_true", help="Use optimisations")
    argparser.add_argument("-token", action="store_true", help="Print tokens")

    args = argparser.parse_args()
    input_file_name = args.input_file
    opt = args.opt

    if input_file_name:
        interpret_file(input_file_name, args.ast, opt)
    else:
        run_interactive_console(args.ast, args.token)


if __name__ == '__main__':
    main()
