import os
import re
from glob import glob
from datetime import datetime


def getDateTimeFromFile(fileName):
    dtStringToMatch = "_[0-9]{6}_[0-9]{6}"
    dtString = re.search(dtStringToMatch, fileName).group(0)
    dateTime = datetime.strptime(dtString, "_%y%m%d_%H%M%S")
    return(dateTime)

def getFolderNameForDateTime(dateTime):
    folderName = dateTime.strftime("%y%m%d")
    return(folderName)

def sortFilesInThisDirectory(directoryPath):
    os.chdir(directoryPath)
    files = glob("eRC*")
    for file in files:
        dt = getDateTimeFromFile(file)
        folderName = getFolderNameForDateTime(dt)
        if(!os.path.exists(folderName)):
            os.mkdirs(folderName)
        shutil.moves(file, folderName)
    return(0)
          
    
    
    
