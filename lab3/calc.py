from lexer import Lexer
from parser import Parser


def main():
    lexer = Lexer()
    lexer.build()
    parser = Parser(lexer.tokens)
    parser.build()

    while True:
        try:
            s = input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        elif s.lower() == "exit":
            break

        parser.parse(lexer, s)


if __name__ == '__main__':
    main()
