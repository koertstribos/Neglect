#this file contains the lowest level data instances, which are used to define how data is stored, and manipulated
#The Class DataInstance contains base neccessities for datainstances
#then, multiple sublclasses are defined here which specificy the type of data that is stored and sometimes further specify how the data is manipulated
#Defining the actual names of each data entry is done in the file DataInstances.py


from datetime import datetime
from tkinter import *
from tkinter import messagebox
from typing import Any
from tkinter import ttk
from tkinter import simpledialog
from Import.SessionData.DataInfo import DataInfo as DI
import threading


#functions

#decorator to ensure a function is ran on the main thread
#source: GitHub Copilot
#should prevent the 'Tcl_AsyncDelete: async handler deleted by the wrong thread' error ??? (not 100% sure if this always works, I have been getting mixed results)
#args:
#   func: callable
#returns:
#   wrapper: callable
def run_on_main_thread(func):
    def wrapper(*args, **kwargs):
        if threading.current_thread() is not threading.main_thread():
            root = Tk()
            result = None
            def run_func():
                nonlocal result
                result = func(*args, **kwargs)
                root.quit()
            root.after(0, run_func)
            root.mainloop()
            return result
        else:
            return func(*args, **kwargs)
    return wrapper

#function to check if an object is iterable
#To check if an object is iterable in Python, the iter function is used, and a TypeError is raised if the object is not iterable.
#args:
#   obj: Any
#returns:
#   bool: True if the object is iterable, False if the object is not iterable
def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

# # # # #
#objects#
# # # # #    

#a DataInstance defines a singular data entry
#subclasses of DataInstance are used to define data format
#lowest level sublclasses are used to define actual data (see DataInstances.py)
class DataInstance():
    def __init__(self):
        self._question = "Some data thing"
        self._defaultAnswer = "-"
        self._printHeader = "Data: "
        self._type = str
        self._locked = False

    #TrySetAnswer is called with the answer, and sets the answer if it is valid
    #When the answer is invalid enough to warrant an exception, this is printed and the code continues
    #args:
    #   answer: any, is checked to match self.type    
    #returns: 
    #   False on failure, None on success
    def TrySetAnswer(self, answer):
        try:
            self._result = self._type(answer)
            self.PrepareRead()
        except Exception as e:
            print("Exception in TrySetAnswer(")
            print(e)
            return False
        
    #PrepareRead
    #Sets the defaultAnswer to result if it exists
    #returns:
    #   None    
    def PrepareRead(self):
        if hasattr(self, "_result"):
            self._defaultAnswer = self._result

    #Append
    #Appends a string to the data entry result
    #used to append an identifier to the name of a file to ensure that no duplicate files are created (In DataInfo.py DataInfo.AppendUniqueIdentifier())    
    #args:
    #   appendation: string, that is appended to the result
    #returns:
    #   None    
    def Append(self, appendation):
        if hasattr(self, "_result"):
            self._result = str(self._result) + str(appendation)

    #answerInvalidErrorText
    #the text that is shown on an invalid input
    @property
    def answerInvalidErrorText(self):
        return "Invalid answer"
    
    #value
    #property that obtains the result, or None if no result exists
    @property
    def value(self):
        if hasattr(self, '_result'):
            return self._result
        else:
            return None

    #locked
    #property that returns whether the data entry is locked    
    @property
    def locked(self):
        if hasattr(self, '_locked'):
            return self._locked
        else:
            return False
        
    #SetLock
    #Function that locks a DataInstance
    #args:
    #     value: any
    #returns:
    #    None
    def SetLock(self, value):
        self._locked = True

    #question
    #the question that is shown to the user when they fill in this entry
    #refers to self._question, which is overwritten in the lowest sublcasses
    @property
    def question(self):
        return "Please enter " + self._question

    #simpledialog
    #returns the result of a simpledialog requesting input
    @property
    def simpledialog(self):
        self.PrepareRead()
        return simpledialog.askstring("Input", self.question, initialvalue=self._defaultAnswer)

    #SimpleDialog
    #Function that calls a simpledialog and tries to set the answer with the resulting value
    #Returns:
    #    None if the user cancels the dialog, or the result of TrySetAnswer()
    @run_on_main_thread
    def SimpleDialog(self):
        res = self.simpledialog
        if res is not None:
            #return to overview, with answer filled in
            return self.TrySetAnswer(res)
        else:
            #return to previous overview, no answer given
            return None

    #property for checking whether the entry has an answer
    @property 
    def needsInput(self):
        return not hasattr(self, "_result")

    #__str__
    #returns the result of the data entry in string format, or "No_answer" if no result exists
    def __str__(self):
        if self.needsInput:
            return "No_answer"
        else:
            return str(self._result)

    #__repr__
    #returns the printHeader and __str__ of the data entry
    def __repr__(self):
        return self._printHeader + str(self)

    #return an overview widget (usually a label limited to 60 chars)
    #args:
    #   root: tkinter root
    #returns:
    #   Label: a label with the __repr__ of the data entry
    def GetOverviewWidget(self, root):
        res = Label(root, text=repr(self)[:60])
        if self.locked:
            res.config(fg="gray")
        return res
        
