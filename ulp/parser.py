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

from lexer import *
import expression_parser
from node import Node

# dictionary of names
identifiers = { }

class Parser:

    currentToken = None
    lexer = None
    expressionParser = None

    def __init__(self, data, lexer):
        self.lexer = lexer
        self.lexer.input(data)
        self.currentToken = self.lexer.token()
        self.expressionParser = expression_parser.parser
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
                    identifier = self.parseIdentifier()
                    statements.append(self.parseDeclaration(type, identifier))
                elif self.currentToken.type in ('INT', 'BOOL'): #Function or declaration           
                    type = self.parseStdType(False)
                    identifier = self.parseIdentifier()
                    statements.append(self.parseDeclaration(type, identifier))
                    
                    if self.currentToken.type == 'LPAREN':
                        statements.append(self.parseFunction(type, identifier))
                else:
                    break 
            else:
                break

        if self.currentToken != None:
            self.error('at token "%s" on line %d: Did not expect any token, but found token of type %s' % (self.currentToken.value, self.currentToken.lineno, self.currentToken.type))

        return statements
    
    def parseDeclaration(self, type, identifier):
        varList = []
        
        #TODO structs
        #TODO scalars
        #TODO arrays
        varList.append(identifier)
        if self.currentToken.type == 'COMMA':
            varList.extend(self.parseVariableList())
                    
        if self.currentToken.type == 'SEMI':
            self.accept('SEMI')
            return Node('VarDecl', varList, type)

    def parseFunction(self, type, identifier):
        children = []
        self.accept('LPAREN')
        parameters = self.parseParameters()
        self.accept('RPAREN')
        self.accept('LCURLYPAREN')
        children.extend(self.parseBodyStatements())
        self.accept('RCURLYPAREN')

        return Node('Function', children, (type, identifier))
    
    def parseParameters(self):
        parameters = []
        while self.currentToken.type in ('INT', 'BOOL', 'CONST'):
            isConst = False
            if self.currentToken.type == 'CONST':
                self.accept('CONST')
                isConst = True
            type = self.parseStdType(isConst) 
            #TODO add support for &
            identifier = self.parseIdentifier()
            parameters.append( Node('Parameter', [], (type, identifier)) )
            #TODO arrays
            if self.currentToken.type == 'COMMA':
                self.accept('COMMA')

        return parameters
   
    def parseBodyStatements(self):
        statements = []
        while self.currentToken.type != 'RCURLYPAREN':
            if self.currentToken.type in ('IDENTIFIER', 'NUMBER', 'MINUS', 'PLUS'):
                expression = self.expressionParser.parse()
             
        return statements 

#    def parseExpression(self):
#        n = None
#
#        if self.currentToken.type == 'IDENTIFIER':
#            n = self.parseIdentifier()
#        elif self.currentToken.type == 'NUMBER':
#            n = Node('Number', [], self.currentToken.value)
#            self.accept('NUMBER')
#        elif self.currentToke.type in ('MINUS', 'PLUS', 'NOT'):
#            n = self.parseUnary()
#        elif self.currentToken.type == 'TRUE':
#            self.accept('TRUE')
#            n = Node('True')
#        elif self.currentToken.type == 'FALSE':
#            self.accept('FALSE')
#            n = Node('False')
#        elif self.currentToken.type == 'LPAREN':
#            n = self.parseExpression()
#        
#
#    def parseUnary(self):
#        if self.currentToke.type == 'MINUS':
#            self.accept('MINUS')
#            return = Node('Minus')
#        elif self.currentToke.type == 'PLUS':
#            self.accept('PLUS')
#            return = Node('Plus')
#        elif self.currentToke.type == 'NOT':
#            self.accept('NOT')
#            return = Node('Not')
#        else:
#            self.error('unknown Unary token')

    def parseVariableList(self):
        children = []
        while self.currentToken.type == 'COMMA':
            self.accept('COMMA')
            children.append(self.parseIdentifier())
         
        return children

    def parseIdentifier(self):
        n = Node('Identifier', [], self.currentToken.value)
        self.accept('IDENTIFIER')
        return n

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
            return self.parseStdType()
    
    def parseFuncType(self):
        if self.currentToken.type == 'VOID':
            self.accept('VOID')
            return Node('TypeVoid')

    def parseStdType(self, isConst):
        if self.currentToken.type == 'INT':
            self.accept('INT')
            if isConst:
                return Node('TypeConstInt')
            else:
                return Node('TypeInt')
        elif self.currentToken.type == 'BOOL':
            self.accept('BOOL')
            if isConst:
                return Node('TypeConstBool')
            else:
                return Node('TypeBool')

    def accept(self, expectedTokenType):
        if self.currentToken.type == expectedTokenType:
            self.currentToken = self.lexer.token()
        else:
            self.error('at token %s on line %d: Expected %s but was %s' % (self.currentToken.value, self.currentToken.lineno, expectedTokenType, self.currentToken.type))

    def error(self, msg):
            print 'Error: Parser error', msg
        
# vim:ts=4:sw=4:expandtab
