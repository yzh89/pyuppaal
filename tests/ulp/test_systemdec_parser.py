#!/usr/bin/python
import sys
import os
import unittest
from pyuppaal.ulp import lexer
from pyuppaal.ulp.systemdec_parser import SystemDeclarationParser


class TestBasicParsing(unittest.TestCase):

    def test_parse_very_simple_systemdec(self):
        sysdec = """system Process;"""

        #lex = lexer.lexer
        pars = SystemDeclarationParser(sysdec)
        res = pars.parse()
        #res = pars.AST.children
        res.visit()

        self.assertEqual(res.type, 'SystemDec')
        self.assertEqual(len(res.children), 1)
        self.assertEqual(res.children[0].type, 'System')
        systemnode = res.children[0]
        self.assertEqual(len(systemnode.children), 1)
        self.assertEqual(systemnode.children[0].type, 'Identifier')
        self.assertEqual(systemnode.children[0].leaf, 'Process')

    def test_parse_simple_systemdec(self):
        sysdec = """// Place template instantiations here.
Process = Template();

// List one or more processes to be composed into a system.
system Process;"""

        pars = SystemDeclarationParser(sysdec)
        res = pars.parse()

        print "hephey"
        res.visit()

        self.assertEqual(res.type, 'SystemDec')
        self.assertEqual(len(res.children), 2)
        self.assertEqual(res.children[0].type, 'Assignment')
        self.assertEqual(res.children[0].leaf.type, 'Identifier')
        self.assertEqual(res.children[0].leaf.leaf, 'Process')
        self.assertEqual(len(res.children[0].children), 1)
        self.assertEqual(res.children[0].children[0].type, 'TemplateInstantiation')
        self.assertEqual(res.children[0].children[0].leaf.type, 'Identifier')
        self.assertEqual(res.children[0].children[0].leaf.leaf, 'Template')
        self.assertEqual(len(res.children[0].children[0].children), 0)

        self.assertEqual(res.children[1].type, 'System')
        systemnode = res.children[1]
        self.assertEqual(len(systemnode.children), 1)
        self.assertEqual(systemnode.children[0].type, 'Identifier')
        self.assertEqual(systemnode.children[0].leaf, 'Process')

    def test_parse_parameter_binding(self):
        sysdec = """//Insert process assignments.

N0 := Node(0,1);
N1 := Node(1,0);
N2 := Node(2,5);
N3 := Node(3,4);
N4 := Node(4,2);
N5 := Node(5,3);
N6 := Node(5,3,42, 47);


//Edit system definition.
system N0, N1, N2, N3, N4, N5;"""

        #lex = lexer.lexer
        pars = SystemDeclarationParser(sysdec)
        res = pars.parse()
        #res = pars.AST.children
        res.visit()

        self.assertEqual(res.type, 'SystemDec')
        self.assertEqual(len(res.children), 8)
        for i in range(0, 6):
            self.assertEqual(res.children[i].type, 'Assignment')
            self.assertEqual(res.children[i].leaf.type, 'Identifier')
            self.assertEqual(res.children[i].leaf.leaf, 'N' + str(i))
            self.assertEqual(len(res.children[i].children[0].children), 2)
            self.assertEqual(res.children[i].children[0].children[0].type, 'Number')
            self.assertEqual(res.children[i].children[0].children[1].type, 'Number')

        self.assertEqual(res.children[6].type, 'Assignment')
        self.assertEqual(res.children[6].leaf.type, 'Identifier')
        self.assertEqual(res.children[6].leaf.leaf, 'N6')
        self.assertEqual(res.children[6].children[0].type, 'TemplateInstantiation')
        self.assertEqual(len(res.children[6].children[0].children), 4)
        self.assertEqual(res.children[6].children[0].children[0].leaf, 5)
        self.assertEqual(res.children[6].children[0].children[1].leaf, 3)
        self.assertEqual(res.children[6].children[0].children[2].leaf, 42)
        self.assertEqual(res.children[6].children[0].children[3].leaf, 47)

        self.assertEqual(res.children[7].type, 'System')
        systemnode = res.children[7]
        self.assertEqual(len(systemnode.children), 6)
        for i in range(0, 6):
            self.assertEqual(systemnode.children[i].type, 'Identifier')
            self.assertEqual(systemnode.children[i].leaf, 'N' + str(i))



if __name__ == '__main__':
    unittest.main()
