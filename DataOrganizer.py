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

def getFolderNamesList(files):
    folderNameList = []
    for file in files:
        dt = getDateTimeFromFile(file)
        folderName = getFolderNameForDateTime(dt)
        if folderName not in folderNameList:
            folderNameList.append(folderName)
    return(folderNameList)

def sortFilesinDirectory(directoryPath):
    files = glob("eRC*")
    folderNamesList = getFolderNamesList(files)
    for folder in folderNamesList:
        os.system("mkdir " + folder)
        
    
    
