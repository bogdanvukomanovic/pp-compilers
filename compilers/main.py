from _lexer.lexer import Lexer
from _parser.parser import Parser
from _grapher.grapher import Grapher
from _symbolizer.symbolizer import Symbolizer
from _generator.generator import Generator
from _runner.runner import Runner

import sys

def main( argv ):

    with open( argv[1] ) as file:
        
        text = file.read()

        lexer = Lexer( text )
        tokens = lexer.lex()

        parser = Parser( tokens )
        ast = parser.parse()
        
        grapher = Grapher( ast )
        source = grapher.graph()
        source.view()
         
        symbolizer = Symbolizer( ast )
        symbolizer.symbolize()
        
        generator = Generator( ast )
        generator.generate( argv[2] )

        runner = Runner( ast )
        runner.run()


# python main.py ./test_files/01.pas generated.txt
if __name__ == "__main__":
    main( sys.argv )