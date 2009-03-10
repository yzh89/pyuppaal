#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
    Copyright (C) 2008 Mads Christian Olesen <mchro@cs.aau.dk>
                       Andreas Engelbredt Dalsgaard <andreas.dalsgaard@gmail.com>
                       Arild Martin Møller Haugstad <arild@cs.aau.dk>

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

import pygraphviz
import cgi
import xml.etree.cElementTree as ElementTree
import subprocess
import re

def require_keyword_args(num_unnamed):
    """Decorator s.t. a function's named arguments cannot be used unnamed"""
    def real_decorator(fn):
        def check_call(*args, **kwargs):
            if len(args) > num_unnamed:
                raise TypeError("%s should be called with only %s unnamed arguments" 
                    % (fn, num_unnamed))
            return fn(*args, **kwargs)
        return check_call
    return real_decorator

UPPAAL_LINEHEIGHT = 15
class NTA:
    def __init__(self, declaration="", system="", templates=[]):
        self.declaration = declaration
        self.system = system
        self.templates = templates

    def add_template(self, t):
        if not t in self.templates:
            self.templates += [t]

    def to_xml(self):
        templatesxml = ""
        for t in self.templates:
            templatesxml += t.to_xml() + "\n"
        return """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC "-//Uppaal Team//DTD Flat System 1.1//EN" "http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd">
<nta>
  <declaration>%s</declaration>
  %s
  <system>%s</system>
</nta>""" % (cgi.escape(self.declaration), templatesxml, cgi.escape(self.system))

class Template:
    def __init__(self, name, declaration="", locations=[], initlocation=None, transitions=[], parameter=None):
        self.name = name
        self.declaration = declaration
        self.locations = locations
        self.transitions = transitions
        self.initlocation = initlocation
        self.parameter = parameter

    def assign_ids(self):
        i = 0
        for l in self.locations:
            l.oldid = getattr(l, 'id', None)
            l.id = 'id' + str(i)
            i = i + 1

    def dot2uppaalcoord(self, coord):
        return int(-int(coord)*1.5)

    def layout(self, auto_nails=False):
        self.assign_ids()

        G = pygraphviz.AGraph(strict=False)
        for l in self.locations:
            #TODO: initial node should be the first (dot will place it at the top then)
            G.add_node(l.id)
            node = G.get_node(l.id)
            node.attr['label'] = l.invariant.get_value().replace('\n', '\\n')
        for t in self.transitions:
            if auto_nails:
                t.nails = []
            curnode = t.source
            for nextnode in t.nails + [t.target]:
                G.add_edge(curnode.id, nextnode.id, key=t.id)
                #add label to first segment
                if curnode == t.source:
                    edge = G.get_edge(curnode.id, nextnode.id)
                    label = '';
                    for a in [t.select, t.guard, t.synchronisation, t.assignment]:
                        if a.get_value() != None:
                            label += a.get_value().replace('\n', '\\n')+'\\n'
                    if len(label) > 0:
                        label = label[0:len(label)-2]
                    edge.attr['label'] = label
                curnode = nextnode
        G.layout(prog='dot')
        G.write('/tmp/test1.dot')

        for l in self.locations:
            (l.xpos, l.ypos) = map(self.dot2uppaalcoord, G.get_node(l.id).attr['pos'].split(','))
            (l.name.xpos, l.name.ypos) = (l.xpos, l.ypos + UPPAAL_LINEHEIGHT)
            (l.invariant.xpos, l.invariant.ypos) = (l.xpos, l.ypos + 2 * UPPAAL_LINEHEIGHT)
        for t in self.transitions:
            #for nail in t.nails:
            #    nailnode = G.get_node(nail.id)
            #    (nail.xpos, nail.ypos) = map(self.dot2uppaalcoord, nailnode.attr['pos'].split(','))
            #    curnode = nail

            #first segment
            edge = G.get_edge(t.source.id, (t.nails + [t.target])[0].id, key=t.id)
            if auto_nails:
                t.nails = []
                for nailpos in edge.attr['pos'].split(" "):
                    xpos, ypos = map(self.dot2uppaalcoord, nailpos.split(","))
                    t.nails += [Nail(xpos, ypos)]

            ydelta = 0
            for a in ['select', 'guard', 'synchronisation', 'assignment']:
                label = getattr(t, a)
                if label.get_value() != None:
                    (x, y) = map(self.dot2uppaalcoord, edge.attr['lp'].split(','))
                    label.xpos = x
                    label.ypos = y+ydelta
                    ydelta += UPPAAL_LINEHEIGHT

    def _parameter_to_xml(self):
        if self.parameter:
            return '<parameter>%s</parameter>' % (cgi.escape(self.parameter))
        return ""

    def to_xml(self):
        return """  <template>
    <name x="5" y="5">%s</name>
    %s
    <declaration>%s</declaration>
    %s
    %s
    <init ref="%s" />
    %s
  </template>""" % (self.name, 
    self._parameter_to_xml(),
    cgi.escape(self.declaration),
    "\n".join([l.to_xml() for l in self.locations if isinstance(l, Location)]),
    "\n".join([l.to_xml() for l in self.locations if isinstance(l, Branchpoint)]),
    self.initlocation.id,
    "\n".join([l.to_xml() for l in self.transitions]))

