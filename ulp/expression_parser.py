""" 
    Copyright (C) 2009 
    Mads Chr. Olesen <mchro@cs.aau.dk>
    Andreas Engelbredt Dalsgaard <andreas.dalsgaard@gmail.com>

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

import ply.yacc as yacc
from lexer import *
from node import Node

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = Node('Number', leaf=int(p[1]))

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    p[0] = Node('Identifier', leaf=p[1])

def p_expression_field_access(p):
    'expression : expression DOT IDENTIFIER'
    p[0] = Node('FieldAccess', children=[p[1], Node('Identifier', leaf=p[3])])

def p_expression_binary(p):
    """expression : expression AND expression
                | expression OR expression
                | expression LESS expression
                | expression LESSEQ expression
                | expression GREATER expression
                | expression GREATEREQ expression
                | expression EQUAL expression
                | expression NOTEQUAL expression
                | expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression
                | expression MODULO expression
                | expression BITAND expression
                | expression BITOR expression"""
    p[0] = Node(p[2], children=[p[1], p[3]])

def p_error(p):
    if p != None:
        print "Syntax error at token", p.type
#.parser.pleasestop
    else:
        print "Last token"
    parser.pleasestop = True
    yacc.errok()
    #return None

def eof_tokenfunc():
    print "eof_tokenfunc"
    #import pdb; pdb.set_trace()
    t = lex.LexToken()
    t.type = '$end'
    return t


#Precedence - listed from lowest to highest!
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'BITOR'),
    ('left', 'BITAND'),
    ('left', 'EQUAL', 'NOTEQUAL'),
    ('left', 'LESS', 'LESSEQ', 'GREATER', 'GREATEREQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('left', 'DOT'),
)

# Build the parser
parser = yacc.yacc()

# vim:ts=4:sw=4:expandtab
