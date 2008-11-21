#!/usr/bin/python
import pyuppaal
import sys

file = open(sys.argv[1])

nta = pyuppaal.from_xml(file)

for template in nta.templates:
    template.layout(auto_nails=True)

file = open(sys.argv[2], 'w')
file.write(nta.to_xml())

# vim:ts=4:sw=4:expandtab
