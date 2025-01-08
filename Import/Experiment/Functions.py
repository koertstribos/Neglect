#this file contains functions used in the experiment
import math
import constants

# # # # constants # # # #
sqrt2 = math.sqrt(2)

# # # # functions # # # # 
#Distance method
#distance between two points
#scaled to the inverse of the scale, if it is given
#args:
#       pos1: the first point
#       pos2: the second point
#       scale: the scale to use (2-dimensional tuple)
#returns:
#       the distance between the two points, scaled to the given scale
def Distance(pos1, pos2, scale = None):
    if scale == None:
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
    else:
        dx = (pos1[0] - pos2[0]) / scale[0]
        dy = (pos1[1] - pos2[1]) / scale[1]
        
    res = math.sqrt(dx**2 + dy**2)
    return(res)

#GetRoughArea_Elliptical method
#returns
#   the rough area of an ellipse (a rectange that contains the ellipse)
def GetRoughArea_Elliptical(pos, widthAllowed, heightAllowed):
    xmin, xmax = pos[0] -widthAllowed/2, pos[0]+widthAllowed/2
    ymin, ymax = pos[1] -heightAllowed/2, pos[1]+heightAllowed/2

    return (xmin, xmax, ymin, ymax)

#CheckGazeElliptical_DuringStimulus method
#returns 
#   False if gaze is outside ellipse, or if gaze is blinking for longer than allowedBlinkDuration
#   True otherwise
def CheckGazeElliptical_DuringStimulus(pos, gc, ellipseDims, allowedBlinkDuration = 0):  
    if gc.Blink():
        return not gc.BlinkTimeOver(allowedBlinkDuration)
    return CheckGazeElliptical(pos, gc.track, ellipseDims)

#CheckGazeElliptical_InterStimulus method
#returns:
#   False if gaze is outside ellipse, or if blink detected
#   True otherwise
def CheckGazeElliptical_InterStimulus(pos, gc, ellipseDims):
    if gc.Blink():
        return False
    else:
        return CheckGazeElliptical(pos, gc.track, ellipseDims)

#CheckGazeElliptical method
#returns: 
#   False if gaze is outside ellipse
#   True otherwise
def CheckGazeElliptical(pos, tracker, ellipseDims):
    gazePos = tracker.sample()
    
    xmin, xmax, ymin, ymax = GetRoughArea_Elliptical(pos, ellipseDims[0], ellipseDims[1])
    
    # check if gaze falls outside of bounding rectangle
    if (gazePos[0] < xmin or gazePos[0] > xmax or gazePos[1] < ymin or gazePos[1] > ymax):
        return False

    #if gaze is within bounding rectangle, use Distance function, which scales the distance to the inverse of the ellipse dimensions
    return Distance(gazePos, pos, scale=ellipseDims) <= 1
    
    