import shutil
import os
import re
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime
import DataOrganizer as DO


dataDirectory = '/media/AllDetectorData/Detectors/'
eventDirectory = os.path.expanduser('~/Desktop/Events/')
tgfTime = datetime(2022, 7, 26, 4, 57,00)


## Returns a datetime object, seconds precision (obviously)
def getDateTimeFromFile(fileName):
    dtStringToMatch = "_[0-9]{6}_[0-9]{6}"
    dtString = re.search(dtStringToMatch, fileName).group(0)
    dateTime = datetime.strptime(dtString, "_%y%m%d_%H%M%S")
    return(dateTime)


## i.e. eRC3143 returns 3143
def getSerialNoFromFile(fileName):
    snStringToMatch = "(?<=eRC)[0-9]{4}"
    match = re.search(snStringToMatch, fileName)
    if(type(match) is not None):
        return(int(match.group(0)))
    else:
        return(0)
    
    
## .xtr or xtr.gz returns TRUE, otherwise FALSE
def isTraceFile(fileName):
    isTrace = "xtr" in fileName
    return(isTrace)


## creates a Pandas dataframe object describing all the files in the folder
## Columns: file name, serial number, datetime, isTrace
def getFileDataFrame(files):
    files = [file for file in files if 'eRC' in file]
    serialNos = [getSerialNoFromFile(file) for file in files]
    DTs = [getDateTimeFromFile(file) for file in files]
    isTraceColumn = [isTraceFile(file) for file in files]
    dat = pd.DataFrame({'file': files, 'SN': serialNos, 
                        'dateTime': DTs, 'isTrace': isTraceColumn})
    return(dat)


## fileTime - dateTime = TimeToFile, given in seconds
def getTimeToFile(fileName, dateTime):
    fileDate = getDateTimeFromFile(fileName)
    timeDiff = (fileDate - dateTime).total_seconds()
    return(timeDiff)


## This will return the file that SHOULD contain the dateTime in question
## However it's only based off that file being the first available one prior to
## the datetime provided, e.g. provide 4:53 you may get the file for 4:51
def returnClosestFile(files, dateTime):
    files = files.reset_index(drop = True)
    timeDiffs = [getTimeToFile(file, dateTime) for file in files]
    if(not any([x > 0 for x in timeDiffs])):
        return('NoFilesFound')
    minDiff = max([x for x in timeDiffs if x < 0])
    index = timeDiffs.index(minDiff)
    return(files[index])

##Once inside the correct data directory, you should run this function to 
## return all the files over every detector that conatin the time of interest
def returnClosestFilesForEventInThisDirectory(dateTime):
    files = glob('*')

    data = getFileDataFrame(files)
    eventFiles = data.groupby(['SN', 'isTrace']).apply(lambda x: 
                    returnClosestFile(x.file, dateTime)).reset_index(drop = True)
    eventFiles = [file for file in eventFiles if 'eRC' in file]
    return(eventFiles)
    
## Given a time of interest and the name of a detector, this should move you into
## The correct DAY directory of the right DETECTOR. Alternatively, we could just
## return all the absolute file paths instead of changing into that directory
## I'm not sure if this makes things simpler to process mentally or not
def changeToDetectorDirectory(detector, dateTimeUTC, dataDirectory = dataDirectory):
    os.chdir(dataDirectory)
    dirs = glob('*/') + glob('THOR/THOR[0-9]/')
    print(dirs)
    
    targetDir = [x for x in dirs if detector.lower() in x.lower()]
    print(targetDir)
    if len(targetDir) == 1:
        targetDir = targetDir[0]
    else:
        print("No match")
        return()
    
    targetDir = dataDirectory + targetDir + 'Data/' + DO.getFolderNameForDateTime(dateTimeUTC)
    os.chdir(targetDir)
    print('Changing to ' + targetDir)
    return(targetDir)

## Creates the new directory structure for an event, with a folder for Detector Data,
## Radio Data, Weather Data, Misc., and a README file to be filled out
def TransferFilesToNewEventFolder(files, newDirName, eventDir = eventDirectory):
    destination = eventDir + newDirName
    foldersToMake = ['DetectorFiles/', 'RadioData', 'WeatherData', 'MiscData']
    os.makedirs(destination, exist_ok = True)
    [os.makedirs(folder) for folder in foldersToMake]
    for file in files:
        print(file + " going to " + destination + foldersToMake[0])
        shutil.copy2(file, destination + foldersToMake[0])
    return()


## Starting with the datetime of the TGF and the name of the detector, this will run 
## through the whole process of retreiving the list & trace files and copying them into
## nice, newly created event folder to be placed in the same directory as other events
def CreateTgfFolder(dateTimeUTC, detectorName, eventDir = eventDirectory, 
                    dataDirectory = dataDirectory):
    newDirectoryName = DO.getFolderNameForDateTime(dateTimeUTC) + '_' + detectorName + '/'
    changeToDetectorDirectory(detectorName, dateTimeUTC, dataDirectory) ## this changes the directory
    files = returnClosestFilesForEventInThisDirectory(dateTime = dateTimeUTC)
    ## Tranfer files to new folder
    TransferFilesToNewEventFolder(files = files, newDirName = newDirectoryName)
    return()
    
    
        



    
        


    


    
          
    
    
    
