#!/usr/bin/python
import sys
import os
import unittest
import lexer
import parser
import expressionParser
import node

class TestBasicParsing(unittest.TestCase):

    def test_parse_declaration(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_simple_declarations2.txt'), "r")

        self.variables = []
        self.clocks = []
        self.channels = []
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)

        last_type = None
        def visit_identifiers(node):
            global last_type
            if node.type == 'VarDecl':
                last_type = node.leaf.type
            elif node.type == 'Identifier':
                if last_type == 'TypeInt':
                    self.variables += [(node.leaf, 'int')]
                elif last_type == 'TypeClock':
                    #TODO calculate max constant
                    self.clocks += [(node.leaf, 10)]
                elif last_type == 'TypeChannel':
                    self.channels += [node.leaf]
            #if node.type == 'ChanDecl':
            #    last_type = node.leaf.type
        pars.AST.visit(visit_identifiers)
        #pars.AST.visit()

        self.assertEqual(self.variables, [('L', 'int')])
        self.assertEqual(self.clocks, [('time', 10), ('y1', 10), ('y2', 10), ('y3', 10), ('y4', 10)])
        self.assertEqual(self.channels, ['take', 'release'])


    def test_parse_empty_query(self):
        lex = lexer.lexer
        pars = parser.Parser("", lex)

        self.assertEqual(len(pars.AST.children), 0)

    def test_parse_expression(self):
        parser = testParser(lexer.lexer)
        res = parser.parse("5")
        self.assertEqual(res.type, "Number")
        self.assertEqual(res.leaf, 5)
  
        res = parser.parse("5 > 5")
        self.assertEqual(res.type, "Greater") 
        self.assertEqual(res.children[0].type, "Number")
        self.assertEqual(res.children[0].leaf, 5)
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 5)
  
        res = parser.parse("5 and 4")
        self.assertEqual(res.type, "And")
        self.assertEqual(res.children[0].type, "Number")
        self.assertEqual(res.children[0].leaf, 5)
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 4)
  
        res = parser.parse("5 < 5 and 4 > 3")
        self.assertEqual(res.type, "And")
  
        self.assertEqual(res.children[0].type, "Less")
        self.assertEqual(res.children[0].children[0].type, "Number")
        self.assertEqual(res.children[0].children[0].leaf, 5)
        self.assertEqual(res.children[0].children[1].type, "Number")
        self.assertEqual(res.children[0].children[1].leaf, 5)
  
        res = parser.parse("Viking1.safe and Viking2.safe") #TODO add struct support
        res.visit()
  
        res = parser.parse(
            "Viking1.safe and Viking2.safe and Viking3.safe and Viking4.safe")

#TODO clean this up a bit
class myToken:
    type = None

    def __init__(self, type):
        self.type = type
        
class testParser:
    currentToken = None
    lex = None

    def __init__(self, lexer):
        self.lex = lexer

    def parse(self, str):
        self.lex.input(str)
        self.currentToken = self.lex.token()
        exParser = expressionParser.ExpressionParser(self.lex, self)
        return exParser.parse()

    def parseNumber(self):
        n = node.Node('Number', [], self.currentToken.value)
        self.accept('NUMBER')
        return n

    def parseIdentifier(self):
        n = node.Node('Identifier', [], self.currentToken.value)
        self.accept('IDENTIFIER')
        return n

    def accept(self, expectedTokenType):
        if self.currentToken.type == expectedTokenType:
            self.currentToken = self.lex.token()
            if self.currentToken == None:
                t = myToken('UNKNOWN')
                self.currentToken = t
        else:
            self.error('at token %s on line %d: Expected %s but was %s' % (self.currentToken.value, self.currentToken.lineno, expectedTokenType, self.currentToken.type))

    def error(self, msg):
            print 'Error: Parser error', msg
 
if __name__ == '__main__':
    unittest.main()