class Label:
    def __init__(self, kind, value=None, xpos=None, ypos=None):
        self.kind = kind
        self.value = value
        self.xpos = xpos
        self.ypos = ypos

    def get_value(self):
        if self.value:
            return self.value
        return ""

    def append(self, expr, auto_newline=True):
        nl = auto_newline and '\n' or ''
        if self.get_value():
            self.value = self.get_value() + "," + nl + expr
        else:
            self.value = expr
            

    def move_relative(self, dx, dy):
        self.xpos += dx
        self.ypos += dy

    def to_xml(self):
        if self.value:
            attrs = ['kind="%s"' % self.kind]
            if self.xpos:
                attrs += ['x="%s"' % self.xpos]
            if self.ypos:
                attrs += ['y="%s"' % self.ypos]

            #special case for location names
            if self.kind == 'name':
                return '<name %s>%s</name>' % \
                    (" ".join(attrs[1:]), cgi.escape(self.value))
            else:
                return '<label %s>%s</label>' % \
                    (" ".join(attrs), cgi.escape(self.value))
        return ''

class Location:
    @require_keyword_args(1)
    def __init__(self, invariant=None, committed=False, name=None, id = None,
        xpos=0, ypos=0):
        self.invariant = Label("invariant", invariant)
        self.committed = committed
        self.name = Label("name", name)
        self.id = id
        self.xpos = xpos
        self.ypos = ypos

    def move_relative(self, dx, dy):
        self.xpos += dx
        self.ypos += dy
        for l in [self.invariant, self.name]:
            l.move_relative(dx, dy)

    def to_xml(self):
        namexml = self.name.to_xml()
        invariantxml = self.invariant.to_xml()
        return """
    <location id="%s" x="%s" y="%s">
      %s
      %s
      %s
    </location>""" % (self.id, self.xpos, self.ypos, namexml, invariantxml,
        self.committed and '<committed />' or '')

class Branchpoint:
    @require_keyword_args(1)
    def __init__(self, id=None, xpos=0, ypos=0):
        self.id = id
        self.xpos = xpos
        self.ypos = ypos

    def to_xml(self):
        return """
    <branchpoint id="%s" x="%s" y="%s" />""" % (self.id, self.xpos, self.ypos)


last_transition_id = 0
class Transition:
    @require_keyword_args(3)
    def __init__(self, source, target, select='', guard='', synchronisation='',
                    assignment=''):
        self.source = source
        self.target = target
        self.select = Label("select", select)
        self.guard = Label("guard", guard)
        self.synchronisation = Label("synchronisation", synchronisation)
        self.assignment = Label("assignment", assignment)
        self.nails = []

        global last_transition_id
        self.id = 'Transition' + str(last_transition_id)
        last_transition_id = last_transition_id + 1

    def to_xml(self):
        return """
    <transition>
      <source ref="%s" />
      <target ref="%s" />
      %s
      %s
      %s
      %s
      %s
    </transition>""" % (self.source.id, self.target.id,
        self.select.to_xml(), self.guard.to_xml(),
        self.synchronisation.to_xml(), self.assignment.to_xml(),
        "\n".join(map(lambda x: x.to_xml(), self.nails))
        )

    def set_num_nails(self, num):
        self.nails = []
        for i in range(num):
            self.nails += [Nail()]

last_nail_id = 0
class Nail:
    def __init__(self, xpos=0, ypos=0):
        global last_nail_id
        self.id = 'Nail' + str(last_nail_id)
        last_nail_id = last_nail_id + 1
        self.xpos = xpos
        self.ypos = ypos

    def to_xml(self):
        return """
    <nail x="%s" y="%s" />""" % \
            (self.xpos, self.ypos)

