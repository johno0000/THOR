import re
import json
import pandas as pd
import glob
import os

files = glob.glob("/thor5/data/eRC*.txt")

def filenameToDataTable(fileName):
    with open(fileName) as f:
        lines = f.readlines()
       
    lmStrings = [s for s in lines if "eRC" in s]
    allData = pd.concat([stringToTable(x) for x in lmStrings], ignore_index = True)
    return(allData)

def stringToTable(lmString):
    jsonDict = json.loads(re.sub("eRC[0-9]{4} ", "", lmString))['lm_data']
    data = pd.DataFrame.from_dict(jsonDict)
    data['Seconds'] = data['wc'] * 12.5e-9
    data['PPS'] = pd.Series([int('{0:08b}'.format(x)[-8]) for x in data['flags']])
    return(data)

def getBgRate(data):
    totalTime = data.Seconds.max() - data.Seconds.min()
    ratePerSecond = len(data) / totalTime
    return(ratePerSecond)

def getBgRateFromFile(fileName):
    data = filenameToDataTable(fileName)
    bgRate = getBgRate(data)
    return(bgRate)

def isGpsWorking(fileName):
    data = filenameToDataTable(fileName)
    diffs = data[data['PPS'] == 1]['Seconds'].diff()
    isGoodTick = diffs.round(3).apply(lambda x: x == 1)
    goodTicks = isGoodTick.sum()
    print(goodTicks)
    print(len(diffs) - 1)
    return goodTicks >= (0.95 * (len(diffs) - 1))

def isGpsWorkingInLastFile():
    files.sort(key = os.path.getmtime)
    toReturn = isGpsWorking(files[-1])
    return toReturn

def getEventsFromData(data, photons = 5, time = 0.001):
    rollingSum = data['Seconds'].diff().abs().rolling(photons).sum()
    events = (data[rollingSum < time]['Seconds'].diff() > 1).astype(int).cumsum()
    data['SpikeID'] = -1
    for eventID in events.unique():
        minTime = data.iloc[[events[events == eventID].index.min()]]['Seconds'].values[0] - 0.1
        maxTime = data.iloc[[events[events == eventID].index.max()]]['Seconds'].values[0] + 0.1
        data.loc[(data['Seconds'].gt(minTime)) & (data['Seconds'].lt(maxTime)), 'SpikeID'] = eventID
    return(data)






