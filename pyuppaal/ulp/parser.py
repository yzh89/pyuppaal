""" 
    Copyright (C) 2009
    Andreas Engelbredt Dalsgaard <andreas.dalsgaard@gmail.com>
    Martin Toft <mt@martintoft.dk>
    Mads Chr. Olesen <mchro@cs.aau.dk>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. """

from collections import OrderedDict

from lexer import *
import expressionParser
from node import Node

def get_class_name_from_complex_identifier(n):
    """Follow the children of a complex identifier node, i.e.
    "a.b.c.d" to just return "d"
    """
    #parse out the actual class name
    classnamenode = n
    while len(classnamenode.children) == 1 and \
            classnamenode.children[0].type == 'Identifier':
        classnamenode = classnamenode.children[0]
    ident = classnamenode.leaf
    return ident

def get_full_name_from_complex_identifier(n):
    """Follow the children of a complex identifier node, i.e.
    "a.b.c.d" to return the full name "a.b.c.d"
    """
    names = [n.leaf]
    cur = n
    while len(cur.children) == 1 and \
            cur.children[0].type == 'Identifier':
        cur = cur.children[0]
        names.append(cur.leaf)
    return names

class Parser:

    currentToken = None
    lexer = None
    expressionParser = None
    
    def __init__(self, data, lexer, typedefDict=None):
        self.lexer = lexer
        self.lexer.input(data+'\n')
        self.currentToken = self.lexer.token()

        self.typedefDict = typedefDict or {}
        self.externList = []
        self.identifierTypeDict = {}

        children = []        
        if self.currentToken != None:
            children = self.parseStatements()
        self.AST = Node('RootNode', children)
  
    def parseStatements(self):
        statements = []

        while 1:
            if self.currentToken:
                if self.currentToken.type in ('VOID'): #Function
                    type = self.parseFuncType()
                    identifier = self.parseIdentifier()
                    statements.append(self.parseFunction(type, identifier))
                elif self.currentToken.type in ('CONST', 'CLOCK', 'CHANNEL', 'URGENT', 'BROADCAST'): #Declaration
                    if self.currentToken.type == 'CONST':
                        self.accept('CONST')
                        type = self.parseStdType(True)
                    else:
                        type = self.parseDeclType()
                    identifier = self.parseIdentifierComplex()
                    statements.append(self.parseDeclaration(type, identifier, isglobal=True))
                elif self.currentToken.type in ('INT', 'BOOL', 'IDENTIFIER'): #Function or declaration           
                    type = self.parseStdType(False)
                    identifier = self.parseIdentifierComplex()
                    
                    if self.currentToken.type == 'LPAREN':  #TODO check that it is not a complex identifier
                        statements.append(self.parseFunction(type, identifier))
                    else:
                        statements.append(self.parseDeclaration(type, identifier)) 
                elif self.currentToken.type == 'STRUCT':
                    structDecl = self.parseStruct()
                    structIden = self.parseIdentifier()
                    self.accept('SEMI')
                    statements.append(Node('Struct', structDecl, structIden))
                elif self.currentToken.type == 'TYPEDEF':
                    statements.append(self.parseTypedef())
                elif self.currentToken.type == 'EXTERN':
                    statements.append(self.parseExtern())
                else:
                    break 
            else:
                break

        if self.currentToken != None:
            self.error('at token "%s" on line %d: Did not expect any token, but found token of type %s' % (self.currentToken.value, self.currentToken.lineno, self.currentToken.type))

        return statements

    def parseStruct(self):
        structDecl = []
        self.accept('STRUCT')
        self.accept('LCURLYPAREN')
        while self.currentToken.type in ('INT', 'BOOL', 'IDENTIFIER'): 
            type = self.parseDeclType()
            identifier = self.parseIdentifierComplex()
            structDecl.append(self.parseDeclaration(type, identifier))

        self.accept('RCURLYPAREN')
        return structDecl

    def parseDeclaration(self, type, identifier, isglobal=False):
        varList = []
        
        #TODO scalars
        #TODO typedef
        varList.append(identifier)
        while self.currentToken.type in ('COMMA', 'EQUALS', 'ASSIGN'):
            if self.currentToken.type == 'COMMA':
                self.accept('COMMA')
                identifier = self.parseIdentifierComplex()
                varList.append(identifier)
            elif self.currentToken.type in ['EQUALS', 'ASSIGN']:
                a = self.parseAssignment(identifier, shorthand=False)
                identifier.children.append(a)
            else:
                self.error('Did not expect token type' + self.currentToken.type)
                return
    
        if self.currentToken.type == 'SEMI':           
            self.accept('SEMI')

        for var in varList:
            self.identifierTypeDict[var.leaf] = type

        return Node('VarDecl', varList, type)

    def parseTypedef(self):
        self.accept('TYPEDEF')
        if self.currentToken.type == 'STRUCT':
            structDecl = self.parseStruct()
            if self.currentToken.type == 'IDENTIFIER':
                typeName = self.currentToken.value
                self.accept('IDENTIFIER')
            else:
                typeName = 'ErrorName'
                self.error('Expected identifier')
            n = Node('NodeTypedef', structDecl, typeName)
            self.typedefDict[typeName] = n
            self.accept('SEMI')
            return n
        else:
            type = self.parseStdType(False)
            if self.currentToken.type == 'IDENTIFIER':
                typeName = self.currentToken.value
                self.accept('IDENTIFIER')
            elif self.currentToken.type == 'CLOCK':
                #allow redefining clock
                typeName = self.currentToken.value
                self.accept('CLOCK')
            else:
                typeName = 'ErrorName'
                self.error('Expected identifier')
            n = Node('NodeTypedef', [type], typeName)
            self.typedefDict[typeName] = n
            self.accept('SEMI')
            return n

    def parseExtern(self):
        self.accept('EXTERN')
        #has the form "extern somelib.somelib.ClassName"
        identnode = self.parseIdentifierComplex()
        n = Node('NodeExtern', [], identnode)

        #parse out the actual class name
        classnamenode = identnode
        while len(classnamenode.children) == 1 and \
                classnamenode.children[0].type == 'Identifier':
            classnamenode = classnamenode.children[0]
        ident = classnamenode.leaf

        #do we have constructor parameters?
        if self.currentToken.type == 'EQUALS':
            self.accept('EQUALS')
            constructor_call_expr = self.parseExpression()
            assert len(constructor_call_expr.children) == 1
            assert constructor_call_expr.children[0].type == 'FunctionCall'
            constructor_call = constructor_call_expr.children[0]
            n.children = [constructor_call]

        self.typedefDict[ident] = n
        self.externList += [ident]

        self.accept('SEMI')
        return n

    def parseIndex(self):
        self.accept('LBRACKET')
        if self.currentToken.type == 'RBRACKET':
            self.error('invalid expression')
            e = None
        else:
            e = self.parseExpression()
        self.accept('RBRACKET')
        return Node('Index', [], e)

    def parseFunction(self, type, identifier):
        children = []
        self.accept('LPAREN')
        parameters = self.parseParameters()
        self.accept('RPAREN')
        self.accept('LCURLYPAREN')
        children.extend(self.parseBodyStatements())
        self.accept('RCURLYPAREN')

        return Node('Function', children, (type, identifier, parameters))
    
    def parseParameters(self):
        parameters = []
        while self.currentToken.type in ('INT', 'BOOL', 'CONST', 'IDENTIFIER'):
            isConst = False
            if self.currentToken.type == 'CONST':
                self.accept('CONST')
                isConst = True
            type = self.parseStdType(isConst) 
            identifier = self.parseIdentifierComplex()
            parameters.append( Node('Parameter', [], (type, identifier)) )
            if self.currentToken.type == 'COMMA':
                self.accept('COMMA')

        return parameters
   
    def parseBodyStatements(self, single = False):
        statements = []
        while self.currentToken.type not in ('RCURLYPAREN', 'ELSE'):
            identifier = None

            if self.currentToken.type in ('INT', 'BOOL', 'CONST'):
                if self.currentToken.type == 'CONST':
                    type = self.parseStdType(True)
                else:
                    type = self.parseStdType(False)
                identifier = self.parseIdentifierComplex()
                statements.append(self.parseDeclaration(type, identifier))
            elif self.currentToken.type == 'FOR':
                statements.append(self.parseForLoop())
            elif self.currentToken.type == 'WHILE':
                statements.append(self.parseWhileLoop())
            elif self.currentToken.type == 'DO':
                statements.append(self.parseDoWhileLoop())
            elif self.currentToken.type in ('IDENTIFIER', 'PLUSPLUS', 'MINUSMINUS'):
                if self.isType(self.currentToken.value):
                    utype = self.parseTypedefType(self.currentToken.value)
                    identifier = self.parseIdentifierComplex()
                    statements.append(self.parseDeclaration(utype, identifier))
                else:
                    if self.currentToken.type == 'IDENTIFIER':
                        identifier = self.parseIdentifierComplex()

                    if self.currentToken.type == 'LPAREN':
                        statements.append(self.parseFunctionCall(identifier))
                    else:
                        statements.append(self.parseAssignment(identifier))
                    self.accept('SEMI')
            elif self.currentToken.type == 'IF':
                statements.append(self.parseIf())
            elif self.currentToken.type == 'RETURN':
                self.accept('RETURN')
                expression = self.parseExpression()
                n = Node('Return', [], expression)
                statements.append(n)
                self.accept('SEMI')
            else:
                self.error('parseBodyStatement unknown token: %s' % self.currentToken.type)
                break

            if single:
                break

        return statements 

    def parseVariableList(self):
        children = []
        while self.currentToken.type == 'COMMA':
            self.accept('COMMA')
            children.append(self.parseIdentifier())
         
        return children

    def parseExpression(self):
        exprParser = expressionParser.ExpressionParser(self.lexer, self)
        return Node('Expression', children=[exprParser.parse()])
       
    def parseNumber(self):
        n = Node('Number', [], self.currentToken.value)
        self.accept('NUMBER')
        return n

    def parseAssignment(self, identifier, shorthand = True):
        if self.currentToken.type in ['EQUALS', 'ASSIGN']:
            self.accept(self.currentToken.type)
            n = self.parseExpression()
            return Node('Assignment', [n], identifier) 
        elif self.currentToken.type in ['ANDEQUAL', 'TIMESEQUAL', 'DIVEQUAL', \
                        'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL', 'LSHIFTEQUAL', \
                        'RSHIFTEQUAL', 'ANDEQUAL', 'OREQUAL', 'XOREQUAL']:
            return self.transformXEqual(identifier)

        elif shorthand:  #add -- support
            if self.currentToken.type == 'PLUSPLUS':
                self.accept('PLUSPLUS')
                if identifier == None:
                    identifier = self.parseIdentifierComplex()
                    ppnode = Node('PlusPlusPre', [identifier])
                else:
                    ppnode = Node('PlusPlusPost', [identifier])         
                return Node('Assignment', children=[Node('Expression', children=[ppnode])])
            elif self.currentToken.type == 'MINUSMINUS':
                self.accept('MINUSMINUS')
                if identifier == None:
                    identifier = self.parseIdentifierComplex()
                    mmnode = Node('MinusMinusPre', [identifier])
                else:
                    mmnode = Node('MinusMinusPost', [identifier])
                return Node('Assignment', children=[Node('Expression', children=[mmnode])])
        self.error('at assignment parsing, at token "%s" on line %d: Did not expect token type: "%s"' % (self.currentToken.value, self.currentToken.lineno, self.currentToken.type))

    def parseBooleanExpression(self):
        exprParser = expressionParser.ExpressionParser(self.lexer, self)
        return Node('BooleanExpression', children=[exprParser.parse()])

    def parseForLoop(self):
        leaf = []
        self.accept('FOR')
        self.accept('LPAREN')
        leaf.append(self.parseAssignment(self.parseIdentifierComplex()))
        self.accept('SEMI')
        leaf.append(self.parseBooleanExpression())
        self.accept('SEMI')
        leaf.append(self.parseAssignment(self.parseIdentifierComplex()))
        self.accept('RPAREN')
        self.accept('LCURLYPAREN')
        children = self.parseBodyStatements()
        self.accept('RCURLYPAREN')

        return Node('ForLoop', children, leaf)
           
    def parseWhileLoop(self):
        leaf = []
        self.accept('WHILE')
        self.accept('LPAREN')
        leaf.append(self.parseBooleanExpression())
        self.accept('RPAREN')
        self.accept('LCURLYPAREN')
        children = self.parseBodyStatements()
        self.accept('RCURLYPAREN')

        return Node('WhileLoop', children, leaf)

    def parseDoWhileLoop(self):
        leaf = []
        self.accept('DO')
        self.accept('LCURLYPAREN')
        children = self.parseBodyStatements()
        self.accept('RCURLYPAREN')
        self.accept('WHILE')
        self.accept('LPAREN')
        leaf.append(self.parseBooleanExpression())
        self.accept('RPAREN')
        self.accept('SEMI')

        return Node('DoWhileLoop', children, leaf)

    def parseIf(self):
        leaf = []
        children = []
        self.accept('IF')
        self.accept('LPAREN')
        leaf.append(self.parseBooleanExpression())
        self.accept('RPAREN')
        if self.currentToken.type == 'LCURLYPAREN':
            self.accept('LCURLYPAREN')
            children.append(Node('IfBodyStatements', self.parseBodyStatements(), leaf))
            self.accept('RCURLYPAREN')
        else:
            children.append(Node('IfBodyStatements', self.parseBodyStatements(single=True), leaf))

        elseCase = False
        while self.currentToken.type == 'ELSE' and elseCase == False:
            self.accept('ELSE')
            if self.currentToken.type == 'IF':
                self.accept('IF')
                leaf = []
                self.accept('LPAREN')
                leaf.append(self.parseBooleanExpression())
                self.accept('RPAREN')

                if self.currentToken.type == 'LCURLYPAREN':
                    self.accept('LCURLYPAREN')
                    children.append(Node('ElseIfBodyStatements', self.parseBodyStatements(), leaf))
                    self.accept('RCURLYPAREN')
                else:
                    children.append(Node('ElseIfBodyStatements', self.parseBodyStatements(single=True), leaf))                
            else:
                elseCase = True
                if self.currentToken.type == 'LCURLYPAREN':
                    self.accept('LCURLYPAREN')
                    children.append(Node('ElseBodyStatements', self.parseBodyStatements(), None))
                    self.accept('RCURLYPAREN')
                else:
                    children.append(Node('ElseBodyStatements', self.parseBodyStatements(single=True), None))

        return Node('If', children)

    def parseIdentifier(self):
        n = Node('Identifier', [], self.currentToken.value)
        self.accept('IDENTIFIER')
        return n

    def parseIdentifierComplex(self):
        n = self.parseIdentifier()
        p = n

        while self.currentToken.type == 'DOT':	#TODO should be possible to intermix DOT's and BRACKET's
            self.accept('DOT')
            element = self.parseIdentifier()
            p.children = [element]
            p = element
        
        p.children = p.children or []
        while self.currentToken.type == 'LBRACKET':
            index = self.parseIndex()
            p.children += [index]
            
        
        return n
   
    ### 
    ### FIXME: Notice similar functionalty exist in expressionParser, 
    ### however not posible to reuse as identifier must be parsed first
    ### should probably be refactored.
    ###
    def parseFunctionCall(self, identifier): 
        self.accept('LPAREN')
        parameters = []
        
        while self.currentToken.type != 'RPAREN':
            expr = self.parseExpression()
            if self.currentToken.type == 'COMMA':
                self.accept('COMMA')
            parameters += [expr]
            
        self.accept('RPAREN')
        return Node('FunctionCall', [identifier], parameters)
    
    def transformXEqual(self, identifier):

        if self.currentToken.type == 'ANDEQUAL':
            self.accept(self.currentToken.type)
            n = self.parseExpression()
            expr = [Node('Expression', [Node('Equal', [identifier, n.children[0]], [])], [])]
            return Node('Assignment', expr, identifier) 
        elif self.currentToken.type == 'PLUSEQUAL':
            self.accept(self.currentToken.type)
            n = self.parseExpression()
            expr = [Node('Expression', [Node('Plus', [identifier, n.children[0]], [])], [])]
            return Node('Assignment', expr, identifier) 
        elif self.currentToken.type == 'MINUSEQUAL':
            self.accept(self.currentToken.type)
            n = self.parseExpression()
            expr = [Node('Expression', [Node('Minus', [identifier, n.children[0]], [])], [])]
            return Node('Assignment', expr, identifier) 
        #elif self.currentToken.type == 'TIMESEQUAL':
        #elif self.currentToken.type == 'DIVEQUAL':
        #elif self.currentToken.type == 'MODEQUAL':
        #elif self.currentToken.type == 'LSHIFTEQUAL':
        #elif self.currentToken.type == 'RSHIFTEQUAL':
        #elif self.currentToken.type == 'ANDEQUAL':
        #elif self.currentToken.type == 'OREQUAL':
        #elif self.currentToken.type == 'XOREQUAL':

        return None


    def parseDeclType(self):
        if self.currentToken.type == 'URGENT':
            self.accept('URGENT')
            if self.currentToken.type == 'CHANNEL':
                self.accept('CHANNEL')
                return Node('TypeUrgentChannel')
            else:
                self.accept('BROADCAST')
                self.accept('CHANNEL')
                return Node('TypeUrgentBroadcastChannel')
        elif self.currentToken.type == 'CHANNEL':
            self.accept('CHANNEL')
            return Node('TypeChannel')
        elif self.currentToken.type == 'BROADCAST':
            self.accept('BROADCAST')
            self.accept('CHANNEL')
            return Node('TypeBroadcastChannel')
        elif self.currentToken.type == 'CLOCK':
            self.accept('CLOCK')
            return Node('TypeClock')
        else: 
            return self.parseStdType(False)
    
    def parseFuncType(self):
        if self.currentToken.type == 'VOID':
            self.accept('VOID')
            return Node('TypeVoid')

    def parseStdType(self, isConst):
        if self.currentToken.type == 'INT':
            self.accept('INT')
            if self.currentToken.type == 'BITAND' and not isConst:
                self.accept('BITAND')
                return Node('TypeIntPointer')
            elif self.currentToken.type == 'LBRACKET':
                self.accept('LBRACKET')
                #range-constrained int
                lower = self.parseExpression()
                self.accept('COMMA')
                upper = self.parseExpression()
                self.accept('RBRACKET')
                return Node('TypeInt', [lower, upper])
            elif isConst:
                return Node('TypeConstInt')
            else:
                return Node('TypeInt')
        elif self.currentToken.type == 'BOOL':
            self.accept('BOOL')
            if self.currentToken.type == 'BITAND' and not isConst:
                self.accept('BITAND')
                return Node('TypeBoolPointer')
            elif isConst:
                return Node('TypeConstBool')
            else:
                return Node('TypeBool')
        elif self.currentToken.type == 'IDENTIFIER': # and not isConst:
            identn = self.parseIdentifierComplex()
            identn.visit()

            # typedef vardecl, e.g. myint i;
            if len(identn.children) == 0 and self.isType(identn.leaf):
                return self.getType(identn.leaf)
            # extern vardecl child, e.g. oct.intvar x
            elif self.identifierTypeDict[identn.leaf].type == "NodeExtern":
                return Node('TypeExternChild', [identn])
        self.error('Not a type')

    def parseTypedefType(self, str):
        if self.isType(str):
            self.accept('IDENTIFIER')
            return self.getType(str)
        else:
            self.error('Not a typedef type:'+self.currentToken.value)


    def isType(self, str):
        if str in self.typedefDict:
            return True
        else:
            return False

    def getType(self, str):
        return self.typedefDict[str]
    
    def accept(self, expectedTokenType):
        if self.currentToken.type == expectedTokenType:
            self.currentToken = self.lexer.token()
        else:
            self.error('at token %s on line %d: Expected %s but was %s' % (self.currentToken.value, self.currentToken.lineno, expectedTokenType, self.currentToken.type))

    def error(self, msg):
            raise Exception('Error: Parser error '+ msg)

