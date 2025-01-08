from Import.Experiment.Functions import *
import os
import random
from PIL import Image
from Import.Experiment.Text import Text
from Import.Browsers.BrowseLocations import *


#functions
#image dimensions
#source: GitHub Copilot
def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width, height

#TrialHandler class
#This class is used to handle trials in the experiment
class TrialHandler():
    def __init__(self):
        self.latestTrial = None
        self.blockNo = 0
        self.countedTrials = -1
        self.trials = []
        self.recycleableTrials = 6
        self._currentTrialValid = True
        self.saveCurrentTrial = True
        
    #SetTrials: set the trials for this block
    #args:
    #       trialNumbers:   numbers that refer to the different types of trials. E.g. use [0,1] for when 2 types of trials are available
    #       shuffle:        whether all trials presented in a shuffled order
    #       blockRepeat:   how many times each trial is repeated within the block
    #       
    #desc:
    #       The code fills self.trials with all numbers in trialNumbers blockRepeat times, and then shuffles if required.
    #returns:
    #       None     
    def SetTrials(self, trialNumbers, shuffle = False, blockRepeat = 1):
        self.trials = []
        for _ in range(blockRepeat):
            self.trials.extend(trialNumbers)
        if shuffle:
            random.shuffle(self.trials)

    #draw a trial from the stack
    #args:
    #       None
    #desc:
    #       draws the next trial from the pool if it exists. If no trials are left, the next trial handler or None is returned        
    #returns:
    #       a trialNumber,  which can refer to a type of trial (e.g. 0 or 1) when there are trials left in the pool
    # or    a trialHandler, which refers to a next set of trials when no trials are left in the pool and a next trialHandler has been specified
    # or    None,           which refers to no trials left and no trialHandlers left.        
    def DrawTrial(self):
        if len(self.trials) > 0:
            trial = self.trials.pop()
            self._currentTrialValid = True
            self.saveCurrentTrial = True
            self.latestTrial = trial
            self.countedTrials += 1
            return trial
        else:
            #if a next trial handler has been added, return that
            if hasattr(self, "nextTrialHandler"):
                return self.nextTrialHandler
            return None  # else return None
        
    #currentTrialIdentifier property
    #return the number of the current trial relative to all trials that have been shown
    #if current trial should not be saved, return None 
    @property
    def currentTrialIdentifier(self):
        if self.saveCurrentTrial:
            return self.countedTrials
        
        return None
    
    #currentTrialValid property
    #returns if the current trial is valid by checking if it is not None
    #current trial can be set to None by InvalidateTrial method
    @property
    def currentTrialValid(self):
        return self._currentTrialValid
    
    #InvalidateTrial method
    #invalidate the current trial, which puts the trial back at the end of the stack if the maximum amount of recycled trials has not been reached
    #also sets self.latestTrial to None
    #if this function is called a second time before drawing a new trial, 
    #       or the maximum amount of recycled trials has already been reached, 
    #       The trial is not pushed back to the end, but it is invalidated. .saveCurrentTrial is kept True
    def InvalidateTrial(self):
        if self.currentTrialValid:
            self._currentTrialValid = False
            
            if self.recycleableTrials>0:
                self.recycleableTrials -= 1
                self.trials.insert(0, self.latestTrial)
                self.latestTrial = None
                self.saveCurrentTrial = False

        
    #AppendNextTrialHandler method
    #append a next trial handler to this trial handler
    #useful for when two blocks have different behaviour or different trials (e.g. the peripheral and full hemisphere slideshows)
    def AppendNextTrialHandler(self, nextTrialHandler):
        self.nextTrialHandler = nextTrialHandler
        nextTrialHandler.blockNo = self.blockNo + 1
        

    #SetInitialisationDict method
    #is passed a number of keyword arguments, which is then saved to this TrialHandler
    #the dict can be obtained in the Experiment when needed    
    def SetInitialisationDict(self, kwargs):
        self._initialisationDict = kwargs
        
    #initialisationDict property
    #returns _initialisationDict if is has been set with SetInitialisationDict()    
    @property
    def initialisationDict(self):
        if hasattr(self, '_initialisationDict'):
            return self._initialisationDict
        else:
            print('no initialisation dict set for this trial handler')
            return None
        