#Text
#Textual data entry
class Text(DataInstance):
    def __init__(self):
        super().__init__()
        self._type = str
        

#Option
#Option data entry
class Option(DataInstance):
    def __init__(self, options):
        super().__init__()
        self._type = str
        if options != None:
            self._options = options

    #"simple" dialog
    #We cannot use a basic tkinter messagebox for this
    #Instead we make a quick tkinter window
    @run_on_main_thread    
    def SimpleDialog(self):
        def SetAnswer():
            res = self.TrySetAnswer(selectedOption.get())
            root.destroy()
            root.quit()
            return res

        root = Tk()
        root.title("Dropdown Menu")


        options = self._options
        selectedOption = StringVar(root)

        if hasattr(self, "_result"):
            #find _result in options. If it does not exist, choose the last option
            try:
                index = options.index(self._result)
            except:
                index = -1
            selectedOption.set(options[index])
        else:
            selectedOption.set(options[0])

        questionLabel = Label(root, text=self.question)
        questionLabel.pack()

        dropdown = OptionMenu(root, selectedOption, *options)
        dropdown.pack()
        buttonYes = Button(root, text="Select", command=SetAnswer)
        buttonYes.pack()

        root.mainloop()

    @property
    def question(self):
        return "Please select " + self._question
    
#Option_specifyOther
#Option data entry, but with one option specified as 'other', which the user can fill in themselves    
class Option_specifyOther(Option):
    def __init__(self, options):
        #add "other" to options if it does not exist yet
        if "other" not in options:
            options.append("other")
        super().__init__(options)

    #simpleDialogInitialValue
    #a string that either contains the result of the dataInstance, or 'unspecified'    
    @property
    def simpleDialogInitialValue(self):
        if hasattr(self, "_result"):
            return self._result
        else:
            return "unspecified"
        
    #We only need to overwrite this function to make sure that the user can specify their own answer
    def TrySetAnswer(self, answer):
        if answer == "other":
            answer = simpledialog.askstring("Input", "Please specify", initialvalue=self.simpleDialogInitialValue)
            if answer is None:
                return None
            
            
        super().TrySetAnswer(answer)
        

#DataInfo
#reference to another dataInfo container
#subclass of 'Option', as the user can select a dataInfo save 
#additionally, we add an option for a 'new' dataInfo (see TrySetAnswer)        
#TODO: Change it so that the DataInfo reference is cloned and saved seperately from the DataInfo it originated from        
class DataInfo(Option):
    def __init__(self, optionPaths, dataType):
        
        self.dataType = dataType
        self._paths = optionPaths
        
        DIoptions = [DI.LoadPickle(path) for path in optionPaths]
        optionsText = [di.proposedName for di in DIoptions]
        optionsText.append("new")
        
        super().__init__(optionsText)
        self._defaultAnswer = "new"
        
    #TrySetAnswer
    #if the answer is 'new', a new dataInfo is created using DataInfo.CreateFromScratch(), and the path is returned
    #Note that the newly created dataInfo is saved just like any other dataInfo.
    #args:
    #   answer: a string
    #returns:
    #   False on failure, None on success    
    def TrySetAnswer(self, answer):
        if answer == "new":
            dataInstance = self.dataType.CreateFromScratch()
        else:
            path = self._paths[self._options.index(answer)]
            dataInstance = self.dataType.LoadPickle(path)
            
        try:
            self._result = dataInstance
            self.PrepareRead()
        except Exception as e:
            print("Exception in DataInstanceTypes.DataInfo.TrySetAnswer(")
            print(e)
            return False
        
        
    #Overwrite the value property so that it returns the dataInfo object, which is loaded from the path
    @property
    def value(self):
        if hasattr(self, "_result"):
            return self._result
        else:
            return None
        
    #SimpleDialog
    #returns:
    #   super().SimpleDialog() or None   
    @run_on_main_thread
    def SimpleDialog(self):
        if not hasattr(self, "_result"):
            return super().SimpleDialog()
        #else, show an overview of the selected dataInfo
        subDI = self.value
        if messagebox.askyesno("Overview", subDI.overviewText):
            for di in subDI._dataInstances:
                di.SimpleDialog()

       
