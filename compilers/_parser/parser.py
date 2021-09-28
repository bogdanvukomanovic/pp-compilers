from . import ast
from _lexer.lexer import Class

from functools import wraps
import pickle

class Parser():

    def __init__( self, tokens ):
        self.tokens = tokens
        self.curr = tokens.pop(0)
        self.prev = None


    def eat( self, class_ ):
        if self.curr.class_ == class_:
            self.prev = self.curr
            self.curr = self.tokens.pop(0)
        else:
            self.die_type( class_.name, self.curr.class_.name )

    # Used for lookahead.
    def restorable( call ):
        
        @wraps( call )
        def wrapper( self, *args, **kwargs ):
        
            state = pickle.dumps( self.__dict__ )
            result = call( self, *args, **kwargs )
            self.__dict__ = pickle.loads( state )
        
            return result
        
        return wrapper


    @restorable
    def is_logic_assign( self ):
        
        try:
            self.expr()
            
            if self.curr.class_ == Class.EQ or self.curr.class_ == Class.NEQ or self.curr.class_ == Class.LT or self.curr.class_ == Class.LTE or self.curr.class_ == Class.GT or self.curr.class_ == Class.GTE:
                return True
        
        except:
            return False
            

    def program( self ):
        
        nodes = []

        while self.curr.class_ != Class.EOF:

            if self.curr.class_ == Class.VAR:
                nodes.append( self.var() )
            elif self.curr.class_ == Class.BEGIN:
                nodes.append( self.begin() )
            elif self.curr.class_ == Class.PROCEDURE:
                nodes.append( self.procedure() )
            elif self.curr.class_ == Class.FUNCTION:
                nodes.append( self.function() )
            else:
                print( "LEXER ERROR AT PROGRAM(): ", self.curr.lexeme )
                self.die_deriv( self.program.__name__ )

        return ast.Program( nodes )
    
    
	# Handles var block.
    def var( self ):
        
        self.eat( Class.VAR )
        
        variables = []
        arrays = []
        #identifiers = [] # Var block can have multiple rows, every row has it's own identifiers array.
        
        while self.curr.class_ != Class.BEGIN and self.curr.class_ != Class.EOF:

            identifiers = []  # Look up.

            # Left side of ':'
            while self.curr.class_ != Class.COLON:
              
                if len( identifiers ) > 0:
                    self.eat( Class.COMMA )
            
                identifiers.append( self.id_() )
        
            self.eat( Class.COLON )                                   # :
            
            # Right side of ':'
            if self.curr.class_ == Class.TYPE:
                
                type_ = self.type_()                
                
                # TODO: if self.curr.clas_ == Class.LBRACKET:       OR      if self.curr.lexeme == string ?
            
                for i in range( len( identifiers ) ):
                    variables.append( ast.Decl( type_, identifiers[i] ) )

                
            elif self.curr.class_ == Class.ARRAY:
                
                self.eat( Class.ARRAY )                     # ARRAY

                self.eat( Class.LBRACKET )                  # [ 
                ( first, second ) = self.arrsize_()
                size = ast.Int( abs( first - second ) + 1 )
                self.eat( Class.RBRACKET )                  # ]
                
                self.eat( Class.OF )                        # OF
                
                type_ = self.type_()    

                elems = None
                if self.curr.class_ == Class.EQ:
                    
                    self.eat( Class.EQ )
                    self.eat( Class.LPAREN )
                    elems = self.elems()
                    self.eat( Class.RPAREN )
                
                for i in range( len( identifiers ) ):
                    arrays.append( ast.ArrayDecl( type_, identifiers[i], size, elems ) )
                
            self.eat( Class.SEMICOLON )

        return ast.Var( variables, arrays )   


    # Hendluje begin blok koji je na globalnom scope-u -> main begin blok, odnosno blok koji se zavrsava sa 'end.'
    def begin( self ):

        self.eat( Class.BEGIN )
        
        begin_blocks = []

        while self.curr.class_ != Class.DOT:

            if self.curr.class_ == Class.IF:
                begin_blocks.append( self.if_() )
            
            elif self.curr.class_ == Class.FOR: 
                begin_blocks.append( self.for_() )

            elif self.curr.class_ == Class.WHILE:
                begin_blocks.append( self.while_() )

            elif self.curr.class_ == Class.REPEAT:
                begin_blocks.append( self.repeat_() )

            elif self.curr.class_ == Class.BREAK:
                begin_blocks.append( self.break_() )
            elif self.curr.class_ == Class.CONTINUE:
                begin_blocks.append( self.continue_() )
            elif self.curr.class_ == Class.EXIT:
                begin_blocks.append( self.exit_() )

            elif self.curr.class_ == Class.ID:
                begin_blocks.append( self.id_() )
                self.eat( Class.SEMICOLON )
            
            elif self.curr.class_ == Class.END:
                self.eat( Class.END )                       # end
            
            else:
                self.die_deriv( self.block.__name__ )
    
        self.eat( Class.DOT )                               # .
        
        return ast.BeginMain( begin_blocks )

    # Hendluje procedure blokove
    def procedure( self ):
        
        # procedure fun(a, b: integer);
        self.eat( Class.PROCEDURE )
        
        id_ = self.id_()
        self.eat( Class.LPAREN )
        params = self.params()
        self.eat( Class.RPAREN )
        self.eat( Class.SEMICOLON )

        block = None
        var_block = None
        
        if self.curr.class_ == Class.BEGIN:
            block = self.block()
        if self.curr.class_ == Class.VAR:
            var_block = self.var()
        if self.curr.class_ == Class.BEGIN:
            block = self.block()
        
        
        self.eat( Class.SEMICOLON )

        return ast.ProcedureImpl( id_, params, block, var_block )


    def function( self ):

        # function fun3(p, q, r: integer) : integer;
        self.eat( Class.FUNCTION )
        id_ = self.id_()
        self.eat( Class.LPAREN )                                      
        params = self.params()
        self.eat( Class.RPAREN )
        self.eat( Class.COLON )
        return_type = self.type_() 
        self.eat( Class.SEMICOLON )
        
        block = None
        var_block = None
        if self.curr.class_ == Class.BEGIN:
            block = self.block()
        if self.curr.class_ == Class.VAR:
            var_block = self.var()
        if self.curr.class_ == Class.BEGIN:
            block = self.block()

        self.eat( Class.SEMICOLON )

        return ast.FunctionImpl( id_, params, block, var_block, return_type )
        

    def block( self ):
        
        self.eat( Class.BEGIN )

        blocks = []

        while self.curr.class_ != Class.END:
            
            if self.curr.class_ == Class.IF:
                blocks.append( self.if_() )
            
            elif self.curr.class_ == Class.FOR: 
                blocks.append( self.for_() )

            elif self.curr.class_ == Class.WHILE:
                blocks.append( self.while_() )

            elif self.curr.class_ == Class.REPEAT:
                blocks.append( self.repeat_() )

            elif self.curr.class_ == Class.BREAK:
                blocks.append( self.break_() )
            elif self.curr.class_ == Class.CONTINUE:
                blocks.append( self.continue_() )
            elif self.curr.class_ == Class.EXIT:
                blocks.append( self.exit_() )
            

            elif self.curr.class_ == Class.ID:
                blocks.append( self.id_() )
                self.eat( Class.SEMICOLON )
            
            else:
                self.die_deriv( self.block.__name__ )

        self.eat( Class.END )
  
        return ast.Block( blocks )

    # ---------------------------------------------------------------------------------------------------------------------

    # Hendluje identifikatore unutar BeginMain i Block
    def id_( self ):

        if ( self.prev.class_ == Class.PROCEDURE or self.prev.class_ == Class.FUNCTION ):
            id_ = ast.Id( self.curr.lexeme )
            self.eat( Class.ID )
            return id_

        id_ = ast.Id( self.curr.lexeme )
        self.eat( Class.ID )

        # Poziv funkcije - '('
        if self.curr.class_ == Class.LPAREN and self.prev.class_ != Class.PROCEDURE and self.prev.class_ != Class.FUNCTION:    

            self.eat( Class.LPAREN )
                     
            args = self.args()
            self.eat( Class.RPAREN )
            
            return ast.FuncCall( id_, args )     

        # Pristup elementu niza - '['
        elif self.curr.class_ == Class.LBRACKET:
            
            self.eat( Class.LBRACKET )
            index = self.expr()
            self.eat( Class.RBRACKET )
            id_ = ast.ArrayElem( id_, index )
        
        # Dodela vrednosti - ':='
        if self.curr.class_ == Class.ASSIGN:

            self.eat( Class.ASSIGN )
            
            # I don't need this check, expr shold be equal to self.logic()...
            if self.is_logic_assign():
                expr = self.compare()
            else:
                expr = self.expr()

           
            return ast.Assign( id_, expr ) 

        else:
            return id_                       


    def arrsize_( self ):
        
        first = 0
        second = 0

        if self.curr.class_ == Class.INTEGER:
            
            first = self.curr.lexeme
            self.eat( Class.INTEGER )
            
            if self.curr.class_ == Class.DOT:
                self.eat( Class.DOT )
                self.eat( Class.DOT )
                second = self.curr.lexeme
                self.eat( Class.INTEGER )
        
        return ( first, second )


    # Konzumira i vraca Type objekat
    def type_( self ):

        type_ = ast.Type( self.curr.lexeme )
        self.eat( Class.TYPE )

        return type_

    # ----------------------------------------------------------------------------------------------------------------------------------
    
    def print_format( self ):
        
        self.eat( Class.COLON )
        first = ast.Int( self.curr.lexeme )
        self.eat( Class.INTEGER )

        self.eat( Class.COLON )
        second = ast.Int( self.curr.lexeme )
        self.eat( Class.INTEGER )

        # Should be changed, currently support only something like "X:0:2", should break if input is "X:0", "X:2" etc.
        return ast.PrintFormat( first, second )

    # Vraca argumente funkcije u obliku objekta Args()
    def args( self ):

        args = []
        # (a + b):0:2, ' ', (a - b):0:2, ' ', (a / b):0:2);
        while self.curr.class_ != Class.RPAREN:
            
            if len( args ) > 0:
                self.eat( Class.COMMA )

            args.append( self.expr() )

            if self.curr.class_ == Class.COLON:
                args.append( self.print_format() )

        return ast.Args( args )

    # Vraca parametre funkcije u obliku objekta Param()
    def params( self ):
        
        params = []
        #a, b: integer);
        identifiers = []
        identifiers.append( self.id_() )
        
        while self.curr.class_ != Class.COLON:
            
            if len( identifiers ) > 0:
                self.eat( Class.COMMA )
            
            identifiers.append( self.id_() )

        self.eat( Class.COLON )

        while self.curr.class_ != Class.RPAREN:

            type_ = self.type_()

            for i in range( len( identifiers ) ):
                params.append( ast.Decl( type_, identifiers[i] ) )

        return ast.Params( params )

    # Vraca elemente niza u obliku objekta Elems()
    def elems( self ):

        elems = []

        while self.curr.class_ != Class.RPAREN:
            if len( elems ) > 0:
                self.eat( Class.COMMA )
            elems.append( self.expr() )

        return ast.Elems( elems )
    
    # ----------------------------------------------------------------------------------------------------------------------------------
    
    def if_( self ):
        
        self.eat( Class.IF )
        cond = self.logic()        
        self.eat( Class.THEN )
        true = self.block()                    
        
        false = None
        if self.curr.class_ != Class.SEMICOLON:
            
            self.eat( Class.ELSE )           
            false = self.block()
            
        self.eat( Class.SEMICOLON )

        return ast.If( cond, true, false )


    def while_( self ):

        self.eat( Class.WHILE )
        cond = self.logic()
        self.eat( Class.DO )
        block = self.block()
        self.eat( Class.SEMICOLON )

        return ast.While( cond, block )


    def for_( self ):
        
        self.eat( Class.FOR )
        init = self.id_()
        
        for_type = None
        if self.curr.class_ == Class.TO:
            
            self.eat( Class.TO )
            for_type = 'TO'

        elif self.curr.class_ == Class.DOWNTO:
            
            self.eat( Class.DOWNTO )
            for_type = 'DOWNTO'

        cond = self.logic()
        self.eat( Class.DO )

        block = self.block()
        self.eat( Class.SEMICOLON )   # Eat SEMICOLON here because of the IF handling...
        
        if for_type == 'TO':
            return ast.For( init, cond, block )
        elif for_type == 'DOWNTO':
            return ast.DowntoFor( init, cond, block )

        
    def repeat_( self ):

        self.eat( Class.REPEAT )
        repeat_block = self.repeat_block()
        cond = self.logic()
        self.eat( Class.SEMICOLON )

        return ast.Repeat( repeat_block, cond )


    def repeat_block( self ):

        blocks = []

        while self.curr.class_ != Class.UNTIL:
            
            if self.curr.class_ == Class.IF:
                blocks.append( self.if_() )
            
            elif self.curr.class_ == Class.FOR: 
                blocks.append( self.for_() )

            elif self.curr.class_ == Class.WHILE:
                blocks.append( self.while_() )

            elif self.curr.class_ == Class.REPEAT:
                blocks.append( self.repeat_() )

            elif self.curr.class_ == Class.BREAK:
                blocks.append( self.break_() )
            elif self.curr.class_ == Class.CONTINUE:
                blocks.append( self.continue_() )
            elif self.curr.class_ == Class.EXIT:
                blocks.append( self.exit_() )
            
            elif self.curr.class_ == Class.ID:
                blocks.append( self.id_() )
                self.eat( Class.SEMICOLON )
            
            else:
                self.die_deriv( self.block.__name__ )

        self.eat( Class.UNTIL )
  
        return ast.Block( blocks )

 # -----------------------------------------------------------------------------------------------------------------------------------  

    def factor( self ):
        
        if self.curr.class_ == Class.INTEGER:
            value = ast.Int( self.curr.lexeme )
            self.eat( Class.INTEGER )
            return value

        elif self.curr.class_ == Class.CHAR:
            value = ast.Char( self.curr.lexeme )
            self.eat( Class.CHAR )
            return value

        elif self.curr.class_ == Class.STRING:
            
            # Move to Lexer... No need to do this check here.
            if len( self.curr.lexeme ) == 1: 
                value = ast.Char( self.curr.lexeme )
            else:
                value = ast.String( self.curr.lexeme )
            
            self.eat( Class.STRING )
            
            return value

        elif self.curr.class_ == Class.ID:
            return self.id_()

        elif self.curr.class_ in [ Class.MINUS, Class.NOT ]:
            op = self.curr
            self.eat( self.curr.class_ )
            first = None
            if self.curr.class_ == Class.LPAREN:
                self.eat( Class.LPAREN )
                first = self.logic()
                self.eat( Class.RPAREN )
            else:
                first = self.factor()
            return ast.UnOp( op.lexeme, first )

        elif self.curr.class_ == Class.LPAREN:
            self.eat( Class.LPAREN )
            first = self.logic()
            self.eat( Class.RPAREN )
            return first

        elif self.curr.class_ == Class.SEMICOLON:
            return None

        else:
            self.die_deriv( self.factor.__name__ )


    def term( self ):

        first = self.factor()

        while self.curr.class_ in [ Class.STAR, Class.FWDSLASH, Class.MOD, Class.DIV ]:

            if self.curr.class_ == Class.STAR:
                op = self.curr.lexeme
                self.eat( Class.STAR )
                second = self.factor()
                first = ast.BinOp( op, first, second )

            elif self.curr.class_ == Class.FWDSLASH:
                op = self.curr.lexeme
                self.eat( Class.FWDSLASH )
                second = self.factor()
                first = ast.BinOp( op, first, second )

            elif self.curr.class_ == Class.MOD:
                op = self.curr.lexeme
                self.eat( Class.MOD )
                second = self.factor()
                first = ast.BinOp( op, first, second )
            
            elif self.curr.class_ == Class.DIV:
                op = self.curr.lexeme
                self.eat( Class.DIV )
                second = self.factor()
                first = ast.BinOp( op, first, second )
        
        return first


    def expr( self ):
        
        # TODO: Check should this be at this level?
        if self.curr.class_ in [ Class.TRUE, Class.FALSE ]:

            if self.curr.class_ == Class.TRUE:
                self.eat( Class.TRUE )
                return ast.TrueCond()

            elif self.curr.class_ == Class.FALSE:
                self.eat( Class.FALSE )
                return ast.FalseCond()

        first = self.term()
        
        while self.curr.class_ in [ Class.PLUS, Class.MINUS ]:

            if self.curr.class_ == Class.PLUS:
                op = self.curr.lexeme
                self.eat( Class.PLUS )
                second = self.term()
                first = ast.BinOp( op, first, second )

            elif self.curr.class_ == Class.MINUS:
                op = self.curr.lexeme
                self.eat( Class.MINUS )
                second = self.term()
                first = ast.BinOp( op, first, second )
                
        return first
    

    def compare( self ):

        first = self.expr()
        
        if self.curr.class_ == Class.EQ:                # =

            op = self.curr.lexeme
            self.eat( Class.EQ )
            second = self.expr()

            return ast.BinOp( op, first, second )

        elif self.curr.class_ == Class.NEQ:             # <>

            op = self.curr.lexeme
            self.eat( Class.NEQ )
            second = self.expr()

            return ast.BinOp( op, first, second )

        elif self.curr.class_ == Class.LT:              # <
        
            op = self.curr.lexeme
            self.eat( Class.LT )
            second = self.expr()

            return ast.BinOp( op, first, second )

        elif self.curr.class_ == Class.GT:              # >

            op = self.curr.lexeme
            self.eat( Class.GT )
            second = self.expr()

            return ast.BinOp( op, first, second )

        elif self.curr.class_ == Class.LTE:             # <=

            op = self.curr.lexeme
            self.eat( Class.LTE )
            second = self.expr()

            return ast.BinOp( op, first, second )

        elif self.curr.class_ == Class.GTE:             # >=

            op = self.curr.lexeme
            self.eat( Class.GTE )
            second = self.expr()

            return ast.BinOp( op, first, second )
            
        else:
            return first


    def logic_term( self ):

        first = self.compare()
        
        while self.curr.class_ == Class.AND:
            op = self.curr.lexeme
            self.eat( Class.AND )
            second = self.compare()
            first = ast.BinOp( op, first, second )

        return first


    def logic( self ):
        
        first = self.logic_term()
        
        while self.curr.class_ == Class.OR:
            op = self.curr.lexeme
            self.eat( Class.OR )
            second = self.logic_term()
            first = ast.BinOp( op, first, second )
            
        return first
    
 # -----------------------------------------------------------------------------------------------------------------------------------
    
    def break_ ( self ):
        self.eat( Class.BREAK )
        self.eat( Class.SEMICOLON )
        return ast.Break()

    def continue_( self ):
        self.eat( Class.CONTINUE )
        self.eat( Class.SEMICOLON )
        return ast.Continue()
    
    def exit_( self ):

        self.eat( Class.EXIT )
        
        if self.curr.class_ == Class.SEMICOLON:
            self.eat( Class.SEMICOLON )
            return ast.Exit( None )
        
        else:

            self.eat( Class.LPAREN )
            logic = self.logic()
            self.eat( Class.RPAREN )
            self.eat( Class.SEMICOLON )

            return ast.Exit( logic )

 # -----------------------------------------------------------------------------------------------------------------------------------
        
    def parse( self ):
        return self.program()

    def die( self, text ):
        raise SystemExit( text )

    def die_deriv( self, fun ):
        print( "Derivation error lexeme: ", self.curr.lexeme )
        self.die( "Derivation error: {}".format( fun ) )

    def die_type( self, expected, found ):
        self.die( "Expected: {}, Found: {}".format( expected, found ) )