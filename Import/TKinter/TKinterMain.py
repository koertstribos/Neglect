import Import.TKinter.TKinterBase as tkb
from tkinter import *


#_Main class
#not for standalone use
#This class defines some behaviour of the main screen. See main.py for usage example
class _Main(tkb._NeglectTKinterScreen):
    #subs is a list of NeglectTKinterSubScreen objects
    #each sub object will be added to the main screen
    def __init__(self, subs):
        super().__init__()
        self._subs = subs
        self._passivesubs = []
        self._activesub = None

        #initialise subs from this object
        for index, sub in enumerate(self._subs):
            self._AddSub(sub, index)

    #_AddSub
    #set the sub reference to this obj
    #pack the Start button from each sub
    #args:
    #   sub: _Sub object (see TKinterSub.py)
    #   index: int
    #returns:
    #   None        
    def _AddSub(self, sub, index):
        sub.AddMain(self)
        button = sub.startButton
        button.grid(row = 0, column = index,
                    padx = tkb.pad_x, pady = tkb.pad_y, 
                    ipadx = tkb.ipad_x, ipady = tkb.ipad_y,
                    sticky = "nsew")


#NeglectTKinterMainScreen class
#This class is for the main screen of the application        
class NeglectTKinterMainScreen(_Main):
    #subs is a list of NeglectTKinterSubScreen objects
    #each sub object will be added to the main screen (see _Main)
    def __init__(self, subs):
        super().__init__(subs)
        self._DataControlWidgets = []

    #RefreshDataControlWidgetGrid
    #Function for refreshing the data control widget grid
    #args:
    #   newWidgets: list of Widgets
    #returns:
    #   None    
    def RefreshDataControlWidgetGrid(self, newWidgets):
        for wid in self._DataControlWidgets:
            wid.grid_forget()

        self._DataControlWidgets = newWidgets
        for index, wid in enumerate(newWidgets):
            wid.grid(row = 1,
                        column = index,
                        sticky = "ns")

    #RemoveActivesub
    #Function for removing the current active screen
    #If another screen was active before the current screen, it will be made active again
    #returns:
    #   None        
    def RemoveActivesub(self):
        self._activesub._RemoveSelf()
        if len(self._passivesubs) > 0:
            self._activesub = self._passivesubs.pop()
        else:
            pass

    #StackSub
    #Function for stacking a new screen
    #stack a new screen, save the active screen
    #args:
    #   sub: _Sub object (see TKinterSubs.py)
    #returns:
    #   None    
    def StackSub(self, sub):
        print(f"stacking {sub}")
        #save the current active sub if it exists
        if self._activesub != None:
            self._passivesubs.append(self._activesub)

        #set the new sub to be the active sub, and call the new sub to show itself
        self._activesub = sub
        self._activesub._ShowSelf()
