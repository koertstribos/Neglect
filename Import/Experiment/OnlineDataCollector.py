from Import.Experiment.Experiment import *
from Import.SessionData.SessionInfo import *
from Import.GazeContingency.Rule import Rule
from constants import invalidationCommentText


#_OnlineDataCollector class
#base class for OnlineDataCollector
#not for standalone use
class _OnlineDataCollector:
    def __init__(self):
        self._cache = []
        self._comments = []

    #_ReceiveSample method
    #do something with a sample (append it to the cache, and trim the cache)    
    def _ReceiveSample(self, sample):
        self._cache.append(sample)
        self._TrimCache()

    #_TrimCache method
    #trim the cache so that it does not exceed the cacheLength
    def _TrimCache(self):
        while len(self._cache) > self.cacheLength:
            self._cache.pop(0)
            
    #_CacheBaseline method
    #save the baseline samples to _cachedBaseline
    def _CacheBaseline(self, baselineTime):
        #calculate the number of samples to save
        samplesToSave = int(baselineTime/1000 * self.samplingFrequency)
        print(f"saving baseline samples {samplesToSave}")

        if samplesToSave > len(self._cache):
            print(f"Warning: baseline depth ({samplesToSave}) exceeds current cache content ({len(self._cache)}) Only saving the cache as far as it goes")
            samplesToSave = len(self._cache)

        #save the samples
        self.cachedBaseline = []
        for i in range(samplesToSave):
            self.cachedBaseline.append(self._cache[-samplesToSave + i])

#OnlineDataCollector class
#the class used to collect data            
class OnlineDataCollector(_OnlineDataCollector):
    def __init__(self, sessionInfo):
        super().__init__()
        self.sessionInfo = sessionInfo
        self.cacheLength = 0
        self.cachedBaseline = []
        self.recording = False
        
    #LinkGC method
    #Link a gazecontingency object    
    def LinkGC(self, gazeContingency):
        print("Linking GazeContingency to OnlineDataCollector")
        self.GC = gazeContingency
        
    #UnlinkGC method
    #Unlink a gazecontingency object
    def UnlinkGC(self):
        print("Unlinking GazeContingency from OnlineDataCollector")
        self.GC = None
        
    #ResumeCaching method
    #resumes caching after it has been paused    
    def ResumeCaching(self):
        if hasattr(self, 'samplingFrequency') and hasattr(self, 'samplingTime'):
            print(f"Resuming caching @{self.samplingFrequency} Hz for {self.samplingTime / 1000} s")
            self.recording = True
            self._TrimCache()
        
    #StartCaching method
    #start caching samples, with a certain frequency and duration
    def StartCaching(self, frequencyHertz, timeMS):
        print(f"Starting caching @{frequencyHertz} Hz for {timeMS / 1000} s")
        self.recording = True
        self.samplingFrequency = frequencyHertz
        self.samplingTime = timeMS
        self.cacheLength = frequencyHertz * timeMS / 1000
        print(f'cache length = {self.cacheLength}')
        self._TrimCache()
        
        #make a rule that always returns True, and is called for every cache sample
        #this rule is passed to the GazeContingency object, and will trigger the GetSample method
        timedRule = Rule(1000/frequencyHertz, lambda: True)
        tracker = self.GC.track
        #GetSample method
        #get a sample from the eyetracker, and append it to the cache
        def GetSample():
            if self.recording:
                self._ReceiveSample([*tracker.sample(), tracker.pupil_size()])
        self.GC.AddRule(GetSample, timedRule)
        
    #StopCaching method
    #Stops caching    
    def StopCaching(self):
        print("Stopping caching")
        self.recording = False
        
    #SaveToSessionInfo method
    #Saves trial to session info, with trialNo, blockNo, and category    
    def SaveToSessionInfo(self, experiment, trialNo, blockNo, trialCategory = "no category"):
        if trialNo == None:
            return
        expString = PygazeExperiment.SubClassKey(experiment.__class__.__name__)
        print(f"saving Cache to exp {expString} trial {trialNo}")
        self.sessionInfo.SaveTrialSamples(expString, trialNo, blockNo, self.cache, self.cachedBaseline, trialCategory, self._comments)
        self._comments = []

    #CacheBaseline method
    #Caches a baseline
    def CacheBaseline(self, baselineTimeMS):
        if baselineTimeMS > self.samplingTime:
            raise Exception(f"Baseline depth ({baselineTimeMS} ms) exceeds sampling time ({self.samplingTime} ms), not saving")
        else:
            self._CacheBaseline(baselineTimeMS)
            
    #SetTrialComment method
    #set a comment for a trial (e.g. when it is invalid)        
    def SetTrialComment(self, comment):
        self._comments.append(comment)
        
    #invalidationComment property
    #some text that represents an invalid trial    
    @property
    def invalidationComment(self):
        return invalidationCommentText
    
        
    #SetInvalidationComment method
    #sets self._comments to contain the invalidationComment
    def SetInvalidationComment(self):
        if self.invalidationComment not in self._comments:
            self.SetTrialComment(self.invalidationComment)
        
    #cache property
    #a list of cached samples        
    @property
    def cache(self):
        if len(self._cache) < self.cacheLength:
            print('warning, cache is retrieved, but has not been filled completely')
            
        res = []
        for sample in self._cache:
            res.append(sample)
            
        return res
            

