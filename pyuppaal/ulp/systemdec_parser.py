""" 
    Copyright (C) 2011
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

#from lexer import *
import lexer
import expressionParser
from node import Node

import ply.yacc as yacc

class SystemDeclarationParser:
    def __init__(self, data, lex_optimize=True,
            lextab='pyuppaal_systemdec_parser.lextab',
            yacc_optimize=False,
            yacctab='pyuppaal_systemdec_parser.yacctab',
            yacc_debug=False):
        
        self.data = data

        self.tokens = lexer.tokens
        # Build the parser
        self.systemdec_parser = yacc.yacc(module=self, 
            start='systemdec',
            debug=yacc_debug,
            optimize=yacc_optimize,
            tabmodule=yacctab)

    def parse(self):
        return self.systemdec_parser.parse(self.data)

    #start rule
    def p_systemdec(self, p):
        '''systemdec : systemdec statement SEMI
                     | statement SEMI'''
        if len(p) == 3: #one statement
            p[0] = Node("SystemDec", [p[1]])
        else:
            assert isinstance(p[1], Node)
            assert p[1].type == 'SystemDec'
            assert isinstance(p[2], Node)

            p[1].children += [p[2]]
            p[0] = p[1]

    def p_empty(self, p):
        'empty :'
        pass


    def p_instantiation(self, p):
        '''statement : IDENTIFIER EQUALS IDENTIFIER LPAREN arguments RPAREN
                   |   IDENTIFIER ASSIGN IDENTIFIER LPAREN arguments RPAREN'''
        ident = Node('Identifier', [], p[1])
        templateident = Node('Identifier', [], p[3])
        arguments = p[5]

        inst = Node("TemplateInstantiation", arguments, templateident)
        p[0] = Node("Assignment", [inst], ident)

    def p_arguments(self, p):
        '''arguments : expression COMMA arguments
                   | expression
                   | empty
        '''
        if len(p) == 2: #one or zero arguments
            if p[1]:
                p[0] = [p[1]]
            else:
                p[0] = []
        else:
            p[0] = [p[1]] + p[3] 

    #XXX, let's see if we can get away with only parsing numbers for now
    #otherwise, we should hook up the expressionParser

    def p_expression(self, p):
        '''expression : NUMBER'''
        p[0] = Node('Number', [], p[1])

    def p_system(self, p):
        'statement : SYSTEM systemslist'
        p[0] = Node("System", p[2])

    def p_systemslist(self, p):
        '''systemslist : IDENTIFIER COMMA systemslist
                    | IDENTIFIER
        '''
        if len(p) == 2: #one identifier
            ident = Node('Identifier', [], p[1])
            p[0] = [ident]
        else:
            ident = Node('Identifier', [], p[1])
            p[0] = [ident] + p[3]


