#the class from which SessionInfo and ParticipantInfo and SetupInfo Inherit their stuff
#Also contains the DataInfoViewer class, which is used to couple a DataInfo object to a TKinter subscreen

import pickle
import os
from Import.Browsers.BrowseLocations import *

#DataInfoViewer class
#Used for coupling a DataInfo object to a TKinter subscreen
class DataInfoViewer:
    def __init__(self, dataInfo, TKinter):
        self.TKinter = TKinter
        self.dataInfo = dataInfo
        self._pickleFilename = None

        TKinter.DataInfoOverView(self)

    #dataInstances property
    #calling DataInfoViewer.dataInstances returns the list of dataInstances of the child dataInfo
    @property 
    def dataInstances(self):
        return self.dataInfo._dataInstances
    
    #GetWidgetList 
    #Returns a list of clickable widgets that link to dataInstances of the child dataInfo
    #For each widget, if the dataInstance is not locked, the widget is clickable and will call GotoEdit
    #args:
    #   tk: the TKinter object
    #   canvas: the canvas object
    #returns:
    #   a list of widgets
    def GetWidgetList(self, tk, canvas):
        
        #here two functions are defined that change the background color of the widget when the mouse hovers over it
        # '#f0f0f0' is the apparently default background color
        def on_mouse_over(event):
            event.widget.config(bg = "lightblue")    
        def on_mouse_leave(event):
            event.widget.config(bg = '#f0f0f0')

        res = []
        for dataInstance in self.dataInstances:
            widget = dataInstance.GetOverviewWidget(canvas)
            if not dataInstance.locked:
                widget.bind("<Button-1>", lambda event, x = dataInstance, y = tk: self.GotoEdit(dataInstance = x, tk = y))
                widget.bind("<Enter>", on_mouse_over)
                widget.bind("<Leave>", on_mouse_leave)            
            res.append(widget)
        return res

    #GotoEdit 
    #This function is called by clicking a dataInstance in GetWidgetList(), and calls the SimpleDialog function of that dataInstance
    #If the SimpleDialog function has a return value, this is a tuple pair of dataInstance types that need to be added to the list of dataInstances
    #The MaybeInsert function is called to insert the new dataInstances if it exists
    #args:
    #   dataInstance: the dataInstance that is clicked
    #   tk: the TKinter object
    #returns:
    #   None
    def GotoEdit(self, dataInstance, tk = None):
        res = dataInstance.SimpleDialog()
        self.dataInfo.MaybeInsert(dataInstance, res)
        self.TKinter.DataInfoOverView(self)

    #needsInput property
    #property for checking if all the dataInstances have been filled in
    @property 
    def needsInput(self):
        for di in self.dataInfo._dataInstances:
            if di.needsInput:
                return True
        return False

    #AttemptSave
    # calls dataInfo.SavePickle
    def AttemptSave(self):
        self.dataInfo.SavePickle()

    #AttemptDelete
    #calls dataInfo.DeletePickle
    def AttemptDelete(self):
        self.dataInfo.DeletePickle()

