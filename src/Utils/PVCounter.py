'''
Created on Nov 13, 2012

@author: roehrig
'''

from epics import PV
from epics.wx import EpicsFunction
from epics.wx import DelayedEpicsCallback

class PVCounter(object):
    '''
    This class will monitor a PV that is increasing and save the PV value.
    When the PV reaches a user defined value, it executes a user supplied
    function and then resets itself to zero.
    '''

    def __init__(self, pvName, doneValue, function, display):
        '''
        Constructor
        
        pvName - The name of the PV to monitor
        doneValue - The value to monitor for
        function - A user supplied function
        display - A control used to show the current PV value
        '''
        self._countedPV = PV(pvName, callback=self.DoneCounting)
        self._doneCounting = doneValue
        self._doneFunction = function
        self._currentTotal = 0.0
        self._runningTotal = 0.0
        self._displayControl = display
        self._enable = False
        
        return
    
    def StartCounter(self):
        self.ResetCounter()
        self._enable = True
        return
    
    # This is the function that is called whenever the PV
    # value changes.  It is executed in its own thread.
    @DelayedEpicsCallback  
    def DoneCounting (self, **kwargs):
        if self._enable:
            # Save the PV value and update the display.
            self._currentTotal = self._countedPV.value
            self._displayControl.SetValue(str(self._currentTotal))
        
            # If the PV value is greater than the specified value,
            # execute the user supplied function and reset the
            # maintained value to zero.
            if (self._currentTotal >= self.__doneCounting):
                self._doneFunction()
                self._currentTotal = 0.0
            
        return
    
    def StopCounter(self):
        self._enable = False
        return
    
    @EpicsFunction        
    def ResetCounter (self):
        self._currentTotal = 0.0
        self._runningTotal = 0.0
        self._displayControl.SetValue(str(self._currentTotal))
        return
        
    def StopAndResetCounter(self):
        self.StopCounter()
        self.ResetCounter()
        return

class PVCounterWithUserFunctions(PVCounter):
    '''
    This inherits from PVCounter.  It differs in that it will execute a user
    supplied funtion when the counter is started and it will execute a separate
    function when the counter is finished.
    '''
    def __init__(self, pvName, doneValue, function, display, startFunction, endFunction):
        '''
        Constructor
        
        pvName - The name of the PV to monitor
        doneValue - The value to monitor for
        function - A user supplied function
        display - A control used to show the current PV value
        startFunction - A user supplied function that executes when the counter starts.
        '''
        
        PVCounter.__init__(self, pvName, doneValue, function, display)
        
        self._startFunction = startFunction
        self._endFunction = endFunction
        return
    
    def StartCounter(self):
        self._startFunction()
        PVCounter.StartCounter(self)
        return
    
    @DelayedEpicsCallback  
    def DoneCounting (self, **kwargs):
        if self._enable:
            self._currentTotal = self._countedPV.value
            self._displayControl.SetValue(str(self._currentTotal))
        
            if (self._currentTotal >= self._doneCounting):
                self._enable = False
                self._endFunction()
                self._doneFunction()
                self._currentTotal = 0.0
            
        return