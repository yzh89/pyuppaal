"""
    Copyright (C) 2008 Andreas Engelbredt Dalsgaard <andreas.dalsgaard@gmail.com>

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

"""This file contains the lexer rules and the list of valid tokens."""
import ply.lex as lex
import sys
import re

reserved = {
'int' : 'INT',
'bool' : 'BOOL',
'chan' : 'CHANNEL',
'clock' : 'CLOCK',
'urgent' : 'URGENT',
'broadcast' : 'BROADCAST',
'const' : 'CONST',
'if' : 'IF',
'else' : 'ELSE',
'while' : 'WHILE',
'struct' : 'STRUCT'
}

# This is the list of token names.
tokens = [
    'IDENTIFIER',
    'LPAREN',
    'RPAREN',
    'LCURLYPAREN',
    'RCURLYPAREN',
    'LSQUAREBRACKET',
    'RSQUAREBRACKET',
    'ASSIGN',
    'EQUAL',
    'SEMI',
	'COMMA',
    'PLUS',
    'NOT',
    'LESS',
    'GREATER' ] +list(reserved.values())
# These are regular expression rules for simple tokens.
t_ASSIGN = r':='
t_EQUAL = r'='
t_SEMI = r';'
t_COMMA = r','
t_PLUS = r'\+'
t_NOT = r'!'
t_LESS = r'<'
t_GREATER = r'>'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURLYPAREN = r'\{'
t_RCURLYPAREN = r'\}'
t_LSQUAREBRACKET = r'\['
t_RSQUAREBRACKET = r'\]'


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'IDENTIFIER')    # Check for reserved words
    return t

# Read in an int.
def t_NUMBER(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

# Ignore comments.
def t_comment(t):
    r'[//][^\n]*'
    pass

# Track line numbers.
def t_newline(t):
    r'\n+'
    t.lineno += len(t.value)
# These are the things that should be ignored.
t_ignore = ' \t'

# Handle errors.
def t_error(t):
    raise SyntaxError("syntax error on line %d near '%s'" %
        (t.lineno, t.value))
# Build the lexer.
lex.lex()

# vim:ts=4:sw=4:expandtab
