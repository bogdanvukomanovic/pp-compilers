from _visitor.visitor import Visitor
from _symbolizer.symbols import Symbol, Symbols
from _parser import ast

import sys


class Runner( Visitor ):
    
    def __init__( self, ast ):

        self.ast = ast

        # Support for variable scope.
        self.current_scope = "BEGIN_MAIN"   # Initial scope is BEGIN_MAIN.
        self.begin_main_scope = {}
        self.fun_proc_scope = {}
        
        self.function_procedure_map = {}
        
        self.break_ = None
        # self.continue_ = None
        self.return_ = False                


    # [1] Helper method.
    def put_symbol( self, symbol ):
        
        if self.current_scope == "BEGIN_MAIN":        
            self.begin_main_scope[ symbol.id_ ] = symbol.copy()
        else:
            self.fun_proc_scope[ self.current_scope ][ symbol.id_ ] = symbol.copy()

    # [2] Helper method.
    def get_symbol( self, id_ ):#node ):
        
        if self.current_scope == "BEGIN_MAIN":    
            symbol = self.begin_main_scope[ id_ ]
        else:
            symbol = self.fun_proc_scope[ self.current_scope ][ id_ ]
        
        return symbol


    def visit_Program( self, parent, node ):
        
        for symbol in node.symbols:
            self.function_procedure_map[ symbol.id_ ] = symbol.value

        for n in node.nodes:
            self.visit( node, n )

    
    def visit_Var( self, parent, node ):

        # Support for variable scope.         
        for symbol in node.symbols:
            self.put_symbol( symbol )

        for n in node.variables:
            self.visit( node, n )       # Effectively goes to 'visit_Decl'.

        for n in node.arrays:
            self.visit( node, n )       # Effectively goes to 'visit_ArrayDecl'.


    def visit_BeginMain( self, parent, node ):
        
        self.current_scope == "BEGIN_MAIN"

        for block in node.blocks:
            self.visit( node, block )


    def visit_Decl( self, parent, node ):
        pass
    

    def set_symbol_type( self, string_input, symbol ):

        #if string_input.isdigit():
        if string_input.lstrip("-").isdigit():
            symbol.value = int( string_input )
        elif string_input.replace( '.', '', 1 ).isdigit() and string_input.count( '.' ) < 2:
            symbol.value = float( string_input )
        else:
            symbol.value = string_input


    def visit_FuncCall( self, parent, node ):
        
        func = node.id_.value
        args = node.args.args
        
        if func == 'readln':
            inputs = input().split()
                
            for i, arg in enumerate( args ):
                    
                symbol = self.get_symbol( arg.value )
                self.set_symbol_type( inputs[i], symbol )

        elif func == 'read':
            
            inputs = ""
            while True:
        
                c = sys.stdin.read( 1 )         # Reads one byte at a time, similar to getchar().
                if c == '\n' or c == ' ':
                    break
                else:
                    inputs += c
                
            
            if isinstance( args[0], ast.ArrayElem ):
                
                symbol = self.get_symbol( args[0].id_.value )

                index = self.get_symbol( args[0].index.value ).value

                symbol.elems[ index - 1 ] = int( inputs )

            else:
                symbol = self.get_symbol( args[0].value )
                self.set_symbol_type( inputs, symbol )
            #else:
            #    id_ = arg.value
            #    symbol_ = node.symbols.get( id_ )
           
            # symbol_.value = input_
        

            
        elif func in [ "write", "writeln" ]:
            
            to_print = []

            for arg in args:
                
                if type( arg ) is not ast.PrintFormat:     
                    
                    value_ = self.visit( node, arg )
                    if isinstance( value_, Symbol ):  
                        value_ = value_.value
                    to_print.append( value_ )
                
                else:
                    format_element = to_print.pop()
                    to_print.append( "%.2f" % round( format_element, arg.second.value ) )

            if func == "write":
                print( *to_print, sep = '', end = '' )      # WRITE
            else:
                print( *to_print, sep = '', end = '\n' )    # WRITELN.


        elif func == 'chr':

            chr_ = self.visit( node, args[0] )
            if isinstance( chr_, Symbol ):
                chr_ = chr_.value

            chr_ = chr( chr_ )
                    
            return chr_

        elif func == 'ord':
              
            ord_ = self.visit( node, args[0] )
            if isinstance( ord_, Symbol ):
                ord_ = ord_.value

            ord_ = ord( ord_ )
                        
            return ord_


        elif func == 'length':
            pass
        
        elif func == 'insert':
            pass
        
        elif func == 'inc':
            pass
        
        elif func == 'dec':
            pass


        else:
            
            self.current_scope = func

            execution_block = self.function_procedure_map[ func ]
            number_of_params = self.get_number_of_params( func )
            
            if number_of_params > len( args ):
                return
            
            self.set_local_variables( func, node, args, number_of_params )
            value = self.visit( node, execution_block )
            
            self.current_scope = "BEGIN_MAIN"
            
            self.return_ = False # TODO: Do I need this ?
            
            return value

            
    def get_number_of_params( self, name ):
        
        scope = self.fun_proc_scope[ name ]
        return scope[ "PARAM_COUNT" ]


    def set_local_variables( self, name, node, args, number_of_params ):

        scope = self.fun_proc_scope[ name ]
        
        values = []
        for arg in args:
            
            self.current_scope = "BEGIN_MAIN"
            
            v = self.visit( node, arg )
            if isinstance( v, Symbol ):
                v = v.value
            
            self.current_scope = name

            values.append( v )
                    
        for i, ( k, v ) in enumerate( scope.items() ):
            
            if i < number_of_params:
                scope[k].value = values[i]

            elif i > number_of_params:
                scope[k].value = None

    
    def visit_UnOp( self, paren, node ):
        
        first = self.visit( node, node.first )        
        
        if isinstance( first, Symbol ):
            first = first.value
        
        if node.symbol == '-':
            return -first
        
        elif node.symbol == 'not': 
            bool_first = first != 0 
            return not bool_first
        
        else:
            return None


    def visit_BinOp( self, parent, node ):
        
        # Get value of first operand.
        first = self.visit( node, node.first )
        if isinstance( first, Symbol ):
            first = first.value
        
        # Get value of second operand.
        second = self.visit( node, node.second )
        if isinstance( second, Symbol ):
            second = second.value
        

        if node.symbol == '+':
            return first + second
        elif node.symbol == '-':
            return first - second
        elif node.symbol == '*':
            return first * second
        elif node.symbol == '/':
            return first / second
        elif node.symbol == 'div':
            return first // second 
        elif node.symbol == 'mod':
            return first % second
        elif node.symbol == '=':
            return first == second
        elif node.symbol == '<':
            return first < second
        elif node.symbol == '>':
            return first > second
        elif node.symbol == '<=':
            return first <= second
        elif node.symbol == '>=':
            return first >= second
        elif node.symbol == 'and':
            return first and second
        
        else:
            return None

    
    def visit_PrintFormat( self, parent, node ):
        pass
    
    def visit_Char( self, parent, node ):
        return node.value

    def visit_String( self, parent, node ):
        return node.value

    def visit_Int( self, parent, node ):
        return node.value 
    
    def visit_Id( self, parent, node ):
        return self.get_symbol( node.value )
    

    def visit_ProcedureImpl( self, parent, node ):
        
        procedure_name = node.id_.value
        self.current_scope = procedure_name

        self.visit( node, node.params )
        if node.var_block is not None:
            self.visit( node, node.var_block )

        self.current_scope = "BEGIN_MAIN"

    
    def visit_FunctionImpl( self, parent, node ):
        
        function_name = node.id_.value
        self.current_scope = function_name
        
        self.visit( node, node.params )
        if node.var_block is not None:
            self.visit( node, node.var_block )

        self.current_scope = "BEGIN_MAIN"


    def visit_Params( self, parent, node ):
        
        # Initialise new nested scope dictionary - add it this if to vistit_Var() too.
        if self.current_scope not in self.fun_proc_scope.keys():
            self.fun_proc_scope[ self.current_scope ] = {}
        
        for s in node.symbols:
            self.fun_proc_scope[ self.current_scope ][ s.id_ ] = s.copy()                   # Add it to appropriate scope.
        
        self.fun_proc_scope[ self.current_scope ][ "PARAM_COUNT" ] = len( node.symbols )


    def visit_Assign( self, parent, node ):
        
        id_ = self.visit( node, node.id_ )
        value = self.visit( node, node.expr )

        if isinstance( value, Symbol ):   # CASE:   x := y
            value = value.value
        
        # ArrayElem has no attribute 'value'.
        if isinstance( node.id_, ast.ArrayElem ):
            
            symbol = self.get_symbol( node.id_.id_.value )
            index = self.get_symbol( node.id_.index.value )
            symbol.elems[ index.value - 1 ] = value  # symbol.value = value
        
        else:

            symbol = self.get_symbol( node.id_.value )
            symbol.value = value

        return symbol


    def visit_Block( self, parent, node ):
        
        result = None
        ignore = False

        for n in node.nodes:
            
            if self.break_:
                break
        
            if self.return_:
                break
            
            if isinstance( n, ast.Break ):
                self.break_ = True
                break
            
            elif isinstance( n, ast.Continue ):
                break

            elif isinstance( n, ast.Exit ):
                
                if n.expr is not None:
                    result = self.visit( n, n.expr )
                
                self.return_ = True 
                break

            else: 
                result = self.visit( node, n )
        
        return result

    
    def visit_If( self, parent, node ):
        
        result = None

        cond = self.visit( node, node.cond )
        
        if isinstance( cond, Symbol ):
            cond = cond.value

        if cond:
            result = self.visit( node, node.true )
               
        else:
            if node.false is not None:
                result = self.visit( node, node.false )

        return result 
            

    def visit_DowntoFor( self, parent, node ):
        
        start_value_symbol = self.visit( node, node.init )
        cond = self.visit( node, node.cond )
        
        if start_value_symbol.value < cond:
            return

        while start_value_symbol.value >= cond:

            self.visit( node, node.block )
            start_value_symbol.value -= 1

    
    def visit_Repeat( self, parent, node ):
        
        self.visit( node, node.block )
        
        cond = self.visit( node, node.cond )
        
        while cond is not True:
            
            cond = self.visit( node, node.cond )
            self.visit( node, node.block )
            
            if self.break_ == True:
                break
        

    def visit_FalseCond( self, parent, node ):
        return False
    

    def visit_TrueCond( self, parent, node ):
        return True


    def visit_For( self, parent, node ):
        
        start_value_symbol = self.visit( node, node.init )
        cond = self.visit( node, node.cond )

        if isinstance( cond, Symbol ):
            cond = cond.value 

        if start_value_symbol.value > cond:
            return

        while start_value_symbol.value <= cond:
    
            self.visit( node, node.block )
            start_value_symbol.value += 1


    def visit_ArrayDecl( self, parent, node ):
    
        id_ = self.get_symbol( node.id_.value )
        id_.symbols = node.symbols 
        size, elems = node.size, node.elems
        
        array_elems_initialised = []
        if elems is not None:
            self.visit(node, elems)
        
        elif size is not None:
            for i in range( size.value ):
                array_elems_initialised.append( None )

        id_.elems = array_elems_initialised
        

    def visit_ArrayElem( self, parent, node ):
        
        index = self.visit( node, node.index )
        if isinstance( index, Symbol ):
            index = index.value
        
        return self.get_symbol( node.id_.value ).elems[ index - 1 ]


    def run( self ):
        self.visit( None, self.ast )      