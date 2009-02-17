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
            node.attr['label'] = l.invariant.replace('\n', '\\n')
        for t in self.transitions:
            if auto_nails:
                t.nails = []
            curnode = t.source
            for nextnode in t.nails + [t.target]:
                G.add_edge(curnode.id, nextnode.id, key=t.id)
                #add label to first segment
                if curnode == t.source:
                    edge = G.get_edge(curnode.id, nextnode.id)
                    edge.attr['label'] = t.guard.replace('\n', '\\n')+\
                        '\\n'+t.assignment.replace('\n', '\\n')
                curnode = nextnode
        G.layout(prog='dot')
        G.write('/tmp/test1.dot')

        for l in self.locations:
            (l.xpos, l.ypos) = map(self.dot2uppaalcoord, G.get_node(l.id).attr['pos'].split(','))
            (l.invariant_xpos, l.invariant_ypos) = (l.xpos, l.ypos + UPPAAL_LINEHEIGHT)
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

            (t.guard_xpos, t.guard_ypos) = map(self.dot2uppaalcoord, edge.attr['lp'].split(','))
            (t.assignment_xpos, t.assignment_ypos) = map(self.dot2uppaalcoord, edge.attr['lp'].split(','))
            t.assignment_ypos += UPPAAL_LINEHEIGHT
            (t.synchronisation_xpos, t.synchronisation_ypos) = map(self.dot2uppaalcoord, edge.attr['lp'].split(','))
            t.synchronisation_ypos += 2 * UPPAAL_LINEHEIGHT

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

class Location:
    def __init__(self, invariant="", committed=False, name="", id = "",
        xpos=0, ypos=0):
        self.invariant = invariant
        self.invariant_xpos = xpos
        self.invariant_ypos = ypos + 10
        self.committed = committed
        self.name = name
        self.name_xpos = xpos
        self.name_ypos = ypos + 20
        self.id = id
        self.xpos = xpos
        self.ypos = ypos

    def to_xml(self):
        namexml = ""
        invariantxml = ""
        if self.invariant != "":
            invariantxml = '<label kind="invariant" x="'+str(self.invariant_xpos)+'" y="'+str(self.invariant_ypos)+'">'+cgi.escape(self.invariant)+'</label>'
        if self.name != "":
            namexml = '<name x="'+str(self.name_xpos)+'" y="'+str(self.name_ypos)+'">'+self.name+'</name>'
        return """
    <location id="%s" x="%s" y="%s">
      %s
      %s
      %s
    </location>""" % (self.id, self.xpos, self.ypos, namexml, invariantxml,
        self.committed and '<committed />' or '')

    def move_relative(self, x, y):
        if self.invariant:
            self.invariant_xpos = self.invariant_xpos+x
            self.invariant_ypos = self.invariant_ypos+x

        if self.name:
            self.name_xpos = self.name_xpos+x
            self.name_ypos = self.name_ypos+x

        self.xpos = self.xpos+x
        self.ypos = self.ypos+y

class Branchpoint:
    def __init__(self, id = "", xpos=0, ypos=0):
        self.id = id
        self.xpos = xpos
        self.ypos = ypos
        self.invariant = ""

    def to_xml(self):
        return """
    <branchpoint id="%s" x="%s" y="%s" />""" % (self.id, self.xpos, self.ypos)


