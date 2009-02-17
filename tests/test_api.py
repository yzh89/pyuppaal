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

if __name__ == '__main__':
    unittest.main()
