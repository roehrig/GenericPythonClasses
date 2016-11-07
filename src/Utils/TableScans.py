'''
Created on Dec 7, 2012

@author: roehrig
'''

import math
import wx
import epics
from epics import PV
from epics.wx import DelayedEpicsCallback
from numpy import zeros

class ScanSection(object):
    '''
    classdocs
    '''
    def __init__(self):
        
        self._start = 0.0
        self._end = 0.0
        self._stepSize = 0.0
        self._stepCount = 0
        
        return
    
    def SetStart (self, startVal):
        '''
        Set the start point of the scan section.
        
        startVal - The value of the starting point.
        '''
        try:
            self._start = float(startVal)
        except TypeError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetStart", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        except ValueError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetStart", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        return
    
    def SetEnd (self, endVal):
        '''
        Set the end point of the scan section.
        
        endVal - The value of the starting point.
        '''
        try:
            self._end = float(endVal)
        except TypeError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetEnd", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        except ValueError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetEnd", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        return
    
    def SetStepSize(self, sizeVal):
        '''
        Set the step size of the scan section.
        
        sizeVal - The value of the step size, the distance between each point.
        '''
        try:
            self._stepSize = float(sizeVal)
        except TypeError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetStepSize", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        except ValueError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetStepSize", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        return
    
    def SetStepCount(self, countVal):
        '''
        Set the number of points in the scan section.
        
        countVal - The value of the number of points in the section.
        '''
        try:
            self._stepCount = int(countVal)
        except TypeError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetStepCount", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        except ValueError as e:
            dialogBox = wx.MessageDialog(self, e, caption="Error in class ScanSection:SetStepCount", style=wx.ICON_ERROR)
            dialogBox.ShowModal()
            dialogBox.Destroy()
        return
    
    def GetStart(self):
        return self._start
    
    def GetEnd(self):
        return self._end
    
    def GetStepSize(self):
        return self._stepSize
    
    def GetStepCount(self):
        return self._stepCount
    
    def CalculateStepSize(self):
        if (not self._start == self._end) and (self._stepCount > 1):
            self.SetStepSize((self._start - self._end) / (self._stepCount - 1))
        return
        
    def CalculateStepCount(self):
        if (not self._start == self._end) and (not self._stepSize == 0):
            self.SetStepCount(int(math.fabs(int((self._start - self._end) / self._stepSize)) + 1))
        return
    

