from enum import Enum, auto

class Class( Enum ):

    # Non-aligned movement:
    ASSIGN = auto()         # :=
    COLON = auto()          # :
    DOT = auto()            # .
    SEMICOLON = auto()      # ;
    COMMA = auto()          # ,
    
    BEGIN = auto()          # begin
    END = auto()            # end
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]

    # Data types:
    VAR = auto()
    TYPE = auto()           
    INTEGER = auto()
    REAL = auto()
    BOOLEAN = auto()
    CHAR = auto()
    STRING = auto()

    # Identifier:
    ID = auto()
    
    # Binary and unary arithmetic operators:
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    FWDSLASH = auto()       # /
    DIV = auto()            # div
    MOD = auto()            # mod

    # Binary and unary logic operators:
    NOT = auto()
    AND = auto()
    OR = auto()
    XOR = auto()

    # Relational operators:
    EQ = auto()             # =
    NEQ = auto()            # <>
    LT = auto()             # <   
    GT = auto()             # >
    LTE = auto()            # >=
    GTE = auto()            # <=

    # IF-ELSE statement
    IF = auto()             
    ELSE = auto()
    THEN = auto()

    # Statements ( REPEAT-UNTIL, WHILE-DO, FOR-DO ) with BREAK and CONTINUE:
    REPEAT = auto()
    UNTIL = auto()
    WHILE = auto()
    FOR = auto()
    DOWNTO = auto()
    TO = auto()
    DO = auto()

    BREAK = auto()
    CONTINUE = auto()

    # Array keywords:
    ARRAY = auto()
    OF = auto()
    
    # User defined functions and procedures ( FUNCTION, PROCEDURE, EXIT ):
    FUNCTION = auto()
    PROCEDURE = auto()
    EXIT = auto()

    # True and False:
    TRUE = auto()
    FALSE = auto()

    # End Of File:
    EOF = auto()


class Token:

    def __init__( self, class_, lexeme ):
        self.class_ = class_
        self.lexeme = lexeme

    def __str__( self ):
        return "<{} {}>".format( self.class_, self.lexeme )