#OrderedSelection
#contains a list of options, which can be re-ordered
#result is an array of True/False
#the options are saved in self._options        
class OrderedSelection(DataInstance):
    def __init__(self, options):
        
        super().__init__()
        self._type = list
        self._options = list(options)
        
    #just like the Option class, we need to make a custom dialog
    @run_on_main_thread
    def SimpleDialog(self):
        
        root = Tk()
        root.title("Selection Menu")

        options = self._options

        results = []
        
        #get results. If they exist read them. Else, set all results to False
        if hasattr(self, "_result"):
            #read results
            for res in self._result:
                results.append(BooleanVar(value=res))
        else:
            for _ in options:
                results.append(BooleanVar(value=True))
        
        def Move(optionIndex, direction):
            index = optionIndex
            if direction == "left":
                if index > 0:
                    for _list in (options, results):
                        _list[index], _list[index - 1] = _list[index - 1], _list[index]
                    
            elif direction == "right":
                if index < len(self._options) - 1:
                    for _list in (options, results):
                        _list[index], _list[index + 1] = _list[index + 1], _list[index]
                        
            RePackOptions()
            
        def Select(optionIndex):
            index = optionIndex
            results[index].set(not results[index].get())
            RePackOptions()

        def SetAnswer():
            res = self.TrySetAnswer((options, results))
            root.destroy()
            root.quit()
            return res
            
        def RePackOptions():            
            
            #remove all widgets
            for widget in root.winfo_children():
                widget.grid_forget()

            questionLabel = Label(root, text=self.question)
            questionLabel.grid(row=0, column=0, columnspan=len(options), pady=10)

            #create widget for 'save'
            buttonSave = Button(root, text="Save", command = SetAnswer)
            buttonSave.grid(row = 2, column = 0, pady=10)

            for index, option in enumerate(options):
                #make a slave frame that represents an option
                #the slave frame should contain a left and right button to move order, and a checkbox to (de)select

                #get colour
                if results[index].get():
                    colourFg = "black"
                else:
                    colourFg = "grey"

                #make the frame
                frame = Frame(root, highlightbackground="grey", highlightthickness=1)
                frame.grid(row = 1, column = index, padx= 2)
                
                #make a label with the option text
                label = Label(frame, fg=colourFg,text=option)
                label.pack()
                
                #left and right buttons
                buttonLeft = Button(frame, text = "<", fg=colourFg, command = lambda x=index: Move(x, "left"))
                buttonLeft.pack(side=LEFT)
                buttonRight = Button(frame, text = ">", fg=colourFg, command = lambda x=index: Move(x, "right"))
                buttonRight.pack(side=RIGHT)
                
                #checkbox
                checkbox = Checkbutton(frame, variable=results[index], fg=colourFg, command= lambda x=index: Select(x))
                if results[index].get():
                    checkbox.select()
                checkbox.pack(side=LEFT)

        RePackOptions()
        root.mainloop()

    #TrySetAnswer
    #modified function that accepts a tuple as answer arg
    #the tuple is split into self._options and self._result
    #args:
    #   answer: tuple
    #returns:
    #   None 
    def TrySetAnswer(self, answer):
        options, results = answer
        try:
            self._options = options
            self._result = [res.get() for res in results]
        except Exception as e:
            print("Error in DataInstanceTypes.OrderedSelection.TrySetAnswer")
            print(e)

    #string representation of the result
    #returns each selected option, separated with comma, contained in square brackets        
    def __str__(self):
        if hasattr(self, "_result"):
            res = "["
            for option, result in zip(self._options, self._result):
                if result:
                    res += f"{option}, "
            return res[:-2] + "]"
        else:
            return "default"
        
    #value property
    #returns a list of results that have been selected    
    @property
    def value(self):
        if hasattr(self, "_result"):
            res = []
            for option, result in zip(self._options, self._result):
                if result:
                    res.append(option)
            return res
        else:
            return None
        
#float
#float data entry
class Float(DataInstance):
    def __init__(self):
        super().__init__()
        self._type = float
        
    #overwrite the simpledialog function to 'askfloat'
    @property
    def simpledialog(self):
        answer = simpledialog.askstring("Input", self.question, initialvalue=self._defaultAnswer)
        if answer is not None:
            answer = answer.replace(",", ".")
            try:
                answer = float(answer)
            except:
                messagebox.show(error="please enter a number")
                return self.simpledialog()
            
        return answer