class VarDecl:
    """
    A nicer representation of a VarDecl node.

    @identifier is name of var
    @type is type used at declaration, e.g. "addr" if a typedef'ed var
    @basic_type is the underlying type, e.g. "TypeInt"
    """
    def __init__(self, identifier, type, array_dimensions=None, initval=None):
        self.identifier = identifier
        self.type = type
        self.basic_type = type
        self.array_dimensions = array_dimensions or []
        self.initval = initval
        #Default ranges
        if self.type in ("TypeInt", "TypeConstInt"):
            self.range_min = Node("Number", [], -32767)
            self.range_max = Node("Number", [], 32767)
        elif self.type in ("TypeBool", "TypeConstBool"):
            self.range_min = Node("Number", [], 0)
            self.range_max = Node("Number", [], 1)
        else:
            self.range_min = None
            self.range_max = None

    def __iter__(self):
        "For backwards compatibility."
        for x in (self.identifier, self.type, self.array_dimensions, self.initval):
            yield x

class DeclVisitor:
    def __init__(self, parser):
        self.parser = parser

        #calculate variables, clocks and channels
        self.constants = OrderedDict()
        #variables: list of VarDecl objects
        self.variables = []
        self.clocks = []
        self.channels = []
        self.urgent_channels = []
        self.broadcast_channels = []
        self.urgent_broadcast_channels = []
        self.functions = []

        last_type = None
        last_type_node = None
        def visit_identifiers(node):
            global last_type, last_type_node
            
            if node.type == 'VarDecl':
                last_type = node.leaf.type
                last_type_node = node.leaf
            elif node.type == 'NodeTypedef':
                last_type = 'TypeTypedef'
            elif node.type == 'NodeExtern':
                last_type = 'TypeExtern'
            elif node.type == 'Identifier':
                ident = node.leaf
                
                #parse out entire name (follow dots)
                curnode = node
                while len(curnode.children) > 0 and curnode.children[0].type == 'Identifier':
                    assert len(curnode.children) == 1
                    curnode = curnode.children[0]
                    ident += '.' + curnode.leaf

                #find array dimensions (if any)
                array_dimensions = []
                for child in [c for c in curnode.children if c.type == 'Index']:
                    array_dimensions += [child.leaf]
                
                if last_type == 'TypeInt':
                    if len(node.children) > 0 and \
                            node.children[0].type == "Assignment":
                        initval = node.children[0].children[0]
                        vdecl = VarDecl(ident, last_type, array_dimensions, initval)
                    else:
                        vdecl = VarDecl(ident, last_type, array_dimensions, 0)
                    #ranges
                    if len(last_type_node.children) == 2:
                        vdecl.range_min = last_type_node.children[0]
                        vdecl.range_max = last_type_node.children[1]

                    self.variables += [vdecl]
                elif last_type == 'TypeConstInt':
                    self.constants[ident] = node.children[0].children[0].children[0]
                elif last_type == 'TypeConstBool':
                    self.constants[ident] = node.children[0].children[0].children[0]
                elif last_type == 'TypeBool':
                    if len(node.children) > 0 and \
                            node.children[0].type == "Assignment":
                        #parse initial value
                        initval = node.children[0].children[0]
                        self.variables += [VarDecl(ident, last_type, array_dimensions, initval)]
                    else:
                        self.variables += [VarDecl(ident, last_type, array_dimensions, False)]
                elif last_type == 'TypeClock':
                    #'clock' may have been typedef'ed
                    clocktypedef = parser.typedefDict.get('clock', None)
                    if clocktypedef:
                        #treat clock as normal variable
                        clocktype = clocktypedef.children[0].leaf.leaf
                        self.variables += [VarDecl(ident, clocktype, array_dimensions, None)]
                    else:
                        self.clocks += [(node.leaf, 10)]
                elif last_type == 'TypeChannel':
                    self.channels += [(ident, array_dimensions)]
                elif last_type == 'TypeUrgentChannel':
                    self.urgent_channels += [(ident, array_dimensions)]
                elif last_type == 'TypeBroadcastChannel':
                    self.broadcast_channels += [(ident, array_dimensions)]
                elif last_type == 'TypeUrgentBroadcastChannel':
                    self.urgent_broadcast_channels += [(ident, array_dimensions)]
                elif last_type == 'NodeExtern':
                    classident = get_class_name_from_complex_identifier(last_type_node.leaf)
                    self.variables += [VarDecl(ident, classident, array_dimensions, None)]
                elif last_type == "TypeExternChild":
                    classident = get_full_name_from_complex_identifier(last_type_node.children[0])
                    self.variables += [VarDecl(ident, classident, array_dimensions, None)]
                elif last_type == 'NodeTypedef':
                    if len(node.children) > 0 and \
                            node.children[0].type == "Assignment":
                        initval = node.children[0].children[0]
                        vdecl = VarDecl(ident, last_type_node.leaf, array_dimensions, initval)
                    else:
                        vdecl = VarDecl(ident, last_type_node.leaf, array_dimensions, None)
                    #ranges from typedef
                    typedef = parser.typedefDict[last_type_node.leaf]
                    vdecl.basic_type = parser.typedefDict[last_type_node.leaf].children[0].type
                    if len(typedef.children[0].children) == 2:
                        vdecl.range_min = typedef.children[0].children[0]
                        vdecl.range_max = typedef.children[0].children[1]
                    self.variables += [vdecl]
                
                #else:
                #    print 'Unknown type: ' + last_type
                return False #don't recurse further
            elif node.type == 'Parameter':
                (t,iden) = node.leaf
                t.visit(visit_identifiers)
                if t.type == 'NodeTypedef':
                    last_type_node = t
                    last_type = 'NodeTypedef'
                iden.visit(visit_identifiers) 
            else:
                last_type = node.type
            if node.type == 'Function':
                self.functions.append(node)
                last_type == 'Function'
                last_type_node = node
                return False

            return True
        parser.AST.visit(visit_identifiers)

    def get_vardecl(self, ident):
        """Return the VarDecl object for ident, assumes the type of ident is a
           variable type."""
        return [x for x in self.variables if x.identifier == ident][0]

    def get_type(self, ident):
        """Return the type of ident"""
        if ident in [n for (n, _, _, _) in self.variables]:
            (n, t) = [(n, t) for (n, t, _, _) in self.variables if n == ident][0]
            if t == 'TypeInt':
                return "TypeInt"
            elif t == 'TypeBool':
                return "TypeBool"
            elif isinstance(t, str):
                #some extern type
                return t
            elif isinstance(t, list):
                #some extern child type
                return t
            else:
                assert False
        elif ident in [c for (c, _) in self.clocks]:
            return "TypeClock"
        elif ident in self.constants.keys():
            return "TypeConstInt"
        elif ident in [n for (n, _) in self.channels]:
            return "TypeChannel"
        elif ident in [n for (n, _) in self.urgent_channels]:
            return "TypeUrgenChannel"
        elif ident in [n for (n, _) in self.broadcast_channels]:
            return "TypeBroadcastChannel"
        elif ident in [n for (n, _) in self.urgent_broadcast_channels]:
            return "TypeUrgentBroadcastChannel"
        return None


# vim:ts=4:sw=4:expandtab
