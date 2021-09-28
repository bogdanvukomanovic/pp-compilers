from _visitor.visitor import Visitor
from _symbolizer.symbols import Symbols
from _parser import ast

import re

class Generator( Visitor ):

    def __init__( self, ast ):
         
        self.ast = ast      # Abstract Syntax Tree that Generator is visiting using Visitor pattern.
        self.py = ""        # String which is going to contain generated C code.                                TODO: change from .py to .c 
        self.level = 0      # Indentation level.


        # Support for generating Function calls such as printf(), scanf() etc.
        self.current_fc = ""
        self.fc_flag = 0
        self.fc = ""
        
        self.current_type = ""

        # Support for Symbolizer scope.
        self.current_scope = ""
        self.begin_main_scope = {}
        self.fun_proc_scope = {}               # { FUNCTION/PROCEDURE NAME : { ID : SYMBOLI } ... }


    # Helper method [0]
    def append_fc( self, text ):
        self.fc += str( text )

    # Helper method [1]
    def append( self, text ):
        self.py += str( text )

    # Helper method [2]
    def newline( self ):
        self.append( '\n\r' )     

    # Helper method [3]
    def indent( self ):
        for _ in range( self.level ):
            self.append( '\t' )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def visit_Program( self, parent, node ):
        
        self.append( '#include <stdio.h>' )
        self.newline()
        self.append( '#include <string.h>' )
        self.newline()

        for n in node.nodes:
            
            # Declarations from Var block should be in main().
            if type( n ) is ast.Var:
                continue
    
            self.visit( node, n )
            self.newline()
 
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def visit_BeginMain( self, parent, node ):

        self.current_scope = "BEGIN_MAIN"

        self.append( 'int main()' )
        self.newline()
        self.append( '{' )
        self.newline()
        
        self.level += 1

        # Declarations from Var block should be in main().
        for n in parent.nodes:
            if type( n ) is ast.Var:
                self.visit( node, n )

        for n in node.blocks:

            self.indent()
            self.visit( node, n )
            self.newline()

        self.append( '\treturn 0;' )
        self.newline()
        self.append( '}' )

        self.level -= 1


    def visit_Var( self, parent, node ):
        
        # Symboliser support:    
        if type( parent ) == ast.BeginMain:
            for s in node.symbols:
                self.begin_main_scope[ s.id_ ] = s.copy()

        variables = node.variables
        for v in variables:
            
            self.indent()
            self.visit( node, v )
            self.newline()

        arrays = node.arrays
        for a in arrays:
            self.indent()
            self.visit( node, a )
            self.newline()
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def visit_ProcedureImpl( self, parent, node ):
        
        procedure_name = node.id_.value
        
        self.current_scope = procedure_name

        self.append( 'void ' )
        self.append( procedure_name )
        self.append( '( ' )
        self.visit( node, node.params )
        self.append( ' )' )

        self.newline()
        self.append( '{' )
        self.newline()

        self.level += 1
        if node.var_block is not None:
            self.visit( node, node.var_block )
        self.level -= 1

        self.visit( node, node.block )
        
        self.append( '}' )


    def visit_FunctionImpl( self, parent, node ):
        
        function_name = node.id_.value

        self.current_scope = function_name

        self.visit( node, node.return_type )
        self.append( ' ' )
        self.append( function_name )
        self.append( '( ' )
        self.visit( node, node.params )
        self.append( ' )' )

        self.newline()
        self.append( '{' )
        self.newline()

        self.level += 1
        if node.var_block is not None:
            self.visit( node, node.var_block )
        self.level -= 1

        self.visit( node, node.block )
        
        self.append( '}' )


    def visit_Params( self, parent, node ):

        # Initialise new nested scope dictionary - add it this if to vistit_Var() too.
        if self.current_scope not in self.fun_proc_scope.keys():
            self.fun_proc_scope[ self.current_scope ] = {}

        for s in node.symbols:
            self.fun_proc_scope[ self.current_scope ][ s.id_ ] = s.copy()                   # Add it to appropriate scope.

        for i, p in enumerate( node.params ):
        
            if i > 0:
                self.append(', ')

            self.visit( p, p.type_ )
            self.append( ' ' )
            self.visit( p, p.id_ )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def visit_Decl( self, parent, node ):
        
        self.visit( node, node.type_ )

        self.append( ' ' )
        self.visit( node, node.id_ )

        if self.current_type == "string":
            self.append( '[100] = {0}' )
        
        self.append( ';' )
        

    def visit_Assign( self, parent, node ):
        
        self.visit( node, node.id_ )
        
        self.append( ' = ' )
        self.visit( node, node.expr )
        self.append( ';' )
        
        # TODO: This is temp fix... if we have "for arr[3] = 1 ..." this should not work...
        if type( parent ) in [ ast.For, ast.DowntoFor ]:
            return node.id_.value
    

    def visit_ArrayDecl( self, parent, node ):
        
        self.visit( node, node.type_ )
        self.append( ' ' )
        self.visit( node, node.id_ )

        self.append( '[' )
        self.visit( node, node.size )
        self.append( ']' )
        
        if node.elems is not None:
            self.append(' = ')
            self.append(' {0}; // TODO !')

        elif node.size is not None:
            self.append(' = ')
            self.append('{0};')

    
    def visit_ArrayElem( self, parent, node ):
        
        self.visit( node, node.id_ )
        self.append( '[ ' ) if self.fc_flag == 0 else self.append_fc( '[ ' )
        self.visit( node, node.index )
        self.append( ' - 1 ]' ) if self.fc_flag == 0 else self.append_fc( ' - 1 ]' )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def visit_Type( self, parent, node ):
        
        type_ = node.value

        if type_ == 'integer':
            self.current_type = "int"
            self.append( 'int' )
        if type_ == 'char':
            self.current_type = "char"
            self.append( 'char' )
        if type_ == 'real':
            self.current_type = "float"
            self.append( 'float' )
        if type_ == 'boolean':
            self.current_type = "boolean"
            self.append( 'int' )
        if type_ == 'string':
            self.current_type = "string"
            self.append( 'char' )


    def visit_Id( self, parent, node ):
           
        if self.fc_flag == 1:
            
            type_ = self.set_current_type( node )
        
            if self.current_fc == "scanf" and type_ == "string":
                self.fc = self.fc[:-1]
              
        self.append( node.value ) if self.fc_flag == 0 else self.append_fc( node.value )


    def visit_Int( self, parent, node ):
        self.append( node.value ) if self.fc_flag == 0 else self.append_fc( node.value )

    def visit_Char( self, parent, node ):
        
        if self.current_fc == "printf":
            self.current_type = "string"
            self.append( "'" + node.value + "'" ) if self.fc_flag == 0 else self.append_fc( '"' + node.value + '"' ) # Look down...
        
        else:
            self.append( ord( node.value ) ) if self.fc_flag == 0 else self.append_fc( ord( node.value ) )

    def visit_String( self, parent, node ):
        
        # TODO: if self.fc_flag != 0: ?
        if self.fc_flag == 1:
            self.current_type = "string"
            
        self.append( "'" + node.value + "'" ) if self.fc_flag == 0 else self.append_fc( '"' + node.value + '"' )    # This might backfire ( "'" vs '"' ).

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def visit_BinOp( self, parent, node ):
       
        self.visit( node, node.first )
        
        self.append( ' ' ) if self.fc_flag == 0 else self.append_fc( ' ' )

        symbol = node.symbol
        
        if symbol == 'and':     
            self.append( '&&' ) if self.fc_flag == 0 else self.append_fc( '&&' )
        elif symbol == 'or':
            self.append( '||' ) if self.fc_flag == 0 else self.append_fc( '||' ) 
        elif symbol == 'mod':
            self.append( '%' ) if self.fc_flag == 0 else self.append_fc( '%' )
        elif symbol == 'div':
            self.append( '/' ) if self.fc_flag == 0 else self.append_fc( '/' )
        elif symbol == '=':
            self.append( '==' ) if self.fc_flag == 0 else self.append_fc( '==' )
        elif symbol == '<>':
            self.append( '!=' ) if self.fc_flag == 0 else self.append_fc( '!=' )

        else:
            self.append( symbol ) if self.fc_flag == 0 else self.append_fc( symbol )

        self.append( ' ' ) if self.fc_flag == 0 else self.append_fc( ' ' )
        
        self.visit( node, node.second )


    def visit_UnOp( self, parent, node ):
        
        symbol = node.symbol
 
        if symbol == 'not':
            self.append( '!' ) if self.fc_flag == 0 else self.append_fc( '!' )
        else:
            self.append( symbol ) if self.fc_flag == 0 else self.append_fc( symbol )
        
        self.visit( node, node.first )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def visit_Block( self, parent, node ):
        
        self.level += 1
        
        for n in node.nodes:

            self.indent()
            self.visit( node, n )
            self.newline()

        self.level -= 1


    def visit_For( self, parent, node ):

        self.append( 'for ( ' )
        
        condition_id = self.visit( node, node.init ) # Assign mostly...
        self.append( ' ' )

        self.append( condition_id )
        self.append( ' <= ' )
        self.visit( node, node.cond )
        self.append( '; ' )

        self.append( condition_id )
        self.append( '++' )

        self.append( ' ) {' )

        self.newline()

        self.visit( node, node.block )
        
        self.indent()
        self.append( '}' )


    def visit_DowntoFor( self, parent, node ):

        self.append( 'for ( ' )
        
        condition_id = self.visit( node, node.init ) # Assign mostly...
        self.append( ' ' )

        self.append( condition_id )
        self.append( ' >= ' )
        self.visit( node, node.cond )
        self.append( '; ' )

        self.append( condition_id )
        self.append( '--' )

        self.append( ' ) {' )

        self.newline()

        self.visit( node, node.block )
        
        self.indent()
        self.append( '}' )


    def visit_Repeat( self, parent, node ):
        
        self.append( 'do {' )
        self.newline()

        self.visit( node, node.block )

        self.indent()
        self.append( '} while ( !' )
        self.visit( node, node.cond )
        self.append( ' );' )


    def visit_If( self, parent, node ):
    
        self.append( 'if ( ' )
        self.visit( node, node.cond )
        self.append( ' ) {' )

        self.newline()

        self.visit( node, node.true )
        
        if node.false is not None:
            self.indent()
            self.append('} else {')
            self.newline()
            self.visit( node, node.false )
            self.indent()
            self.append( '}' ) 

        else:
            self.indent()
            self.append( '}' )


    def visit_While( self, parent, node ):
        
        self.append( 'while ( ' )
        self.visit( node, node.cond )
        self.append( ' ) {' )

        self.newline()
        self.visit( node, node.block )

        self.indent()
        self.append( '}' )


    def visit_Continue( self, parent, node ):
        self.append( 'continue;' )
    
    def visit_Break( self, parent, node ):
        self.append( 'break;' )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def set_current_type( self, node ):

        id_ = node.value
        
        if self.current_scope == "BEGIN_MAIN":
            
            #print( self.begin_main_scope[id_] )

            symbol = self.begin_main_scope[ id_ ]
            type_ = symbol.type_

            self.current_type = type_
        
        else:
        
            symbol = self.fun_proc_scope[ self.current_scope ][ id_ ]
            type_ = symbol.type_

            self.current_type = type_

        return type_


    def printf_generator( self, node, args, new_line_flag ):
        
        self.append( 'printf( "' )
        self.fc_flag += 1
        
        for i in range( len( args ) ):
            
            if type( args[i] ) != ast.PrintFormat: 
                
                self.visit( node.args, args[i] )

                self.append_fc( ", " )
                
                if self.current_type == 'integer':
                    self.append( '%d' )
                if self.current_type == 'char':
                    self.append( '%c' )
                if self.current_type == 'real':
                    self.append( '%f' )
                if self.current_type == 'string':
                    self.append( '%s' )
                if self.current_type == 'boolean':
                    self.append( '%d' )
            else:
                
                self.fc_flag -= 1
                
                last_specifier = self.py[ -1 ]
                self.py = self.py[ : -1 ] 
                self.visit( node.args, args[i] )
                self.append( last_specifier )
                
                self.fc_flag += 1

        if len( args ) == 0:
            self.append( '"' ) if new_line_flag == 0 else self.append_fc( '\\n"' )
        else:
            self.append( '", ' ) if new_line_flag == 0 else self.append( '\\n", ' )            
            self.fc = self.fc[ : -2 ]

        self.append_fc( " );" )
        self.append( self.fc )    
                    
        self.fc_flag -= 1       # Turn the flag off.
        self.fc = ""            # We need to restart self.fc for next function call.


    def scanf_generator( self, node, args ):
        
        self.append( 'scanf( "' )    
            
        self.fc_flag += 1

        for i in range( len( args ) ):

            self.append_fc( "&" )

            self.visit( node.args, args[i] )

            self.append_fc( ", " )
            
            if self.current_type == 'integer':
                self.append( '%d' )
            if self.current_type == 'char':
                self.append( '%c' )
            if self.current_type == 'real':
                self.append( '%f' )
            if self.current_type == 'string':
                self.append( '%s' )
            if self.current_type == 'boolean':
                self.append( '%d' )
    
        if len( args ) == 0:
            self.append( '"' )
        else:
            self.append( '", ' )
            self.fc = self.fc[ : -2 ]
                    
        self.append_fc( " );" )
        self.append( self.fc )                   

        self.fc_flag -= 1       # Turn the flag off.
        self.fc = ""            # We need to restart self.fc for next function call.


    def visit_FuncCall( self, parent, node ):
        
        func = node.id_.value
        args = node.args.args

        if func == 'write':
            self.current_fc = "printf"
            self.printf_generator( node, args, 0 )
            self.current_fc = ""    
            
        elif func == 'writeln':
            self.current_fc = "printf"  
            self.printf_generator( node, args, 1 )  # TODO: Can pass node and extract args in function? No need for that...
            self.current_fc = ""
           
        elif func in [ 'readln', 'read' ]:
            self.current_fc = "scanf" 
            self.scanf_generator( node, args )
            self.current_fc = ""

        elif func == 'ord':
            
            self.fc_flag += 1

            self.append_fc( '(int)' )
            for i in range( len( args ) ):
                self.visit( node.args, args[i] )

            if self.fc_flag == 1:
                self.append( self.fc )
                self.fc = ""
            
            self.fc_flag -= 1
        
        elif func == 'chr':
            
            self.fc_flag += 1
            
            self.append_fc( '(char)' )
            for i in range( len( args ) ):
                self.visit( node.args, args[i] )

            if self.fc_flag == 1:
                self.append( self.fc )
                self.fc = ""
            
            self.fc_flag -= 1
        
        elif func == 'length':
            self.append( 'strlen( ' )
            for i in range( len( args ) ):
                self.visit( node.args, args[i] )
            self.append( ' )' )

        elif func == 'insert':

            self.visit( node.args, args[1] )

            self.append( '[ ' )
            self.visit( node.args, args[2] )
            self.append( ' - 1 ] = ' )

            self.visit( node.args, args[0] )

            self.append( ';' )

        elif func == 'inc':

            self.visit( node.args, args[0] )
            self.append( '++;' )
        
        elif func == 'dec':

            self.visit( node.args, args[0] )
            self.append( '--;' )

        else:

            self.current_scope = func
            
            self.append( func ) if self.fc_flag == 0 else self.append_fc( func )
            self.append( '( ' ) if self.fc_flag == 0 else self.append_fc( '( ' )


            for i in range( len( args ) ):
                self.visit( node.args, args[i] )
                self.append( ', ' ) if self.fc_flag == 0 else self.append_fc( ', ' )
            
        
            if self.fc_flag == 0: 
                self.py = self.py[ : -2 ]
            else: 
                self.fc = self.fc[ : -2 ]

            # Might fireback if function is called in recursively ( in function or procedure ).
            if type( parent ) == ast.BeginMain:
                self.append( ' );' ) if self.fc_flag == 0 else self.append_fc( ' );' )
            else:
                self.append( ' )' ) if self.fc_flag == 0 else self.append_fc( ' )' )

            self.current_scope = "BEGIN_MAIN"
               

    def visit_PrintFormat( self, parent, node ):
        
        self.append( '.' )
        self.visit( node, node.second )
        

    def visit_Exit( self, parent, node ):
        
        self.append( 'return' )
        
        if node.expr is not None:
            self.append( ' ' )
            self.visit( node, node.expr )
        
        self.append( ';' )


    def visit_TrueCond( self, parent, node ):
        self.append( '1' )

    def visit_FalseCond( self, parent, node ):
        self.append( '0' )
        
    

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def generate( self, path ):

        self.visit( None, self.ast )                            # Pozivamo visit za root AST-a, dalje ce se rekurzivno pozvati visit metode za svu decu root-a.
        
        self.py = re.sub( '\n\s*\n', '\n', self.py )            # Ako imamo nekoliko spojenih praznih linija (\n\s*\n), samo cemo da ih zamenimo sa jednom linijom (\n).
        
        with open( path, 'w' ) as source:                       # Otvaramo fajl 'path', pisemo u njega...
            source.write( self.py )
        
        return path                                             # ... vracamo tu putanju kako bismo mogli da pokrenemo taj fajl. 