class Lexer:

    def __init__( self, text ):
        
        self.text = text
        self.len = len( text )
        self.pos = -1


    def next_char( self ):
        
        self.pos += 1

        if self.pos >= self.len:
            return None

        return self.text[ self.pos ]
    

    def read_space( self ):
        
        while self.pos + 1 < self.len and self.text[ self.pos + 1 ].isspace():
           self.next_char()


    def read_int( self ):
        
        lexeme = self.text[ self.pos ]
        
        while self.pos + 1 < self.len and self.text[ self.pos + 1 ].isdigit():
            lexeme += self.next_char()

        return int( lexeme )


    def read_keyword( self ):
        
        lexeme = self.text[ self.pos ]

        while self.pos + 1 < self.len and ( self.text[ self.pos + 1 ].isalnum() or self.text[ self.pos + 1 ] == '_' ):
            lexeme += self.next_char()
        

        if lexeme == 'begin':
            return Token( Class.BEGIN, lexeme )
        elif lexeme == 'end':
            return Token( Class.END, lexeme )
        elif lexeme == 'var':
            return Token( Class.VAR, lexeme )
        
        elif lexeme == 'integer' or lexeme == 'real' or lexeme == 'boolean' or lexeme == 'char' or lexeme == 'string':
            return Token( Class.TYPE, lexeme )
        
        elif lexeme == 'array':
            return Token( Class.ARRAY, lexeme )
        elif lexeme == 'of':
            return Token( Class.OF, lexeme )
        
        elif lexeme == 'div':
            return Token( Class.DIV, lexeme )
        elif lexeme == 'mod':
            return Token( Class.MOD, lexeme )

        elif lexeme == 'not':
            return Token( Class.NOT, lexeme )
        elif lexeme == 'and':
            return Token( Class.AND, lexeme )
        elif lexeme == 'or':
            return Token( Class.OR, lexeme )
        elif lexeme == 'xor':
            return Token( Class.MOD, lexeme )

        elif lexeme == 'if':
            return Token( Class.IF, lexeme )
        elif lexeme == 'else':
            return Token( Class.ELSE, lexeme )
        elif lexeme == 'then':
            return Token( Class.THEN, lexeme )
        elif lexeme == 'repeat':
            return Token( Class.REPEAT, lexeme )
        elif lexeme == 'until':
            return Token( Class.UNTIL, lexeme )
        elif lexeme == 'while':
            return Token( Class.WHILE, lexeme )
        elif lexeme == 'for':
            return Token( Class.FOR, lexeme )
        elif lexeme == 'downto':
            return Token( Class.DOWNTO, lexeme )
        elif lexeme == 'to':
            return Token( Class.TO, lexeme )
        elif lexeme == 'do':
            return Token( Class.DO, lexeme )    
        elif lexeme == 'break':
            return Token( Class.BREAK, lexeme )
        elif lexeme == 'continue':
            return Token( Class.CONTINUE, lexeme )
        
        elif lexeme == 'function':
            return Token( Class.FUNCTION, lexeme )
        elif lexeme == 'procedure':
            return Token( Class.PROCEDURE, lexeme )
        elif lexeme == 'exit':
            return Token( Class.EXIT, lexeme )

        elif lexeme == 'true':
            return Token( Class.TRUE, lexeme )
        elif lexeme == 'false':
            return Token( Class.FALSE, lexeme )
        
        return Token( Class.ID, lexeme )


    def read_string( self ):
        lexeme = ''
        while self.pos + 1 < self.len and self.text[ self.pos + 1 ] != '\'':
            lexeme += self.next_char()
        self.pos += 1
        return lexeme
   

    def die( self, char ):
        raise SystemExit( "Unexpected character: {}".format( char ) )


    def next_token( self ):

        self.read_space() 
        
        curr = self.next_char()

        if curr is None:
            return Token( Class.EOF, curr )

        token = None
        
        if curr.isalpha():
            token = self.read_keyword()
        elif curr.isdigit():
            token = Token( Class.INTEGER, self.read_int() )
        elif curr == '\'':
            token = Token( Class.STRING, self.read_string() )

        elif curr == ':':
            curr = self.next_char()
            if curr == '=':
                token = Token( Class.ASSIGN, ':=' )
            else:
                token = Token( Class.COLON, ':' )
                self.pos -= 1

        elif curr == '.':
            token = Token( Class.DOT, curr )
        elif curr == ';':
            token = Token( Class.SEMICOLON, curr )
        elif curr == ',':
            token = Token( Class.COMMA, curr )

        elif curr == '(':
            token = Token( Class.LPAREN, curr )
        elif curr == ')':
            token = Token( Class.RPAREN, curr )
        elif curr == '[':
            token = Token( Class.LBRACKET, curr )
        elif curr == ']':
            token = Token( Class.RBRACKET, curr )

        elif curr == '+':
            token = Token( Class.PLUS, curr ) 
        elif curr == '-':
            token = Token( Class.MINUS, curr )
        elif curr == '*':
            token = Token( Class.STAR, curr )
        elif curr == '/':
            token = Token( Class.FWDSLASH, curr )
        
        elif curr == '=':
            token = Token( Class.EQ, curr )

        elif curr == '<':
            curr = self.next_char()
            if curr == '>':
                token = Token( Class.NEQ, '<>' )
            elif curr == '=':
                token = Token( Class.LTE, '<=' )
            else:
                token = Token( Class.LT, '<' )
                self.pos -= 1
        
        elif curr == '>':
            curr = self.next_char()
            if curr == '=':
                token = Token( Class.GTE, '>=' )
            else:
                token = Token( Class.GT, '>' )
                self.pos -= 1

        else:
            self.die( curr )


        return token


    def lex( self ):
        
        tokens = []
        
        while True:

            curr = self.next_token()
            tokens.append( curr )

            if curr.class_ == Class.EOF:
                break

        return tokens