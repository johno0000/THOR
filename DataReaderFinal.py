import re # Regular expressions module for string operations
import json
import pandas as pd
import glob
import os
import numpy as np
import scipy
from scipy.stats import poisson
from datetime import datetime

def fileNameToData(fileName):
    with open(fileName) as f:
        lines = f.read().splitlines()
    data = thorFileToData(lines)
    return(data)


def thorFileToData(lines):
    dataList = list()
    for i in range(5, len(lines), 6):
        lmString = lines[i]
        timeString = lines[i - 2]
        dateTime = datetime.strptime(timeString, "%Y %m %d %H %M %S %f")
        dataList.append(stringToTable(lmString, dateTime))
    data = pd.concat(dataList)
    return(data)
    
def stringToTable(lmString, dateTime):
    jsonDict = json.loads(re.sub("eRC[0-9]{4} ", "", lmString))['lm_data']
    data = pd.DataFrame.from_dict(jsonDict)
    data['PPS'] = pd.Series([int('{0:08b}'.format(x)[-8]) for x in data['flags']]) ## very useful column for future operations - separates out GPS signal from the Flags column
    data['Seconds'] = getSecondsFromWallClock(data)
    data['UnixTime'] = dateTime.timestamp() + data['Seconds'] - data['Seconds'].iloc[-1] ## this assigns dateTime to the final photon in the table, and works backwards from there to previous photons
    firstDT = datetime.fromtimestamp(data['UnixTime'].min())
    data['SecondsOfDay'] = data['UnixTime'] - datetime(firstDT.year, firstDT.month, firstDT.day).timestamp() ## subtracts out 00:00:00 of the earliest day in UNIX time. For files that cross midnight this will result in SecondsOfDay exceeding 86000 or whatever
    
    unixTimeCorrection = data[data['PPS'] == 1]['SecondsOfDay'].apply(lambda x: (x - round(x))).median()
    data['SecondsOfDay'] = data['SecondsOfDay'] + unixTimeCorrection
    data['UnixTime'] = data['UnixTime'] + unixTimeCorrection ## some of this precision is going to get truncated. If that's a big deal then you need to recreate a DateTime object by adding the adjusted SecondsOfDay to firstDT.
    return(data)

def getSecondsFromWallClock(data):
    rolloverCorrection = (data['wc'].diff() < 0).cumsum() * pow(2, 36)  ## Every time you encounter the wallclock going backwards, assume it's rollover. Count how many times its rolled over and multiply that by 2^36 for each row's correction.
    data['wc'] = data['wc'] + rolloverCorrection ## Changing the contents of the object passed in the function - there might be a better way to do this but it should work since Python passes by object reference
    wallClockCorrection = (data['wc'][data['PPS'] == 1]).diff().median()
    if(abs(wallClockCorrection - 8e7) > 1e4):
        raise Exception("wallclock and GPS clocks in significant disagreement")
    Seconds = data['wc'] / wallClockCorrection
    return(Seconds)
    
