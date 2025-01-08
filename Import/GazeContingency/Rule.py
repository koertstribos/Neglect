from typing import Callable


#Rule class
#saves a reference to a function, and Evaluates the function when called by Screen
class Rule:
    def __init__(self, interval: int, func:Callable[[], bool]):
        self.f = func
        self.interval = interval
        self.nextCall = 0

    #Evaluate method
    #if interval has passed after the last time this rule was evaluated,
    #   evaluate the rule and set a new nextCall time    
    #args:
    #   time: time in experiment at time of evaluation
    #returns:
    #   None if the rule is not evaluated
    #   boolean representing rule outcome if the rule is evaluated    
    def Evaluate(self, time):
        if time > self.nextCall:
            self.nextCall = time + self.interval
            return self._Evaluate()

    #_Evaluate method
    #Returns a function call 
    #returns
    #   the function outcome  
    def _Evaluate(self):
        return self.f()

