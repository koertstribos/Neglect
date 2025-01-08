from tkinter import messagebox, simpledialog
import Import.TKinter.TKinterBase as tkb
from tkinter import *
import Import.Experiment.ExperimentLauncher as exp
import Import.SessionData.SessionInfo as ses
import Import.SessionData.DataInstanceTypes as dit
import Import.Browsers.FileBrowser as bro
import Import.SessionData.SessionInfo as session
import Import.SessionData.SetupInfo as setup
import Import.SessionData.ParticipantInfo as participant
import Import.SessionData.DataInfo as data_base
from threading import Thread
from PIL import ImageTk as itk
from Import.Experiment.Text import TextEditor
import traceback

#General variables
DataInstancePackY = 10
DataInstancePackX = 5

OptionPackY = 10
OptionPackX = 5

DataInstanceWidgetAttributeName = "PromptWidgets"

#base class for all subscreens
#this class is not for standalone use
class _Sub(tkb._NeglectTKinterScreen):
    #initialise the class
    def __init__(self):
        self._StartButtonText = "Start"

    #_StartButton
    #initialise startbutton    
    def _StartButton(self):
        self._startButton = Button(self._main.root, text = self.startButtonText, command = self.AppendToStackCommand)

    #AppendToStackCommand
    #Append self to the stack of subscreens in the main screen
    def AppendToStackCommand(self):
        self._main.StackSub(self)

    #_AddMain
    #define a main screen
    #args:
    #   main, NeglectTKinterMainScreen (see TKinterMain.py)    
    def _AddMain(self, main):
        self._main = main

    #ShowSelf
    #call the self.show() command
    #returns:
    #   None    
    def _ShowSelf(self):
        self.UpdatePackOptions()
        self.Show()

    #ResetCanvas
    #Resets the canvas associated with this sub
    #This function is usually called quite often
    #returns:
    #   None    
    def ResetCanvas(self):
        if not hasattr(self, 'canvas'):
            self.InstCanvas()
        else:
            #maybe replace this with a quicker way of resetting the canvas
            self.RemoveCanvas()
            self.ResetCanvas()

    #RemoveCanvas
    #Removes all attributes of the canvas
    #returns:
    #   None        
    def RemoveCanvas(self):
        if hasattr(self, 'canvas'):
            self.canvas.grid_forget()
            delattr(self, 'canvas')
            self.scrollbar.grid_forget()
            delattr(self, 'scrollbar')
            self.scrollable_frame.grid_forget()
            delattr(self, 'scrollable_frame')

    #InstCanvas
    #function that sets up the canvas, is called when canvas is reset as well
    #returns:
    #   None        
    def InstCanvas(self):
        #create a canvas, scrollbar and frame
        self.canvas = Canvas(self._main.root)
        self.scrollbar = Scrollbar(self._main.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row = 2, column = 1, sticky = "nsew", columnspan = 3)

        self.scrollbar.grid(row = 2, column = 0, sticky = "ns")
    
#_NeglectTKinterSubScreen class
#Base class for a subscreen
#not for standalone use        
class _NeglectTKinterSubScreen(_Sub):
    def __init__(self):
        super().__init__()
        self._optionWidgets = []

    #.main
    #reference to main tkinter object
    @property
    def main(self):
        if self._main != None:
            return self._main
        else:
            return None

    #.root
    #reference to the root of the main tkinter object
    @property 
    def root(self):
        return self._main.root

    #.startButton
    #reference to the start button
    @property
    def startButton(self):
        if hasattr(self, '_startButton'):
            return self._startButton
        else:
            self._StartButton()
            return self.startButton

    #AddMain
    #links main screen to self
    #args:
    #     main, NeglectTKinterMainScreen (see TKinterMain.py)  
    #returns:
    #   None    
    def AddMain(self, main):
        print(f"adding main to {self}")
        self._AddMain(main)

    #.startButtonText
    #the text that is displayed on a startButton
    #overwrite self.StartButtonText in subclass to change this
    #_StartButtonText is the default value ("Start")
    @property 
    def startButtonText(self):
        if hasattr(self, 'StartButtonText'):
            return self.StartButtonText
        else:
            return self._StartButtonText

    #Show
    #called when the screen is activated (from function _ShowSelf())
    #overwrite this function in subclass
    def Show(self):
        print("NeglectTKinterSubScreen activated")

    #UpdatePackOptions 
    #if this sub has options widgets    
        #update the options widgets and pack them horizontally
    #returns:
    #   None    
    def UpdatePackOptions(self):
        if hasattr(self, "optionWidgets") and len(self.optionWidgets) > 0:
            self._main.RefreshDataControlWidgetGrid(self.optionWidgets)

    #DataInfoOverView
    #function for viewing an overview of a dataInfo object
    #args:
    #   dataInfoViewer: DataInfoViewer object (see DataInfo.py)
    #returns:
    #   None    
    def DataInfoOverView(self, dataInfoViewer):
        print(f"packing")
        #remove all widgets
        self.ResetCanvas()
        
        #get the widgets from the dataInfoViewer
        widgets = dataInfoViewer.GetWidgetList(self, self.scrollable_frame)
        
        #pack the widgets
        for index, widget in enumerate(widgets):
            widget.grid(row=index, column = 0)

    #DataInstanceForgetInputWidgets
    #removes all widgets coupled to the dataInstance
    #this function might not be used at all
    #returns:
    #   None        
    def DataInstanceForgetInputWidgets(self):
        if hasattr(self, DataInstanceWidgetAttributeName):
            for widget in getattr(self, DataInstanceWidgetAttributeName):
                widget.grid_forget()
            delattr(self, DataInstanceWidgetAttributeName)
            

