#!/usr/bin/python
import sys
import os
import unittest
from pyuppaal.ulp import lexer, parser, expressionParser, node

class TestBasicParsing(unittest.TestCase):

    def test_parse_declarations(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_simple_declarations.txt'), "r")

        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        res = pars.AST.children

        #pars.AST.visit()

        declvisitor = parser.DeclVisitor(pars)

        self.assertEqual(declvisitor.variables, [('a', 'int', []), ('b', 'bool', []), ('b1', 'bool', []), ('b2', 'bool', [])])

        self.assertEqual(len(declvisitor.clocks), 1)
        self.assertEqual(declvisitor.clocks[0][0], 'c')

        self.assertEqual(declvisitor.channels, [('d', [])])
        self.assertEqual(declvisitor.urgent_channels, [('e', [])])
        self.assertEqual(declvisitor.broadcast_channels, [('f', [])])
        self.assertEqual(declvisitor.urgent_broadcast_channels, [('g', [])])

    def test_parse_declarations2(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_simple_declarations2.txt'), "r")

        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        res = pars.AST.children

        #pars.AST.visit()

        declvisitor = parser.DeclVisitor(pars)

        self.assertEqual(res[7].type, 'VarDecl')
        self.assertEqual(res[7].leaf.type, 'TypeInt')
        self.assertEqual(res[7].children[0].type, 'Identifier')
        self.assertEqual(res[7].children[0].leaf, 'lalala')
        self.assertEqual(res[7].children[0].children[0].type, 'Assignment')
        self.assertEqual(res[7].children[0].children[0].leaf.type, 'Identifier')
        self.assertEqual(res[7].children[0].children[0].leaf.leaf, 'lalala')


        self.assertEqual(res[12].type, 'VarDecl')
        self.assertEqual(res[12].leaf.type, 'TypeBool')
        self.assertEqual(res[12].children[0].type, 'Identifier')
        self.assertEqual(res[12].children[0].leaf, 'msg')
        self.assertEqual(res[12].children[0].children[0].type, 'Index')
        self.assertEqual(res[12].children[0].children[1].type, 'Index')


        self.assertEqual(declvisitor.variables[0], ('L', 'int', []))
        self.assertEqual(declvisitor.variables[1], ('lalala', 'int', []))

        self.assertEqual(declvisitor.clocks, [('time', 10), ('y1', 10), ('y2', 10), ('y3', 10), ('y4', 10)])
        self.assertEqual(declvisitor.channels, [('take', []), ('release', [])])

        


    def test_parse_empty_query(self):
        lex = lexer.lexer
        pars = parser.Parser("", lex)

        self.assertEqual(len(pars.AST.children), 0)

    def test_parse_array(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_array.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(len(pars.AST.children), 7) #TODO add more asserts
        res = pars.AST.children
        #pars.AST.visit()
        self.assertEqual(res[0].children[0].children[0].type, "Index") 
        self.assertEqual(res[1].children[0].children[0].type, "Index") 
        self.assertEqual(res[2].children[0].children[0].type, "Index") 
        self.assertEqual(res[3].children[0].children[0].type, "Index") 
        self.assertEqual(res[4].children[0].children[0].type, "Index") 
        self.assertEqual(res[6].children[0].children[0].type, "Index") 
        self.assertEqual(res[6].children[0].children[1].type, "Index") 

        #mchro 07-04-2011: don't allow empty brackets, it's not a valid expression
        #myParser = testParser(lexer.lexer)
        #res = myParser.parse("a[]")
        #self.assertEqual(res.type, "Identifier") 
        #self.assertEqual(len(res.children), 0)

    def test_struct(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_struct.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(len(pars.AST.children), 1) #TODO add more asserts
        
    def test_parse_typedef_simple(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_typedef_simple.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        #pars.AST.visit()


        self.assertEqual(len(pars.AST.children), 4)
        self.assertEqual(pars.AST.type, "RootNode")
        self.assertEqual(pars.AST.children[0].type, "NodeTypedef") 
        self.assertEqual(pars.AST.children[0].leaf, "id_t") 
        self.assertEqual(pars.AST.children[0].children[0].type, "TypeInt")
        self.assertEqual(pars.AST.children[1].type, "NodeTypedef") 
        self.assertEqual(pars.AST.children[1].leaf, "id_t") 
        self.assertEqual(pars.AST.children[1].children[0].type, "TypeInt")
        self.assertEqual(pars.AST.children[1].children[0].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[1].children[0].children[0].children[0].leaf, 0)
        self.assertEqual(pars.AST.children[1].children[0].children[1].type, "Expression")
        self.assertEqual(pars.AST.children[1].children[0].children[1].children[0].leaf, 4)
        self.assertEqual(pars.AST.children[2].type, "NodeTypedef") 
        self.assertEqual(pars.AST.children[2].leaf, "id_t") 
        self.assertEqual(pars.AST.children[2].children[0].type, "TypeInt")
        self.assertEqual(pars.AST.children[2].children[0].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[2].children[0].children[1].type, "Expression")
        self.assertEqual(pars.AST.children[2].children[0].children[1].children[0].leaf, 4)
        self.assertEqual(pars.AST.children[2].type, "NodeTypedef") 
        self.assertEqual(pars.AST.children[2].leaf, "id_t") 
        self.assertEqual(pars.AST.children[2].children[0].type, "TypeInt")
        self.assertEqual(pars.AST.children[2].children[0].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[2].children[0].children[1].type, "Expression")
        self.assertEqual(pars.AST.children[2].children[0].children[1].children[0].leaf, 4)

        self.assertEqual(len(pars.typedefDict), 1)
        self.assertTrue('id_t' in pars.typedefDict)


    def test_parse_typedef(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_typedef.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        #pars.AST.visit()
        self.assertEqual(len(pars.AST.children), 7)

        self.assertEqual(len(pars.typedefDict), 4)
        self.assertTrue('myStructType' in pars.typedefDict)
        self.assertTrue('adr' in pars.typedefDict)
        self.assertTrue('DBMClock' in pars.typedefDict)
        self.assertTrue('clock' in pars.typedefDict)

        ctype = pars.typedefDict['clock']
        self.assertEqual(ctype.type, 'NodeTypedef')
        self.assertEqual(ctype.leaf, 'clock')
        self.assertEqual(len(ctype.children), 1)
        self.assertEqual(ctype.children[0], pars.typedefDict['DBMClock'])

        declvisitor = parser.DeclVisitor(pars)
        #XXX parses to deeply into structs!
        self.assertEqual(len(declvisitor.variables), 4)
        #print declvisitor.variables

        varnames = [x for (x, _, _) in declvisitor.variables]
        self.assertTrue('m' in varnames)
        self.assertTrue(('m', 'myStructType', []) in declvisitor.variables)
        self.assertTrue('n' in varnames)
        self.assertTrue(('n', 'adr', []) in declvisitor.variables)
        self.assertTrue('c' in varnames)
        self.assertTrue(('c', 'DBMClock', []) in declvisitor.variables)
        #XXX parses to deeply into structs!
        #self.assertFalse('a' in varnames)

    def test_parse_brackets(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_brackets.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)

    def test_comments(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_comments.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(pars.AST.type, "RootNode")
        self.assertEqual(pars.AST.children[0].type, "VarDecl") 
        self.assertEqual(pars.AST.children[1].type, "Function")
        self.assertEqual(pars.AST.children[1].children[0].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[0].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[1].children[0].children[0].children[0].type, "Divide")
        self.assertEqual(len(pars.AST.children), 2) 

    def test_operators(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_operators.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(pars.AST.type, "RootNode")
        self.assertEqual(pars.AST.children[0].type, "VarDecl") 
        self.assertEqual(pars.AST.children[1].type, "Function")
        self.assertEqual(pars.AST.children[1].children[0].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[0].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[1].children[0].children[0].children[0].type, "Plus")
        self.assertEqual(pars.AST.children[1].children[1].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[1].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[1].children[1].children[0].children[0].type, "Minus")
        self.assertEqual(pars.AST.children[1].children[2].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[2].children[0].children[0].type, "Times")
        self.assertEqual(pars.AST.children[1].children[3].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[3].children[0].children[0].type, "Divide")
        self.assertEqual(pars.AST.children[1].children[4].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[4].children[0].children[0].type, "UnaryMinus")
        self.assertEqual(pars.AST.children[1].children[5].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[5].children[0].children[0].type, "Minus")
        self.assertEqual(pars.AST.children[1].children[5].children[0].children[0].children[0].type, "UnaryMinus")
        self.assertEqual(pars.AST.children[1].children[6].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[6].children[0].children[0].type, "Minus")
        self.assertEqual(pars.AST.children[1].children[6].children[0].children[0].children[0].type, "PlusPlusPost")
        self.assertEqual(pars.AST.children[1].children[7].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[7].children[0].children[0].type, "Plus")
        self.assertEqual(pars.AST.children[1].children[7].children[0].children[0].children[0].type, "PlusPlusPost")
        self.assertEqual(pars.AST.children[1].children[8].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[8].children[0].children[0].type, "Plus")
        self.assertEqual(pars.AST.children[1].children[8].children[0].children[0].children[0].type, "PlusPlusPre")
        self.assertEqual(pars.AST.children[1].children[9].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[9].children[0].children[0].type, "Plus")
        self.assertEqual(pars.AST.children[1].children[9].children[0].children[0].children[0].type, "PlusPlusPre")
        self.assertEqual(pars.AST.children[1].children[9].children[0].children[0].children[1].type, "PlusPlusPost")
        self.assertEqual(pars.AST.children[1].children[10].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[10].children[0].children[0].type, "Plus")
        self.assertEqual(pars.AST.children[1].children[10].children[0].children[0].children[0].type, "PlusPlusPost")
        self.assertEqual(pars.AST.children[1].children[10].children[0].children[0].children[1].type, "PlusPlusPre")
        self.assertEqual(pars.AST.children[1].children[11].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[11].children[0].children[0].type, "Minus")
        self.assertEqual(pars.AST.children[1].children[11].children[0].children[0].children[0].type, "MinusMinusPost")
        self.assertEqual(pars.AST.children[1].children[12].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[12].children[0].children[0].type, "Minus")
        self.assertEqual(pars.AST.children[1].children[12].children[0].children[0].children[0].type, "MinusMinusPost")
        self.assertEqual(pars.AST.children[1].children[12].children[0].children[0].children[1].type, "MinusMinusPre")
        self.assertEqual(pars.AST.children[1].children[13].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[13].children[0].children[0].type, "Plus")
        self.assertEqual(pars.AST.children[1].children[13].children[0].children[0].children[0].type, "MinusMinusPost")
        self.assertEqual(pars.AST.children[1].children[14].type, "Assignment")
        self.assertEqual(pars.AST.children[1].children[14].children[0].children[0].type, "Plus")
        self.assertEqual(pars.AST.children[1].children[14].children[0].children[0].children[0].type, "MinusMinusPre")
        #TODO add more operators pars.AST.visit() 
        self.assertEqual(len(pars.AST.children), 2)   

    def test_parse_assignments(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_assignments.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(pars.AST.type, "RootNode")
        self.assertEqual(pars.AST.children[0].type, "VarDecl") 
        self.assertEqual(pars.AST.children[1].type, "VarDecl") 
        self.assertEqual(pars.AST.children[2].type, "Function")
        self.assertEqual(pars.AST.children[2].children[0].type, "Assignment")
        self.assertEqual(pars.AST.children[2].children[0].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[2].children[0].children[0].children[0].type, "PlusPlusPost")
        self.assertEqual(pars.AST.children[2].children[1].type, "Assignment")
        self.assertEqual(pars.AST.children[2].children[1].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[2].children[1].children[0].children[0].type, "PlusPlusPre")
        self.assertEqual(pars.AST.children[2].children[2].type, "Assignment")
        self.assertEqual(pars.AST.children[2].children[2].children[0].type, "Expression")
        self.assertEqual(pars.AST.children[2].children[2].children[0].children[0].type, "MinusMinusPre")
        self.assertEqual(pars.AST.children[2].children[3].type, "Assignment")
        self.assertEqual(pars.AST.children[2].children[3].children[0].children[0].type, "Times")
        self.assertEqual(pars.AST.children[2].children[3].children[0].children[0].children[0].type, "PlusPlusPre")
        self.assertEqual(pars.AST.children[2].children[3].children[0].children[0].children[1].type, "PlusPlusPost")
        self.assertEqual(pars.AST.children[2].children[4].type, "Assignment")
        self.assertEqual(pars.AST.children[2].children[4].children[0].children[0].type, "Times")
        self.assertEqual(pars.AST.children[2].children[4].children[0].children[0].children[0].type, "Times")
        self.assertEqual(pars.AST.children[2].children[4].children[0]. \
                        children[0].children[0].children[0].type, "PlusPlusPre")
        self.assertEqual(pars.AST.children[2].children[4].children[0]. \
                        children[0].children[0].children[1].type, "PlusPlusPost")
        self.assertEqual(pars.AST.children[2].children[4].children[0]. \
                        children[0].children[0].children[1].type, "PlusPlusPost")
        self.assertEqual(len(pars.AST.children), 3) 

    def test_parse_for_loop(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_for_loop.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(len(pars.AST.children), 1) #TODO add more asserts

    def test_parse_while_loop(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_while_loop.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(len(pars.AST.children), 1) #TODO add more asserts

    def test_parse_do_while_loop(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_do_while_loop.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(len(pars.AST.children), 1) #TODO add more asserts

    def test_parse_simple_function(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_simple_function.txt'), "r")
        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        self.assertEqual(len(pars.AST.children), 3) #TODO add more asserts

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
  
        res = parser.parse("3 * 2 + 4")
        self.assertEqual(res.type, "Plus")
        self.assertEqual(res.children[0].type, "Times")
        self.assertEqual(res.children[0].children[0].type, "Number")
        self.assertEqual(res.children[0].children[0].leaf, 3)
        self.assertEqual(res.children[0].children[1].type, "Number")
        self.assertEqual(res.children[0].children[1].leaf, 2)
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 4)

        res = parser.parse("Viking1.safe and Viking2.safe") #TODO add struct support
        self.assertEqual(res.type, "And")
        self.assertEqual(res.children[0].type, "Identifier")
        self.assertEqual(res.children[0].leaf, "Viking1")
        self.assertEqual(res.children[0].children[0].type, "Identifier")
        self.assertEqual(res.children[0].children[0].leaf, "safe")
        self.assertEqual(res.children[1].type, "Identifier")
        self.assertEqual(res.children[1].leaf, "Viking2")
        self.assertEqual(res.children[1].children[0].type, "Identifier")
        self.assertEqual(res.children[1].children[0].leaf, "safe")

        res = parser.parse(
            "Viking1.safe and Viking2.safe and Viking3.safe and Viking4.safe")
        self.assertEqual(res.type, "And")
        self.assertEqual(res.children[0].type, "And")
        self.assertEqual(res.children[1].type, "Identifier")
        self.assertEqual(res.children[1].leaf, "Viking4")
        self.assertEqual(res.children[1].children[0].type, "Identifier")
        self.assertEqual(res.children[1].children[0].leaf, "safe")

        self.assertEqual(res.children[0].children[0].type, "And")
        self.assertEqual(res.children[0].children[1].type, "Identifier")
        self.assertEqual(res.children[0].children[1].leaf, "Viking3")
        self.assertEqual(res.children[0].children[1].children[0].type, "Identifier")
        self.assertEqual(res.children[0].children[1].children[0].leaf, "safe")

        self.assertEqual(res.children[0].children[0].children[0].type, "Identifier")
        self.assertEqual(res.children[0].children[0].children[0].leaf, "Viking1")
        self.assertEqual(res.children[0].children[0].children[0].children[0].type, "Identifier")
        self.assertEqual(res.children[0].children[0].children[0].children[0].leaf, "safe")
        self.assertEqual(res.children[0].children[0].children[1].type, "Identifier")
        self.assertEqual(res.children[0].children[0].children[1].leaf, "Viking2")
        self.assertEqual(res.children[0].children[0].children[1].children[0].type, "Identifier")
        self.assertEqual(res.children[0].children[0].children[1].children[0].leaf, "safe")

        res = parser.parse("N - 1")
        self.assertEqual(res.type, "Minus") 
        self.assertEqual(res.children[0].type, "Identifier")
        self.assertEqual(res.children[0].leaf, 'N')
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 1)

        res = parser.parse("f() == 2")
        self.assertEqual(res.type, "Equal") 
        self.assertEqual(res.children[0].type, "FunctionCall")
        self.assertEqual(res.children[0].children[0].type, "Identifier")
        self.assertEqual(res.children[0].children[0].leaf, "f")
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 2)

    def test_parse_array_index_expression(self):
        parser = testParser(lexer.lexer)
        res = parser.parse("a[1] == 2")
        #parser = testParser(lexer.lexer)
        #res = pars.parse()
        #res.visit()
        self.assertEqual(res.type, "Equal") 
        self.assertEqual(res.children[0].type, "Identifier")
        self.assertEqual(res.children[0].children[0].type, "Index")
        self.assertEqual(res.children[0].children[0].leaf.type, "Number")
        self.assertEqual(res.children[0].children[0].leaf.leaf, 1)
        self.assertEqual(res.children[1].type, "Number")
        self.assertEqual(res.children[1].leaf, 2)

        #TODO, this is misparsed
        #res = parser.parse("N-1")
        #res.visit()
        #self.assertEqual(res.type, "Minus") 
        #self.assertEqual(res.children[0].type, "Identifier")
        #self.assertEqual(res.children[0].leaf, 'N')
        #self.assertEqual(res.children[1].type, "Number")
        #self.assertEqual(res.children[1].leaf, 1)

    def test_parse_extern(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_extern.txt'), "r")

        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        res = pars.AST.children

        #pars.AST.visit()

        declvisitor = parser.DeclVisitor(pars)

    def test_parse_extern_dbm(self):
        test_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'test_extern_dbm.txt'), "r")

        lex = lexer.lexer
        pars = parser.Parser(test_file.read(), lex)
        res = pars.AST.children

        #pars.AST.visit()

        declvisitor = parser.DeclVisitor(pars)
        #print declvisitor.variables

        self.assertEqual(len(declvisitor.variables), 5)

        self.assertEqual(declvisitor.variables[0], ('dbm', 'DBMFederation', []))
        self.assertEqual(declvisitor.variables[1], ('dbm.x', 'DBMClock', []))
        self.assertEqual(declvisitor.variables[2], ('dbm.c', 'DBMClock', []))
        self.assertEqual(declvisitor.variables[3][0], 'dbm.y') #('dbm.y', 'DBMClock', [10])
        self.assertEqual(declvisitor.variables[3][1], 'DBMClock')
        self.assertEqual(len(declvisitor.variables[3][2]), 1)
        self.assertEqual(declvisitor.variables[3][2][0].children[0].leaf, 10)
        self.assertEqual(declvisitor.variables[4][0], 'dbm.z') #('dbm.z', 'DBMClock', [10, 20])
        self.assertEqual(declvisitor.variables[4][1], 'DBMClock')
        self.assertEqual(len(declvisitor.variables[4][2]), 2)
        self.assertEqual(declvisitor.variables[4][2][0].children[0].leaf, 10)
        self.assertEqual(declvisitor.variables[4][2][1].children[0].leaf, 20)




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

    def parseIdentifierComplex(self):
        n = node.Node('Identifier', [], self.currentToken.value)
        self.accept('IDENTIFIER')
     
        p = n
        while self.currentToken.type == 'DOT':
            self.accept('DOT')
            element = node.Node('Identifier', [], self.currentToken.value)
            self.accept('IDENTIFIER')
            p.children = [element]
            p = element

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
