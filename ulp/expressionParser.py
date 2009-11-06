""" 
    Copyright (C) 2009 
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
    along with this program.  If not, see <http://www.gnu.org/licenses/>. 

    This program is based on the public domain example programs from the blog post:
    <http://eli.thegreenplace.net/2009/03/20/a-recursive-descent-parser-with-an-infix-expression-evaluator/>
    made by: Eli Bendersky (eliben@gmail.com)
"""

from lexer import *
from node import Node
import operator

class ExpressionParser:

    def __init__(self, lexer, parser):
        self.lexer = lexer
        self.parser = parser

    def parse(self):
        o = self._infix_eval()
        return o
    ##
    ## The infix expression evaluator. 
    ## Returns the value of the evaluated expression.
    ##
    ## Infix expressions are numbers and identifiers separated by
    ## binary (and unary) operators, possibly with parts delimited
    ## by parentheses. The operators supported by this evaluator
    ## and their precedences are controlled through the _ops 
    ## table.
    ##
    ## Internally, uses two stacks. One for keeping the operations
    ## that still await results, and another for keeping the 
    ## results.
    ##
    ##

    def _infix_eval(self):
        """ Run the infix evaluator and return the result.
        """
        self.op_stack = []
        self.res_stack = []
        
        self.op_stack.append(self._sentinel)
        self._infix_eval_expr()
        return self.res_stack[-1]
    
    class Op(object):
        """ Represents an operator recognized by the infix 
            evaluator. Each operator has a numeric precedence, 
            and flags specifying whether it's unary/binary and 
            right/left associative.
        """
        def __init__(   self, name, op, prec, 
                        unary=False, right_assoc=False):
            self.name = name
            self.op = op
            self.prec = prec
            self.unary = unary
            self.binary = not self.unary
            self.right_assoc = right_assoc
            self.left_assoc = not self.right_assoc
            
        def apply(self, *args):
            return Node(self.name, args)

        def precedes(self, other):
            """ The '>' operator from the Shunting Yard algorithm.
                I don't call it '>' on purpose, as its semantics 
                are unusual (i.e. this is not the familiar 
                algebraic '>')
            """
            if self.binary and other.binary:
                if self.prec > other.prec:
                    return True
                elif self.left_assoc and (self.prec == other.prec):
                    return True
            elif self.unary and other.binary:
                return self.prec >= other.prec
            
            return False

        def __repr__(self):
            return '<%s(%s)>' % (self.name, self.prec)

    # The operators recognized by the evaluator.
    #
    _ops = {
        'uMINUS':    Op('UnaryMinus', operator.neg, 90, unary=True),
        'TIMES':     Op('Times', operator.mul, 50),
        'DIVIDE':    Op('Divide', operator.div, 50),
        'PLUS':      Op('Plus', operator.add, 40),
        'MINUS':     Op('Minus', operator.sub, 40),
        'LSHIFT':    Op('LeftShift', operator.lshift, 35),
        'RSHIFT':    Op('RightShift', operator.rshift, 35),
        'BITAND':    Op('BitAnd', operator.and_, 30),
        'XOR':       Op('xor', operator.xor, 29),
        'BITOR':     Op('BitOr', operator.or_, 28),
        'GREATER':   Op('Greater', operator.gt, 20),
        'GREATEREQ': Op('GreaterEqual', operator.ge, 20),
        'LESS':      Op('Less', operator.lt, 20),
        'LESSEQ':    Op('LessEqual', operator.le, 20),
        'EQUAL':     Op('Equal', operator.eq, 15),
        'NOTEQUAL':  Op('NotEqual', operator.ne, 15),
        'AND':       Op('And', operator.and_, 15),
        'OR':        Op('Or', operator.and_, 15),
    }          
    
    # A set of operators that can be unary. If such an operator
    # is found, 'u' is prepended to its symbol for finding it in
    # the _ops table
    #
    _unaries = set(['MINUS'])
    
    # Dummy operator with the lowest possible precedence (the 
    # Sentinel value in the Shunting Yard algorithm)
    #
    _sentinel = Op(None, None, 0)

    def _infix_eval_expr(self):
        """ Evaluates an 'expression' - atoms separated by binary
            operators.
        """
        self._infix_eval_atom()
 
        while ( self.parser.currentToken.type in self._ops and 
                self._ops[self.parser.currentToken.type].binary):
            self._push_op(self._ops[self.parser.currentToken.type])
            self._get_next_token()
            self._infix_eval_atom()
        
        while self.op_stack[-1] != self._sentinel:
            self._pop_op()
        
    def _infix_eval_atom(self):
        """ Evaluates an 'atom' - either an identifier/number, or
            an atom prefixed by a unary operation, or a full
            expression inside parentheses.
        """
        if self.parser.currentToken.type in ['IDENTIFIER', 'NUMBER']:
            if self.parser.currentToken.type == 'IDENTIFIER':
                self.res_stack.append(self.parser.parseIdentifier())
            else:
                self.res_stack.append(self.parser.parseNumber())
        elif self.parser.currentToken.type == 'LPAREN':
            self._get_next_token()
            self.op_stack.append(self._sentinel)
            self._infix_eval_expr()
            self._match('RPAREN')
            self.op_stack.pop()
        elif self.parser.currentToken.type in self._unaries:
            self._push_op(self._ops['u' + self.parser.currentToken.type])
            self._get_next_token()
            self._infix_eval_atom()
    
    def _push_op(self, op):
        """ Pushes an operation onto the op stack. 
            But first computes and removes all higher-precedence 
            operators from it.
        """
        #~ print 'push_op: stack =', self.op_stack
        #~ print '    ...', op
        while self.op_stack[-1].precedes(op):
            self._pop_op()
        self.op_stack.append(op)
        #~ print '    ... =>', self.op_stack
    
    def _pop_op(self):
        """ Pops an operation from the op stack, computing its
            result and storing it on the result stack.
        """
        #~ print 'pop_op: op_stack =', self.op_stack
        #~ print '    ... res_stack =', self.res_stack
        top_op = self.op_stack.pop()
        
        if top_op.unary:
            self.res_stack.append(top_op.apply(self.res_stack.pop()))
        else:
            if len(self.res_stack) < 2:
                self.parser.error('Not enough arguments for operator %s' % top_op.name)
                
            t1 = self.res_stack.pop()
            t0 = self.res_stack.pop()
            self.res_stack.append(top_op.apply(t0, t1))
        #~ print '    ... => res_stack =', self.res_stack

    def _get_next_token(self):
        self.parser.currentToken = self.lexer.token()
  
