#This file contains the definition of the ParticipantInfo class, which is a subclass of DataInfo. See DataInfo.py
#ParticipantInfo contains the data from a participant (e.g. demographics and damage information)

import Import.SessionData.DataInfo as base
import Import.SessionData.DataInstances as dat
import os

class ParticipantInfo(base.DataInfo):
    def __init__(self):
        #definition of the set of DataInstances
        self._dataInstances = [dat.Alias(),
                               dat.CurrentAge(), 
                               dat.Sex(), 
                               dat.PresentationLanguage(),
                               dat.Handedness(),
                               dat.TimePostInjury(),
                               dat.DamageType(),
                               dat.DamageLocation(),
                               dat.DamagedVessel(),
                               dat.DamageComment(),
                               dat.PreviousTestsCount(),
                               dat.Hemianopia(),
                               dat.PreviousBrainDamage(), 
                               dat.PatientComments()
                               ]

    #ext property
    #.part    
    @property
    def ext(self):
        return '.part'

    #filenameIdentifierType property
    #the alias (name) of participant
    @property 
    def filenameIdentifierType(self):
        return dat.Alias

    #folder property
    #returns the folder where the participant data is stored
    @property 
    def folder(self):
        return os.path.join(self.datafolder, "Participants")

    #picklepath property
    #the path where the participant data is stored as pickle file
    @property 
    def picklepath(self):
        return os.path.join(self.folder, self.filename)
    
    