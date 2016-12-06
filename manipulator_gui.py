'''
Software to control SM-10 micromanipulator controller

Tkinter:
http://apprendre-python.com/page-tkinter-interface-graphique-python-tutoriel
http://fsincere.free.fr/isn/python/cours_python_tkinter.php
'''
from Tkinter import *
import tkFileDialog
from devices import *
from numpy import array, zeros
import pickle

ndevices = 2
#dev = LuigsNeumann_SM10()
dev = Device()
microscope = VirtualDevice(dev, [7,8,9])
manip = [VirtualDevice(dev, [1,2,3]),
         VirtualDevice(dev, [4,5,6])]
transformed = [Manipulator(manip[i]) for i in range(2)]

print "Device initialized"

window = Tk()
window.title('Manipulator')

device_name = ['Left','Right']

class DeviceFrame(LabelFrame):
    '''
    A named frame that displays device coordinates
    '''
    def __init__(self, master = None, cnf = {}, dev = None, **kw):
        LabelFrame.__init__(self, master, cnf, **kw)

        self.dev = dev # device
        self.coordinate = [0,0,0]
        self.coordinate_text = [StringVar(), StringVar(), StringVar()]
        self.refresh_coordinates()
        self.coordinate_label = [None, None, None]
        #for j in range(3):
        #    self.coordinate_label[j] = Label(self, textvariable = self.coordinate_text[j])
        #    self.coordinate_label[j].pack()

        self.coordinate_label[0] = Spinbox(self, from_=-50000, to=50000, increment=10, textvariable=self.coordinate_text[0], command=lambda: self.move(0))
        self.coordinate_label[0].pack()
        self.coordinate_label[1] = Spinbox(self, from_=-50000, to=50000, increment=10, textvariable=self.coordinate_text[1], command=lambda: self.move(1))
        self.coordinate_label[1].pack()
        self.coordinate_label[2] = Spinbox(self, from_=-50000, to=50000, increment=10, textvariable=self.coordinate_text[2], command=lambda: self.move(2))
        self.coordinate_label[2].pack()


    def refresh_coordinates(self):
        for i in range(3):
            self.coordinate[i] = self.dev.position(i)
            self.coordinate_text[i].set(self.coordinate[i]) #"{:7.1f}".format(self.coordinate[i]))# + " um")
            #self.coordinate_text[i].set("{:7.1f}".format(self.coordinate[i]) + " um")

    def move(self, j):
        self.dev.move(float(self.coordinate_text[j].get()), axis = j)

class TransformedFrame(Frame):
    '''
    A named frame that displays device coordinates
    '''
    def __init__(self, master = None, cnf = {}, dev = None, **kw):
        Frame.__init__(self, master, cnf, **kw)

        self.dev = dev # device
        self.coordinate = [0,0,0]
        self.coordinate_text = [StringVar(), StringVar(), StringVar()]
        self.refresh_coordinates()
        self.coordinate_label = [None, None, None]
        for j in range(3):
            self.coordinate_label[j] = Label(self, textvariable = self.coordinate_text[j])
            self.coordinate_label[j].pack()

    def refresh_coordinates(self):
        self.dev.update()
        for i in range(3):
            self.coordinate[i] = self.dev.position(i)
            self.coordinate_text[i].set("{:7.1f}".format(self.coordinate[i]) + " um")

frame_microscope = DeviceFrame(window, text = 'Microscope', dev = microscope)
#frame_microscope.pack(side=LEFT, padx=10, pady=10)
frame_microscope.grid(row=1, column = 0, padx = 5, pady = 5)

def move_manip():
    x = array([microscope.position(i) for i in range(3)])
    transformed[0].move(x)

locked = False

def lock_manip():
    # Lock the manipulator to the camera view
    # Should be a check
    global locked_position

    if locked[0].get():
        transformed[0].update()
        x = array([microscope.position(i) for i in range(3)])
        locked_position = transformed[0].position() - x
        print "locked at",locked_position

go_command = [move_manip, window.quit]
lock_command = [lock_manip, window.quit]

frame_manipulator = []
frame_transformed = []
go_button = []
cancel_button = []
locked = [IntVar(), IntVar()]
for i in range(ndevices):
    frame_manipulator.append(DeviceFrame(window, text = device_name[i], dev = manip[i]))
    frame_manipulator[i].grid(row=0, column = i+1, padx = 5, pady = 5) #pack(side=LEFT, padx=10, pady=10)
    frame_transformed.append(TransformedFrame(window, dev=transformed[i]))
    frame_transformed[i].grid(row=1, column=i + 1, padx = 5, pady = 5)  # pack(side=LEFT, padx=10, pady=10)
    go_button = Button(window, text="Go", command=go_command[i])
    go_button.grid(row = 2, column = i+1)
    cancel_button = Button(window, text="Withdraw", command=window.quit)
    cancel_button.grid(row = 3, column = i+1)
    lock_button = Checkbutton(window, text="Locked", variable = locked[i], command=lock_command[i])
    lock_button.grid(row=4, column=i + 1)

status_text=StringVar(value = "Move pipette to center")
status = Label(window, textvariable = status_text)
status.grid(row = 5, column = 0, columnspan = 3, pady = 30)

n = 0
x = zeros((4,3))
y = zeros((4,3))

def pipette_moved():
    global n, old_position
    # Store positions
    x[n] = array([microscope.position(i) for i in range(3)])
    transformed[0].update()
    y[n] = transformed[0].y
    # Move to new axis
    if n<3:
        old_position = manip[0].position(axis = n)
        manip[0].move(old_position + 500.,axis = n) # relative move
    n+= 1
    if n == 4: # Done
        transformed[0].calibrate(x,y)
        microscope.move(x[0])
        manip[0].move(y[0])
        # Save configuration
        cfg = {'x' : x, 'y' : y}
        pickle.dump(cfg, open("config.cfg","wb"))


OK_button = Button(window, text="OK", command=pipette_moved)
OK_button.grid(row = 6, column = 0, columnspan = 3, padx = 5, pady = 5)

cfg = pickle.load(open("config.cfg","rb"))
x = cfg['x']
y = cfg['y']
transformed[0].calibrate(x,y)

def refresh():
    global locked_position
    frame_microscope.refresh_coordinates()
    for i in range(ndevices):
        frame_manipulator[i].refresh_coordinates()
        frame_transformed[i].refresh_coordinates()
    if locked[0].get():
        # manipulator 1 is locked to the camera view
        x = array([microscope.position(i) for i in range(3)])
        transformed[0].move(x+locked_position)


    window.after(500, refresh)

window.after(500, refresh)

"""
microscope.move(0, axis = 0)
microscope.move(0, 1)
microscope.move(0, 2)
"""
window.mainloop()
