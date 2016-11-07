'''
Created on Nov 13, 2012

@author: roehrig
'''

import epics
import time
from epics.wx import EpicsFunction

class PVRecorder(object):
    '''
    classdocs
    '''


    def __init__(self, primaryPV, pvList, fileName):
        '''
        Constructor
        '''
        
        self.__primaryPV = primaryPV
        self.__pvList = pvList
        self.__fileName = fileName
        
        return
    
    @EpicsFunction
    def RecordValues(self):
        try:
            with open(self.__fileName, 'a') as fileHandle:
                print "Recording data"
                currentTime = time.strftime("%d %B %Y %H:%M:%S", time.localtime())
                line = "Data written %s.\n" % currentTime
                fileHandle.write(line)
                
                pvValue = epics.caget(self.__primaryPV, as_string=True)
                line = "%s : %s\n" % (self.__primaryPV, pvValue)
                fileHandle.write(line)
                
                for pv in self.__pvList:
                    pvName = pv.GetValue()
                    pvValue = epics.caget(pvName, as_string=True)
                    line = "%s : %s\n" % (pvName, pvValue)
                    fileHandle.write(line)
                    
                line = "End of data.\n\n"
                fileHandle.write(line)
                    
        except IOError as e:
            return
        
        return