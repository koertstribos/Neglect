#here, data is converted into experimentResults

from numpy import mean
import constants
import matplotlib.pyplot as plt
from constants import invalidationCommentText

#_ExperimentResults class
#base class for experiment results
#not for standalone use
class _ExperimentResults():
    def __init__(self, expData, conversionDataInfo):
        self._conversionDataInfo = conversionDataInfo #this should be named conversionDataInstance
        self._trialCount = 0
        self.SetResult(expData)
        
        print("Experiment results made!")
        print(f"name: {self._name}")
        print(f"res: {self.result} (n={self.trialCount})")
        
    #SetResult method
    #this function is used in subclasses to set the results
    #the function is called from _ExperimentResults.__init__()    
    def SetResult(self, expData):
        raise Exception("Unimplemented")
    
    #result property
    #returns the result of the experiment if it exists
    @property
    def result(self):
        if hasattr(self, '_result'):
            return self._result
        else:
            return None
        
    #trialCount property
    #returns the amount of trials used for result calculation    
    @property
    def trialCount(self):
        if hasattr(self, '_trialCount'):
            return self._trialCount
        else:
            return None
        
    #PupSize method
    #converts pupsize in arbitrary units to Diameter millimeter
    #it uses a conversion DataInstance (incorrectly labeled as DataInfo)    
    def PupSize(self, arbitraryUnitValue):
        return self._conversionDataInfo.GetDiameterMM(arbitraryUnitValue)
        
#_PupilBiasResults class
#base class for both blocks of the pupil bias experiments
#not for standalone use
#self_trialContainers and self._name are defined in subclasses    
class _PupilBiasResults(_ExperimentResults):
    def __init__(self, expData, conversionFactor):
        super().__init__(expData, conversionFactor)
        

    #SetResult method
    #this function is used in subclasses to set the results
    #function is based on the following paper:
    # Ten Brink, A. F., Van Heijst, M., Portengen, B. L., Naber, M., & Strauch, C. (2023).
    #  Uncovering the (un) attended: Pupil light responses index persistent biases of spatial attention in neglect.
    #  Cortex, 167, 101-114.   
    #  """ 
        #Left/rightward bias in the pupil light response (‘pupil bias score’) 
        #was determined per participant using the average pupil size change 
        #relative to baseline starting from 550 ms after stimulus presentation, 
        #separately for white/black and black/white displays 
        #and then subtracting these average changes, 
        #pooling data of both blocks (as no differences were observed between blocks). 
        #In other words, this value indicates 
        #how much more the pupil responded to what was presented on the right (positive values) 
        #or on the left (negative values; zero means similar responses).
    #  """
    def SetResult(self, expData):
        samplingRate = constants.SAMPLINGRATE

        WB = []
        BW = []
        #iterate over all experiments
        for expName, expDictionary in expData.items():
            #don't do anything with the slideshow experiment
            if expName != "Slideshow":
                pass
            else:
                for trial in expDictionary:
                    #get trial name and see if trial is relevant to this result
                    trialName = trial["name"]
                    container = None
                    #first, check if trial was invalidated
                    if invalidationCommentText in trial['comments']:
                        continue
                    #second, get the container that will take this data from the trial name
                    elif trialName == self._trialContainers[0]:
                        container = BW
                    elif trialName == self._trialContainers[1]:
                        container = WB
                    else: #if trial is not relevant to this result (since both FullHemisphere and Peripheral are passed to this function twice)
                        continue
                    
                    if container != None:
                        #get baseline; average pupil size from 0-200 ms after stimulus presentation
                        baseline = trial['samples'][:int(0.2*samplingRate)]
                        baseline = [self.PupSize(pupSize) for _, _, pupSize in baseline if pupSize != 0]
                        baseline = mean(baseline)
                        #get pupil size; average pupilsize from 550 after stimulus presentation
                        affectedPupilSize = trial['samples'][int(0.55*samplingRate):]
                        affectedPupilSize = [self.PupSize(pupSize) for _, _, pupSize in affectedPupilSize if pupSize != 0]
                        affectedPupilSize = mean(affectedPupilSize)
                        #get pupil bias score for this trial
                        container.append(baseline-affectedPupilSize)
                
        if len(WB) == 0:
            self._result = None
            return
                
        self._result = (mean(BW)-mean(WB))
        self._trialCount = len(BW) + len(WB)
        
#PupilBiasResultsPeripheral class
#subclass of _PupilBiasResults used to contain the results of the peripheral pupil bias experiment
class PupilBiasResultsPeripheral(_PupilBiasResults):
    def __init__(self, expData, conversionFactor):
        self._trialContainers = ["Peripheral_BlackWhite", #right
                                 "Peripheral_WhiteBlack"] #left
        self._name = "peripheral slide pupilbias"
        super().__init__(expData, conversionFactor)
        
#PupilBiasResultsFullHemisphere class
#subclass of _PupilBiasResults used to contain the results of the full hemisphere pupil bias experiment        
class PupilBiasResultsFullHemisphere(_PupilBiasResults):
    def __init__(self, expData, conversionFactor):
        self._trialContainers = ["FullHemisphere_BlackWhite", #right
                                 "FullHemisphere_WhiteBlack"] #left
        self._name = "Full hemisphere slide pupilbias"
        super().__init__(expData, conversionFactor)
        
#HorizontalBiasResults class
#subclass of _ExperimentResults used to contain the results of the slideshow experiment        
class HorizontalBiasResults(_ExperimentResults):
    def __init__(self, expData, conversionFactor):
        self._name = "horizontal gaze bias"

        super().__init__(expData, conversionFactor)

    #Horizontal gaze bias is calculated as the difference in average x-coordinates between 
    #   the first second of image presentation, and the overall viewing of the image (7 seconds)
    def SetResult(self, expData):
        screenwidth = constants.DISPSIZE[0]
        screenMidpoint = screenwidth/2
        samplingRate = constants.SAMPLINGRATE
        res = []
        
        #returns True when x coordinate is on-screen (invalid is saved as -1)
        def xValid(x):
            return x <= screenwidth and x >= 0

        for expName, expDictionary in expData.items():
            if expName != "Images":
                pass
            else:
                for trial in expDictionary:
                    #first, check if trial was invalidated
                    if invalidationCommentText in trial['comments']:
                        continue
                    
                    #get gaze data
                    gazeData = trial['samples']
                    #get x-coordinates
                    xCoords = [(x-screenMidpoint)/screenMidpoint for x, _, _ in gazeData if xValid(x)]
                    #get x-coordinates of first second
                    xCoordsFirst = xCoords[:samplingRate]
                    #get x-coordinates of last 6 seconds
                    xCoordsLast = xCoords[samplingRate:]
                    #calculate average x-coordinates
                    avgXFirst = mean(xCoordsFirst)
                    avgXLast = mean(xCoordsLast)
                    
                    if isinstance(avgXFirst, (int, float)) and isinstance(avgXLast, (int, float)):
                        #calculate gaze bias
                        res.append(avgXFirst - avgXLast)

        if len(res)==0:
            self._result = None
        else:
            self._result = mean(res)
            self._trialCount = len(res)
    