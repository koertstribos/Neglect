from tkinter import *
from tkinter import ttk


#Variables that will be used as general settings

baseSize = (720, 50) #width, height

pad_y = 20 #y padding
pad_x = 20 #x padding
ipad_y = 3 #internal y padding
ipad_x = 3 #internal x padding

backgroundcolour = "lightblue" #background colour

#NeglectTKinterScreen class
#not for use as a standalone class
class _NeglectTKinterScreen():
    def __init__(self):
        self.root = Tk()
        self.root.title("Neglect App")
        self.root.configure(background=backgroundcolour)
        self.root.configure(width=baseSize[0], height=baseSize[1])

    #mainloop
    #start the mainloop of the tkinter window    
    def mainloop(self):
        self.root.mainloop()

