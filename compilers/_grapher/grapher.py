from _visitor.visitor import Visitor

from graphviz import Digraph, Source


class Grapher( Visitor ):

    def __init__( self, ast ):

        self.ast = ast                           
        self._count = 1                         
        self.dot = Digraph()
        self.dot.node_attr['shape'] = 'box'
        self.dot.node_attr['height'] = '0.1'
        self.dot.edge_attr['arrowsize'] = '0.5'


    # add_node and add_edge:
    
    def add_node( self, parent, node, name = None ):
        
        node._index = self._count
        self._count += 1
        caption = type( node ).__name__ # var

        if name is not None:                                      
            caption = '{} : {}'.format( caption, name )

        self.dot.node( 'node{}'.format( node._index ), caption )        

        if parent is not None:
            self.add_edge( parent, node )

  
    def add_edge( self, parent, node ):
        src, dest = parent._index, node._index
        self.dot.edge( 'node{}'.format( src ), 'node{}'.format( dest ) )


    # visit_* methods:

    def visit_Program( self, parent, node ):
        
        self.add_node( parent, node )
        
        for n in node.nodes:
            self.visit( node, n )

    def visit_Decl( self, parent, node ):
        
        self.add_node( parent, node )
        self.visit( node, node.type_ )
        self.visit( node, node.id_ )

    def visit_ArrayDecl( self, parent, node ):
       
        self.add_node( parent, node )        
        self.visit( node, node.type_ )      
        self.visit( node, node.id_ )
        
        if node.size is not None:
            self.visit( node, node.size )
        if node.elems is not None:
            self.visit( node, node.elems )

    def visit_ArrayElem( self, parent, node ):
        
        self.add_node( parent, node )
        self.visit( node, node.id_ )
        self.visit( node, node.index )

    def visit_Assign( self, parent, node ):
        
        self.add_node( parent, node )
        self.visit( node, node.id_ )
        self.visit( node, node.expr )

    def visit_If( self, parent, node ):
        
        self.add_node( parent, node )
        self.visit( node, node.cond )
        self.visit( node, node.true )
        
        if node.false is not None:
            self.visit( node, node.false )

    def visit_While( self, parent, node ):
        
        self.add_node( parent, node )
        self.visit( node, node.cond )
        self.visit( node, node.block )

    def visit_FuncImpl( self, parent, node ):
        
        self.add_node( parent, node )
        self.visit( node, node.type_ )
        self.visit( node, node.id_ )
        self.visit( node, node.params )
        self.visit( node, node.block )

    def visit_FuncCall( self, parent, node ):
        
        self.add_node( parent, node )
        self.visit( node, node.id_ )
        self.visit( node, node.args )

    def visit_Block( self, parent, node ):
        
        self.add_node( parent, node )
        
        for n in node.nodes:
            self.visit( node, n )

    def visit_Params( self, parent, node ):
        
        self.add_node( parent, node )
        
        for p in node.params:
            self.visit( node, p )

    def visit_Args( self, parent, node ):
        self.add_node( parent, node )
        for a in node.args:
            self.visit( node, a )

    def visit_Elems( self, parent, node ):
        
        self.add_node( parent, node )
        for e in node.elems:
            self.visit( node, e )

    def visit_Break( self, parent, node ):
        self.add_node( parent, node )

    def visit_Continue( self, parent, node ):
        self.add_node( parent, node )

    def visit_Type( self, parent, node ):
        name = node.value
        self.add_node( parent, node, name )

    def visit_Int( self, parent, node ):
        name = node.value
        self.add_node( parent, node, name )

    def visit_Char( self, parent, node ):
        name = node.value
        self.add_node( parent, node, name )

    def visit_String( self, parent, node ):
        name = node.value
        self.add_node( parent, node, name )

    def visit_Id( self, parent, node ):
        name = node.value
        self.add_node( parent, node, name )

    def visit_BinOp( self, parent, node ):
        name = node.symbol
        self.add_node( parent, node, name )
        self.visit( node, node.first )
        self.visit( node, node.second )

    def visit_UnOp( self, parent, node ):
        name = node.symbol
        self.add_node( parent, node, name )
        self.visit( node, node.first )

    def visit_Exit( self, parent, node ):
        self.add_node( parent, node )
        if node.expr is not None:
            self.visit( node, node.expr )
        
    def visit_FunctionImpl( self, parent, node ):
        self.add_node( parent, node )

        self.visit( node, node.id_ )
        self.visit( node, node.params )

        if ( node.block != None ):
            self.visit( node, node.block )
        
        if ( node.var_block != None ):
            self.visit( node, node.var_block )

        self.visit( node, node.return_type )

    def visit_ProcedureImpl( self, parent, node ):
        self.add_node( parent, node )

        self.visit( node, node.id_ )
        self.visit( node, node.params )
        
        if ( node.block != None ):
            self.visit( node, node.block )
        
        if ( node.var_block != None ):
            self.visit( node, node.var_block )

    def visit_Repeat( self, parent, node ):
        self.add_node( parent, node )

        self.visit( node, node.block )
        self.visit( node, node.cond )

    def visit_For( self, parent, node ):
        self.add_node( parent, node )

        self.visit( node, node.init )
        self.visit( node, node.cond )
        self.visit( node, node.block )

    def visit_DowntoFor( self, parent, node ):
        self.add_node( parent, node )

        self.visit( node, node.init )
        self.visit( node, node.cond )
        self.visit( node, node.block )

    def visit_BeginMain( self, parent, node ):
        self.add_node( parent, node )
        
        for n in node.blocks:
            self.visit( node, n )

    def visit_Var( self, parent, node ):
        self.add_node( parent, node )
        
        for n in node.variables:
            self.visit( node, n )

        for n in node.arrays:
            self.visit( node, n )

    def visit_PrintFormat( self, parent, node ):
        self.add_node( parent, node )
        self.visit( node, node.first )
        self.visit( node, node.second )

    def visit_TrueCond( self, parent, node ):
        self.add_node( parent, node )

    def visit_FalseCond( self, parent, node ):
        self.add_node( parent, node )
    

    def graph( self ):

        self.visit( None, self.ast )
        s = Source( self.dot.source, filename = 'graph', format = 'png' )             # Making .dot file.

        return s