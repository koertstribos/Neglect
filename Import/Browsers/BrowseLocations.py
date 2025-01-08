
import os
import sys

#function up
#used to go up the directory tree
#args:
#       path: the starting path
#       levels: the number of levels to go up
#returns:
#       the path after going up the levels
def up(path, levels):
    if levels == 0:
        return path
    else:
        return up(os.path.dirname(path), levels-1)

#function GetBasePath
#used to get the base path of the application
#returns:
#       the base path of the application    
def GetBasePath():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (PyInstaller)
        base_path = sys._MEIPASS
    else:
        # If the application is run as a script
        base_path = up(os.path.dirname(os.path.abspath(__file__)), 2)
    return base_path

#function Data
#used to get the data folder path
#returns:
#       the path to folder 'Data', where data files are stored
def Data():
    return os.path.join(GetBasePath(), "Data")

#function Materials
#used to get the Materials folder path
#returns:
#       the path to folder 'Materials', where assets are stored
def Materials():
    return os.path.join(GetBasePath(), "Materials")

#function BlinkingGIF_folder
#used to get the folder path where the blinking GIF is stored
#returns:
#       the path to the folder where the blinking GIF is stored
def BlinkingGIF_folder():
    return os.path.join(Materials(), "Image_software", "blinkingImgs")

#function BlinkingGIF_list
#used to get the list of paths referencing all images that make up the blinking GIF
#returns:
#       a list of paths referencing all images that make up the blinking GIF
def BlinkingGIF_list():
    folder = BlinkingGIF_folder()
    res = os.listdir(folder)
    res.sort()
    
    return [os.path.join(folder, path) for path in res]

