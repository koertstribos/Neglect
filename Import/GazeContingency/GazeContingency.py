from __future__ import annotations
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import libinput
from pygaze import eyetracker
from typing import Callable
from Import.GazeContingency.Screen import Screen
from Import.GazeContingency.Rule import Rule

#GazeContingency class
#This class is used to create a gaze-contingent experiment
class GazeContingency:
    def __init__(self, display: libscreen.Display, eyetracker: eyetracker.EyeTracker, keyboard: libinput.Keyboard, framerate, copy_libinput_Keyboard_defaultkeys = True):

        self.disp = display
        self.track = eyetracker
        self.keyb = keyboard
        self.loop = True
        
        self.timeOnScreen = 0
        self.blinkOnScreen = 0
        self.framerate = framerate
        self.frameTime = 1000/framerate

        self.screens = {}
        self.screenCurrent = None

        self.rules = []
        self.keysToCheck = []
        if copy_libinput_Keyboard_defaultkeys:
            for key in self.keyb.klist:
                print(f"adding {key} to GazeContingency.keysToCheck")
                self.keysToCheck.append(key)
        self.keys = []

    #SetKeysCheck method
    #sets a list of keys to check     
    def SetKeysCheck(self, keylist):
        self.keysToCheck = keylist

    #AddKeyCheck method
    #adds a key that needs to be checked
    def AddKeyCheck(self, key):
        self.keysToCheck.append(key)

    #GetLastKey method
    #returns the last pressed key    
    def GetLastKey(self):
        return(self.keys[-1])

    #_Flush method
    #resets all relevant keys
    def _Flush(self, key, target):
        if target == 'all':
            self.keys = []
        elif target =="self":
            while key in self.keys:
                self.keys.remove(key)

    #GetIfKey method
    #args:
    #      keys:    string or list of strings representing keys that are to be checked
    #            
    #      reset:   'self': resets found key on find
    #               'all':  resets all keys on find
    #               'none:  doesn't reset keys on find
    #               *   :   doesn't reset keys on find
    #returns:
    #       True if a key in self.keys has been pressed
    #       False if no key from self.keys has been pressed          
    def GetIfKey(self, keys, reset = "self"):
        #ensure keys is a list
        if isinstance(keys, str):
            keys = [keys]
        # check if all keys are in self.keystocheck
        for key in keys:
            if not key in self.keysToCheck:
                print(f"looking whether {key} has been pressed, but this key is not being saved on press.")
                print("please use GazeContingency.SetKeysCheck, or GazeContingency.AddKeyCheck()")

        return self._GetIfKey(keys, reset)

    #_GetIfKey method
    #returns whether a key in keys has been pressed
    #also calls _Flush for the first key that has been found
    #_Flush resets either the found key, all keys, or no keys
    #args:
    #       keys:   list of keys to check
    #       reset:  string indicating whether to reset the found key, or all keys
    #               'self': resets found key on find
    #               'all':  resets all keys on find
    #               'none:  doesn't reset keys on find
    #               *   :   doesn't reset keys on find
    #returns:
    #   True if a key in keys has been pressed

    def _GetIfKey(self, keys, reset):
        for key in keys:
            if key in self.keys:
                print(f"detected key {key}, flushing {reset}")
                self._Flush(key, reset)
                return True
        return False

    #GetKeylist method
    #returns a list of keys that have been pressed
    #args:
    #       flipped:    True: flip the list of keys before returning
    #returns:
    #       list of keys that have been pressed
    def GetKeylist(self, flipped=True):
        if not flipped:
            return self.keys
        else:
            fkeys = []
            for key in self.keys:
                fkeys.insert(0, key)
            return fkeys

    #Loop method
    #starts the experiment by going to the starting screen
    #then, loops untill GoToScreen() is called with final=True)    
    #args:
    #   libTime: PyGaze libtime object
    #   startingScreen: string referring to the first screen
    #returns:
    #   None    
    def Loop(self, libTime, startingScreen):
        self.GotoScreen(startingScreen)

        startTime = libTime.get_time()
        frameStart = startTime
        while(self.loop):

            frameStart = libTime.get_time()
            self.CallRules(frameStart)

            frameTime = libTime.get_time() - frameStart

            if frameTime > self.frameTime:
                self.IncrTime(frameTime)

            else:
                libTime.pause(self.frameTime - frameTime)
                self.IncrTime(self.frameTime)

    #IncrTime method
    #increases the timer for how long this screen has been active
    #increases the blink timer for this screen if necessary       
    #args:
    #   time: int, the amount of time that is added to the clock
    #returns:
    #   None     
    def IncrTime(self, time):
        self.timeOnScreen += time
        if self.Blink():
            self.blinkOnScreen += time
            
    #Blink method
    #returns:
    #   True is blink is detected at this moment
    #   False otherwise        
       
    def Blink(self):
        if hasattr(self.track, "blinking"):
            #print(f"found blinking-variable in tracker, which presumably only happens in dummy mode. Returning {self.track.blinking}")
            return self.track.blinking
        
        return self.track.pupil_size()<=0
    
    #BlinkTimeOver method
    #return True if the user blinked for more than the specified time in this screen
    #args:
    #   time: int, the time that is checked against the blink timer
    #returns:
    #   True if the user blinked for more than the specified time in this screen
    #   False otherwise
    def BlinkTimeOver(self, time):
        return self.blinkOnScreen >= time
        
    #AddScreen method
    #function for adding a screen. 
    #args:
    #   screen:     PyGaze.libscreen.Screen object
    #   screentype: string
    #               key that refers to the screen
    #returns:
    #   None
    def AddScreen(self, screen, screentype):
        if screentype in self.screens:
            self.screens[screentype].ReplaceScreen(screen)
        else:
            if isinstance(screen, libscreen.Screen):
                self.screens[screentype] = Screen(self, screen)

            elif isinstance(screen, str):
                self.screens[screentype] = Screen(self, screen)
            else:
                try:
                    self.screens[screentype] = screen 
                except: Exception(f"{screen} is not a GazeContingency Screen, Pygaze.libscreen Screen, or string ")
    

    #AddRule function
    #function for adding rules
    #args:
    #   target_screen_or_command:   dict key for the Screen that is switched to on succesful result of rule evaluation 
    #                               OR callable function that is called on succesful result of rule evaluation 
    #   when_rule:                  Rule object, containing a function that is evaluated as rule
    #   at_screen:                  Reference to the screen on which this rule is to be evaluated.
    #                               if at_screen=='any', the rule is evaluated every frame regardless of Screen
    #returns:
    #   None            
    def AddRule(self, target_screen_or_command, when_rule, at_screen='any'):
        rule = when_rule
        target = target_screen_or_command
        screenType = at_screen

        if isinstance(screenType, str):
            if screenType == 'any':
                self.rules.append([rule, target])
            elif screenType in self.screens:
                self.screens[screenType].AddRule(rule, target)

        else:
            Exception("AddRule")

    #CallRules method
    #calls all rules coupled to any screen and the current active screen
    #also, fetch keypresses
    #args:
    #   time: int representing the current time of the experiment in ms
    #returns:
    #   None        
    def CallRules(self, time):
        #fetch keypress
        key = self.keyb.get_key(keylist=self.keysToCheck, timeout=1)[0]
        if key != None:
            self.keys.append(key)

        #call all rules coupled to the GC obj
        for rule, target in self.rules:
            if rule.Evaluate(time):
                if isinstance(target, str):
                    self.GotoScreen(target)
                if isinstance(target, Callable):
                    target()
        #call all rules coupled to the current screen      
        self.screenCurrent.CallRules(time)


    #Screen method
    #function for getting a Screen object, even if it does not exist
    #args:
    #   screenType: string, or Screen object
    #returns:
    #   a Screen object from the list of screens, or a new basic screen    
    def Screen(self, screenType):
        if screenType in self.screens:
            return self.screens[screenType]
        else:
            try:
                tempScreen = libscreen.Screen()
                tempScreen.draw_text(text=f"{screenType}", fontsize=24)
                return Screen(self, tempScreen)
            except:
                tempScreen = libscreen.Screen()
                print("GazeContingency.Screen error")
                tempScreen.draw_text(text=f"error: {screenType} is not a string", fontsize=24)
                return Screen(self, tempScreen)

    #GotoScreen method
    #Get the experiment to go to a specific screen
    #args:
    #       screenType: String that contains the reference to the screen defined in AddScreen
    #       final:      Bool that represents whether the experiment is over
    #returns:
    #   None        
    def GotoScreen(self, screenType: str, final = False):
        if final:
            self.loop = False
            return

        self.track.log("S: showing screen %s" % screenType)
        self.timeOnScreen = 0
        self.blinkOnScreen = 0
        self.screenCurrent = self.Screen(screenType)
        self.disp.fill(self.screenCurrent.screen)
        self.disp.show()
        #flush all keys
        self._Flush(None, 'all')

    #ReturnScreenString method
    #returns the key that links to a Screen object in self.screens 
    #args:
    #   screen: Screen object
    #returns:
    #   a string that references to the Screen object in self.screens
    #   or None if no matching Screen object exists    
    def ReturnScreenString(self, screen):
        for key, value in self.screens.items():
            if value == screen:
                return key

    #CurrentScreenKey method
    #returns the key of the Screen which is currently active
    #returns:
    #   a string referencing the currently active Screen  
    def CurrentScreenKey(self):
        return self.ScreenKey(self.screenCurrent)
        
    #ScreenKey method
    #returns the key of a given Scren
    #args:
    #   screen: Screen object
    #returns:
    #   a string referencing the given Screen object
    #   or "no screen" if the Screen object is not found
    def ScreenKey(self, screen):
        for key, Screen in self.screens.items():
            if Screen == screen:
                return key
        else:
            return "no screen"

    #__str__ method
    #returns a string describing of the object
    def __str__(self):
        return("GazeContingency Object")

    #__repr__ method
    #returns a string representation of the object
    def __repr__(self):
        return(f"GazeContingency Object @ screen {self.CurrentScreenKey()}")
