#this file contains all the data instances that are used in the program
#Each class in this file defines the final information needed to define the saved data
#See DataInstanceTypes.py for higher-order class definitions

from Import.SessionData.DataInstanceTypes import *
from Import.Experiment.Experiment import PygazeExperiment
import os
import Import.Experiment.Text as txt
from Import.Browsers.BrowseLocations import *
from screeninfo import get_monitors
from math import e, sqrt, pi
import tkinter as tk

# # # # patient stuff # # # #

#Name of the participant
    #can be a full name, or only initials
class Alias(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "participant alias: "
        self._question = "an alias that refers to the patient."

#current age
    #Number, open answer, rounded to multiple of 5
class CurrentAge(RoundedInt):
    def __init__(self):
        super().__init__(rounding = 5)
        self._printHeader = "Age (+/-2.5): "
        self._question = "the current age of the participant."

class TimePostInjury(Int):
    def __init__(self):
        super().__init__()
        self._printHeader = "Time post injury (months): "
        self._question = "the time since the last injury in months"
        
#Language in which the instructions are given to the participant
    #Option, defined by the languages that are available according to the Text module
class PresentationLanguage(Option):
    def __init__(self):
        super().__init__(None)
        self._printHeader = "Language of instructions: "
        self._question = "the language in which the instructions are given to the participant."
    
    @property    
    def _options(self):
        return txt.Text.languageOptions()

#sex
    #Option_specifyOther, m/f/other
class Sex(Option_specifyOther):
    def __init__(self):
        super().__init__(options = ["male", "female", "other"])
        self._printHeader = "Sex: "
        self._question = "the sex of the participant."

#handedness
    #Option_specifyOther, l/r/other
class Handedness(Option_specifyOther):
    def __init__(self):
        super().__init__(options = ["right", "left"])
        self._printHeader = "Handedness: "
        self._question = "the handedness of the participant."

#Previous brain damage
    #Option, yes/no/unknown
class PreviousBrainDamage(Option):
    def __init__(self):
        super().__init__(options = ["no", "yes", "unknown"])
        self._printHeader = "Previous brain damage: "
        self._question = "whether the patient had brain damage before the last occurence"

#known hemianopia?
    #Option, yes/no
class Hemianopia(Option):
    def __init__(self):
        super().__init__(options = ["no", "yes"])
        self._printHeader = "Known hemianopia: "
        self._question = "whether the patients has (been diagnosed with) hemianopia"

#previous test enumeration
    #Enumeration, any number
class PreviousTestsCount(Enumerate):
    def __init__(self):
        super().__init__(PreviousTests)
        self._printHeader = "Amount of previously taken tests: "
        self._question = "The amount of previously taken tests"

#previous test set
    #Multiple
class PreviousTests(Multiple):
    def __init__(self):
        previousTestSet = [PreviousTestName,PreviousTestScore ,PreviousTestTimePostInjury ,PreviousTestObservations]
        super().__init__(subDataInstanceClasses = previousTestSet)
        self._printHeader = "Previous test: "
        self._question = "Multiple questions concerning each previously taken test"
        
#previous test name
    #Text
class PreviousTestName(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "test name: "
        self._question = "the name of a previous test"
        
#previous test score
    #Text
class PreviousTestScore(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "test score: "
        self._question = "the score of the previous test"
        
#previous test year
    #Number, unrounded?
class PreviousTestTimePostInjury(Int):
    def __init__(self):
        super().__init__()
        self._printHeader = "previous test time after injury (months): "
        self._question = "Months after injury that the previous test was taken"
        
#previous test observations
    #Text
class PreviousTestObservations(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "test observation: "
        self._question = "additional observations from the previous test"

#patient comments
    #text
class PatientComments(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "Comment on patient: "
        self._question = "comments on the patient: "

# # # # damage stuff (patient)
#type of brain damage
    #Text
class DamageType(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "Type of damage: "
        self._question = "the type of damage from which the patient suffered (stroke/ablation/etc.)"

#hemispheres/location of brain damage
    #Text
class DamageLocation(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "Location of damage: "
        self._question = "the location of the damage (brain area)"

#affected artery/vessel
    #Text
class DamagedVessel(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "Damaged vessels/arteries: "
        self._question = "the affected vessels/arteries (if known)"
    
#damage comments
    #Text
class DamageComment(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "Comments on damage: "
        self._question = "comments on the damage"

# # # # setup stuff # # # #

#name of this setup
    #Text, e.g. "lab e.012"
class SetupName(Text):
    def __init__(self):
        super().__init__()
        self._printHeader = "reference name: "
        self._question = "the name of this setup"
        
#Screen information set
    #Multiple others        
class ScreenInfo(Multiple):
    def __init__(self):
        screenSet = [ScreenMultiple, ScreenPixels, ScreenDistance,ScreenRefreshRate, ScreenCentimeters]
        super().__init__(subDataInstanceClasses = screenSet)
        self._printHeader = "Screen info: "
        self._question = "The information regarding the screen used for stimulus presentation"

    #function to prompt a single sub DataInstance for manual setup
    #args:
    #   index: the index referrint to the DataInstance in self._subDataInstances that is called
    #returns:
    #   None    
    def SetManually(self, index):
        self._subDataInstances[index].SimpleDialog()

    #simple dialog for screen information
    #see DataInstanceTypes.py SimpleDialog for default behaviour
    @run_on_main_thread
    def SimpleDialog(self):
        #print an overview of the values if known, and prompt user to return, fill in manually, or automatically
        
        #check if all values are known
        needsAnswers = False
        for di in self._subDataInstances:
            if di.needsInput:
                needsAnswers = True
                break
            
        #if all values are known, prompt user to change screen information
        #this prompt also displays the information    
        if not needsAnswers:
            resp = tk.messagebox.askyesno("Change screen information?", f"Screen nr {self._subDataInstances[0]} {self._subDataInstances[1]} pix, dist: {self._subDataInstances[2]} cm @{self._subDataInstances[3]}Hz size:{self._subDataInstances[4]} cm. Change info?")
        else:
            resp = True

        #if not all values are known, or user responded 'yes' to change, resp is now set to False
            
        if not resp:
            return
        #if screen information is being changed, prompt the user whether they want to do this with automisation or manually
        elif not tk.messagebox.askyesno("Setting screen info", "Do you want to fill in the screen information with automisation? (no will only prompt all raw values)"):
            for di in self._subDataInstances:
                di.SimpleDialog()
            return

        #if not manually, the information is retrieved hereunder.
       
        #function that sets the monitor number and pixels when a monitor is selected
        def ConfirmMonitors(number):
            if number < 0 or number >= len(monitors):
                for i in range(2):
                    self.SetManually(i)
            else:
                self._subDataInstances[0].TrySetAnswer(number)
                self._subDataInstances[1].TrySetAnswer((monitors[number].width, monitors[number].height))
                root.destroy()
                root.quit()

        #function that cancels the monitor selection and sets the values manually
        def CancelMonitors():
            root.destroy()
            root.quit()
            for i in range(2):
                self.SetManually(i)
                
        #get monitors using screeninfo.get_monitors()
        monitors = get_monitors()
        #create a root window
        root = tk.Tk()
        label = tk.Label(root, text="Select the monitor used for stimulus presentation")
        
        #hereunder, create a window for each monitor, and a button to select the monitor
        #the seperate windows are displayed on each screen, the buttons are displayed on the root window
        windows = []
        for number, monitor in enumerate(monitors):
           window = tk.Toplevel()
           window.title(f"Monitor {number}")
           window.geometry(f"200x100+{monitor.x}+{monitor.y}")
           label = tk.Label(window, text=str(number), font=("Arial", 48))
           label.pack(expand=True)

           rootButton = tk.Button(root, text=f"select {str(number)}", command = lambda index = number: ConfirmMonitors(index))
           rootButton.pack(side=LEFT, padx = 2)
           windows.append(window)
           
        #button to cancel the process 
        cancelButton = tk.Button(root, text='Cancel', command = lambda: CancelMonitors())
        cancelButton.pack(side=LEFT)

        #call root.mainloop
        root.mainloop()
        
        #when the root window is destroyed, destroy all other windows
        #is this step really necessary? 
        for win in windows:
            win.destroy()

        #now we should have the monitor number and pixels
        monitor = monitors[self._subDataInstances[0].value]


        #prompt refreshrate and distance from participant to screen for manual input
        self._subDataInstances[2].SimpleDialog()
        self._subDataInstances[3].SimpleDialog()
        
        #get screen size in cm. (creditcard calibration is defined in the ScreenCentimeters class)
        self._subDataInstances[4].SimpleDialog(monitor)


#distance between participant and screen
    #Float
class ScreenDistance(Float):
    def __init__(self):
        super().__init__()
        self._printHeader = "Distance between participant and screen (cm): "
        self._question = "the distance between the participant and the screen"

#stimulus screen refreshrate
    #Int
class ScreenRefreshRate(Int):
    def __init__(self):
        super().__init__()
        self._printHeader = "Screen refresh rate: "
        self._question = "the refresh rate of the screen"
        
#stimulus screen resolution set
    #Multiple (Width and height)       
class ScreenPixels(Multiple):
    def __init__(self):
        pixelSet = [ScreenWidthPixels, ScreenHeightPixels]
        super().__init__(subDataInstanceClasses = pixelSet)
        self._printHeader = "Screen resolution: "
        self._question = "The resolution of the screen"
        
    def __repr__(self):
        return f"{str(self)} pixels"

    def __str__(self):
        return f"({self._subDataInstances[0].value}x{self._subDataInstances[1].value})"

#stimulus screen width pixels
    #int
class ScreenWidthPixels(Int):
    def __init__(self):
        super().__init__()
        self._defaultAnswer = "-"
        self._printHeader = "Stimulus screen width (pixels): "
        self._question = "the width of the stimulus screen in pixels"

#stim screen height pixels
    #int
class ScreenHeightPixels(Int):
    def __init__(self):
        super().__init__()
        self._printHeader = "Stimulus screen height (pixels): "
        self._question = "the width of the stimulus screen in pixels"

#stimulus screen size set
    #Multiple (Width and height)        
class ScreenCentimeters(Multiple):
    def __init__(self):
        centimetersSet = [ScreenWidthCm, ScreenHeightCm]
        super().__init__(subDataInstanceClasses = centimetersSet)
        self._printHeader = "Screen size: "
        self._question = "The size of the screen in centimeters"
        
    def __repr__(self):
        return f"{self._printHeader}({self._subDataInstances[0].value}x{self._subDataInstances[1].value}) cm"

    #'simple' dialog for screen size
    #see DataInstanceTypes.py SimpleDialog for default behaviour
    @run_on_main_thread
    def SimpleDialog(self, monitor = None):
        #if monitor number is not provided, return default behaviour (prompt all values manually)
        if monitor == None:
            return super().SimpleDialog()

        try:
            #first, probe user if they want to use creditcard or fill in manually
            creditcard = tk.messagebox.askyesno("Creditcard", "Get screensize with creditcard?")
            #if user does not want to use creditcard, return default behaviour (prompt all values manually)
            if not creditcard:
                return super().SimpleDialog()
            
            #hereunder, creditcard calibration is performed
            #first, create a root window
            root = tk.Tk()
            root.title = (f"creditcard validation")
            #default credit card size: 8.56 cm × 5.40 cm
            #ratio: 1.58577250834 
            def Height(width):
                return int(width / 1.58577250834)

            def Width(height):
                return int(height * 1.58577250834)

            #set the starting width and height of the window
            self.windowStartingWidth = 400
            self.windowStartingHeight = Height(self.windowStartingWidth)

            #function to confirm the values
            def Confirm():
                wh = (horizontal_slider.get(), vertical_slider.get())
                scales = (wh[0]/monitor.width, wh[1]/monitor.height) #ratio of creditcard to full screen
                sizes = (round(8.56 / scales[0], 2), round(5.40 / scales[1],2))
                self.TrySetAnswer(sizes)

                root.destroy()
                root.quit()

            #function to cancel the values
            def Cancel():
                root.destroy()
                root.quit()

            #function to resize the canvas from a slider event
            #one argument is always passed to this event via the tkinter callback     
            def Resize(_=None):
                #get slider values
                width, height = horizontal_slider.get(), vertical_slider.get()
                
                #if width or height has been adjusted, adjust the other value accordingly
                if width != self.windowStartingWidth: #width has been adjusted
                    height = Height(width)
                    vertical_slider.set(height)
                    self.windowStartingWidth, self.windowStartingHeight = width, height
                elif height != self.windowStartingHeight: #height has been adjusted
                    width = Width(height)
                    horizontal_slider.set(width)
                    self.windowStartingWidth, self.windowStartingHeight = width, height
                    
                #resize the canvas
                canvas.config(width=self.windowStartingWidth, height=self.windowStartingHeight)

            #label to instruct the user
            label = tk.Label(root, text="use the sliders to scale the grey area to the size of your creditcard")
            label.pack()
            
            # Create a horizontal slider
            horizontal_slider = tk.Scale(root, from_=1, to=monitor.width, orient='horizontal', label="Width", command=Resize)
            horizontal_slider.pack(fill='x', padx=20)

            # Create a vertical slider
            vertical_slider = tk.Scale(root, from_=1, to=monitor.height, orient='vertical', label="Height", command=Resize)
            vertical_slider.pack(side='left', fill='y', pady=20)

            # Create a canvas that will be scaled to the size of the creditcard
            canvas = tk.Canvas(root, width=self.windowStartingWidth, height=self.windowStartingHeight, bg="grey")
            canvas.pack()

            # Create a confirm and cancel button
            buttonConfirm = tk.Button(root, text="confirm", command=lambda: Confirm())
            buttonConfirm.pack()
            buttonCancel = tk.Button(root, text="cancel", command=lambda: Cancel())
            buttonCancel.pack()

            # Set initial values for the sliders
            horizontal_slider.set(self.windowStartingWidth)
            vertical_slider.set(self.windowStartingHeight)

            # Set the window size to 3 times the size of the canvas
            root.geometry(f"{self.windowStartingWidth*3}x{self.windowStartingHeight*3}+{monitor.x}+{monitor.y}")
            root.mainloop()

        except Exception as e:
            #if an error occurs, return default behaviour (prompt all values manually)
            super().SimpleDialog()
            
    def __repr__(self):
        return f"{str(self)} cm"

    def __str__(self):
        return f"({self._subDataInstances[0].value}x{self._subDataInstances[1].value})"


#stimulus screen width cm
    #float
class ScreenWidthCm(Float):
    def __init__(self):
        super().__init__()
        self._printHeader = "Stimulus screen width (cm): "
        self._question = "the width of the stimulus screen in cm"

#stim screen height cm
    #float
class ScreenHeightCm(Float):
    def __init__(self):
        super().__init__()
        self._printHeader = "Stimulus screen height (cm): "
        self._question = "the width of the stimulus screen in cm"

#the scale that the screen needs to be multiplied by to get the set width in visual degrees
    #float        
class ScreenScale(Float):
    def __init__(self):
        super().__init__()
        self._printHeader = "Used screen width: "
        self._question = "The scale of the screen used to present stimuli 56 visual degrees wide"
        self._locked = True


#Which screen is used for stimulus presentation
    #Integer
class ScreenMultiple(Int):
    def __init__(self):
        super().__init__()
        self._defaultAnswer = 0
        self._printHeader = "Stimulus presentation screen nr (0 for 1 screen): "
        self._question = "On which screen stimuli were presented: "


#tracker type
    #option
class TrackerType(Option):
    def __init__(self):
        super().__init__(options = ['mouse', 'smi', 'eyelink', 'tobii'])
        self._printHeader = "Tracker used: " 
        self._question = "which tracker is used: "
        
    #the value 'mouse' is not accepted by pygaze, but for the sake of clarity,
    #   we give the user the option to select 'mouse', which we replace with 'dummy' when value is requested in-code
    @property
    def value(self):
        res = super().value
        if res == 'mouse':
            return 'dummy'
        return res
    
#all info for conversion
    #multiple
    #also contains functions for converting pupil size    
class PupilConversionMultiple(Multiple):
    def __init__(self):
        conversionSet = [PupilStartingDimension, PupilConversionRatio]
        super().__init__(subDataInstanceClasses = conversionSet)
        self._printHeader = "Pupil size conversion info: "
        self._question = "The information needed to convert pupil size to mm"
        
    def __repr__(self):
        if self._subDataInstances[1].value != 0:
            return self._printHeader + 'known'
        else:
            return self._printHeader + 'unknown'
    
    @property
    def factor(self):
        if self._subDataInstances[1].value == 0:
            raise Exception("Pupil size conversion factor not set")
        else:
            return self._subDataInstances[1].value
    
    @property
    def isDiameter(self):
        return self._subDataInstances[0].value == 'diameter'
        
    #GetDiameterMM
    #function to convert pupil size to mm
    #args:
    #   pupilSize: the pupil size in arbitrary units
    #returns:
    #   the pupil size in mm
    def GetDiameterMM(self, pupilSize):
        #if factor is not given, return the raw value
        if self._subDataInstances[1].value == 0:
            return pupilSize
        if not self.isDiameter:
            return sqrt(pupilSize) * self.factor
        else: #pupil size is given in diameter a.u.
            pupilSize = pi * (pupilSize/2)**2
            return pupilSize * self.factor
        
#conversion ratio
    #float
    #the value by which pupil size (a.u.) is multiplied by to get pupil size in mm
class PupilConversionRatio(Float):
    def __init__(self):
        super().__init__()
        self._printHeader = "Pupil size conversion ratio: "
        self._question = "Pupil size conversion factor (if known)"
        self._defaultAnswer = 0
        self._result = 0
        
#conversion starting dimension
    #option
    #the dimensionality in which pupil size is reported by the tracker        
class PupilStartingDimension(Option):
    def __init__(self):
        super().__init__(options = ['area', 'diameter'])
        self._printHeader = "Pupil size dimension: "
        self._question = "The dimension in which pupil size is reported by the eye tracker"
        

# # # # session stuff # # # #

#date
    #date
class TestDate(Date):
    def __init__(self):
        super().__init__()
        self._printHeader = "Date of test: "
        self._question = "the date of this test"

#Consent for data upload
    #Option, No/Yes     
class ShareDataConsent(Option):
    def __init__(self):
        super().__init__(options = ['yes', 'no'])
        self._printHeader = "Participant consent to uploading data? "
        self._question = "whether the participant agrees to uploading the data from this experiment"
        
#Experiment order
    #OrderedSelection        
class ExperimentOrder(OrderedSelection):
    def __init__(self):
        super().__init__(options = PygazeExperiment.SubClasses().keys())
        self._printHeader = "Experiment order: "
        self._question = "which experiments are conducted, in order"

#Dummy mode: Whether experiment is ran with mouse instead of tracker
    #Option, No/Yes        
class DummyMode(Option):
    def __init__(self):
        super().__init__(options = ['no', 'yes'])
        self._printHeader = "Dummy mode: "
        self._question = "whether mouse is used instead of eyetracker"
        
#Gaze Region: The region of visual degrees in which fixation is accepted
    #Number, default=3
class GazeRegion(Float):
    def __init__(self):
        super().__init__()
        self._printHeader = "Scale of gaze region: "
        self._defaultAnswer = 1
        self._question = "How much gaze region is scaled up from 1.74 * 3.48 visual deg. radius"
        
#ParticipantInfo, reference to all information regarding the participant
    #DataInfo        
class ParticipantInfo(DataInfo):
    def __init__(self, type_ = None):
        folder = os.path.join(Data(), "Participants")
        optionPaths = [os.path.join(folder,filename) for filename in os.listdir(folder)]
        super().__init__(optionPaths, type_)
        self._printHeader = "Tested participant: "
        self._question = "The participant that is being tested"
        
#SetupInfo, reference to all information regarding the setup
    #DataInfo        
class SetupInfo(DataInfo):
    def __init__(self, type_ = None):
        folder = os.path.join(Data(), "Setups")
        optionPaths = [os.path.join(folder,filename) for filename in os.listdir(folder)]
        super().__init__(optionPaths, type_)
        self._printHeader = "Used Setup: "
        self._question = "The setup that is used"
        
#Observed Pupil bias for the full hemisphere slide presentation. 
    #ExperimentResult
class FullHemispherePupilBias(ExperimentResult):
    def __init__(self, bias):
        super().__init__()
        self._printHeader = "Pupil bias for full hemishpere experiment: "
        self._defaultAnswer = bias
        self._result = bias
        self._question = "The observed pupil bias during the full hemisphere slideshow"
        
#Observed Pupil bias for the peripheral slide presentation.
    #ExperimentResult        
class PeripheralPupilBias(ExperimentResult):
    def __init__(self, bias):
        super().__init__()
        self._printHeader = "Pupil bias for peripheral experiment: "
        self._defaultAnswer = bias
        self._result = bias
        self._question = "The observed pupil bias during the peripheral slideshow"
        
#Observed horizontal gaze position bias for the free viewing experiment
    #ExperimentResult    
class FreeViewingHorizontalBias(ExperimentResult):
    def __init__(self, bias):
        super().__init__()
        self._printHeader = "free viewing horizontal bias: "
        self._defaultAnswer = bias
        self._result = bias
        self._question = "The observed horizontal gaze position bias in the Image experiment"

#comments for observations during data collection
    #Text
class ExperimentComments(Text):
    def __init__(self):
        super().__init__()
        self._result = "None"
        self._printHeader = "Comments after experiment: "
        self._question = "comments regarding this specific session"