#AllExperiments class
#container for all experiments
class AllExperiments():
    def __init__(self, moduleDict):
        
        #import all modules and save them in this object
        for key, item in moduleDict.items():
            setattr(self, key, item)
            
        self.experiments = []

    #Add method
    #add an experiment to the list of experiments
    #__init__ function of the experiment is called in this function, 
    #   so only the class of the experiment should be passed
    #   see PygazeExperiment.SubClasses 
    def Add(self, experimentClass):
        self.experiments.append(experimentClass())
    
    #RunExperiments method
    #runs all experiments
    #neatly handles pygaze stuff needed for the experiments
    def RunExperiments(self, onlineDataCollector):

        self.libtime.expstart()
        print("Running experiments!!")
        
        #make pygaze objects
        keyboard = self.libinput.Keyboard(keylist = ['space', 'escape', 'r'], timeout = None)
        log = self.liblog.Logfile()
        
        disp = self.libscreen.Display()
        tracker = self.eyetracker.EyeTracker(disp, trackertype = constants.TRACKERTYPE)

        try:
            tracker.calibrate()
        except Exception as e:
            print(f"calibration aborted: {e}")
            print("closing display and returning")
            disp.close()
            return
        
        tracker.start_recording()
        #run each experiment
        for exp in self.experiments:
            print("in for-loop, calling run experiment")
            #log start of experiment
            exp.RunExperiment(self, onlineDataCollector, tracker, disp, keyboard, log)
        #end the tracker connection etc
        tracker.stop_recording()
        #tracker.close()
        disp.close()
            
