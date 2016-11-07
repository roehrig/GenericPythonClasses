'''
Created on Nov 21, 2012

@author: roehrig
'''

import wx
import epics
from epics.wx import EpicsFunction

class PVText(wx.TextCtrl):
    '''
    This text control will check to see if a string that was entered is a vaild PV.
    When a key is pressed, a 2 second timer is started.  As long as another key is
    pressed, the timer is restarted.  When the timer expires, it tries to connect
    to the PV.  If successful, the text is set to black.  If not successful, the
    text is set to red.
    '''

    def __init__(self, parent, idNum=-1, value=wx.EmptyString, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, validator=wx.DefaultValidator, name=wx.TextCtrlNameStr):
        '''
        Constructor
        '''
        style = style | wx.TE_RICH
        wx.TextCtrl.__init__(self, parent, idNum, value, pos, size, style, validator, name)
        
        self._timer = wx.Timer(self, -1)
        
        self.Bind(wx.EVT_KEY_UP, self.OnKeyReleased, self)
        self.Bind(wx.EVT_TIMER, self.OnTimerExpired, self._timer)
        
        return
    
    def OnKeyReleased(self, event):
        self._timer.Start(2000)
        
        return
    
    @EpicsFunction
    def OnTimerExpired(self, event):
        self._timer.Stop()
        
        pvValue = epics.caget(pvname=self.GetValue(), timeout=1)
        
        if pvValue == None:
            self.SetForegroundColour(wx.RED)
        else:
            self.SetForegroundColour(wx.BLACK)
            
        return