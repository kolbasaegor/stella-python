import sys

from antlr4 import *
from antlr4.tree.Trees import Trees
from stella.stellaParser import stellaParser
from stella.stellaLexer import stellaLexer
from typecheker import Typecheker


def main(argv):
    if len(argv) > 1:
        input_stream = FileStream(argv[1])
    else:
        input_stream = StdinStream()

    lexer = stellaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = stellaParser(stream)
    program = parser.program()
    typechecker = Typecheker()
    
    # print(Trees.toStringTree(program, None, parser), end='\n\n')
    exit_code = typechecker.handle_program_context(program)
    print(f'exit code: {exit_code}')


if __name__ == '__main__':
    main(sys.argv)
