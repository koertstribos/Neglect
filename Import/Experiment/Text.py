import os
from tkinter import *
from tkinter import messagebox
from Import.SessionData.DataInstanceTypes import run_on_main_thread
from Import.Browsers.BrowseLocations import *
        
#Text class
#This class is used to load text in the experiment
#It can be used to load text in different languages
class Text():
    def __init__(self, language = None):
        #if no language is given, use the default language english
        if language != None:
            self.language = language
        else:
            self.language = "english"

        #create a dictionary to store the text
        self.dict = {}
        #look for language file that matches the language
        #if not found, use default language (english)
        txtPath = os.path.join(Materials(), "Instructions", str(language)+".txt")
        print(f"language txtPath={txtPath}")
        if not os.path.exists(txtPath):
            txtPath = os.path.join(Materials(), "Instructions", "english.txt")
        try:
            with open(txtPath, "r") as f:
                lines = f.readlines()
        except:
            lines = []
        #read all lines in the txt file and store them in the dictionary
        for line in lines:
            key, text = line.split(";")
            self.dict[key.strip()] = text.strip()

    #languageOptions method
    #returns a list of available languages
    #by reading all filenames at /Materials/Instructions, and stripping .txt
    @staticmethod
    def languageOptions():
        startPath = os.path.join(Materials(), "Instructions")
        files = os.listdir(startPath)
        return [file.replace(".txt", "") for file in files]

    #__getitem__ method
    #calls __getitem__ on self.dict (where the text is saved)
    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        else:
            return "The experimenter will explain the research. \n They can press space to start the experiment"
        
#TextEditor class
#This class is used to edit instructions
#It is comparible with DataInfoViewer classes, but does not contain DataInstances
class TextEditor():
    def __init__(self, path, TKinter):
        self.TKinter = TKinter
        self.texts = {}
        self.path = path

        print(f"loading textfile at {path}")
        
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    key, text = line.split(";")
                    self.texts[key.strip()] = text.strip()
        except Exception as e:
            print(f"error loading {path}")
            print(e)
            raise Exception(e)
        
        self.altTexts = {}
        #read all items in baseLanguage
        baseLanguage = Text()
        for key, item in baseLanguage.dict.items():
            self.altTexts[key] = item  
            
        TKinter.TxtOverView(self)

    #FromScratch method
    #create a new language, given the name of that language
    #the user will have to fill in the instruction texts themselves
    @staticmethod
    def FromScratch(languageName, tkinter):
        txtPath = os.path.join(Materials(), "Instructions", str(languageName)+".txt")
        baseLanguage = Text()
        #create txt file and write all keys from baseLanguage
        with open(txtPath, "w") as f:
            for key in baseLanguage.dict:
                f.write(f"{key.strip()};-\n")

        return TextEditor(txtPath, tkinter)

    #SimpleDialog method
    #create a dialog to edit a single instruction
    @run_on_main_thread
    def SimpleDialog(self, key):
        def EnterPressHandler(e):
            #discard e
            SetAnswer()

        def SetAnswer():
            try:
                res = answer.get()
                self.texts[key] = res
            except Exception as e:
                print("error setting answer", e)
                
            root.destroy()
            root.quit()
            return

        root = Tk()
        root.title(f"setting key {key}")
        
        explLabel = Label(root, text="English text:")
        explLabel.pack()
        altTextLabel = Label(root, text=self.altTexts[key])
        altTextLabel.pack()

        explLabel2 = Label(root, text="Translated text:")
        explLabel2.pack()

        res = self.texts[key]
        answer = Entry(root, width=69)
        answer.insert(0, res)
        
        answer.pack()

        buttonYes = Button(root, text="Set", command=SetAnswer)
        buttonYes.pack()
        root.bind('<Return>',EnterPressHandler)

        root.mainloop()
        
    #GotoEdit method
    #function that calls SimpleDialog method
    #GotoEdit is bound to text widgets in GetWidgetList    
    def GotoEdit(self, key, tk = None):
        self.SimpleDialog(key)
            
        self.TKinter.TxtOverView(self)

    #GetWidgetList method
    #returns a list of widgets that show the instruction keys and text
    #widgets are clickable    
    def GetWidgetList(self, tk, canvas):
        #here two functions are defined that change the background color of the widget when the mouse hovers over it
        def on_mouse_over(event):
            event.widget.config(bg = "lightblue")    
        def on_mouse_leave(event):
            event.widget.config(bg = '#f0f0f0')

        #create a list of widgets that show the key
        #each widget is clickable, which triggers the function GotoEdit    
        res = []
        for key in self.texts:
            widget = Label(canvas, text=key)
            widget.bind("<Button-1>", lambda event, x = key, y = tk: self.GotoEdit(key = x, tk = y))
            widget.bind("<Enter>", on_mouse_over)
            widget.bind("<Leave>", on_mouse_leave)            
            res.append(widget)
        return res
    

    #AttemptSave method
    #attempts to save the Text object as txt file
    def AttemptSave(self):
        #check if all keys are present
        baseLang = Text()
        
        self._texts = self.texts
        self.texts = {}
        
        for key in baseLang.dict:
            if key in self._texts:
                self.texts[key] = self._texts[key]
            else:
                print(f"key {key} not found in language")
                self.texts[key] = baseLang.dict[key]

        #save the texts to a txt file
        with open(self.path, "w") as f:
            for key, text in self.texts.items():
                interpolatedString = f"{key};{text}".strip()
                interpolatedString += "\n"
                print(interpolatedString)
                f.write(interpolatedString)
            
    #AttemptDelete method
    #attempts to delete the associated text file
    #does not work for the language english            
    def AttemptDelete(self):
        #check if language is not english
        if self.path.endswith("english.txt"):
            messagebox.showinfo(title = "error", message="English instructions cannot be deleted")
            return
        
        #delete the txt file
        os.remove(self.path)
        