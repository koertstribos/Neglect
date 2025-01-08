import os
from PIL import Image as img
from Import.Browsers.BrowseLocations import *

#initialise pictograms in a dictionary
pictogramsLocation = os.path.join(Materials(), "Image_software")
pictograms = [f for f in os.listdir(pictogramsLocation) if f.endswith(".bmp")]
pictdict = {}
for pict in pictograms:
    extensionIndex = pict.find(".bmp")
    key = pict[:extensionIndex]
    path = os.path.join(pictogramsLocation, pict)
    image = img.open(path)
    pictdict[key] = image

#Browser class
#each Browser returns a list of their respective options (defined by self._path and self._extension)
#selecting such an option opens the objectviewer for that option 
#this class is not for standalone use    
class Browser:
    def __init__(self, launcher):
        self._launcher = launcher
        
    #startPath is the path where the browser starts looking for files
    #see BrowseLocations.py    
    @property
    def startPath(self):
        return Data()

    #list is a list of BrowserResult objects at self._path ending in self._extension
    #see BrowserResult
    @property 
    def list(self):
        files = os.listdir(self._path)
        res = []
        for fil in files:
            if fil.endswith(self._extension):
                img = pictdict[self._pictkey]
                path = os.path.join(self._path, fil)
                desc = path.replace(self._path, "")
                result = BrowserResult(path, desc[1:], img, self._launcher)
                res.append(result)
        return res
    
    #listnames is a list of the descriptions of the BrowserResult objects in self.list
    @property
    def listnames(self):
        return [res.desc for res in self.list]

#Participantbrowser, Setupbrowser, Sessionbrowser, Instructionbrowser
class Participantbrowser(Browser):
    def __init__(self, launcher):
        super().__init__(launcher)
        self._path = os.path.join(self.startPath, "Participants" )
        self._pictkey = "participant"
        self._extension = ".part"
class Setupbrowser(Browser):
    def __init__(self, launcher):
        super().__init__(launcher)
        self._path = os.path.join(self.startPath, "Setups" )
        self._pictkey = "setup"
        self._extension = ".set"
class Sessionbrowser(Browser):
    def __init__(self, launcher):
        super().__init__(launcher)
        self._path = os.path.join(self.startPath, "Sessions" )
        self._pictkey = "session"
        self._extension = ".ses"
class Instructionbrowser(Browser):
    def __init__(self, launcher):
        super().__init__(launcher)
        self._path = self.startPath
        self._pictkey = "txt"
        self._extension = ".txt"
    #overwrite startpath for the InstructionBrowser as the instructions are not in the Data folder
    @property
    def startPath(self):
        return os.path.join(Materials(), "Instructions")


#BrowserResult
#object for containing a singular browser result
class BrowserResult:
    def __init__(self, path, desc, pictogram, launches):
        self._img = pictogram
        self._path = path
        self._desc = desc
        self._launcher = launches

    #img is the pictogram of the result
    @property
    def img(self):
        return self._img

    #desc is the description of the result
    @property
    def desc(self):
        return self._desc

    #OnResultClick
    #launches the instance view for the result (see TKinterSubs.py)
    def OnResultClick(self, event):
        self._launcher.LaunchInstanceView(self._path)
