#This file contains the definition of the SetupInfo class, which is a subclass of DataInfo. See DataInfo.py
#SetupInfo contains the data from a setup (e.g. screen and tracker information)

import Import.SessionData.DataInfo as base
import Import.SessionData.DataInstances as dat
from Import.SessionData.DataFunctions import *
import os
from math import tau, atan, degrees, tan, ceil
from tkinter import messagebox


class SetupInfo(base.DataInfo):
    ext = '.set'
    def __init__(self):
        super().__init__()
        #definition of the set of DataInstances
        self._dataInstances = [dat.SetupName(), 
                               dat.ScreenInfo(), 
                               dat.TrackerType(),
                               dat.PupilConversionMultiple()]
        #does not look like a lot, but ScreenInfo and PupilConversionMultiple both contain multiple data instances

    #ext property
    #.set
    @property
    def ext(self):
        return '.set'

    #filenameIdentifierType property
    #SetupName instance
    @property 
    def filenameIdentifierType(self):
        return dat.SetupName

    #folder property
    #returns the folder where the setup data is stored
    @property 
    def folder(self):
        return os.path.join(self.datafolder, "Setups")

    #picklepath property
    #the path where the setup data is stored as pickle file
    @property 
    def picklepath(self):
        return os.path.join(self.folder, self.filename)
    
    #FinaliseScreenSize method
    #This method calculates the screen scale based on the screen width and distance
    #the screen should be about 50 degrees wide to fit the standard stimuli
    #if the screen is bigger, it is scaled down vertically
    #if the screen is smaller, a warning is given
    #returns:
    #   None
    def FinaliseScreenSize(self):
        #get screen pixels, size, and screendist. Divide screen dimensions by 2
        width = GetDataInstance(self, dat.ScreenWidthCm)
        dist = GetDataInstance(self, dat.ScreenDistance)
        
        #(size[0]/2) / (dist) = tan(visual angle/2)
        #visual angle = 2*atan(size[0]/2*dist)

        #target radius in radians
        screenSizeTarget_half = 24.9/360*tau
        desiredWidth = tan(screenSizeTarget_half) * dist * 2

        if width > desiredWidth:
            scale = desiredWidth / width
            SetDataInstance(self, dat.ScreenScale, scale)
            
        #if the screen is too small (by more than 2.87 cm), we give a warning
        #we always set screenscale to 1    
        else:
            if width - desiredWidth < -2.87:
                messagebox.showwarning("Warning", "Screen width is smaller than 50 degrees, using a wider screen or moving the screen closer to the participant is recommended")
            SetDataInstance(self, dat.ScreenScale, 1)
            
    #we overwrite the savepickle method to ensure that screen size is finalised when saving
    #additionally, the FinaliseScreenSize method is called whenever an experiment is actually started        
    def SavePickle(self):
        self.FinaliseScreenSize()  
        super().SavePickle()