#DataInfo class
#base class for containing a set of DataInstances
#not for standalone use        
#subclasses of this class define specific sets (participantInfo, setupInfo, and sessionInfo)
class DataInfo:
    def __init__(self):
        self._dataInstances = []

    #picklepath property
    #the location that this object is saved in    
    #this is overwritten in subclasses
    @property 
    def picklepath(self):
        return "datainfo.pkl"

    #folder property
    #the folder in which this object is saved
    @property
    def datafolder(self):
        return Data()

    #filename property
    #the filename of this object
    #this is indirectly overwritten in subclasses
    @property 
    def filename(self):
        return self.proposedName + self.ext

    #identifyingDataInstance property
    #the identifyingDataInstance is the singular DataInstance that can be used as an alias for the entire DataInfo
    #it is defined as the first DataInstance of type filenameIdentifierType
    #filenameIdentifierType is a property that is defined in subclasses
    @property 
    def identifyingDataInstance(self):
        for di in self._dataInstances:
            if isinstance(di, self.filenameIdentifierType):
                return di
        raise Exception(f"no data instance of type {self.filenameIdentifierType}")

    #propsedName property
    #The proposed filename without extension for saving this DataInfo
    @property
    def proposedName(self):
        return str(self.identifyingDataInstance)

    #AppendUniqueIdentifier
    #Takes a string identifier, and appends it to the _result of the identifying DataInstance
    #this is done to ensure that no duplicate filenames are created
    #this is called by MakeIdentifierUnique
    #args:
    #   identifier: string, the identifier to append
    #returns:
    #   None
    def AppendUniqueIdentifier(self, identifier):
        self.identifyingDataInstance.Append("(" + str(identifier) + ")")

    #MakeIdentifierUnique 
    #       proposedName: current identifier
    #checks inside the save folder for any potential duplicate names, and generates an appendation to the identifier
    #changes the corrected proposedName by changing the dataInstance that contains the identifier
    #returns:
    #   None    
    def MakeIdentifierUnique(self):
        proposedName = self.proposedName + self.ext
        othernames = os.listdir(self.folder)
        
        #if the dataInfo object has been loaded from a pickle file,
        #it is logical that a file with the same name already exists
        #we can overwrite this name, so we remove the name from the list
        #if the name was in the list, we will overwrite it 
        if self.haspickle:
            try:
                othernames.remove(self._pickleFilename[-len(proposedName):])
            except Exception as e:
                pass

        #if the proposed name is not in the list of other names, we are done
        if proposedName not in othernames:
            return
        
        #an existing file already has the proposed name, so we need to find a new name
        #do this by adding a number to the proposed name
        i = 0
        while self.proposedName + f"({i})" + self.ext in othernames:
            i += 1
            
        self.AppendUniqueIdentifier(i)
                
    #MaybeInsert
    #this function is called whenever a dataInstance is filled in, and checks whether the dataInstance has a return value
    #if return value is not none, call insertion function (required for DataInstanceTypes.Enumerates)
    #args:
    #   dataInstance: a DataInstance object
    #   res: the result of the SimpleDialog function of the dataInstance
    #returns:
    #   None    
    def MaybeInsert(self, dataInstance, res):
        if res != None and res != False:
            print(f'res: {res}')
            self.InsertDataInstances(dataInstance, res)
    
    #InsertDataInstances 
    #Is called to insert a datainstance multiple times after a specific datainstance
    #   or to remove previously inserted datainstances
    #args:
    #   after: DataInstance after which the new DataInstance is inserted
    #   insertion: DataInstance that is inserted
    #returns:
    #   None     
    def InsertDataInstances(self, after, insertion):
        if after == 0:
            return
        
        insertionCount = insertion[1]
        insertionType = insertion[0]
        #get index of the dataInstance that will need to be inserted after
        index = self._dataInstances.index(after) + 1

        i = 0
        #for each item that needs to be inserted, 
        while index + i < index + insertionCount:
            if isinstance(self._dataInstances[index + i],insertionType):
                #if the item at that index is already of the correct type, do nothing
                pass
            else:
                #if the item at that index is a different index, insert a new item
                new = insertionType()
                self._dataInstances.insert(index + i, new)
            i += 1

        #afterwards, for each item after the current index that is the enumerated type
        #            remove that item
        while isinstance(self._dataInstances[index + i], insertionType):
            del self._dataInstances[index + i]
            
    #overviewText property
    #a text that is used as overview of the entire DataInfo         
    @property
    def overviewText(self):
        res = "do you want to edit? \n"
        for di in self._dataInstances:
            res += repr(di) + "\n"
        return res
    
    #__str__
    #returns the proposedName of the DataInfo
    def __str__(self):
        return self.proposedName
            
    #haspickle property
    #returns whether the DataInfo has a pickle file associated with it
    @property
    def haspickle(self):
        if hasattr(self, '_pickleFilename') and self._pickleFilename != None:
            return True
        else:
            return False

    #LoadPickle
    #loads DataInfo from given path and returns it
    #version stability: if any new dataInstances are added to the class that is loaded
    #   Those dataInstances are quickly added to the loaded dataInfo object
    #args:
    #   path: string representing the path of the pickle file
    #returns:
    #   DataInfo object    
    @staticmethod
    def LoadPickle(path):
        with (open(path, "rb")) as pklfile:
            res = pickle.load(pklfile)
            res._pickleFilename = path
            # Create a new object of the same class as res
            new_res = type(res)()
            # for all dataInstance in res, check if they are in res
            for di in new_res._dataInstances:
                for di0 in res._dataInstances:
                    if type(di) == type(di0):
                        break
                else:
                    res._dataInstances.append(di)
            
            return res
                
    #SavePickle
    #Saves DataInfo to own path
    #returns:
    #   None    
    def SavePickle(self):
        self.MakeIdentifierUnique()
        pklFile = open(self.picklepath, 'wb')
        pickle.dump(self, pklFile)
        pklFile.close()
        print(f"Saved DataInfo at {self.picklepath}")

    #DeletePickle
    #Deletes Pickle from own path
    #returns:
    #   None    
    def DeletePickle(self):
        #find the file that belongs to this datainfo
        try:
            os.remove(self.picklepath)

        except Exception as e:
            print(e)
            print("error while deleting pickle.")

    #CreateFromScratch
    #Creates a new DataInfo from scratch
    #Used when no DataInfoViewer is used
    #Instead of presenting all items at once, each item is requested serially.
    #returns:
    #   DataInfo object        
    @classmethod
    def CreateFromScratch(cls):
        newDataInfo = cls()
        for di in newDataInfo._dataInstances:
            if di.value == None:
                res = di.SimpleDialog()
                newDataInfo.MaybeInsert(di, res)
                
        return newDataInfo








        