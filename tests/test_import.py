#!/usr/bin/python
import sys
import os.path
projdir = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path = [projdir] + sys.path
import pyuppaal
import unittest
import os

class TestMinimalImport(unittest.TestCase):
    def test_import_minimal(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'minimal.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(len(nta.templates), 1)
        self.assertEqual(len(nta.templates[0].locations), 1)
        self.assertEqual(len(nta.templates[0].transitions), 0)
        self.assertEqual(nta.templates[0].locations[0].xpos, 16)
        self.assertEqual(nta.templates[0].locations[0].ypos, -40)
        self.assertTrue(nta.templates[0].locations[0] == nta.templates[0].initlocation)
        self.assertEqual(nta.declaration, '// Place global declarations here.\n')
        self.assertEqual(nta.system, """// Place template instantiations here.
Process = Template();

// List one or more processes to be composed into a system.
system Process;""")

    def test_import_small(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'small.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(len(nta.templates), 1)
        self.assertEqual(len(nta.templates[0].locations), 2)
        self.assertEqual(len(nta.templates[0].transitions), 1)
        self.assertEqual(nta.templates[0].locations[1].committed, True)

#    def test_import_petur_boegholm(self):
#        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'petur_boegholm_testcase.xml'))
#        nta = pyuppaal.from_xml(file)
#        self.assertEqual(len(nta.templates), 20)
#        schedulerTemplate = nta.templates[0]
#        self.assertEqual(schedulerTemplate.name, 'Scheduler')
#        self.assertEqual(len(schedulerTemplate.locations), 4)
#        self.assertEqual(len(schedulerTemplate.transitions), 6)
#        schedulerTemplate.layout()
#        for template in nta.templates:
#            print "Layouting ", template.name
#            template.layout()

    def test_import_petur_boegholm_minimal(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'petur_boegholm_testcase_minimal.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(len(nta.templates), 1)
        schedulerTemplate = nta.templates[0]
        self.assertEqual(schedulerTemplate.name, 'Scheduler')
        self.assertEqual(len(schedulerTemplate.locations), 4)
        self.assertEqual(len(schedulerTemplate.transitions), 6)
        schedulerTemplate.layout(auto_nails=True)

    def test_import_template_parameter_minimal(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'parameter_minimal.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(len(nta.templates), 1)
        self.assertEqual(nta.templates[0].parameter, 'int id')

    def test_import_minimal_noinitlocation(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'noinit_minimal.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(nta.templates[0].initlocation, None)

    def test_import_minimal_name(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'minimal_name.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(nta.templates[0].initlocation.name, "abemad")

    def test_import_strangeguard(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'strangeguard.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(nta.templates[0].transitions[0].guard, "")
        self.assertEqual(nta.templates[0].transitions[0].guard_xpos, -44)
        self.assertEqual(nta.templates[0].transitions[0].guard_ypos, -10)

    def test_import_noxypos(self):
        file = open(os.path.join(os.path.dirname(sys.argv[0]), 'location_no_xypos.xml'))
        nta = pyuppaal.from_xml(file)
        self.assertEqual(nta.templates[0].locations[0].xpos, 0)
        self.assertEqual(nta.templates[0].locations[0].ypos, 0)

if __name__ == '__main__':
    unittest.main()
