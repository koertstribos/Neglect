import math

## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##    PyGaze is a Python module for easily creating gaze contingent experiments
##    or other software (as well as non-gaze contingent experiments/software)
##    Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013)

def DegToPix(deg, dist, pixPerCm):
    # tan(10degrees) = radius/distance
    # radius = tan(angle) * distance
    rad = deg/360 * math.tau
    dist = math.tan((rad)) * SCREENDIST
    if __name__ == "__main__":
        print(f'converting {deg} to pixels on-screen')
        print(f"tan(rad)={math.tan((rad))}")
        print(f"dist: {dist} cm, {dist * pixPerCm} pix" )
        print('-------------------------------')
    # convert from cm to pixels
    return dist * pixPerCm



#
# some values are set to none in first import. They are later defined by calling SetConstants(session)
#

# MAIN
DUMMYMODE = None # False for gaze contingent display, True for dummy mode (using mouse or joystick)
LOGFILENAME = None # logfilename, without path
LOGFILE = None # .txt; adding path before logfilename is optional; logs responses (NOT eye movements, these are stored in an EDF file!)

# DISPLAY
# used in libscreen, for the *_display functions. The values may be adjusted,
# but not the constant's names
SCREENNR = 0 # number of the screen used for displaying experiment
DISPTYPE = 'psychopy'
DISPSIZE = None #(2560,1440) # canvas size,  set with sessionInfo
DISPSIZE_scaled = None

LANGUAGE = None

def SCREENMIDPOINT():
    global DISPSIZE
    return (DISPSIZE[0]/2, DISPSIZE[1]/2)

SCREENSIZE = None# e.g. (59.8, 33.6) # physical display size in cm,  set with sessionInfo
SCREENDIST = None # e.g. 67.5 #distance from participant to screen,  set with sessionInfo

MOUSEVISIBLE = False # mouse visibility
BGC = (126,126,126,255) # backgroundcolour
FGC = (255,255,255,255) # foregroundcolour

SCREENREFRESHRATE = None #e.g. 100  set with sessionInfo
SCREENFRAMETIME = None

pixPerCm = None
#EXPERIMENT INFO
GAZEREGION = None #extra distance the gaze is allowed to drift from a ROI before the experiment takes action
ELLIPSESIZE = None

#calculating the radius at which targets will be drawn

INTERTIME_CHECKGAZEPOS = 5
SAMPLINGRATE = 60

# INPUT
# used in libinput. The values may be adjusted, but not the constant names.
MOUSEBUTTONLIST = None # None for all mouse buttons; list of numbers for buttons of choice (e.g. [1,3] for buttons 1 and 3)
MOUSETIMEOUT = None # None for no timeout, or a value in milliseconds
KEYLIST = None # None for all keys; list of keynames for keys of choice (e.g. ['space','9',':'] for space, 9 and ; keys)
KEYTIMEOUT = 1 # None for no timeout, or a value in milliseconds
JOYBUTTONLIST = None # None for all joystick buttons; list of button numbers (start counting at 0) for buttons of choice (e.g. [0,3] for buttons 0 and 3 - may be reffered to as 1 and 4 in other programs)
JOYTIMEOUT = None # None for no timeout, or a value in milliseconds

# EYETRACKER
# general
TRACKERTYPE = None # either 'smi', 'eyelink' or 'dummy' (NB: if DUMMYMODE is True, trackertype will be set to dummy automatically)
SACCVELTHRESH = None# degrees per second, saccade velocity threshold
SACCACCTHRESH = None # degrees per second, saccade acceleration threshold
# EyeLink only
# SMI only
SMIIP = None
SMISENDPORT = None
SMIRECEIVEPORT = None

# FRL
# Used in libgazecon.FRL. The values may be adjusted, but not the constant names.
FRLSIZE = 200 # pixles, FRL-size
FRLDIST = 125 # distance between fixation point and FRL
FRLTYPE = 'gauss' # 'circle', 'gauss', 'ramp' or 'raisedCosine'
FRLPOS = 'center' # 'center', 'top', 'topright', 'right', 'bottomright', 'bottom', 'bottomleft', 'left', or 'topleft'

