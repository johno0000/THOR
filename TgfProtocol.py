import shutil
import os
import re
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime


dataDirectory = '/media/AllDetectorData/Detectors'


def getDateTimeFromFile(fileName):
    dtStringToMatch = "_[0-9]{6}_[0-9]{6}"
    dtString = re.search(dtStringToMatch, fileName).group(0)
    dateTime = datetime.strptime(dtString, "_%y%m%d_%H%M%S")
    return(dateTime)


def getFolderNameForDateTime(dateTime):
    folderName = dateTime.strftime("%y%m%d")
    return(folderName)


def sortFilesInThisDirectory(directoryPath = os.getcwd()):
    os.chdir(directoryPath)
    files = glob("eRC*")
    for file in files:
        dt = getDateTimeFromFile(file)
        folderName = directoryPath + "/" + getFolderNameForDateTime(dt) + "/"
        if not os.path.exists(folderName):
            os.mkdir(folderName)
        shutil.move(file, folderName)
    return(0)


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
    serialNos = [getSerialNoFromFile(file) for file in files]
    DTs = [getDateTimeFromFile(file) for file in files]
    dat = pd.DataFrame({'file': files, 'SN': serialNos, 'dateTime': DTs})
    return(dat)

def getTimeToFile(fileName, dateTime):
    fileDate = getDateTimeFromFile(fileName)
    timeDiff = (fileDate - dateTime).total_seconds()
    return(timeDiff)
    


    
          
    
    
    
