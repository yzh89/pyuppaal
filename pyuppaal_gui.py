#!/usr/bin/python

"""
    This program is a graphical user interface for pyuppaal. It uses goocanvas and 
    was initially inspired from examples included in the python bindings of goocanvas.

    Copyright (C) 2008 Andreas Engelbredt Dalsgaard <andreas.dalsgaard@gmail.com>
                       Mads Christian Olesen <mchro@cs.aau.dk>

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


import pyuppaal
from pyuppaal import *
import goocanvas
import gtk
import os
import gtk.glade
import math

class TemplateUI:
    def __init__(self, template, canvas):
        self.template = template

class TransitionUI:
    def __init__(self, transition, canvas):
        self.canvas = canvas
        self.root = canvas.get_root_item_model()
        self.transition = transition
        group = goocanvas.GroupModel (parent = self.root)
        ellipse_source = goocanvas.EllipseModel (parent = group,
                                       center_x = 0,
                                       center_y = 0,
                                       radius_x = 5,
                                       radius_y = 5,
                                       visibility = goocanvas.ITEM_INVISIBLE,
                                       pointer_events = goocanvas.EVENTS_ALL)
        x_source_p = get_locationNail_x_coordinate(self.transition.source, self.transition.target.xpos, self.transition.target.ypos, 25)
        y_source_p = get_locationNail_y_coordinate(self.transition.source, self.transition.target.xpos, self.transition.target.ypos, 25)
        x_target_p = get_locationNail_x_coordinate(self.transition.target, self.transition.source.xpos, self.transition.source.ypos, 25)
        y_target_p = get_locationNail_y_coordinate(self.transition.target, self.transition.source.xpos, self.transition.source.ypos, 25)

        path = goocanvas.PathModel(parent = group, data="M " + 
                    str(x_source_p)+" "+str(y_source_p)+
                    " L "+str(x_target_p)+" "+str(y_target_p))
        ellipse_target = goocanvas.EllipseModel (parent = group,
                                       center_x = 0,
                                       center_y = 0,
                                       radius_x = 5,
                                       radius_y = 5,
                                       visibility = goocanvas.ITEM_INVISIBLE,
                                       pointer_events = goocanvas.EVENTS_ALL)

        path.set_data("start_x", x_source_p)
        path.set_data("start_y", y_source_p)
        path.set_data("end_x", x_target_p)
        path.set_data("end_y", y_target_p)
	    
        x_source = get_locationNail_x_coordinate(self.transition.source, self.transition.target.xpos, self.transition.target.ypos, 25+2.5)
        y_source = get_locationNail_y_coordinate(self.transition.source, self.transition.target.xpos, self.transition.target.ypos, 25+2.5)
        x_target = get_locationNail_x_coordinate(self.transition.target, self.transition.source.xpos, self.transition.source.ypos, 25+2.5)
        y_target = get_locationNail_y_coordinate(self.transition.target, self.transition.source.xpos, self.transition.source.ypos, 25+2.5)
        ellipse_source.translate (x_source, y_source)
        ellipse_target.translate (x_target, y_target)

        item = canvas.get_item(ellipse_source)
        item.connect("button_press_event", on_transition_button_press)
        item.connect("button_release_event", on_transition_button_release)
        item.connect("motion_notify_event", on_transition_source_motion)
        item.connect("enter_notify_event", on_transition_enter)
        item.connect("leave_notify_event", on_transition_leave)

        if self.transition.guard:
            add_text(self.transition.guard, self.transition.guard_xpos, self.transition.guard_ypos, group)
    
        if self.transition.assignment:
            add_text(self.transition.assignment, self.transition.assignment_xpos, self.transition.assignment_ypos, group)

        if self.transition.synchronisation:
            add_text(self.transition.synchronisation, self.transition.synchronisation_xpos, self.transition.synchronisation_ypos, group)

        item = canvas.get_item(ellipse_target)
        item.connect("button_press_event", on_transition_button_press)
        item.connect("button_release_event", on_transition_button_release)
        item.connect("motion_notify_event", on_transition_target_motion)
        item.connect("enter_notify_event", on_transition_enter)
        item.connect("leave_notify_event", on_transition_leave)
    
        ellipse_source.set_data("group", group)
        ellipse_source.set_data("path", path)
        ellipse_target.set_data("group", group)
        ellipse_target.set_data("path", path)
        canvas.set_data(self.transition.id, group)
        # TODO lower path.lower(1)

# not class functions
def on_transition_enter(item, target, event):
    tmp = item.get_model()
    tmp.set_property("visibility", goocanvas.ITEM_VISIBLE)

def on_transition_leave(item, target, event):
    tmp = item.get_model()
    tmp.set_property("visibility", goocanvas.ITEM_INVISIBLE)

def on_transition_button_press(item, target, event):
        return on_button_press(item, target, event)

def on_transition_button_release(item, target, event):
        return on_button_release(item, target, event)

def on_transition_source_motion(item, target, event):
        if not event.state & gtk.gdk.BUTTON1_MASK:
            return False
        else:
            ellipse_source = item.get_model()
            path = ellipse_source.get_data("path")
            ellipse_source.translate(event.x, event.y)
            start_x = path.get_data("start_x")+event.x
            start_y = path.get_data("start_y")+event.y
            end_x = path.get_data("end_x")
            end_y = path.get_data("end_y")
            path.set_data("start_x", start_x)
            path.set_data("start_y", start_y)
            path.set_property("data", "M " + str(start_x)+" "+str(start_y)+" L "+str(end_x)+" "+str(end_y))
            return True

def on_transition_target_motion(item, target, event):
        if not event.state & gtk.gdk.BUTTON1_MASK:
            return False
        else:
            ellipse_target = item.get_model()
            path = ellipse_target.get_data("path")
            ellipse_target.translate(event.x, event.y)
            start_x = path.get_data("start_x")
            start_y = path.get_data("start_y")
            end_x = path.get_data("end_x")+event.x
            end_y = path.get_data("end_y")+event.y
            path.set_data("end_x", end_x)
            path.set_data("end_y", end_y)
            path.set_property("data", "M " + str(start_x)+" "+str(start_y)+" L "+str(end_x)+" "+str(end_y))
            return True

class LocationUI:
    def __init__(self, location, canvas):
        self.location = location
        self.canvas = canvas
        self.root = self.canvas.get_root_item_model()
   
        group = goocanvas.GroupModel (parent = self.root)
        ellipse = goocanvas.EllipseModel (parent = group,
                                       center_x = 0,
                                       center_y = 0,
                                       radius_x = 25,
                                       radius_y = 25,
                                       fill_color = "#204a87")
        ellipse.translate (location.xpos, location.ypos)
        ellipse.set_data("location", location)

        item = canvas.get_item(ellipse)
        item.connect("button_press_event", on_button_press)
        item.connect("button_release_event", on_button_release)
        item.connect("motion_notify_event", on_motion)

        if location.invariant:
            add_text(location.invariant, (location.invariant_xpos), (location.invariant_ypos), group)
    
        if location.name:
            add_text(location.name, (location.name_xpos), (location.name_ypos), group)

        ellipse.set_data("group", group)
        canvas.set_data(location.id, group)

def get_locationNail_x_coordinate(l, x1, y1, r):
        x0 = l.xpos
        y0 = l.ypos
        a = abs(y1-y0)
        b = abs(x1-x0)
        if b == 0:
            return x0

        if x1 > x0:
            return x0 + r * math.cos(math.atan(a/b))
        else:
            return x0 - r * math.cos(math.atan(a/b))
            

def get_locationNail_y_coordinate(l, x1, y1, r):
        x0 = l.xpos
        y0 = l.ypos
        a = abs(y1-y0)
        b = abs(x1-x0)
        if b == 0:
            if y1 > y0:
                return y0 + r
            else:
                return y0 - r

        if y1 > y0:
            return y0 + r * math.sin(math.atan(a/b))
        else:
            return y0 - r * math.sin(math.atan(a/b))
 
# Not class functions
def on_motion(item, target, event):
        canvas = item.get_canvas ()
        change = False
        if not event.state & gtk.gdk.BUTTON1_MASK:
            return False
        else:
            ellipse = item.get_model()
            location = ellipse.get_data("location")
            location.move_relative(event.x, event.y)
            group = ellipse.get_parent()
            group = ellipse.get_data("group")
            group.translate(event.x, event.y)
            return True

def on_button_press(item, target, event):
        fleur = gtk.gdk.Cursor(gtk.gdk.FLEUR)
        canvas = item.get_canvas ()
        canvas.pointer_grab(item, 
                            gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_RELEASE_MASK,
                            fleur, event.time)
        return True

def on_button_release(item, target, event):
        canvas = item.get_canvas ()
        canvas.pointer_ungrab(item, event.time)
        return True

def add_text(str, xpos, ypos, group):
   text = goocanvas.TextModel (parent = group,
                                 x = xpos,
                                   y = ypos,
                                  text = str)
   group.add_child(text, -1)

def setup_canvas (canvas, nta):
    root = goocanvas.GroupModel ()

    canvas.set_root_item_model (root)
    for t in nta.templates:
        for l in t.locations:
            LocationUI(l, canvas)

    for t in nta.templates:
        for transition in t.transitions:
            TransitionUI(transition, canvas)

def setup_nta():
    loc2 = Location("z < Max", True, "Location 2", "id", -100, -200)
    loc1 = Location()
    loc3 = Location()
    loc4 = Location()

    transitions = [
      Transition(loc1, loc2, guard='c1 < 10', assignment='c1 = 0'),
      Transition(loc1, loc3, guard='c1 >= 10', assignment='c1 = 0'),
      Transition(loc2, loc4),
      Transition(loc3, loc4),
    ]

    temp1 = Template("Template1", "",
     locations=[loc1, loc2, loc3, loc4],
     initlocation=loc1,
     transitions=transitions)
    temp1.layout()

    nta1 = NTA("clock c1;","Process = Template1(); system Process;",[temp1])
    return nta1

class MainWindow:

    def __init__(self):
        self.nta = setup_nta ()

        self.canvas = goocanvas.Canvas ()
        self.canvas.set_size_request (700, 600)
        self.canvas.set_bounds (-500, -500, 500, 500)
        setup_canvas (self.canvas, self.nta)
        self.canvas.add_events(gtk.gdk.SCROLL_MASK)
        #self.canvas.connect("button-release-event", self.on_canvas_button_release)
        self.canvas.connect("scroll-event", self.on_canvas_scroll_event)

        #Set the Glade file
        #TODO, find real path
        self.gladefile = os.path.join("data", "pyuppaal.glade")
        self.wTree = gtk.glade.XML(self.gladefile)

        self.mainWin = self.wTree.get_widget("mainWindow")
        self.mainWin.connect ("destroy", gtk.main_quit)

        self.wTree.get_widget("scrwWorkspace").add(self.canvas)

        self.wTree.signal_autoconnect(self)

        self.mainWin.show_all ()
        
    def on_canvas_scroll_event(self, widget, event):
        #CTRL-scrolling zooms
        if event.get_state() & gtk.gdk.CONTROL_MASK:
            if event.direction == gtk.gdk.SCROLL_DOWN:
                self.on_zoom_out()
                return True
            elif event.direction == gtk.gdk.SCROLL_UP:
                self.on_zoom_in()
                return True
            #unknown direction, let someone else handle it
        #SHIFT-scrolling scrolls left-right
        if event.get_state() & gtk.gdk.SHIFT_MASK:
            if event.direction == gtk.gdk.SCROLL_DOWN:
                event.direction = gtk.gdk.SCROLL_RIGHT
            if event.direction == gtk.gdk.SCROLL_UP:
                event.direction = gtk.gdk.SCROLL_LEFT
            

    def on_add_location(self, widget):
        location = Location()
        LocationUI(location, self.canvas)

    def on_add_transition(self, widget):
        transition = Transition()
        TransitionUI(transition, self.canvas)

    def on_quit(self, widget):
        gtk.main_quit()

    def on_save(self, widget):
        #TODO
        print("on_save called")

    def on_save_as(self, widget):
        file_save = gtk.FileChooserDialog(title="Save UPPAAL XML file", 
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(gtk.STOCK_CANCEL,
                        gtk.RESPONSE_CANCEL,
                        gtk.STOCK_SAVE,
                        gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("UPPAAL XML files")
        filter.add_pattern("*.xml")
        file_save.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        file_save.add_filter(filter)

        if file_save.run() == gtk.RESPONSE_OK:
            filename = file_save.get_filename()
            file_save.destroy()
        else:
            file_save.destroy()
            return

        if not filename.endswith(".xml") and not os.path.exists(filename):
            filename = filename + ".xml"
            
        filesock = open(filename, "w")
        filesock.write(self.nta.to_xml())
        filesock.close()
    
    def on_open(self, widget):
        file_open = gtk.FileChooserDialog(title="Open UPPAAL XML file", 
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,
                        gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OPEN,
                        gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("UPPAAL XML files")
        filter.add_pattern("*.xml")
        file_open.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        file_open.add_filter(filter)

        if file_open.run() == gtk.RESPONSE_OK:
            filename = file_open.get_filename()
            file_open.destroy()
        else:
            file_open.destroy()
            return
            
        filesock = open(filename, "r")
        self.nta = pyuppaal.from_xml(filesock)
        setup_canvas(self.canvas, self.nta)
        filesock.close()

    def on_zoom_in(self, widget=None):
        curscale = self.canvas.get_scale()
        self.canvas.set_scale(curscale+0.4)

    def on_zoom_out(self, widget=None):
        curscale = self.canvas.get_scale()
        self.canvas.set_scale(curscale-0.4)

    def on_zoom_normal(self, widget=None):
        self.canvas.set_scale(1.0)

def main ():
    window = MainWindow()
    
    gtk.main ()

if __name__ == "__main__":
    main()

# vim:ts=4:sw=4:expandtab
