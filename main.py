from Import.TKinter.TKinterMain import NeglectTKinterMainScreen
from Import.TKinter.TKinterSubs import ExperimentLauncher, SessionViewer, SetupViewer, ParticipantViewer, InstructionViewer

#define the subs, which are passed to the main screen Initialisation function
subs = [ExperimentLauncher(), SessionViewer(), SetupViewer(), ParticipantViewer(), InstructionViewer()]

#initialise the main screen, and call mainloop()
mainScreen = NeglectTKinterMainScreen(subs)
mainScreen.mainloop()