#Int
#Integer data entry
class Int(DataInstance):
    def __init__(self):
        super().__init__()
        self._type = int

    #overwrite the simpledialog function to 'askinteger'
    @property
    def simpledialog(self):
        return simpledialog.askinteger("Input", self.question, initialvalue=self._defaultAnswer)

#RoundedInt
#rounded integer data entry
class RoundedInt(Int):
    def __init__(self, rounding = 1):
        self._rounding = rounding
        super().__init__()
        self._type = int

    def __repr__(self):
        res = self._printHeader + str(self)
        return res

    #TrySetAnser 
    #this function rounds the answer, and then calls the higher-order TrySetAnswer
    #args:
    #   answer: int, or something that can cast to int
    #returns:
    #   super().TrySetAnswer()
    def TrySetAnswer(self, answer):
        try:
            answer = int(answer)
            answer = round(answer / self._rounding) * self._rounding
        except Exception as e:
            print("Exception in DataInstanceTypes.RoundedInt.TrySetAnswer():")
            print(e)
            pass

        return super().TrySetAnswer(answer)

#Enumerate
#Number of times a different DataInstance is repeated
#e.g. for previous tests: Enumerate is used to track how many previous tests get an entry
#The __init__ for Enumerate needs a reference to the DataInstance that is enumerated
class Enumerate(DataInstance):
    def __init__(self, enumerates):
        super().__init__()
        self._defaultAnswer = 0
        self._type = int
        self._enumerates = enumerates

    #special case of SimpleDialog: 
    #returns a tuple set of (type, int)
    #generally, that type is added int times after this DataInstance (See DataInfo.CreateFromScratch() and DataInfoViewer.GoToEdit() in DataInfo.py. 
    #   Both funcitons use the return type of SimpleDialog in a call to MaybeInsert()))
    @run_on_main_thread    
    def SimpleDialog(self):
        super().SimpleDialog()
        if hasattr(self, "_result"):
            return (self._enumerates, self._result)
        else:
            return None

#Date
#Date (Saved as string)
class Date(DataInstance):
    def __init__(self):
        super().__init__()
        self._defaultAnswer = datetime.now().date()
        self._type = str
        

#Multiple
#A set of Multiple DataInstances
#useful for when multiple questions are asked regarding one subject, such as a previously taken test.
#The __init__ function takes a List of class references to all the contained DataInstances        
#Each DataInstance in the set is probed in sequence
class Multiple(DataInstance):
    def __init__(self, subDataInstanceClasses):
        super().__init__()
        self._subDataInstances = []
        for subDIC in subDataInstanceClasses:
            self._subDataInstances.append(subDIC())
        self._printHeader = "Multiple"
        self._defaultAnswer = None
        self._type = None

    #overwrite the PrepareRead function to do nothing
    def PrepareRead(self):
        pass
    
    #SimpleDialog
    #calls all the SimpleDialog functions of the contained DataInstances
    @run_on_main_thread
    def SimpleDialog(self):
        for subDI in self._subDataInstances:
            subDI.SimpleDialog()

    @property
    def needsInput(self):
        for subDI in self._subDataInstances:
            if subDI.needsInput:
                return True
        return False

    @property
    def _result(self):
        res = ""
        for subDI in self._subDataInstances:
            res.append(str(subDI))
            res.append('\n')
        return res

    def __str__(self):
        return "Multiple answers"

    def __repr__(self):
        res = self._printHeader
        if self.needsInput:
            pass
        else:
            res += " ..."
        return res
    

    #GetOverviewWidget
    #args:
    #   root: tkinter root
    #returns:
    #    Label with the __repr__ of the data entry
    def GetOverviewWidget(self, root):
        res = Label(root, text=repr(self)[:60])
        return res

    #TrySetAnswer
    #args:
    #   answers: list of answers
    #returns:
    #   None
    def TrySetAnswer(self, answers):
        if len(answers) != len(self._subDataInstances):
            raise Exception("given answers do not match number of subDataInstances")
        for subDi, answer in zip(self._subDataInstances, answers):
            subDi.TrySetAnswer(answer)
            

#ExperimentResult
#result of the experiment
#These are appended to a sessionInfo after the experiment is completed
#not really a flashy object    
class ExperimentResult(Float):
    def __init__(self):
        super().__init__()
        
        




