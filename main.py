import argparse

from graphviz import Digraph

from compiler.errors import *
from compiler.lexer import Lexer
from compiler.names import NamesTable
from compiler.parser import Parser
import compiler.tree_printer

lexer = Lexer()
lexer.build()
parser = Parser(lexer.tokens)
parser.build()
names = NamesTable()


def print_tokens(code):
    lexer.lexer.input(code)
    tok = lexer.lexer.token()
    while tok:
        print(tok)
        tok = lexer.lexer.token()


def run(code, ast_file_name=None):
    res = parser.parse(lexer, code)
    try:
        res.execute(names)

        if ast_file_name:
            graph = Digraph(format="png")
            res.print_tree(graph)
            graph.render(ast_file_name)

    except BinaryOperationError as err:
        msg, = err.args
        print("Error with binary operation: " + msg)
    except ConditionError as err:
        msg, = err.args
        print("Error with given condition: " + msg)
    except ConversionError as err:
        msg, = err.args
        print("Error with conversion: " + msg)
    except AssignmentError as err:
        msg, = err.args
        print("Error with assignment: " + msg)


def interpret_file(file_name, ast_file_name):
    with open(file_name, "r") as input_file:
        code = input_file.read()
        run(code, ast_file_name)


def run_interactive_console(ast_file_name):
    while True:
        try:
            s = input('calc > ')
        except (EOFError, KeyboardInterrupt):
            break
        if not s:
            continue
        elif s.lower() == "exit":
            break

        run(s, ast_file_name)


def main():
    argparser = argparse.ArgumentParser(description="Compiler")
    argparser.add_argument("input_file", nargs="?", type=str, help="Path to file with code")
    argparser.add_argument("-ast", type=str, help="Draw AST to given filename")

    args = argparser.parse_args()
    input_file_name = args.input_file

    if input_file_name:
        interpret_file(input_file_name, args.ast)
    else:
        run_interactive_console(args.ast)


if __name__ == '__main__':
    main()