last_transition_id = 0
class Transition:
    def __init__(self, source, target, guard='', assignment='',
                    synchronisation=''):
        self.source = source
        self.target = target
        self.guard = guard
        self.assignment = assignment
        self.synchronisation = synchronisation
        self.nails = []
        self.guard_xpos = 0
        self.guard_ypos = 0

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
    </transition>""" % (self.source.id, self.target.id,
        self.guard_to_xml(), self.assignment_to_xml(),
        self.synchronisation_to_xml(),
        "\n".join(map(lambda x: x.to_xml(), self.nails))
        )

    def set_num_nails(self, num):
        self.nails = []
        for i in range(num):
            self.nails += [Nail()]

    def move_relative(self, x, y):
        if self.guard:
            self.guard_xpos = self.guard_xpos+x
            self.guard_ypos = self.guard_ypos+y

        if self.assignment:
            self.assignment_xpos = self.assignment_xpos+x
            self.assignment_ypos = self.assignment_ypos+y

        if self.synchronisation:
            self.synchronisation_xpos = self.synchronisation_xpos+x
            self.synchronisation_ypos = self.synchronisation_ypos+y

    def guard_to_xml(self):
        if self.guard:
            return '<label kind="guard" x="%s" y="%s">%s</label>' % \
                (self.guard_xpos, self.guard_ypos, cgi.escape(self.guard))
        return ''

    def assignment_to_xml(self):
        if self.assignment:
            return '<label kind="assignment" x="%s" y="%s">%s</label>' % \
                (self.assignment_xpos, self.assignment_ypos, cgi.escape(self.assignment))
        return ''

    def synchronisation_to_xml(self):
        if self.synchronisation:
            return '<label kind="synchronisation" x="%s" y="%s">%s</label>' % \
                (self.synchronisation_xpos, self.synchronisation_ypos, cgi.escape(self.synchronisation))
        return ''

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
    xmlsock.close()

    def getChildsByTagName(node, tagname):
        for cn in node.getchildren():
            if getattr(cn, 'tagName', '') == tagname:
                yield cn

    #ntaxml = xmldoc.getElementsByTagName("nta")[0]
    ntaxml = xmldoc
    system_declaration = ntaxml.findtext('declaration')
    system = ntaxml.findtext('system')
    templates = []
    for templatexml in ntaxml.getiterator("template"):
        locations = {}
        for locationxml in templatexml.getiterator("location"):
            name = locationxml.findtext("name")
            location = Location(id=locationxml.get('id'),
                xpos=int(locationxml.get('x', 0)),
                ypos=int(locationxml.get('y', 0)), name=name)
            if locationxml.find("committed") != None:
                location.committed = True
            for labelxml in locationxml.getiterator("label"):
                if labelxml.get('kind') == 'invariant':
                    location.invariant = labelxml.text
                    location.invariant_xpos = labelxml.get('x', 0)
                    location.invariant_ypos = labelxml.get('y', 0)

                #TODO other labels
            locations[location.id] = location
        for branchpointxml in templatexml.getiterator("branchpoint"):
            branchpoint = Branchpoint(id=branchpointxml.get('id'),
                xpos=int(branchpointxml.get('x', 0)),
                ypos=int(branchpointxml.get('y', 0)))
            locations[branchpoint.id] = branchpoint
        transitions = []
        for transitionxml in templatexml.getiterator("transition"):
            transition = Transition(
                locations[transitionxml.find('source').get('ref')],
                locations[transitionxml.find('target').get('ref')],
                )
            for labelxml in transitionxml.getiterator("label"):
                if labelxml.get('kind') == 'guard':
                    transition.guard = labelxml.text or ''
                    transition.guard_xpos = int(labelxml.get('x', 0) or 0)
                    transition.guard_ypos = int(labelxml.get('y', 0) or 0)
                if labelxml.get('kind') == 'assignment':
                    transition.assignment = labelxml.text
                    transition.assignment_xpos = int(labelxml.get('x', 0) or 0)
                    transition.assignment_ypos = int(labelxml.get('y', 0) or 0)
                if labelxml.get('kind') == 'synchronisation':
                    transition.synchronisation = labelxml.text
                    transition.synchronisation_xpos = int(labelxml.get('x', 0) or 0)
                    transition.synchronisation_ypos = int(labelxml.get('y', 0) or 0)
            for nailxml in transitionxml.getiterator("nail"):
                transition.nails += [
                    Nail(int(nailxml.get('x', 0) or 0), int(nailxml.get('y', 0) or 0))]
            transitions += [transition]

        declaration = templatexml.findtext("declaration")
        parameter = templatexml.findtext("parameter")

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

# vim:ts=4:sw=4:expandtab
