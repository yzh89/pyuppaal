#!/usr/bin/python
import sys
import os
import unittest
import lexer
import parser
import expression_parser

class TestBasicParsing(unittest.TestCase):

    def test_parse_declaration(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_simple_declarations2.txt'), "r")

        self.variables = []
        self.clocks = []
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)

        last_type = None
        def visit_identifiers(node):
            global last_type
            if node.type == 'VarDecl':
                last_type = node.leaf.type
            if node.type == 'Identifier':
                if last_type == 'TypeInt':
                    self.variables += [(node.leaf, 'int')]
                if last_type == 'TypeClock':
                    #TODO calculate max constant
                    self.clocks += [(node.leaf, 10)]
        pars.AST.visit(visit_identifiers)

        self.assertEqual(self.variables, [('L', 'int')])
        self.assertEqual(self.clocks, [('time', 10), ('y1', 10), ('y2', 10), ('y3', 10), ('y4', 10)])


    def test_parse_empty_query(self):
        lex = lexer.lexer
        pars = parser.Parser("", lex)

        self.assertEqual(len(pars.AST.children), 0)

    def test_parse_expression(self):
        res = expression_parser.parser.parse("5")
        self.assertEqual(res.type, "Number")
        self.assertEqual(res.leaf, 5)

        res = expression_parser.parser.parse("5 > 5")
        self.assertEqual(res.type, ">")
        self.assertEqual(res.children[0].type, "Number")
        self.assertEqual(res.children[0].leaf, 5)
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 5)

        res = expression_parser.parser.parse("5 and 4")
        self.assertEqual(res.type, "and")
        self.assertEqual(res.children[0].type, "Number")
        self.assertEqual(res.children[0].leaf, 5)
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 4)

        res = expression_parser.parser.parse("5 < 5 and 4 > 3")
        self.assertEqual(res.type, "and")

        self.assertEqual(res.children[0].type, "<")
        self.assertEqual(res.children[0].children[0].type, "Number")
        self.assertEqual(res.children[0].children[0].leaf, 5)
        self.assertEqual(res.children[0].children[1].type, "Number")
        self.assertEqual(res.children[0].children[1].leaf, 5)

        res = expression_parser.parser.parse("Viking1.safe and Viking2.safe")
        res.visit()

        res = expression_parser.parser.parse(
            "Viking1.safe and Viking2.safe and Viking3.safe and Viking4.safe")

        

if __name__ == '__main__':
    unittest.main()