class TableScan(object):
    '''
    classdocs
    '''
    def __init__(self, scan, function):
        '''
        Constructor
        
        scan - the name of the scan record, e.g. xxx:scan1
        function - a function that is called whenever a positioner is changed
                   in the scan record
        '''
        self._totalNumPoints = 0
        self._sectionList = [[] for i in range(4)]
        self._positionersList = []
        self._scanRecord = scan
        self._positionersValid = True
        self._scanValid = False
        self._posCallbackFunction = function
        self._scanType = "TableScan"
        
        # Create the positioner PV objects and add a callback to each of them.
        # The index is used to identify which positioner is calling the callback
        # function.
        pos1 = PV(pvname='%s.P1PV' % scan)
        pos1.add_callback(self.PositionerChangedCallback, index=0)
        pos2 = PV(pvname='%s.P2PV' % scan)
        pos2.add_callback(self.PositionerChangedCallback, index=1)
        pos3 = PV(pvname='%s.P3PV' % scan)
        pos3.add_callback(self.PositionerChangedCallback, index=2)
        pos4 = PV(pvname='%s.P4PV' % scan)
        pos4.add_callback(self.PositionerChangedCallback, index=3)
        
        self._positionersList.append(pos1)
        self._positionersList.append(pos2)
        self._positionersList.append(pos3)
        self._positionersList.append(pos4)        
        
        return
    
    def SetScanRecord(self, scan):
        self._scanRecord = scan
        return
    
    def GetScanRecord(self):
        return self._scanRecord
    
    def GetPositionersValid(self):
        return self._positionersValid
    
    def SetTotalNumPoints(self, numPoints):
        self._totalNumPoints = float(numPoints)
        return
    
    def GetTotaNumPoints(self):
        return self._totalNumPoints
    
    def SetPosCallbackFunction(self, function):
        self._posCallbackFunction = function
        return
    
    def GetPosCallbackFunction(self):
        return self._posCallbackFunction
    
    def GetPositionerList(self):
        return self._positionersList
    
    def SetPositioner(self, positionerNum, positionerName):
        '''
        Change the PV used as a positioner in the scan record.
        
        positionerNum - the positioner number, 1 - 4
        positionerName - the name of the new PV to use
        '''
        
        self._positionersList[(positionerNum - 1)].put(positionerName)
        return
    
    def AddSection (self, start, end, positioner, steps=0, size=0.0):
        '''
        Add a section of points to the table scan.  The number
        of steps and the step size must be greater than
        zero.
        
        start - starting point of this section
        end - ending point point of this section
        steps - the number of steps in this section
        size - the step size
        '''
        if (steps <= 0) or (size <= 0):
            raise ValueError('The number of steps and step size must be greater than zero.')
        else:
            newSection = ScanSection()
            newSection.SetStart(start)
            newSection.SetEnd(end)
            newSection.SetStepCount(steps)
            newSection.SetStepSize(size)
        
            self._sectionList[positioner - 1].append(newSection)
        return
    
    def ModifySection (self, sectionNum, start, end, steps, size):
        '''
        Modify a previously added section of the table scan.
        The section number must be positive, while the number
        of steps and step size must be greater than zero.
        
        start - starting point of this section
        end - ending point point of this section
        steps - the number of steps in this section
        size - the step size
        '''
        if sectionNum < 0:
            raise ValueError('The section number must be positive.')
        else:
            if (steps <= 0) or (size <= 0):
                raise ValueError('The number of steps and step size must be greater than zero.')
            else:
                currentSection = self._sectionList[sectionNum]
                currentSection.SetStart(start)
                currentSection.SetEnd(end)
                currentSection.SetStepCount(steps)
                currentSection.SetStepSize(size)
                
        return
    
    def IsTableScanValid(self):
        '''
        Make sure that each positioner has the same number
        of points in the scan.  This is required by the scan record.
        '''
        scanValid = True
        firstSection = True
        firstSectionSteps = 0
        
        for positioner in self._positionersList:
            i = 0
            if positioner.status == 1:
                temp = 0
            
                for section in self._sectionList[i]:
                    if not section.GetStepCount() == 0:
                        temp = temp + section.GetStepCount()
                    
                if firstSection == True:
                    firstSectionSteps = temp
                    firstSection = False
                
                if not temp == firstSectionSteps:
                    scanValid = False
                    return scanValid
                
        self._scanValid = scanValid            
        
        self.SetTotalNumPoints(temp)
        
        return scanValid
    
    def LoadPointsToScanRecord(self, preview=False):
        
        '''
        Calculate an array of points for each positioner in the scan record.
        Load those arrays into the scan record.
        Return the arrays of points or None if the data does
        not make a valid scan.
        
        preview - determines if the arrays should be written to the scan record,
                  a value of true means that the arrays will not be written
        '''
        
        scanValid = self.IsTableScanValid()
        arraysList = None
        
        # Check to see if the scan is valid, which means that
        # all positioners have the same number of points.  If
        # not, exit.
        if not scanValid:
            return arraysList
        
        totalPoints = self.GetTotaNumPoints()
        posNum = 0
        arraysList = []
        
        for positioner in self._positionersList:
            
            # Check to make sure that the number of points is greater
            # than zero and the positioner is not empty.
            if totalPoints > 0 and not positioner.get() == "":
                # Create an array with size equal to the number of points to be done.
                # This array is initially filled with zeros.
                pointsArray = zeros(totalPoints)
                
                sectionNumPoints = 0
                stride = 0
                
                sectionList = self._sectionList[posNum]
                
                # Fill the array with all of the points for the positioner
                for section in sectionList:
                    sectionNumPoints = section.GetStepCount()
                    start = section.GetStart()
                    stepSize = section.GetStepSize()
                    for i in range(sectionNumPoints):
                        pointsArray[stride + i] = start + (i * stepSize)
                    stride = stride + sectionNumPoints
                
                arraysList.append(pointsArray)
                
                if not preview:
                    
                    # Write all the points to the scan record.
                    scanPV = "%s.P%dPA" % (self._scanRecord, posNum + 1)
                    epics.caput(scanPV, pointsArray)
                    # Set the positioner mode to "Table".    
                    scanModePV = "%s.P%dSM" % (self._scanRecord, posNum + 1)
                    epics.caput(scanModePV, 1)
        
        # Write the number of points to the scan record.        
        if totalPoints > 0 and not preview:
            epics.caput("%s.NPTS" % self._scanRecord, totalPoints)    
            
        return arraysList
    
    def CalculatePositionerPointsArray(self, positioner):
        '''
        Create an array with size equal to the number of points to be done.
        Initialize the array elements to zero.
        
        positioner - the number of the positioner in the scan record, 1 - 4
        '''
        pointsArray = zeros(self._totalNumPoints)
        
        numPoints = 0.0
        stride = 0
        for section in self._sectionList[positioner - 1]:
            numPoints = section.GetStepCount()
            start = section.GetStart()
            stepSize = section.GetStepSize()
            for i in range(numPoints):
                pointsArray[stride + i] = start + (i * stepSize)
            stride = stride + numPoints

        return pointsArray
    
    @DelayedEpicsCallback
    def PositionerChangedCallback(self, **kwargs):
        
        positioner = kwargs['value']
        
        # If there is a value entered into the positioner PV,
        # try to get the value of positioner.  If no value can
        # be obtained, assume that the PV is invalid.
        if len(positioner) > 0:
            position = epics.caget(positioner)
            if position == None:
                self._positionersValid = False
        
        # Call the user supplied function
        self._posCallbackFunction(kwargs)
        return
    
    def SaveTableScan(self, fileHandle):
        '''
        Write values of the table scan to a file so that they can
        later be retrieved.
        
        fileHandle - a handle to an open file
        '''
        
        # Write out the four positioner PVs
        posNum = 1
        for positioner in self._positionerList:
            fileHandle.write("[Positioner%s]\n" % posNum)
            pv = positioner.get()
            if pv == "":
                fileHandle.write("None\n")
            else:
                fileHandle.write("%s\n" % pv)
            posNum = posNum + 1
        
        
        # For each table scan associated with a positioner,
        # write the starting point, ending point, and step size
        # for each section. 
        posNum = 1
        for tablescan in self._sectionList:
            fileHandle.write("[TableScan%s]\n" % posNum)
            sectionNum = 1
            
            numSections = len(tablescan)
            fileHandle.write("%d\n" % numSections)
                        
            for scanSection in tablescan:
                fileHandle.write("[Section%s]\n" % sectionNum)
                fileHandle.write("%d\n" % scanSection.GetStart())
                fileHandle.write("%d\n" % scanSection.GetEnd())
                fileHandle.write("%d\n" % scanSection.GetStepSize())
                sectionNum = sectionNum + 1
             
            posNum = posNum + 1
                
        fileHandle.close()
                
        return
    
    def LoadTableScan(self, fileHandle):
        
        line = fileHandle.readline()
        scanNum = -1
        while not line == "":
        # Look for a new table scan
                        
            if "Positioner" in line:
                for i in range(4):
                    positioner = fileHandle.readline()[:-1]
                    if not "None" in positioner:
                        self._positionerList[i].put(positioner)
                    else:
                        self._positionerList[i].put(None)
                    if i < 3:
                        fileHandle.readline()
                    del self._sectionList[i][:]
                                
            if "TableScan" in line:
                scanNum = scanNum + 1

                # This is the number of scan sections that are in
                # the table scan.
                numSections = int(fileHandle.readline())

                for i in range(numSections):
                    line = fileHandle.readline()
                    # Look for the section heading
                    sectionTitle = line.find("Section%d" % (i + 1))
                    if not sectionTitle == -1:
                        # Create a new section object
                        newSection = ScanSection()
                        # Get the section information and use it to set section parameters.
                        newSection.SetStart(int(fileHandle.readline()))
                        newSection.SetEnd(int(fileHandle.readline()))
                        newSection.SetStepSize(int(fileHandle.readline()))
                        newSection.CalculateStepCount()
                        # Add the new scan section to the section list.
                        self._sectionList[scanNum].append(newSection)
                           
            line = fileHandle.readline()
        
        return
    