#base class for all experiments      
#not for standalone use        
class PygazeExperiment():
    def __init__(self):
        print("TkInterExperiment object created")

    #SubClasses method
    #returns the name and class of all available experiments
    #this is used to prompt the user about which experiments they want to run, as well as their order    
    @staticmethod
    def SubClasses():
        return {
                "Images": ImageExperiment,
                "Slideshow": SlideshowExperiment
            }
    
    #SubClassKey method
    #inverse of the dict returned by SubClasses()
    @staticmethod
    def SubClassKey(className):
        classes = PygazeExperiment.SubClasses()
        
        for key, value in classes.items():
            if value.__name__ == className:
                return key
            
        raise ValueError(f'Unkown experiment class: {className}')
        
    #GetSubclass method
    #returns the class of the experiment that is passed
    #the same as SubClasses()[experimentClass]
    @staticmethod
    def GetSubclass(experimentClass):
        classes = PygazeExperiment.SubClasses()
        
        if experimentClass in classes:
            return classes[experimentClass]
        else:
            raise ValueError(f'Unkown experiment type: {experimentClass}')
    
    #RunExperiment method
    #Run the experiment    
    def RunExperiment(self, AllExperiments, onlineDataCollector, tracker, disp, keyboard, log):
        #initialise objects and modules
        self.pygaze = AllExperiments
        self.onlineDataCollector = onlineDataCollector
        self.tracker = tracker
        self.disp = disp
        self.keyboard = keyboard
        self.log = log

        #call DefaultExperimentStart()
        print("Running experiment")
        self.DefaultExperimentStart()
        
        #finalise the experiment
        self.onlineDataCollector.StopCaching()
        self.onlineDataCollector.UnlinkGC()

    #dispSize property
    #return DISPSIZE, defined in constants.py  
    @property
    def dispSize(self):
        return self.pygaze.constants.DISPSIZE
    
    #refreshrate property
    #return SCREENREFRESHRATE, defined in constants.py
    @property
    def refreshrate(self):
        return self.pygaze.constants.SCREENREFRESHRATE
    
    #MakeTrialHandler method
    #makes a trialhandler object
    def MakeTrialHandler(self):
        return TrialHandler()
    
    #trialNumbers property
    #return a list of trial numbers
    #overwrite in inheriting classes
    @property
    def trialNumbers(self):
        return [0]
    
    #SetGCScreens method
    #populate the GazeContingency object with screens
    #overwrite in inheriting classes
    def SetGCScreens(self):
        raise Exception('unimplemented in this hierarchy level')
    
    #SetTrials method
    #set the trials for the experiment
    #overwrite in inheriting classes
    def SetTrials(self):
        raise Exception('unimplemented in this hierarchy level')

    #ScaleImage method
    #turn an image path into a PIL image that has been scaled to the screen size.
    #overwrite this in the peripheral SlideShow experiment to get the visual degrees just right
    def ScaleImage(self, imagePath):
        scales = self.GetImageScale(imagePath)
        #make a PIL image
        img = Image.open(imagePath)
        #resize the image
        img = img.resize((int(img.width*scales[0]), int(img.height*scales[1])))
        return img

    #GetImageScale method
    #get the scale that an image needs to be enlarged (or shrunk) by
    def GetImageScale(self, imagePath):
        #find the scale that the image needs to be enlarged (or shrunk) by
        #get image dimensions
        width, height = get_image_dimensions(imagePath)
        #get screen dimensions
        screenwidth, screenheight = self.dispSize
        #for both width and height, calculate the scale
        scales = [screenwidth/width, screenheight/height]
        #use the smallest scale
        return scales
    
    #DefaultExperimentStart method
    #more initialisation of the experiment
    def DefaultExperimentStart(self):
        #set some modules
        from Import.GazeContingency.GazeContingency import GazeContingency
        self.GazeContingency = GazeContingency
        from Import.GazeContingency.Screen import Screen, GIFScreen
        self.Screen = Screen
        self.GIFScreen = GIFScreen
        from Import.GazeContingency.Rule import Rule
        self.Rule = Rule

        #make trial handler
        self.trialHandler = self.MakeTrialHandler()
        
        #GazeContingency object is created here
        self.gc = GazeContingency(self.disp, self.tracker, self.keyboard, self.refreshrate)
        #OnlineDataCollector is linked to GazeContingency here
        self.onlineDataCollector.LinkGC(self.gc)

        #set text language
        self.txt = Text(self.pygaze.constants.LANGUAGE)
        
        #set trials
        self.SetTrials()

        #populate GC objects
        self.SetGCScreens()
        self.SetFixedRules()

        #start experiment
        self.SetScreenByTrialNo(self.trialHandler.DrawTrial())
        self.onlineDataCollector.StartCaching(constants.SAMPLINGRATE, self.imageTime)
        self.gc.Loop(self.pygaze.libtime, self.expStartScreen)
        #when gc.Loop returns, the experiment is over

    #SetFixedRules method
    #in this method, set rules that are the same for each sublcass
    def SetFixedRules(self):
    #rule 1: when 'r' is pressed, 
    #   When at screen 'interText', do recalibration
    #   When at a different screen, go to 'interText'  
        alwaysRuleRPress = self.Rule(20, lambda: self.gc.GetIfKey('r', reset="all"))
        def AlwaysRuleRCustomBehaviour():
            key = str(self.gc.screenCurrent)
            print(f'keypress R detected @ screen {key} doing the following:')
            if key == 'interText':
                self.tracker.log('Starting recalibration')
                self.onlineDataCollector.StopCaching()
                self.tracker.stop_recording()
                try:
                    self.tracker.calibrate()
                except:
                    print("calibration aborted")
                    self.gc.GotoScreen('ExpOver', final = True)
                self.tracker.start_recording()
                self.onlineDataCollector.ResumeCaching()
            else:
                self.gc.GotoScreen('interText')
                #no need to invalidate current trial, as we will repeat the same trial directly afterwards
                #and we will not be drawing a new trial from TrialHandler
                #so TrialHandler can stay in the same state
        self.gc.AddRule(AlwaysRuleRCustomBehaviour, alwaysRuleRPress)
        
    #rule 2: when 'escape' is pressed,
    #   When at screen 'interText', end experiment
    #   Else: Do nothing
        alwaysRuleEscPress = self.Rule(20, lambda: self.gc.GetIfKey('escape', reset = 'all'))

        def AlwaysRuleEscCustomBehaviour():
            key = str(self.gc.screenCurrent)
            print(f"keypress Esc detected @ screen {key}, doing the following:")
            if key == 'interText':
                self.gc.GotoScreen('ExpOver', final = True)
            else:
                print("no action")
        self.gc.AddRule(AlwaysRuleEscCustomBehaviour, alwaysRuleEscPress)
        
    #CustomBehaviour_GazeOnFixation_CacheBaseline method
    #Custom behaviour function for Caching a baseline and starting image presentation
    def CustomBehaviour_GazeOnFixation_CacheBaseline(self):
        #if not blinking at this moment
        if not self.gc.Blink():
            #tell OnlineDataCollector to cache the baseline and go to imageScreen
            self.onlineDataCollector.CacheBaseline(self.fixationTime)
            self.gc.GotoScreen('Image')
        
