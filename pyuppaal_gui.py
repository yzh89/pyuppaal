#!/usr/bin/python
from pyuppaal import *
import goocanvas
import gtk
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
                                       visibility = goocanvas.ITEM_INVISIBLE)

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
        item.connect("button_press_event", on_transition_source_button_press)
        item.connect("button_release_event", on_transition_source_button_release)
        item.connect("motion_notify_event", on_transition_source_motion)
        item.connect("enter_notify_event", on_transition_source_enter)
        item.connect("leave_notify_event", on_transition_source_leave)

        if self.transition.guard:
            add_text(self.transition.guard, self.transition.guard_xpos, self.transition.guard_ypos, group)
    
        if self.transition.assignment:
            add_text(self.transition.assignment, self.transition.assignment_xpos, self.transition.assignment_ypos, group)

        if self.transition.synchronisation:
            add_text(self.transition.synchronisation, self.transition.synchronisation_xpos, self.transition.synchronisation_ypos, group)

        item = canvas.get_item(ellipse_target)
        item.connect("button_press_event", on_transition_target_button_press)
        item.connect("button_release_event", on_transition_target_button_release)
        item.connect("motion_notify_event", on_transition_target_motion)
    
        ellipse_source.set_data("group", group)
        ellipse_source.set_data("path", path)
        ellipse_target.set_data("group", group)
        ellipse_target.set_data("path", path)
        canvas.set_data(self.transition.id, group)
        # TODO lower path.lower(1)

# not really class functions
def on_transition_source_enter(item, target, event):
    tmp = item.get_model()
    tmp.set_property("visibility", goocanvas.ITEM_VISIBLE)

def on_transition_source_leave(item, target, event):
    tmp = item.get_model()
    tmp.set_property("visibility", goocanvas.ITEM_INVISIBLE)

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

def on_transition_source_button_press(item, target, event):
        return on_button_press(item, target, event)

def on_transition_source_button_release(item, target, event):
        return on_button_release(item, target, event)


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

def on_transition_target_button_press(item, target, event):
        return on_button_press(item, target, event)

def on_transition_target_button_release(item, target, event):
        return on_button_release(item, target, event)

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
 
# Not really class functions
       
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
    
def add_location_clicked (button, canvas):
    location = Location()
    LocationUI(location)

def add_path_clicked (button, canvas):
    transition = Transition()
    TransitionUI(transition)

def setup_canvas (canvas, nta):
    root = goocanvas.GroupModel ()

    canvas.set_root_item_model (root)
    for t in nta.templates:
        for l in t.locations:
            LocationUI(l, canvas)

    for t in nta.templates:
        for transition in t.transitions:
            TransitionUI(transition, canvas)

def create_pyuppaal_page (nta):

    canvas = goocanvas.Canvas ()
    vbox = gtk.VBox (False, 4)
    vbox.set_border_width (4)

    hbox = gtk.HBox (False, 4)
    vbox.pack_start (hbox, False, False, 0)

    w = gtk.Button ("Add Location")
    hbox.pack_start (w, False, False, 0)
    w.connect ("clicked", add_location_clicked, )

    w = gtk.Button ("Add Path")
    hbox.pack_start (w, False, False, 0)
    w.connect ("clicked", add_path_clicked, )

    scrolled_win = gtk.ScrolledWindow ()
    scrolled_win.set_shadow_type (gtk.SHADOW_IN)

    vbox.add (scrolled_win)

    canvas.set_size_request (700, 600)
    canvas.set_bounds (-500, -500, 500, 500)

    scrolled_win.add (canvas)

    setup_canvas (canvas, nta)

    return vbox

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

def create_window():
    nta = setup_nta ()
    v = create_pyuppaal_page(nta)

    w = gtk.Window ()
    w.connect ("destroy", gtk.main_quit)
    w.add (v)
    w.show_all ()
    
    return w

def main ():
    window = create_window ()
#    window = create_window ()
    
    gtk.main ()

if __name__ == "__main__":
    main()

# vim:ts=4:sw=4:expandtab
