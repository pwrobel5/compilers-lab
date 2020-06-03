import argparse

from graphviz import Digraph

import compiler.tree_printer
from compiler.errors import *
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
    if repl_mode:
        code += ";"

    res = parser.parse(lexer, code)
    try:
        if repl_mode:
            statements = res.statement_list
            for statement in statements:
                statement_result = statement.execute(scope, opt)
                if statement_result is not None:
                    print(statement_result)
        else:
            res.execute(scope, opt)

        if ast_file_name:
            graph = Digraph(format="png")
            res.print_tree(graph)
            graph.render(ast_file_name)

    except BinaryOperationError as err:
        msg, = err.args
        print("Error with binary operation: {}".format(msg))
    except ConditionError as err:
        msg, = err.args
        print("Error with given condition: {}".format(msg))
    except ConversionError as err:
        msg, = err.args
        print("Error with conversion: {}".format(msg))
    except AssignmentError as err:
        msg, = err.args
        print("Error with assignment: {}".format(msg))
    except ValueError as err:
        msg, = err.args
        print("Value Error: {}".format(msg))


def interpret_file(file_name, ast_file_name, opt):
    with open(file_name, "r") as input_file:
        code = input_file.read()
        run(code, opt, ast_file_name)


def run_interactive_console(ast_file_name, print_tokens_mode):
    while True:
        try:
            s = input('calc > ')
        except (EOFError, KeyboardInterrupt):
            break
        if not s:
            continue
        elif s.lower() == "exit":
            break

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