#ImageExperiment class
class ImageExperiment(PygazeExperiment):
    def __init__(self):
        super().__init__()
        self.shuffleTrials = False
        self.expStartScreen = 'interText'
        self.ImageFolder= "IMGSfreeview"
        self.interScreen_TextKey = "intro_Images"
        self.fixationTime = 1000 # ms
        self.imageTime = 7000 # ms
        

    #SetScreenByTrialNo method
    #sets the current 'Image' screen to the screen related to the trial number
    def SetScreenByTrialNo(self, trialNumber):
        print(f'going to screen: {trialNumber}')
        self.gc.AddScreen(self.screensViewImage[trialNumber], 'Image')
        
    #imagesFiles property
    #a list of paths leading to the stimuli    
    @property
    def imagesFiles(self):

        imgPath = os.path.join(Materials(), "Image_present", self.ImageFolder)
        images = [os.path.join(Materials(), "Image_present", self.ImageFolder, img) for img in os.listdir(imgPath)]
        return images 
        
    #SetTrials method
    #initialises the trials for the experiment, and passes the numbers to the TrialHandler
    def SetTrials(self):
        trialNumbers = []
        self.screensViewImage = {}

        for index, filename in enumerate(self.imagesFiles):
            screen = self.Screen(self.gc)
            
            screen.screen.draw_image(self.ScaleImage(filename))

            self.screensViewImage[index] = screen
            trialNumbers.append(index)
            
        self.trialHandler.SetTrials(trialNumbers, shuffle = self.shuffleTrials)
        
    #EndTrialCustomBehaviour method
    #custom behaviour for the end of a trial    
    def EndTrialCustomBehaviour(self):
        #finalise previous trial
        #save cached data
        self.onlineDataCollector.SaveToSessionInfo(self, self.trialHandler.currentTrialIdentifier, self.trialHandler.blockNo, "image")

        #draw new trial Number
        trialNo = self.trialHandler.DrawTrial()
        
        if trialNo == None:
            #experiment over
            print('experiment over')
            self.gc.GotoScreen('ExpOver', final = True)
        else:
            self.SetScreenByTrialNo(trialNo)
            self.gc.GotoScreen('FixationOff')
            
    #SetGCScreens method
    #populate the GazeContingency object with screens and their rules
    def SetGCScreens(self):
        #loading constants
        fixationLocation = self.pygaze.constants.SCREENMIDPOINT()
        intertime_GazepositionCheck = 5
        fixationTime = self.fixationTime
        imageTime = self.imageTime

        # # # # # # # # # # # # # # # # # # # #
        #set image screen
        ImageScreen = self.Screen(self.gc)
        self.gc.AddScreen(ImageScreen, 'Image')
        #image screen rules
        timeOverRule = self.Rule(5, lambda: self.gc.timeOnScreen >= imageTime)
        self.gc.AddRule(lambda: self.EndTrialCustomBehaviour(), timeOverRule, 'Image')
        

        # # # # # # # # # # # # # # # # # # # #
        # # # set interText screen # # #
        interBlockText = self.Screen(self.gc)
        interBlockText.screen.draw_text(self.txt[self.interScreen_TextKey], fontsize = 30)
        self.gc.AddScreen(interBlockText, 'interText')
        
        #interText screen rules
        #from interText to ITI when 'space' is pressed
        interTextSpace = self.Rule(1, lambda: self.gc.GetIfKey('space', reset="all"))
        self.gc.AddRule('FixationOff', interTextSpace, 'interText')
        
        # # # # # # # # # # # # # # # # # # # #
        #set fixation screen where gaze is Off the fixation point
        FixationOffScreen = self.Screen(self.gc)
        FixationOffScreen.screen.draw_fixation(fixtype='cross', pw=3, colour = 'lightgrey')
        self.gc.AddScreen(FixationOffScreen, 'FixationOff')
        #fixation screen rules
        
        fixGazeOnCheck = self.Rule(intertime_GazepositionCheck, 
                               lambda: CheckGazeElliptical_InterStimulus(fixationLocation,
                                                                     self.gc,
                                                                     constants.ELLIPSESIZE))
        
        self.gc.AddRule('FixationOn', fixGazeOnCheck, 'FixationOff')
        

        # # # # # # # # # # # # # # # # # # # #
        #Fixation screen gazeOn
        FixationOnScreen = self.Screen(self.gc)
        FixationOnScreen.screen.draw_fixation(fixtype='cross', pw=3, colour = 'lightgrey')
        self.gc.AddScreen(FixationOnScreen, 'FixationOn')
        #fixation screen rules
        fixGazeOffCheck = self.Rule(intertime_GazepositionCheck,
                               lambda: not CheckGazeElliptical_InterStimulus(fixationLocation,
                                                                     self.gc,
                                                                     constants.ELLIPSESIZE,))
        
        self.gc.AddRule('FixationOff', fixGazeOffCheck, 'FixationOn')
        
        fixGazeOnTimer = self.Rule(1, lambda: self.gc.timeOnScreen >= fixationTime)
        self.gc.AddRule(self.CustomBehaviour_GazeOnFixation_CacheBaseline, fixGazeOnTimer, 'FixationOn')
        
