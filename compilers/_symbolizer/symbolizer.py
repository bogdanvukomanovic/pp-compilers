from _visitor.visitor import Visitor
from .symbols import Symbols


class Symbolizer( Visitor ):

    def __init__( self, ast ):
        self.ast = ast

    # Root of AST tree.
    def visit_Program( self, parent, node ):
        
        node.symbols = Symbols()            # This Symbol table is used to store reference to function/procedure calls.
        
        for n in node.nodes:
            self.visit( node, n )

    # Child of Var block.
    def visit_Decl( self, parent, node ):
        parent.symbols.put( node.id_.value, node.type_.value, id( parent ) )

    # Child of Var block.
    def visit_ArrayDecl( self, parent, node ):
        
        '''
        Take this array declaration for example:
        
            x : array[1..3] of integer = ( 14, 7, 21 );
        
        At the Runner ( Interpreter ) component we are going to need to store current value of x[0], x[1] and x[2].
        We can achieve this by giving every ArrayDecl node it's own Symbol table. In this way we achieve something like this:
         
            Symbol( 0, 'integer', x )   :   current_value
            Symbol( 1, 'integer', x )   :   current_value
            Symbol( 2, 'integer', x )   :   current_value
        
        Where 0, 1, 2 are indexes of array 'x'.
        '''

        node.symbols = Symbols()                                                                                                          
        parent.symbols.put( node.id_.value, node.type_.value, id( parent ) )    # We still add array to it's Var block Symbol table.


    def visit_ArrayElem( self, parent, node ):
        pass


    def visit_Assign( self, parent, node ):
        pass


    def visit_If( self, parent, node ):

        self.visit( node, node.true )

        if node.false is not None:
            self.visit( node, node.false )


    def visit_While( self, parent, node ):
        self.visit( node, node.block )

    
    def visit_FuncCall( self, parent, node ):
        pass


    def visit_Block( self, parent, node ):

        node.symbols = Symbols()            # TODO: Not sure if I need this...

        for n in node.nodes:
            self.visit( node, n )


    def visit_Params( self, parent, node ):

        '''
        We need separate Symbol table for function/procedure parameters.
        
        Let's say we have function:
        
        function foo( x : integer ) integer;
        var
            i, j : integer;
        begin
            println( x );
        end;

        When we call this function we do something like this foo( 5 ). We need separate Symbol table to check if function was called incorrectly:
            
            1) foo( 5, 3 );
            2) foo( 1.3 );
            3) foo( 1.3, 5 );
        
        If we combine parameters and local Identifiers we lose that reference. We are also going to add parameters to local Symbol table ( from corresponding Var block ) so
        we can access it's value when it's needed while interpreting ( look at println( x ) in function foo() ).
        '''

        node.symbols = Symbols()

        for p in node.params:
            self.visit( node, p )
            self.visit( parent.block, p )   # TODO: Do I need self.visit( parent.var_block, p ) ? 


    def visit_Args( self, parent, node ):
        pass

    def visit_Elems( self, parent, node ):
        pass

    def visit_Break( self, parent, node ):
        pass

    def visit_Continue( self, parent, node ):
        pass

    def visit_Return( self, parent, node ):
        pass

    def visit_Type( self, parent, node ):
        pass

    def visit_Int( self, parent, node ):
        pass

    def visit_Char( self, parent, node ):
        pass

    def visit_String( self, parent, node ):
        pass

    def visit_Id( self, parent, node ):
        pass

    def visit_BinOp( self, parent, node ):
        pass

    def visit_UnOp( self, parent, node ):
        pass

    def visit_Exit( self, parent, node ):
        pass
 
    def visit_FunctionImpl( self, parent, node ):
        
        parent.symbols.put( node.id_.value, node.return_type.value, id( parent ), node.block )  # Put the reference ( name in this case ) to the Function in Program Symbol table ( Global scope basically ).

        '''
        Function local variables are supported by the fact that every function/procedure has its own Var block, and that corresponding Var block has it's own Symbol table.
        Note that there are cases where functions/procedures does not have Var block.
        '''

        self.visit( node, node.block )      # TODO: Do I even visit block ?.
        self.visit( node, node.params )

        if node.var_block is not None:
            self.visit( node, node.var_block )  # Added this chek it out.
     
    def visit_ProcedureImpl( self, parent, node ):

        '''
        Same as visit_FunctionImpl().
        '''

        parent.symbols.put( node.id_.value, "TYPE_PROCEDURE", id( parent ), node.block )        # Put the reference ( name in this case ) to the Procedure in Program Symbol table ( Global scope basically ).

        self.visit( node, node.block )      # TODO: Do I even visit block ?.
        self.visit( node, node.params )

        if node.var_block is not None:
            self.visit( node, node.var_block )  # Added this chek it out.

    
    def visit_Repeat( self, parent, node ):
        pass

    def visit_For( self, parent, node ):
        self.visit( node, node.block )

    def visit_DowntoFor( self, parent, node ):
        self.visit( node, node.block )

    def visit_BeginMain( self, parent, node ):

        parent.symbols.put( "ID_BEGIN_MAIN", "TYPE_BEGIN_MAIN", id( parent ) )
        
        for n in node.blocks:
            self.visit( node, n )

    # Var block may belong to [1] main begin-end. or [2] function/procedure. If Var block of [1] is above function/procedure, Identifiers from that Var block are available in their scope.
    def visit_Var( self, parent, node ):
        
        node.symbols = Symbols()

        for n in node.variables:
            self.visit( node, n )       # Effectively goes to 'visit_Decl'.

        for n in node.arrays:
            self.visit( node, n )       # Effectively goes to 'visit_ArrayDecl'.

    def visit_PrintFormat( self, parent, node ):
        pass

    def visit_TrueCond( self, parent, node ):
        pass

    def visit_FalseCond( self, parent, node ):
        pass
    

    def symbolize( self ):
        self.visit( None, self.ast )