#_BrowseViewer class
#base class for all subs that can view a list of saved DataInfo objects
#not for standalone use            
class _BrowseViewer(_NeglectTKinterSubScreen):
    def __init__(self):
        super().__init__()

    #optionWidgets property
    #a list of buttons and their functionalities
    @property
    def optionWidgets(self):
        return [Button(self._main.root, text = "New", command = self.NewInstance),
                Button(self._main.root, text = "Save", command = self.SaveInstance),
                Button(self._main.root, text = "Del", command = self.DelInstance)]

    #NewInstance function
    #creates a new instance of the object
    #returns:
    #   None
    def NewInstance(self):
        self.RemoveCanvas()
        res = self.newInstance
        instanceViewer = data_base.DataInfoViewer(res, self)
        self.currentInstanceView = instanceViewer
        instanceViewer.GetWidgetList(self, self._main.root)

    #SaveInstance function
    #saves the current instance (if it exists)
    #returns:
    #   None    
    def SaveInstance(self):
        if hasattr(self, "currentInstanceView"):
            self.currentInstanceView.AttemptSave()
            self.RemoveCanvas()
            self.Show()
        else:
            messagebox.showinfo(title = "error", message="No active Instance, please use the 'New' button or select one")

    #DelInstance function
    #deletes the current instance (if it exists)
    #returns:
    #   None        
    def DelInstance(self):
        if hasattr(self, "currentInstanceView"):
            self.currentInstanceView.AttemptDelete()
            self.RemoveCanvas()
            self.Show()
        else:
            messagebox.showinfo(title = "error", message="No active Instance, please select one.")


    #ListBrowsableInstances
    #makes a list out of all the browsable instances for this type
    #allows the user to click one instance to open it
    #returns:
    #   None        
    def ListBrowsableInstances(self):
        print(f"listing browsable instances for {self}")
        self.ResetCanvas()

        results = self.browser.list

        for index, res in enumerate(results):
            #image
            tkimage = itk.PhotoImage(res.img)
            imgLabel = Label(self.scrollable_frame, image=tkimage)
            imgLabel.image = tkimage #why? I already call image=tkimage hereabove ... but it doesn't work without this line
            imgLabel.grid(row=index, column=0)
                    
            #text
            txtLabel = Label(self.scrollable_frame, text=res.desc)
            txtLabel.grid(row=index, column=1)
            txtLabel.bind("<Button-1>", res.OnResultClick)

    #LaunchInstanceView
    #creates a DataInfoViewer object and links it to self
    #args:
    #   path: string representing the path where a DataInfoViewer object is saved
    #returns:
    #   None     
    def LaunchInstanceView(self, path):
        #make a viewer from path
        instance = self.DataInfoFromPath(path)
        instViewer = data_base.DataInfoViewer(instance, self)
        self.currentInstanceView = instViewer

    #DataInfoFromPath
    #returns a DataInfo object from a path (for loading saved DataInfo objects) 
    #args:
    #   path:  string representing the path where a DataInfoViewer object is saved
    #returns:
    #   None   
    def DataInfoFromPath(self, path):
        if path.endswith('.part'):
            return participant.ParticipantInfo.LoadPickle(path)
        elif path.endswith('.set'):
            return setup.SetupInfo.LoadPickle(path)
        elif path.endswith('.ses'):
            return session.SessionInfo.LoadPickle(path)
        else:
            print(f'no valid object found at {path}')
            return None

# # # # # # # # 
#actual subscreen definitions
# # # # # # # # 