class EnergyScan(TableScan):
    '''
    classdocs
    '''

    def __init__(self, mono, undulator, zpZ, offset, width, radius, scan, function):
        '''
        Constructor
        
        mono - the pv for setting the monochromator energy
        undulator - the pv for setting the undulator energy
        zpZ - the stage that changes the Z position of the zone plate
        offset - the difference between the undulator energy and the monochromator energy
        width - the width of the zone plate's outer zone
        radius - the radius of the zone plate
        scan - the scan record for this energy scan
        function - a callback function for when positioner's change
        '''
        
        TableScan.__init__(self, scan, function)
        
        self._monochromator = PV(mono)
        self._undulator = PV(undulator)
        self._currentEnergy = self._undulator.get()
        self._nextEnergy = 0.0
        self._zpStage = PV(zpZ)
        self._zpCurrentPos = self._zpStage.get()
        self._zpNextPos = 0.0
        self._zpWidth = width
        self._zpRadius = radius
        self._energyOffset = offset
        self._moveZP = False
        self._scanType = "EnergyScan"
        
        return
    
    def SetMoveZP(self, moveZP):
        self._moveZP = moveZP
        return
    
    def GetMoveZP(self):
        return self._moveZP
    
    def CalculateFocalLengthChange(self, deltaEnergy, width, radius):
        '''
        Calculate the change in zone plate position that must occur with each energy change.
        
        deltaEnergy - the amount by which the energy is changing
        width - the width of the outermost zone of the zone plate
        radius - the radius of the zone plate
        '''
        
        h = pow(4.135667516, -15)       # Planck's constant in eV s.
        c = 299792458                   # Speed of light in a vacuum in m/s
        scale = pow(1, -12)             # A scale factor to make the units of length work out.
        
        focalLength = (2 * width * radius * scale * deltaEnergy) / h * c
        
        return focalLength
    
    def CreateEnergyTableScan(self, tableScanList):
        
        self._zpCurrentPos = self._zpZStage.get()
        self._currentEnergy = self._undulator.get()
        
        # Dtermine the number of points in the scan
        totalPoints = 0
        # We are only using data for the first positioner
        tablescan = tableScanList[0]
        for scanSection in tablescan:
            totalPoints = totalPoints + scanSection.getNumSteps()
        
        # Create arrays with size equal to the number of points to be done.
        # Initialize the array elements to zero.
        energyPointsArray = zeros(totalPoints)
        monoPointsArray = zeros(totalPoints)
        zpPointsArray = zeros(totalPoints)
                
        # Generate the points that will be used in the scan and assign
        # them to the elements of the array.        
        numPoints = 0
        stride = 0
        for scanSection in tablescan:
            numPoints = scanSection.getNumSteps()
            for i in range(numPoints):
                energyPointsArray[stride + i] = scanSection.getStartPoint() + (i * scanSection.getStepSize())
                monoPointsArray[stride + i] = energyPointsArray[stride + i] + self.offset
                nextEnergy =  monoPointsArray[stride + i]
                zpPointsArray[stride + i] = self.zpCurrentPos + self.CalculateFocalLengthChange((nextEnergy - self.currentEnergy), self.width, self.radius)
                self.currentEnergy = nextEnergy
            stride = stride + numPoints 
                
        return (energyPointsArray, monoPointsArray, zpPointsArray, totalPoints)
    
    def WriteEnergyScan(self, fileHandle, moveZP):
        '''
        Write values of the table scan to a file so that they can
        later be retrieved.
        
        fileHandle - a handle to an open file
        moveZP - a value of 1 indicates that the zone plate should be moved with
                 each energy change
        '''

        #!fileHandle.write("[Energy Scan]\n")
        #!fileHandle.write("%d\n" % int(energyScan))
        
        fileHandle.write("[Move Zone Plate]\n")
        fileHandle.write("%d\n" % int(moveZP))
        
        # Write out the four positioner PVs
        posNum = 1
        for positioner in self._positionerList:
            fileHandle.write("[Positioner%s]\n" % posNum)
            pv = positioner.get()
            if pv == "":
                fileHandle.write("None\n")
            else:
                fileHandle.write("%s\n" % pv)
            posNum = posNum + 1
        
        
        # For each table scan associated with a positioner,
        # write the starting point, ending point, and step size
        # for each section. 
        posNum = 1
        for tablescan in self._sectionList:
            fileHandle.write("[TableScan%s]\n" % posNum)
            sectionNum = 1
            
            numSections = len(tablescan)
            fileHandle.write("%d\n" % numSections)
                        
            for scanSection in tablescan:
                fileHandle.write("[Section%s]\n" % sectionNum)
                fileHandle.write("%d\n" % scanSection.GetStart())
                fileHandle.write("%d\n" % scanSection.GetEnd())
                fileHandle.write("%d\n" % scanSection.GetStepSize())
                sectionNum = sectionNum + 1
             
            posNum = posNum + 1
                
        fileHandle.close()
                
        return
    
    def LoadEnergyScan(self, fileHandle):
        
        line = fileHandle.readline()
        scanNum = -1
        while not line == "":
        # Look for a new table scan

            if "Energy Scan" in line:
#!                self.energyScanPanel.energyScanCheckBox.SetValue(bool(int(fileHandle.readline())))
#!                self.energyScanPanel.OnSetEnergyScan(wx.EVT_IDLE)
                        
            if "Move Zone Plate" in line:
                self._moveZP = bool(int(fileHandle.readline()))
                #!self.energyScanPanel.moveZP.SetValue(bool(int(fileHandle.readline())))
                        
            if "Positioner" in line:
                #!positionerList = self.tableScan.GetPositionerList()
                for i in range(4):
                    positioner = fileHandle.readline()[:-1]
                    if not "None" in positioner:
                        self._positionerList[i].put(positioner)
                    else:
                        self._positionerList[i].put(None)
                    if i < 3:
                        fileHandle.readline()
                    del self._sectionList[i][:]
                                
            if "TableScan" in line:
                scanNum = scanNum + 1

                # This is the number of scan sections that are in
                # the table scan.
                numSections = int(fileHandle.readline())

                for i in range(numSections):
                    line = fileHandle.readline()
                    # Look for the section heading
                    sectionTitle = line.find("Section%d" % (i + 1))
                    if not sectionTitle == -1:
                        # Create a new section object
                        newSection = ScanSection()
                        # Get the section information and use it to set section parameters.
                        newSection.SetStart(int(fileHandle.readline()))
                        newSection.SetEnd(int(fileHandle.readline()))
                        newSection.SetStepSize(int(fileHandle.readline()))
                        newSection.CalculateStepCount()
                        # Add the new scan section to the section list.
                        self._sectionList.append(newSection)
                           
            line = fileHandle.readline()
        
        return
        
class CircularScan(TableScan):
    '''
    This is a table scan that is defined as one section with a circular shape
    rather than a line.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TableScan.__init__(self)
        
        return