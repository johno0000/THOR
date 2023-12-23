import shutil
import os
import re
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime
import DataOrganizer as DO


dataDirectory = '/media/AllDetectorData/Detectors'


def getDateTimeFromFile(fileName):
    dtStringToMatch = "_[0-9]{6}_[0-9]{6}"
    dtString = re.search(dtStringToMatch, fileName).group(0)
    dateTime = datetime.strptime(dtString, "_%y%m%d_%H%M%S")
    return(dateTime)


def getSerialNoFromFile(fileName):
    snStringToMatch = "(?<=eRC)[0-9]{4}"
    match = re.search(snStringToMatch, fileName)
    if(type(match) is not None):
        return(int(match.group(0)))
    else:
        return(0)
    

def isTraceFile(fileName):
    isTrace = "xtr" in fileName
    return(isTrace)


def getFileDataFrame(files):
    files = [file for file in files if 'eRC' in file]
    serialNos = [getSerialNoFromFile(file) for file in files]
    DTs = [getDateTimeFromFile(file) for file in files]
    isTraceColumn = [isTraceFile(file) for file in files]
    dat = pd.DataFrame({'file': files, 'SN': serialNos, 
                        'dateTime': DTs, 'isTrace': isTraceColumn})
    return(dat)


def getTimeToFile(fileName, dateTime):
    fileDate = getDateTimeFromFile(fileName)
    timeDiff = (fileDate - dateTime).total_seconds()
    return(timeDiff)


def returnClosestFile(files, dateTime):
    files = files.reset_index(drop = True)
    timeDiffs = [getTimeToFile(file, dateTime) for file in files]
    if(not any([x > 0 for x in timeDiffs])):
        return('')
    minDiff = min([x for x in timeDiffs if x > 0])
    index = timeDiffs.index(minDiff)
    return(files[index])


def getFilesForEvent(dateTimeUTC, detector):
    os.chdir(dataDirectory)
    dirs = glob('*') + glob('THOR/*')
    print(dirs)
    
    targetDir = [x for x in dirs if x.lower() in detector.lower()]
    if len(targetDir) == 1:
        os.chdir(targetDir)
    else:
        print("No match")
        return()
    
    dayDir = "/Data/" + DO.getFolderNameForDateTime(dateTimeUTC)
    os.chdir(dayDir)
    files = glob('*')
        
    data = getFileDataFrame(files)
    eventFiles = data.groupby(['SN', 'isTrace']).apply(lambda x: 
                    returnClosestFile(x.file, dateTime)).reset_index(drop = True)
    eventFiles = [file for file in eventFiles if 'eRC' in file]
    return(eventFiles)


    


    
          
    
    
    