#ExperimentLauncher class
#The sub that launches the experiment
class ExperimentLauncher(_NeglectTKinterSubScreen):
    def __init__(self):
        super().__init__()
        self.StartButtonText = "Start Exp"

    #Show function
    #launches the experiment (first make a SessionInfo, see dataInfo.CreateFromScratch. Then launch the experiment, see ExperimentLauncher.Launch)
    #returns:
    #   None    
    def Show(self):
        print("ExperimentLauncher activated")
        #explicitly do this in a try except block, as the user might close the window before the experiment is launched
        try:
            session = ses.FromTKinter(self)
        except Exception as e:
            print("error in creating SessionInfo")
            print(e)
            print(traceback.format_exc())
        #next, Launch the experiment
        #once again explicitly in a try-except block    
        try:
            exp.Launch(session)
        except Exception as e:
            print("error in running experiment")
            print(e)
            print(traceback.format_exc())

#SessionViewer class
#the sub that allows the user to view and edit session definitions (SessionInfo objects)
#SessionInfo objects hold information from performing the experiment            
class SessionViewer(_BrowseViewer):
    def __init__(self):
        super().__init__()
        self.StartButtonText = "View Sessions"
        self.browser = bro.Sessionbrowser(self)

    #overwrite optionWidgets, as the user is not allowed to specify a new SessionInfo object directly
    @property
    def optionWidgets(self):
        return [Button(self._main.root, text = "Del", command = self.DelInstance),
                Button(self._main.root, text = "Save", command = self.SaveInstance)]

    #Show function
    def Show(self):
        print("SessionViewer activated")
        self.ListBrowsableInstances()

    #newInstance property
    #returns:
    #   SessionInfo object    
    @property
    def newInstance(self):
        return session.SessionInfo()


#SetupViewer class
#the sub that allows the user to view and edit setup definitions (SetupInfo objects)
#these contain information about a setup (eye tracker, screen, etc)    
class SetupViewer(_BrowseViewer):
    def __init__(self):
        super().__init__()
        self.StartButtonText = "View Setups"
        self.browser = bro.Setupbrowser(self)

    #newInstance property
    #returns:
    #    SetupInfo object    
    @property
    def newInstance(self):
        return setup.SetupInfo()

    #Show function
    def Show(self):
        print("SetupViewer activated")
        self.ListBrowsableInstances()

#ParticipantViewer class
#the sub that allows the user to view and edit participant definitions (ParticipantInfo objects)
#these contain information about a participant (age, sex, damage info, etc)        
class ParticipantViewer(_BrowseViewer):
    def __init__(self):
        super().__init__()
        self.StartButtonText = "View Participants"
        self.browser = bro.Participantbrowser(self)

    #newInstance property
    #returns:
    #   ParticipantInfo object    
    @property
    def newInstance(self):
       return participant.ParticipantInfo()

    #Show function
    #list all browsable instances
    def Show(self):
        print("ParticipantViewer activated")
        self.ListBrowsableInstances()

#InstructionViewer class
#the sub that allows the user to view and edit textual instructions (Instruction objects)        
class InstructionViewer(_BrowseViewer):
    def __init__(self):
        super().__init__()
        self.StartButtonText = "View Instructions"
        self.browser = bro.Instructionbrowser(self)

    #NewInstance function
    #overwrite this function because a text editor rather than a DataInfoViewer is needed
    #returns:
    #   None    
    def NewInstance(self):
        #promt language name
        langName = simpledialog.askstring("Language name", "language", initialvalue="")
        if langName == None:
            print("failure to create new language name")
            return
        if langName in self.browser.listnames:
            messagebox.showinfo(title = "error", message="Language already exists")
            return

        self.RemoveCanvas()
        instViewer = TextEditor.FromScratch(langName, self)
        self.currentInstanceView = instViewer
        instViewer.GetWidgetList(self, self._main.root)


    #newInstance property
    #returns a new Instruction object        
    @property
    def newInstance(self):
        return dit.Instruction()

    #Show function
    #Lists browsable instances
    def Show(self):
        print("InstructionViewer activated")
        self.ListBrowsableInstances()
        
    #LaunchInstanceView
    #overwrite this function to launch a viewer from a path
    #args:
    #   path: string representing where a InstructionViewer is saved
    #returns:
    #   None    
    def LaunchInstanceView(self, path):
        #make a viewer from path
        instViewer = TextEditor(path, self)
        self.currentInstanceView = instViewer
        
    #TxtOverView
    #function for viewing an overview of a text object
    #called from Text.py in TextEditor.__init__()
    #args:
    #   textEditor: TextEditor object (see Text.py)
    #returns:
    #   None    
    def TxtOverView(self, textEditor):
        print(f"packing")
        self.ResetCanvas()
        widgets = textEditor.GetWidgetList(self, self.scrollable_frame)

        for index, widget in enumerate(widgets):
            widget.grid(row=index, column = 0)
