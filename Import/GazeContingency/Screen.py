from pygaze import libscreen

#Screen class
#contains a libscreen.Screen, as well as a list of rules and commands
class Screen():
    #constructor
    #args:
    #   gazeContingency: GazeContingency object
    #   screen: libscreen.Screen object OR string
    def __init__(self, gazeContingency, screen = None):
        if isinstance(screen, libscreen.Screen):
            self.screen = screen
        elif isinstance(screen, str):
            self.screen = libscreen.Screen()
            self.screen.draw_text(text=screen, fontsize=24)
        else:
            self.screen = libscreen.Screen()
        self.Rules = []
        self.Commands = []
        self.GC = gazeContingency

    #AddRule method
    #adds a rule
    #args:
    #   rule: Rule object
    #   target: name of the Screen that the experiment goes to when rule evaluates true
    #   customBehaviour: instead of screen name, callable that is executed when rule evaluates true    
    def AddRule(self, rule, target, customBehaviour = None):
        self.Rules.append([rule,target,customBehaviour])

    #CallRules method
    #calls all the rules added using AddRule    
    #args:
    #   frameStart: int, representing the time in ms relative in the experiment where the frame is started
    #returns:
    #   None    
    def CallRules(self, frameStart):
        #this can be farbettered
        #as currently, each rule checks if they need to be evaluated using frameStart
        #however, if we would sort the rules by interval, we would only need to check each interval
        for rule, tar, cust in self.Rules:
            if rule.Evaluate(frameStart):
                if cust is None:
                    if isinstance(tar, str):
                        return self.GC.GotoScreen(tar)
                    else:
                        tar()
                else:
                    cust()

    #unused? 
    #CallCommands method
    #calls all commands       
    #returns:
    #   None         
    def CallCommands(self):
        for com in self.Commands:
            com()
            
    #__str__ method
    #returns the key of self used in the GazeContingency object
    def __str__(self):
        return self.GC.ScreenKey(self)

    #ReplaceScreen method
    #replaces the libscreen.Screen coupled to a GC Screen
    #useful for looping over multiple trials with the same rules (e.g. different stimuli)
    #args:
    #       screen: GazeContingency.Screen object OR libscreen.Screen object OR string
    def ReplaceScreen(self, screen):
        if isinstance(screen, Screen):
            self.screen = screen.screen
        elif isinstance(screen, libscreen.Screen):
            self.screen = screen
        elif isinstance(screen, str):
            stringScreen = libscreen.Screen()
            stringScreen.draw_text(text=screen, fontsize = 24)
            self.screen = stringScreen
        else:
            raise Exception(f"{screen} is not a GazeContingency Screen, Pygaze.libscreen Screen, or string ")
        
#GIFScreen class
#a screen that contains a looping GIF         
class GIFScreen(Screen):
    #constructor
    #args:
    #   gazeContingency: GazeContingency object
    #   imagesList: list of images to be displayed in the GIF, passable to pygaze.libscreen
    def __init__(self, gazeContingency, imagesList, frameRate = 15):
        self.frameRate = frameRate
        self.frameTime = 1000/self.frameRate
        self.GIF_startTime = None
        self.frameIndex = 0
        self.frameTimeList = [t*self.frameTime for t in range(len(imagesList))]
        self.GIF_duration = self.frameTime * (len(imagesList))
        self._screens = []
        for img in imagesList:
            _screen = libscreen.Screen()
            _screen.draw_image(img)
            self._screens.append(_screen)
            

        super().__init__(gazeContingency, self._screens[0])

    #_UpdateGIF method
    #called from CallRules
    #updates the GIF based on the frame time    
    #args:
    #   frameStart: int, representing the time in ms relative to the experiment start    
    def _UpdateGIF(self, frameStart):
    #use frameStart to calculate if GIF needs updating
        if self.GIF_startTime == None:
            self.GIF_startTime = frameStart
        
        #if the GIF has been on screen longer than its loop duration, increase GIF_startTime by increments of GIF_duration
        while self.GIF_startTime + self.GIF_duration < frameStart:
            self.GIF_startTime += self.GIF_duration

        #choose new frame
        self.frameIndex = 0
        while not (self.GIF_startTime + (self.frameIndex + 1) * self.frameTime > frameStart): #increment frame nr until a frame is chosen that would
            self.frameIndex += 1
            if self.frameIndex >= len(self._screens):
                print("error in GIFScreen._UpdateGIF: index out of range")
                self.frameIndex = 0
                break

        #set new frame
        self.screen = self._screens[self.frameIndex]
        self.GC.disp.fill(self.screen)
        self.GC.disp.show()
        
    #CallRules method
    #calls the rules of the base object, and updates the GIF
    #args:
    #   frameStart: int, representing the time in ms relative to the experiment start        
    def CallRules(self, frameStart):
        self._UpdateGIF(frameStart)
        super().CallRules(frameStart)
            

        
