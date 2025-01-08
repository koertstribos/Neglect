
import Import.Experiment.OnlineDataCollector as odc
from Import.Experiment.Experiment import AllExperiments
import constants
import pygaze
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import libinput
from pygaze import eyetracker

#Launch method
#This method is called when the experiment is started
#It imports constants.py, sets the constants,
#   creates an onlineDataCollector, and starts the experiment
#after the experiment, it finalises the session
#returns:
#       None
def Launch(session):
    #when ready, get constants.py and make changes to it
    print('starting import of constants.py')
    constants.SetConstants(session)
    try:
        pygaze.settings.settings.read_module(constants)
    except:
        pygaze.settings.read_module(constants)
        
    print('import done')
    

    moduleDict = {}
    moduleDict['constants'] = constants
    moduleDict['libscreen'] = libscreen
    moduleDict['libtime'] = libtime
    moduleDict['liblog'] = liblog
    moduleDict['libinput'] = libinput
    moduleDict['eyetracker'] = eyetracker

    #make an OnlineDataCollector
    onlineDataCollector = odc.OnlineDataCollector(session)
    #start the experiment
    experiments = AllExperiments(moduleDict=moduleDict)
    session.SetExperimentOrder(experiments)
    session.FinaliseScreenSize()

    # call RunExperiments
    experiments.RunExperiments(onlineDataCollector)
    #finalise the session
    session.FinaliseAfterExperiment()