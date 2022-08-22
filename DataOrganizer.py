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

def sortFilesInThisDirectory(directoryPath):
    os.chdir(directoryPath)
    files = glob("eRC*")
    folderNamesList = getFolderNamesList(files)
    for folder in folderNamesList:
        os.system("mkdir -p " + folder) # the -p option means it won't return an error if the directory already exists. With or without this option, mkdir will never overwrite or clear an existing directory
        os.system("cp *_" + folder + "_* ./" + folder) ## This is concise but inefficent : we deleted the information of what goes where and are computing it again. I think this makes things simpler, keeping shell and python tasks relatively separate. If performance boost is needed, simply keep track of what file goes where when the files are used to generate folder names to begin with. 
    return(0)    
    
    
    