# CURSOR
# Used in libgazecon.Cursor. The values may be adjusted, but not the constants' names
CURSORTYPE = 'cross' # 'rectangle', 'ellipse', 'plus' (+), 'cross' (X), 'arrow'
CURSORSIZE = 20 # pixels, either an integer value or a tuple for width and height (w,h)
CURSORCOLOUR = 'pink' # colour name (e.g. 'red'), a tuple RGB-triplet (e.g. (255, 255, 255) for white or (0,0,0) for black), or a RGBA-value (e.g. (255,0,0,255) for red)
CURSORFILL = True # True for filled cursor, False for non filled cursor
CURSORPENWIDTH = 3 # cursor edge width in pixels (only if cursor is not filled)

# trial saving
#define invalidationCommentText
invalidationCommentText = "invalid_due_to_excessive_blink_or_gaze_off_target"


def SetConstants(ses):

    global TRACKERTYPE
    # EYETRACKER
    # general
    TRACKERTYPE = ses['TRACKERTYPE'] # either 'smi', 'eyelink' or 'dummy' (NB: if DUMMYMODE is True, trackertype will be set to dummy automatically)
    print(f'TRAC {TRACKERTYPE}')

    global DUMMYMODE, LOGFILENAME, LOGFILE, MOUSEVISIBLE
    # MAIN
    DUMMYMODE = TRACKERTYPE == 'dummy' or TRACKERTYPE == 'dumbdummy' or ses['DUMMYMODE'] # False for gaze contingent display, True for dummy mode (using mouse or joystick)
    LOGFILENAME = ses['EDFfilename'] # logfilename, without path
    LOGFILE = LOGFILENAME[:] # .txt; adding path before logfilename is optional; logs responses (NOT eye movements, these are stored in an EDF file!)

    MOUSEVISIBLE = DUMMYMODE # mouse visibility

    global SCREENNR, DISPSIZE, LANGUAGE, DISPSIZE_scaled
    # DISPLAY
    # used in libscreen, for the *_display functions. The values may be adjusted,
    # but not the constant's names
    SCREENNR = ses['SCREENNR'] # number of the screen used for displaying experiment
    DISPSIZE = ses['DISPSIZE'] #(2560,1440) # canvas size,  set with sessionInfo
    DISPSIZE_scaled = ses['DISPSIZE_scaled']
    LANGUAGE = ses['LANGUAGE']

    global SCREENSIZE, SCREENDIST
    SCREENSIZE = ses['SCREENSIZE']# e.g. (59.8, 33.6) # physical display size in cm,  set with sessionInfo
    SCREENDIST = ses['SCREENDIST'] # e.g. 67.5 #distance from participant to screen,  set with sessionInfo

    global SCREENREFRESHRATE, SCREENFRAMETIME, pixPerCm
    SCREENREFRESHRATE = ses['SCREENREFRESHRATE'] #e.g. 100  set with sessionInfo
    SCREENFRAMETIME = int(1000/SCREENREFRESHRATE)
    pixPerCm = (DISPSIZE[0] / (2*SCREENSIZE[0])) + (DISPSIZE[1] / (2*SCREENSIZE[1])) 

    #EXPERIMENT INFO
    global GAZEREGION
    GAZEREGION = DegToPix(ses['GAZEREGION'] * 3, SCREENDIST, pixPerCm) #extra distance the gaze is allowed to drift from a ROI before the experiment takes action

    global ELLIPSESIZE
    ELLIPSESIZE =  (ses['GAZEREGION'] * DegToPix(1.74, SCREENDIST, pixPerCm), 
                    ses['GAZEREGION'] * DegToPix(3.48, SCREENDIST, pixPerCm)) #width, height (in visual degrees)

    #calculating the radius at which targets will be drawn


