#this file contains functions used for DataInstance and DataInfo objects

#SeachsSubInstances method
#function to search all dataInstances that are kept within a 'multiple' datainstance object
#args:
#   dataInstance: the dataInstance object to search
#   instanceType: the type of dataInstance to search for
#returns:
#   the dataInstance of the requested type if it is found, None otherwise
def SearchSubInstances(dataInstance, instanceType):
    if hasattr(dataInstance, "_subDataInstances"):
        for sub in dataInstance._subDataInstances:
            if isinstance(sub, instanceType):
                return sub
            subSearch = SearchSubInstances(sub, instanceType)
            if subSearch != None:
                return subSearch
        

#GetDataInstanceObject
#function to get a dataInstance of a certain type from a DataInfo object
#args:
#   dataInfo: the DataInfo object to search            
#   instanceType: the type of the dataInstance to search for
#returns:         
#      the dataInstance of the requested type if it is found, None otherwise
def GetDataInstanceObject(dataInfo, instanceType):
    for di in dataInfo._dataInstances:
        if isinstance(di, instanceType):
            return di
        subSearch = SearchSubInstances(di, instanceType)
        if subSearch != None:
            return subSearch
        
    return None

#GetDataInstance method
#function to get the value of a dataInstance of a certain type from a DataInfo object
def GetDataInstance(dataInfo, instanceType):
    res = GetDataInstanceObject(dataInfo, instanceType)
    if res != None:
        return res.value
    
    #if no dataInstance of the requested type is found, return None
    return None

#SetDataInstance method
#set the value of a dataInstance of a certain type in a DataInfo object.
# If it doesn't exist, make a new one
#args:
#   dataInfo: the DataInfo object to search
#   instanceType: the type of the dataInstance to search for
#   value: the value to set the dataInstance to
#returns:
#   None
def SetDataInstance(dataInfo, instanceType, value):
    res = GetDataInstanceObject(dataInfo, instanceType)
    if res != None:
        res.TrySetAnswer(value)
    else:
        new = instanceType()
        new.TrySetAnswer(value)
        dataInfo._dataInstances.append(new)