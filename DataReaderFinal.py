import re # Regular expressions module for string operations
import json
import pandas as pd
import glob
import os
import numpy as np
import scipy
from scipy.stats import poisson
from datetime import datetime
import gzip


def fileNameToData(fileName):
    if(fileName[-2:] == 'gz'):
        f = gzip.open(fileName, 'rt')
    else:
        f = open(fileName)
    lines = f.read().splitlines()
    if ("xtr" in fileName):
        return(0)
    if(len(lines[0]) == 3):
        data = thorFileToData(lines)
    else:
         mode = 1
         if len(lines[2]) < 50:
            mode = 2
         data = lmFileToData(lines, mode)
    return(data)


def thorFileToData(lines):
    dataList = list()
    for i in range(5, len(lines), 6):
        lmString = lines[i]
        timeString = lines[i - 2]
        dateTime = datetime.strptime(timeString, "%Y %m %d %H %M %S %f")
        data = getDataFromLMthor(lmString)
        data = processDataTiming(data, dateTime)
        dataList.append(data)
    data = pd.concat(dataList)
    return(data)


def lmFileToData(lines, mode):
    dataList = list()
    if mode is 1:
        start = 2
        increment = 2
        tStamp = 1
    elif mode is 2:
        start = 7
        increment = 6
        tStamp = 2
    for i in range(start, len(lines), increment):
        lmString = lines[i]
        timeString = lines[i - tStamp]
        dateTime = datetime.strptime(timeString, "%Y %m %d %H %M %S %f")
        data = getDataFromLM(lmString, mode)
        data = processDataTiming(data, dateTime)
        dataList.append(data)
    data = pd.concat(dataList)
    return(data)


def getDataFromLMthor(lmString):
    jsonDict = json.loads(re.sub("eRC[0-9]{4} ", "", lmString))['lm_data']
    data = pd.DataFrame.from_dict(jsonDict)
    data['PPS'] = pd.Series([int('{0:08b}'.format(x)[-8]) for x in data['flags']]) ## very useful column for future operations - separates out GPS signal from the Flags column
    return(data)


def getDataFromLM(lmString, mode):
    if mode is 1:
        start = 2
        rowLength = 3
    elif mode is 2:
        start = 9
        rowLength = 6
    lmStrings = lmString.split(" ")[start:]
    buffer = [int(y) for y in lmStrings]
    data = np.reshape(buffer, (int(len(buffer)/rowLength), rowLength))
    data = pd.DataFrame(data)
    data = data[~data.duplicated()]
    coarsetick = 65536
    if mode is 2:
        wc = (data[2] + data[3] * coarsetick + data[4] * coarsetick * coarsetick) 
        energy = data[1]
        ticks = pd.Series([int('{0:08b}'.format(x)[-8]) for x in data[5]])
        flags = data[5]
    elif mode is 1:
        wc = (data[1] + data[2] * coarsetick) 
        energy = data[0]
        ticks = data[0] * 0 ## For some reason makes the pd.concat phase much faster
        flags = data[0] * 0
    newData = pd.concat([energy.rename('energy'), wc.rename('wc'), ticks.rename('PPS'), flags.rename('flags')], axis = 1)
    return(newData)


def processDataTiming(data, dateTime):
    data['Seconds'] = getSecondsFromWallClock(data)
    data['UnixTime'] = dateTime.timestamp() + data['Seconds'] - data['Seconds'].iloc[-1] ## this assigns dateTime to the final photon in the table, and works backwards from there to previous photons
    firstDT = datetime.fromtimestamp(data['UnixTime'].min())
    data['SecondsOfDay'] = data['UnixTime'] - datetime(firstDT.year, firstDT.month, firstDT.day).timestamp() ## subtracts out 00:00:00 of the earliest day in UNIX time. For files that cross midnight this will result in SecondsOfDay exceeding 86000 or whatever
    if(data['gpsSync'].all()):
        unixTimeCorrection = data[data['PPS'] == 1]['SecondsOfDay'].apply(lambda x: (x - round(x))).median()
        data['SecondsOfDay'] = data['SecondsOfDay'] + unixTimeCorrection
        data['UnixTime'] = data['UnixTime'] + unixTimeCorrection ## some of this precision is going to get truncated. If that's a big deal then you need to recreate a DateTime object by adding the adjusted SecondsOfDay to firstDT.
    data = data.drop('Seconds', axis = 1)
    return(data)


def getSecondsFromWallClock(data):
    rolloverCorrection = (data['wc'].diff() < 0).cumsum() * pow(2, 36)  ## Every time you encounter the wallclock going backwards, assume it's rollover. Count how many times its rolled over and multiply that by 2^36 for each row's correction.
    data['wc'] = data['wc'] + rolloverCorrection ## Changing the contents of the object passed in the function - there might be a better way to do this but it should work since Python passes by object reference
    wallClockCorrection = (data['wc'][data['PPS'] == 1]).diff().median()
    if(abs(wallClockCorrection - 8e7) > 1e4):
        raise Exception("wallclock and GPS clocks in significant disagreement")
    if(np.isnan(wallClockCorrection)):
        wallClockCorrection = 8e8
        data['gpsSync'] = False
    else:
        data['gpsSync'] = True
    Seconds = data['wc'] / wallClockCorrection
    return(Seconds)





    
