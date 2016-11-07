'''
Created on Oct 30, 2012

@author: roehrig
'''

import wx
from epics import PV

class PVTimer(wx.Timer):
    '''
    This creates an object that monitors a PV for a change.  Every time that the PV
    changes, the timer is reset.  It takes a user supplied function that will be
    executed when the timer expires.
    
    timerOwner - the object that will receiver the wx.EVT_TIMER event
    pvName - the name of the pv to monitor for changes
    userFunction - a user supplied function that can be called whenever the timer expires
    hasMaxResets - True if there is a limited number of times that the userFunction should
                   execute without the timer being reset.  It should be false if 
                   pvName is None.
    timerID - a unique id for the timer object, it defaults to wx.ID_ANY
    '''
    def __init__(self, timerOwner, userFunction=None, pvName=None, hasMaxResets=False, timerID=wx.ID_ANY):
        '''
        Constructor
        '''
        super(PVTimer,self).__init__(timerOwner, timerID)
        if not (pvName is None):
            self._pv = PV(pvName, callback=self.PVTimerReset, form='native', auto_monitor=True)
        self._userFunction = userFunction
        self._timerLength = 10000
        self._numAutoResets = 3
        self._currentReset = 0
        self._userReturnVal = None
        self._owner = timerOwner
        if pvName is None:
            self._hasMaxResets = False
        else:
            self._hasMaxResets = hasMaxResets
        
        return
    
    def PVTimerStart(self, timeInSecs=10, resets=3, oneShot=False):

        self._timerLength = timeInSecs * 1000
        self._numAutoResets = resets
        self._currentReset = 0
        
        self.Start(self._timerLength, oneShot)    
        
        return
    
    def PVTimerStop(self):
        self.Stop()
        return
    
    def PVTimerReset(self, *args, **kwargs):
        if self.IsRunning():
            self.Start(self._timerLength)
            self._currentReset = 0
        return
    
    def Notify(self):
        
        # Increment the number of times that the timer has expired.
        if (self._hasMaxResets):
            self._currentReset = self._currentReset + 1            
        # If the number of times that the user function has been executed
        # is greater than or equal to the maximum, and the maximum is
        # greater than zero, stop the timer.
        if ((self._currentReset >= self._numAutoResets) and (self._numAutoResets > 0)):
            self.Stop()
        else:
            # Call the user supplied function that should run when the
            # timer expires.    
            self._userReturnVal = self._userFunction()

        # Send a timer event to the owner of this timer object.
        # Normally this does not happen if the Notify() method
        # is overridden.
        event = wx.PyCommandEvent(wx.EVT_TIMER.typeId, self._owner.GetId())
        wx.PostEvent(self._owner.GetEventHandler(), event)
        
        return
    
    def GetUserReturnVal(self):
        
        return self._userReturnVal
    
    def GetNumberOfResets(self):
        '''
        This returns the number of times that the timer has reset
        itself without the PV changing value.
        '''
        
        return self._currentReset