def from_xml(xmlsock):
    xmldoc = ElementTree.ElementTree(file=xmlsock).getroot()

    def int_or_none(text):
        if text != None:
            return int(text)
        return None

    #ntaxml = xmldoc.getElementsByTagName("nta")[0]
    ntaxml = xmldoc
    system_declaration = ntaxml.findtext('declaration') or ""
    system = ntaxml.findtext('system') or ""
    templates = []
    for templatexml in ntaxml.getiterator("template"):
        locations = {}
        for locationxml in templatexml.getiterator("location"):
            name = locationxml.findtext("name")
            location = Location(id=locationxml.get('id'),
                xpos=int(locationxml.get('x', 0)),
                ypos=int(locationxml.get('y', 0)), name=name)
            namexml = locationxml.find('name')
            if namexml != None:
                (location.name.xpos, location.name.ypos) = \
                    (int_or_none(namexml.get('x', None)),
                    int_or_none(namexml.get('y', None))
                    )
            if locationxml.find("committed") != None:
                location.committed = True
            for labelxml in locationxml.getiterator("label"):
                if labelxml.get('kind') == 'invariant':
                    location.invariant = Label("invariant", labelxml.text)
                    location.invariant.xpos = int_or_none(labelxml.get('x', None))
                    location.invariant.ypos = int_or_none(labelxml.get('y', None))

                #TODO other labels
            locations[location.id] = location
        for branchpointxml in templatexml.getiterator("branchpoint"):
            branchpoint = Branchpoint(id=branchpointxml.get('id'),
                xpos=int_or_none(branchpointxml.get('x', None)),
                ypos=int_or_none(branchpointxml.get('y', None)))
            locations[branchpoint.id] = branchpoint
        transitions = []
        for transitionxml in templatexml.getiterator("transition"):
            transition = Transition(
                locations[transitionxml.find('source').get('ref')],
                locations[transitionxml.find('target').get('ref')],
                )
            for labelxml in transitionxml.getiterator("label"):
                if labelxml.get('kind') in ['select', 'guard', 'assignment', 
                                            'synchronisation']:
                    label = getattr(transition, labelxml.get('kind'))
                    label.value = labelxml.text
                    label.xpos = int_or_none(labelxml.get('x', None))
                    label.ypos = int_or_none(labelxml.get('y', None))
            for nailxml in transitionxml.getiterator("nail"):
                transition.nails += [
                    Nail(int_or_none(nailxml.get('x', None)), 
                        int_or_none(nailxml.get('y', None)))]
            transitions += [transition]

        declaration = templatexml.findtext("declaration") or ""
        parameter = templatexml.findtext("parameter") or ""

        if templatexml.find("init") != None:
            initlocation=locations[templatexml.find("init").get('ref')]
        else:
            initlocation = None
        template = Template(templatexml.find("name").text,
            declaration,
            locations.values(),
            initlocation=initlocation,
            transitions=transitions,
            parameter=parameter)
        templates += [template]    
        
    nta = NTA(system_declaration, system, templates)
    return nta

class QueryFile:
    def __init__(self):
        self.queries = []

    def addQuery(self, q, comment=''):
        self.queries += [(q, comment)]

    def saveFile(self, fh):
        out = ['//This file was generated from pyUppaal'] + \
            ['/*\n' + comment + '*/\n' + q for (q, comment) in self.queries]
        fh.write("\n\n".join(out))

def verify(modelfilename, queryfilename, verifyta='verifyta',
            searchorder='bfs'):
    searchorder = { 'bfs': '0', #Breadth first
                    'dfs': '1', #Depth first
                    'rdfs': '2', #Random depth first
                    'ofs': '3', #Optimal first
                    'rodfs': '4', #Random optimal depth first
                    'tfs': '6', #Target first
                    }[searchorder]

    proc = subprocess.Popen(
        [verifyta, '-o' + searchorder, '-q', modelfilename, queryfilename], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #TODO - report progress
    (stdoutdata, stderrdata) = proc.communicate()

    lines = stdoutdata.split('\n')

    regex = re.compile('^Verifying property ([0-9]+) at line ')
    res = []
    lastprop = None
    for line in lines:
        match = regex.match(line)
        if lastprop:
            if line.endswith(' -- Property is satisfied.'):
                res += [True]
            elif line.endswith(' -- Property is NOT satisfied.'):
                res += [False]
            else:
                pass #Ignore garbage
            lastprop = None
        elif match:
            lastprop = int(match.group(1))
    return res

# vim:ts=4:sw=4:expandtab