#SlideShowExperiment class
class SlideshowExperiment(PygazeExperiment):
    def __init__(self):
        self.shuffleTrials = True
        self.imageFolder_Block1 = "FullHemisphere"
        self.imageFolder_Block2 = "Peripheral"
        self.imageFolder = "IMGSblackwhite"
        self.extra_ITI = 1500 # ms
        self.expStartScreen = 'interText'
        self.interScreen_TextKey = 'intro_FullHemisphere'
        self.gazeContingencyFeedback_TextKey = 'feedback_Slidesow'
        self.fixationTime = 500 # ms
        self.imageTime = 2500 # ms
        self.feedbackTime = 1000 # ms
        super().__init__()

    #SetScreenByTrialNo method
    #sets the current 'Image' and 'ImageGazeOff' screens to the image related to the trial number
    def SetScreenByTrialNo(self, trialNumber):
        print(f'going to screen: {trialNumber}')
        self.gc.AddScreen(self.screensViewImage[trialNumber], 'Image')
        self.gc.AddScreen(self.screensFixateImage, 'ImageGazeOff')
        
    #imagesFiles_B1 property
    #a list of paths leading to the stimuli for block 1
    @property
    def imagesFiles_B1(self):
        return self.ImagesFiles(self.imageFolder_Block1)
    
    #imagesFiles_B2 property
    #a list of paths leading to the stimuli for block 2
    @property
    def imagesFiles_B2(self):
        return self.ImagesFiles(self.imageFolder_Block2)

    #dispSize property
    #the display size (scaled)
    @property
    def dispSize(self):
        return self.pygaze.constants.DISPSIZE_scaled

    #ImagesFiles Method
    #get all items at f"../../../Materials/Image_present/{self.ImageFolder}/{folder}"
    #return them as string which is passable to draw_image
    def ImagesFiles(self, folder):
        imgPath = os.path.join(Materials(), "Image_present", self.imageFolder, folder)
        return [os.path.join(Materials(), "Image_present", self.imageFolder, folder, img) for img in os.listdir(imgPath)]
        
    #NextBlock method
    #start the next block
    def NextBlock(self, trialHandler):
        for key, value in trialHandler.initialisationDict.items():
            setattr(self, key, value)

        interBlockText = self.Screen(self.gc)
        interBlockText.screen.draw_text(self.txt[self.interScreen_TextKey], fontsize = 30)
        self.gc.AddScreen(interBlockText, 'interText')
        
        self.gc.GotoScreen(self.expStartScreen)
        self.SetScreenByTrialNo(self.trialHandler.DrawTrial())
    
    #SetTrials method
    #Sets all trials for block 1 and block 2    
    def SetTrials(self):
        trialNumbers = []
        
        screenFix = self.Screen(self.gc)
        screenFix.screen.draw_text(text=self.txt[self.gazeContingencyFeedback_TextKey],  fontsize=30)
        self.screensFixateImage = screenFix
        self.screensViewImage = {}
        
        images = self.imagesFiles_B1
        for index, filename in enumerate(images):
            screen = self.Screen(self.gc)
            screen.screen.draw_image(self.ScaleImage(filename))
            screen.screen.draw_fixation(fixtype='cross', pw=3, colour = 'lightgrey')

            self.screensViewImage[index] = screen
            trialNumbers.append(index)
            
        self.trialHandler.SetTrials(trialNumbers, shuffle = self.shuffleTrials, blockRepeat=10)
        
        #also make a secondary trialHandler which will be used for the second block
        secondaryTrialHandler = self.MakeTrialHandler()
        self.trialHandler.AppendNextTrialHandler(secondaryTrialHandler)
        trialNumbers_2 = []
        images = self.imagesFiles_B2
        
        _screensViewImage = {}
        
        for index, filename in enumerate(images):
            screen = self.Screen(self.gc)
            screen.screen.draw_image(self.ScaleImage(filename))
            screen.screen.draw_fixation(fixtype='cross', pw=3, colour = 'lightgrey')
            
            _screensViewImage[index] = screen
            trialNumbers_2.append(index)
            
        secondaryTrialHandler.SetTrials(trialNumbers_2, shuffle = self.shuffleTrials, blockRepeat=10)
        secondaryTrialHandler.SetInitialisationDict({'screensViewImage': _screensViewImage,
                                                     'trialHandler': secondaryTrialHandler,
                                                     'interScreen_TextKey': 'intro_Peripheral'
                                                     })
        
    #EndTrialCustomBehaviour method
    #custom behaviour for the end of a trial
    def EndTrialCustomBehaviour(self):
        
        prevTrialValid = self.trialHandler.currentTrialValid

        #finalise previous trial
        #if the trial should be saved (it was valid, or invalid and not recycled):
        if self.trialHandler.saveCurrentTrial:
            #check if the trial was invalidated
            if not self.trialHandler.currentTrialValid:
                print("setting trial invalidation comment")
                self.onlineDataCollector.SetInvalidationComment()

            #get a string that represents the trial and block
            blockname = ['FullHemisphere', 'Peripheral'][self.trialHandler.blockNo]
            slidename = ['BlackWhite', 'WhiteBlack'][self.trialHandler.latestTrial]
            trialString = f"{blockname}_{slidename}"
            
            #get trial number 
            trialNo = self.trialHandler.currentTrialIdentifier
            
            #save cached data
            print(f"saving trial {trialString}")
            self.onlineDataCollector.SaveToSessionInfo(self, self.trialHandler.currentTrialIdentifier, self.trialHandler.blockNo, trialString)


        #draw new trial Number
        trialNo = self.trialHandler.DrawTrial()
        
        #if trialNo is None, the experiment is over
        if trialNo == None:
            #experiment over
            print('experiment over')
            self.gc.GotoScreen('ExpOver', final = True)
            
        #if trialNo is a new TrialHandler object, a new block is initialised
        elif isinstance(trialNo, TrialHandler):
            self.NextBlock(trialNo)
            
        #if previous trial was valid, set the next trial, and go to InterTrialInterval screen
        elif prevTrialValid:
            self.SetScreenByTrialNo(trialNo)
            self.gc.GotoScreen('ITI')
        #if previous trial was invalid, set the next trial, but first go to a feedback screen
        else:
            self.SetScreenByTrialNo(trialNo)
            self.gc.GotoScreen('ImageGazeOff')

    #CustomBehaviour_GazeOffImage method
    #custom behaviour for when gaze leaves the fixation (or blinktime is exceeded)        
    def CustomBehaviour_GazeOffImage(self):
        #invalidate trial.
        if self.trialHandler.currentTrialValid:
            self.trialHandler.InvalidateTrial()

    #CustomBehaviour_GazeOnFixation_CacheBaseline method
    #custom behaviour for starting a trial, 
    #also calls CacheBaseline method       
    def CustomBehaviour_GazeOnFixation_CacheBaseline(self):
        #tell OnlineDataCollector to cache the baseline
        self.onlineDataCollector.CacheBaseline(self.fixationTime)
        self.gc.GotoScreen('Image')
        
    #SetGCScreens method
    #populates the GazeContingency object with screens and rules   
    def SetGCScreens(self):
        
        fixationLocation = self.pygaze.constants.SCREENMIDPOINT()
        intertime_GazepositionCheck = 5
        fixationTime = self.fixationTime
        imageTime = self.imageTime
        allowedBlinkDuration = 500

        # # # # # # # # # # # # # # # # # # # #
        # # # Image screen # # # 
        ImageScreen = self.Screen(self.gc)
        self.gc.AddScreen(ImageScreen, 'Image')
        #image screen rules
        #from Image to CustomBehaviour_GazeOffImage when fix is OFF fixation or blink detected
        imgGazeOffCheck = self.Rule(intertime_GazepositionCheck, 
                                    lambda: not CheckGazeElliptical_DuringStimulus(fixationLocation,
                                                                     self.gc,
                                                                     constants.ELLIPSESIZE,
                                                                     allowedBlinkDuration=allowedBlinkDuration))
        
        self.gc.AddRule(lambda: self.CustomBehaviour_GazeOffImage(), imgGazeOffCheck, 'Image')
        
        #from Image to custom behaviour (next trial or exp over) on time > fixtime
        ImgTimeOver = self.Rule(1, lambda: self.gc.timeOnScreen >= imageTime)
        self.gc.AddRule(lambda: self.EndTrialCustomBehaviour(), ImgTimeOver, 'Image')
        
        # # # # # # # # # # # # # # # # # # # #
        # # # Image GazeOff screen # # # 
        ImageScreenGazeOff = self.Screen(self.gc)
        self.gc.AddScreen(ImageScreenGazeOff, 'ImageGazeOff')
        
        #Image GazeOff screen rules
        #from Image Off to ITI when spacebar is pressed
        feedbackSpacePress = self.Rule(1, lambda: self.gc.GetIfKey('space', reset="all"))
        
        self.gc.AddRule('ITI', feedbackSpacePress, 'ImageGazeOff')
        
        # # # # # # # # # # # # # # # # # # # #
        # # # set interText screen # # #
        interBlockText = self.Screen(self.gc)
        interBlockText.screen.draw_text(self.txt[self.interScreen_TextKey], fontsize = 30)
        self.gc.AddScreen(interBlockText, 'interText')
        
        #interText screen rules
        #from interText to ITI when 'space' is pressed
        interTextSpace = self.Rule(1, lambda: self.gc.GetIfKey('space', reset="all"))
        self.gc.AddRule('ITI', interTextSpace, 'interText')

        # # # # # # # # # # # # # # # # # # # #
        # # # set ITI screen # # #
        ITIScreen = self.GIFScreen(self.gc, BlinkingGIF_list(), frameRate = 15)
        #ITIScreen.screen.draw_fixation(fixtype='cross', pw=3, colour = 'lightgrey')
        self.gc.AddScreen(ITIScreen, 'ITI')
        
        #ITI screen rules
        #from ITI to FixationOff when time > extra_ITI
        ITITimeOver = self.Rule(1, lambda: self.gc.timeOnScreen >= self.extra_ITI)
        self.gc.AddRule('FixationOff', ITITimeOver, 'ITI')

        # # # # # # # # # # # # # # # # # # # #
        # # # set fixation gazeOff screen # # #
        FixationOffScreen = self.Screen(self.gc)
        FixationOffScreen.screen.draw_fixation(fixtype='cross', pw=3, colour = 'lightgrey')
        self.gc.AddScreen(FixationOffScreen, 'FixationOff')
        
        #fixation screen rules
        #from fixationOff to fixationOn when gaze is ON fixation
        fixGazeOnCheck = self.Rule(intertime_GazepositionCheck, 
                               lambda: CheckGazeElliptical_InterStimulus( fixationLocation,
                                                                self.gc,
                                                                constants.ELLIPSESIZE))
        
        self.gc.AddRule('FixationOn', fixGazeOnCheck, 'FixationOff')
        
        # # # # # # # # # # # # # # # # # # # #
        # # # set fixation gazeOn screen # # # 
        FixationOnScreen = self.Screen(self.gc)
        FixationOnScreen.screen.draw_fixation(fixtype='cross', pw=3, colour = 'lightgrey')
        self.gc.AddScreen(FixationOnScreen, 'FixationOn')
        #fixation screen rules
        #from fixationOn to fixationOff when gaze is OFF fixation
        fixGazeOffCheck = self.Rule(intertime_GazepositionCheck,
                               lambda: not CheckGazeElliptical_InterStimulus(    fixationLocation,
                                                                    self.gc,
                                                                    constants.ELLIPSESIZE))
        
        self.gc.AddRule('FixationOff', fixGazeOffCheck, 'FixationOn')
        
        fixGazeOnTimer = self.Rule(1, lambda: self.gc.timeOnScreen >= fixationTime)
        self.gc.AddRule(self.CustomBehaviour_GazeOnFixation_CacheBaseline, fixGazeOnTimer, 'FixationOn')


        

            
        
