#!/usr/bin/python
from pyuppaal import *
import goocanvas
import gtk

root = goocanvas.GroupModel ()
canvas = goocanvas.Canvas ()

def move_ellipse_model(item, x, y):
    item.props.center_x = x
    item.props.center_y = y

def on_motion(item, target, event):
    canvas = item.get_canvas ()
    change = False
    if not event.state & gtk.gdk.BUTTON1_MASK:
        return False
    else:
        ellipse = item.get_model()
        location = ellipse.get_data("location")
        move_ellipse_model(canvas.get_data(location.id), event.x, event.y)
        location.move_relative(event.x, event.y)
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
    
def add_location_clicked (button):
    location = Location()
    add_from_location(location)

def add_path_clicked (button):
    global root

def add_from_location(location):
    global root, canvas    
    ellipse = goocanvas.EllipseModel (parent = root,
                                       center_x = 0,
                                       center_y = 0,
                                       radius_x = 25,
                                       radius_y = 25,
                                       fill_color = "blue")
    ellipse.translate (location.xpos*-1, location.ypos*-1)
    ellipse.set_data("location", location)

    canvas.set_data(location.id, ellipse)
    item = canvas.get_item(ellipse)
    item.connect("button_press_event", on_button_press)
    item.connect("button_release_event", on_button_release)
    item.connect("motion_notify_event", on_motion)

def add_from_transition(t):
    path = goocanvas.PathModel(parent = root, data="M " + 
                    str(t.source.xpos*-1)+" "+str(t.source.ypos*-1)+
                    " L "+str(t.target.xpos*-1)+" "+str(t.target.ypos*-1))

def setup_canvas (canvas, nta):
    global root

    canvas.set_root_item_model (root)
    for t in nta.templates:
        for l in t.locations:
            add_from_location(l)
		#TODO tegn rect

    for t in nta.templates:
        for t in t.transitions:
            add_from_transition(t)

def create_pyuppaal_page (nta):
    global canvas

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

    canvas.set_size_request (600, 450)
    canvas.set_bounds (0, 0, 1000, 1000)

    scrolled_win.add (canvas)

    setup_canvas (canvas, nta)

    return vbox

def setup_nta():
    loc1 = Location()
    loc2 = Location()
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
