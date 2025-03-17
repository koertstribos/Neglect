#This file contains the definition of the SessionInfo class, which is a subclass of DataInfo. See DataInfo.py
#SessionInfo concerns the data that is collected during a single session of an experiment. 
#It contains a combination of participant and setup info, some experiment-specific info, and the results of the experiment.
import os
from tkinter import messagebox
from Import.SessionData.DataInfo import DataInfo
from Import.SessionData.ParticipantInfo import ParticipantInfo
from Import.SessionData.SetupInfo import SetupInfo
import Import.SessionData.DataInstances as dat
from Import.SessionData.DataProcessing import PupilBiasResultsFullHemisphere, PupilBiasResultsPeripheral, HorizontalBiasResults
from Import.SessionData.DataFunctions import *
from Import.Experiment.Experiment import PygazeExperiment


class SessionInfo(DataInfo):
    def __init__(self):
        super().__init__()
        
        #define the data instances that will be contained in the SessionInfo here
        self._dataInstances = [dat.ParticipantInfo(ParticipantInfo),
                               dat.SetupInfo(SetupInfo),
                               dat.ExperimentOrder(),
                               dat.GazeRegion(),
                               dat.TestDate(), 
                               dat.ShareDataConsent(),
                               dat.DummyMode()
                               ]
        #note: Not all dataInstances that will be contained in the SessionInfo are declared here, some are declared in FinaliseAfterExperiment()
        
        self._experimentResults = {}
        self._hasCSV = False
        
    #ext property
    #extension of pickle files that contain a SessionInfo object    
    @property
    def ext(self):
        return '.ses'

    #filenameIdentifierType property
    #returns the testing date
    @property 
    def filenameIdentifierType(self):
        return dat.TestDate
    
    #proposedName property
    #returns the identifying data instance of the participant and the date
    @property
    def proposedName(self):
        return str(self.participantInfo.identifyingDataInstance) + "_" + str(self.identifyingDataInstance)

    #folder property
    #returns the folder where the session data is stored
    @property 
    def folder(self):
        return os.path.join(self.datafolder, "Sessions")

    #picklepath property
    #returns the path to the pickle file that contains the SessionInfo object
    @property 
    def picklepath(self):
        return os.path.join(self.folder, self.filename)
    
    #experimentResultsFilename property
    #returns the path to the csv file that contains the results of the experiment
    @property
    def experimentResultsFilename(self):
        return os.path.join(self.folder, (self.proposedName + ".csv"))
    
    #setupInfo property
    #returns the SetupInfo data instance
    #see self.__getitem__()
    @property
    def setupInfo(self):
        return self['setup']
    
    #participantInfo property
    #returns the ParticipantInfo data instance
    #see self.__getitem__()
    @property
    def participantInfo(self):
        return self['participant']
    
    #__getitem__ is setup here to allow for quick retrieval of data needed in constants.py
    def __getitem__(self, key):
        if key == 'DUMMYMODE':
            return GetDataInstance(self, dat.DummyMode) == "yes"
        
        elif key == 'DISPSIZE':
            return (GetDataInstance(self.setupInfo, dat.ScreenWidthPixels), 
                    GetDataInstance(self.setupInfo, dat.ScreenHeightPixels))
        
        elif key == 'SCREENSIZE':
            return (GetDataInstance(self.setupInfo, dat.ScreenWidthCm),
                    GetDataInstance(self.setupInfo, dat.ScreenHeightCm))
        
        elif key == 'DISPSIZE_scaled':
            res = self['DISPSIZE']
            scale = GetDataInstance(self.setupInfo, dat.ScreenScale)
            if scale != None:
                res = (res[0]*scale, res[1])
            return res

        elif key == 'SCREENREFRESHRATE':
            return (GetDataInstance(self.setupInfo, dat.ScreenRefreshRate))

        elif key == 'SCREENDIST':
            return (GetDataInstance(self.setupInfo, dat.ScreenDistance))
        
        elif key == 'SCREENNR':
            return(GetDataInstance(self.setupInfo, dat.ScreenMultiple))
        
        elif key == 'GAZEREGION':
            return GetDataInstance(self, dat.GazeRegion)
        
        elif key == 'TRACKERTYPE':
            return GetDataInstance(self.setupInfo, dat.TrackerType)
        
        elif key == 'setup':
            return GetDataInstance(self, dat.SetupInfo)
        
        elif key == 'participant':
            return GetDataInstance(self, dat.ParticipantInfo)

        elif key == 'EDFfilename':
            return [char for char in self.proposedName if char.isalnum()]
        
        elif key == 'LANGUAGE':
            return GetDataInstance(self.participantInfo, dat.PresentationLanguage)
        
        else:
            raise Exception(f"unknown key: {key}")
        
    #FinaliseAfterExperiment
    #Called after the experiment is completed
    #lock the data fields belonging to this session
    #additionally, add the ExperimentComments data field, which is not locked.
    #returns:
    #   None     
    def FinaliseAfterExperiment(self):
        for di in self._dataInstances[2:]:
            di.SetLock(True)
            
        scalingFactor = GetDataInstanceObject(self.setupInfo, dat.PupilConversionMultiple)
            
        #get the results of the experiment
        #see DataProcessing.py
        pupilBiasesFull = PupilBiasResultsFullHemisphere(self._experimentResults, scalingFactor)
        pupilBiasesPeripheral = PupilBiasResultsPeripheral(self._experimentResults, scalingFactor)
        gazeBias = HorizontalBiasResults(self._experimentResults, scalingFactor)
           
        biasFull, biasPeriph = pupilBiasesFull.result, pupilBiasesPeripheral.result
        biasView = gazeBias.result

        #save the results of the experiment as dataInstances
        self._dataInstances.append(dat.FullHemispherePupilBias(biasFull))
        self._dataInstances.append(dat.PeripheralPupilBias(biasPeriph))
        self._dataInstances.append(dat.FreeViewingHorizontalBias(biasView))
        self._dataInstances.append(dat.ExperimentComments())

        #save the results of the experiment
        self.MakeIdentifierUnique() #call this function outside of SavePickle before saving the experiment csv, as we will need the unique identifier in the csv filename as well
        self.SaveExperimentResults()
        self.SavePickle()

    #SetExperimentOrder
    #Called to set the order in which the experiments are presented using the DataInstance ExperimentOrder
    #args:
    #   experiments: Experiments object (see Experiment.py)
    #returns:
    #   None    
    def SetExperimentOrder(self, experiments):
        #get value of ordered selection
        for expName in GetDataInstance(self, dat.ExperimentOrder):
            experiments.Add(PygazeExperiment.GetSubclass(expName))
            
    #FinaliseScreenSize is called to finalise the screen size
    #see SetupInfo.py         
    #returns:
    #   None        
    def FinaliseScreenSize(self):
        self['setup'].FinaliseScreenSize()

    #SaveTrialSamples 
    #Called whenever a trial is finalised, and saves the trial data in the _experimentResults dictionary
    #args:
    #   experimentName: string, name that refers to the experiment
    #   trialNo:        int, refers to the trial number
    #   blockNo:        int, refers to the block number
    #   samples:        the cache of OnlineDataCollector
    #   baseline:       the baseline of the trial (also cached in OnlineDataCollector)
    #   trialCategory:  string referring to the category/condition a trial belongs to
    #   comments:       list of strings, containing comments about the trial (e.g. 'invalidated')
    #returns:
    #   None  
    def SaveTrialSamples(self, experimentName, trialNo, blockNo, samples, baseline, trialCategory, comments):
        if experimentName not in self._experimentResults:
            self._experimentResults[experimentName] = []

        thisTrialDict = {}
        thisTrialDict['block'] = blockNo
        thisTrialDict['trial'] = trialNo
        thisTrialDict['samples'] = samples
        thisTrialDict['name'] = trialCategory
        thisTrialDict['baseline'] = baseline
        thisTrialDict['comments'] = comments

        self._experimentResults[experimentName].append(thisTrialDict)

    #PrintResults is called to print the results of the experiment
    #used for quickly presenting saved data during testing
    #returns:
    #   None    
    def PrintResults(self):
        for expName, dictionary in self._experimentResults.items():
            print("-------------------")
            print("experiment name: ", end = "")
            print(expName)
            print("")
            
            for trialDict in dictionary:
                print(f"trial of type {trialDict['name']}")
                print(f"comments regarding this trial: {trialDict['comments']}")
                print(f"block {trialDict['block']}, trial {trialDict['trial']}")
                print(f"baseline: (length: {len(trialDict['baseline'])}) {trialDict['baseline']}")
                print(f"samples: (length: {len(trialDict['samples'])}) {trialDict['samples']}")
                print("")
                
    #SaveExperimentResults 
    #Called to save the results of the experiment in a csv file
    #returns:
    #   None            
    def SaveExperimentResults(self):
        if not hasattr(self, '_experimentResults'):
            print("error in SessionInfo.SaveExperimentResults: No results to save")
            return
        
        try:
            with open(self.experimentResultsFilename, "w") as write:
                for expName, dictionary in self._experimentResults.items():
                    write.write("expName," + expName)
                    write.write("\n")
                
                    for trialDict in dictionary:
                        write.write("desc," + trialDict['name'] + ",block," + str(trialDict['block']) + ",trialNo," + str(trialDict['trial']))
                        write.write("\n")
                        write.write("comments, " + ", ".join(trialDict['comments']))
                        write.write("\n")
                        write.write("baseline")
                        write.write("\n")
                        write.write("x,y,pupilSize")
                        write.write("\n")
                        for sample in trialDict['baseline']:
                            write.write(f"{sample[0]},{sample[1]},{sample[2]}")
                            write.write("\n")
                        write.write("stimulus")
                        write.write("\n")
                        write.write("x,y,pupilSize")
                        write.write("\n")
                        for sample in trialDict['samples']:
                            write.write(f"{sample[0]},{sample[1]},{sample[2]}")
                            write.write("\n")
        except Exception as e:
            print("error in saving experiment as csv: ")
            print(e)
                        
        self._experimentResults = {}
        self._hasCSV = True
                        
    #LoadExperimentResults
    #Called to load the results of the experiment from a csv file
    #returns:
    #   None    
    def LoadExperimentResults(self):
        if not self._hasCSV:
            print("error in SessionInfo.LoadExperimentResults: No results to load")
            return
        
        with open(self.experimentResultsFilename, "r") as read:
            lines = read.readlines()
            i = 0
            while i < len(lines):
                while(lines[i].split(",")[0] != "expName"):
                    i += 1
                expName = lines[i].split(",")[1]
                self._experimentResults[expName] = []
                thisTrialDict = {}
                while(lines[i].split(",")[0] != "desc"):
                    i += 1
                thisTrialDict['name'], thisTrialDict['block'],thisTrialDict['trial'], = lines[i].split(",")[1],lines[i].split(",")[3],lines[i].split(",")[5]
                while(lines[i].split(",")[0] != "comments"):
                    i += 1
                thisTrialDict['comments'] = lines[i].split(",")[1:]
                while(lines[i].split(",")[0] != "baseline"):
                    i += 1
                while(lines[i] != "x,y,pupilSize"):
                    i += 1
                else: #after finding the line "x,y,pupilSize"
                    i += 1
                while(lines[i] != "stimulus"):
                    thisTrialDict['baseline'].append((lines[i].split(",")[0],lines[i].split(",")[1],lines[i].split(",")[2]))
                    i += 1
                else: #after finding the line "stimulus"
                    i += 2
                while(lines[i] != "expName"):
                    thisTrialDict['samples'].append((lines[i].split(",")[0],lines[i].split(",")[1],lines[i].split(",")[2]))
                    i += 1  
                self._experimentResults[expName].append(thisTrialDict)
                
#FroMTKinter
#make a SessionInfo object from scratch
#required when launching the experiment from the experimentlauncher sub         
#args:
#   TKinterExperimentLauncher: any
#returns:
#   None       
def FromTKinter(TKinterExperimentLauncher):
    print("Making SessionInfo from TKinter ")
    res = SessionInfo.CreateFromScratch()
    return res
