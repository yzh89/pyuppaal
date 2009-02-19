#!/usr/bin/python
import sys
import os.path
projdir = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path = [projdir] + sys.path
from pyuppaal import *
import unittest
import os

class TestAPI(unittest.TestCase):
    def test_transition_create(self):
        l1 = Location()
        l2 = Location()
        t = Transition(l1, l2, guard="abemad")
        try:
            t = Transition(l1, l2, "abemad")
            self.fail("Should have raised exception")
        except TypeError:
            pass

    def test_label_append(self):
        l = Label("guard")
        self.assertEqual(l.get_value(), "")
        l.append("a==b")
        self.assertEqual(l.get_value(), "a==b")
        l.append("c==d")
        self.assertEqual(l.get_value(), "a==b,\nc==d")
        l.append("e==50")
        self.assertEqual(l.get_value(), "a==b,\nc==d,\ne==50")
        l.value = 'a==25'
        self.assertEqual(l.get_value(), "a==25")
        l.append('b==c', auto_newline=False)
        self.assertEqual(l.get_value(), "a==25,b==c")
        l = Label("guard")
        l.append('a==b')
        self.assertEqual(l.get_value(), "a==b")

if __name__ == '__main__':
    unittest.main()
