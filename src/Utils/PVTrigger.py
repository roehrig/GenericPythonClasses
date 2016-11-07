'''
Created on Dec 12, 2012

@author: roehrig
'''
import wx
from epics import PV
from epics.wx import DelayedEpicsCallback

class PVTrigger(object):
    '''
    This creates an object that will monitor a PV and execute a user supplied
    function when that PV has a value specified by the user.
    '''

    def __init__(self, pvName, triggerValue, function, display):
        '''
        Constructor
        '''
        self._triggerPV = PV(pvName, callback=self.Trigger, connection_timeout=2)
        self._triggerValue = triggerValue
        self._triggeredFunction = function
        self._displayControl = display
        self._enable = False
        self._currentValue = self._triggerPV.value
        self._displayControl.SetValue(str(self._currentValue))
        
        return
    
    def StartTrigger(self):
        self._enable = True
        return
    
    @DelayedEpicsCallback  
    def Trigger (self, **kwargs):
        if self._enable:
            self._currentValue = self._triggerPV.value
            self._displayControl.SetValue(str(self._currentValue))
        
            if (self._currentValue == self._triggerValue):
                self._triggeredFunction(self._triggerPV)
            
        return
    
    def StopTrigger(self):
        self._enable = False
        return
    
    def SetTriggerValue(self, newValue):
        self._triggerValue = newValue
        return
    
    def GetTriggerValue(self):
        return self._triggerValue
    
class PVTriggerMultiple(PVTrigger):
    '''
    classdocs
    '''
    
    def __init__(self, pvName, triggerValue, function, display, status, owner, doneValue=0, time=1, iterations=1):
        '''
        Constructor
        '''
        PVTrigger.__init__(self, pvName, triggerValue, function, display)
        
        self._numIterations = iterations
        self._triggerTime = time
        self._period = (self._triggerTime * 1000) / self._numIterations
        self._doneValue = doneValue
        self._statusControl = status
        self._timer = wx.Timer(owner, -1)
        
        return
    
    def GetTimer (self):
        return self._timer
        
    @DelayedEpicsCallback
    def Trigger (self, **kwargs):
        if self._enable:
            self._currentValue = self._triggerPV.value
            self._displayControl.SetValue(str(self._currentValue))
            
            if (self._currentValue == self._triggerValue):
                self._timer.Start(self._period)
                
        return
    
    def ExecuteTrigger(self):
        self._triggeredFunction()
        self._triggerPV.put(self._doneValue)
        return
    