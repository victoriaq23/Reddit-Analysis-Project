#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 14:18:56 2021
This file is used to create data visualizations of prediction results
@author: r21vxquin
"""

import pandas as pd
import plotly
import plotly.io as pio
import plotly.express as px
import os
import csv
#import numpy as nd
pio.renderers.default = "firefox"

#formatFiles formats a specified file to make it compatible with the rest of the
#functions defined below (data should be in a .csv file, formatted like a 
#long type dataframe, with the headers of the csv file being 
#subreddit, courage, fear, guilt, hostility, joy, life-affirming, mortality,
#peaceful, sadness, surprise, month, year)
def formatFiles(inputFileName):
    #inputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/OutputData/'
    inputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/Averages/'
    allData = []
    if 'Posts' in inputFileName:
        endIndex = inputFileName.find('Posts')
    else:
        endIndex = inputFileName.find('Comments')
    subredditName = inputFileName[7:endIndex]
    month = inputFileName[:3]
    year = inputFileName[3:7]
    with open(inputPath + inputFileName + 'results.csv', 'r') as inputfile:
        fileArray = inputfile.readlines()
        for line in fileArray:
            if '#' not in line:
                lineData = []
                lineArray = line.split(',')
                for i in range(0, 10):
                    lineData.append(lineArray[i].replace('[', '').replace(']', ''))
                allData.append(lineData)
    inputfile.close()
    
    outputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/Averages/'
    outputFileName = str(inputFileName)[:-4] + 'formatted.csv'
    with open(outputPath + outputFileName, 'w') as outputfile:
        outputfile.write('subreddit,courage,fear,guilt,hostility,joy,life-affirming,'
                          + 'mortality,peaceful,sadness,surprise,month,year\n')
        for dataArray in allData:
            outputfile.write(subredditName + ',')
            for weight in dataArray:
                outputfile.write(str(weight) + ',')
            outputfile.write(month + ',' + year + '\n')
    outputfile.close()

#getAverage returns the average weights of each of the 10 emotion labels from a 
#single text file
def getAverage(inputFileName):
    inputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/Averages/'
    wide_df = pd.read_csv(inputPath + inputFileName)
    averageDict = {'courage': 0, 'fear': 0, 'guilt': 0, 'hostility': 0, 'joy': 0, 
                   'life-affirming': 0,'mortality': 0, 'peaceful': 0, 'sadness': 0, 
                   'surprise': 0}
    for emotion in averageDict.keys():
        averageDict[emotion] = [wide_df[emotion].mean()]
    with open(inputPath + inputFileName) as csvFile:
        filereader = csv.DictReader(csvFile)
        for row in filereader:
            averageDict['subreddit'] = row['subreddit']
            averageDict['month'] = row['month']
            averageDict['year'] = row['year']
    csvFile.close()
    return averageDict

#createGraph creates a graph of averages using an input file 
def createGraph(inputFileName):
    #inputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/Formatted Output Data/'
    wide_df = pd.DataFrame.from_dict(getAverage(inputFileName))
    print(wide_df)
    fig = px.bar(wide_df, x="subreddit", y=["courage", "fear", "guilt", "hostility",
                                            "joy", "life-affirming", "mortality",
                                            "peaceful", "sadness", "surprise"], 
                                                     title="Emotional Analysis of Reddit Data")
    fig.show()


def makeAverageFile(fileName):
    inputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/Averages/'
    avgDict = getAverage(fileName)
    with open(inputPath + 'averages.csv', 'a') as outputFile:
        outputFile.write('\n')
        for key in avgDict.keys():
            outputFile.write(str(avgDict[key]).replace('[', '').replace(']', ''))
            if not key == 'year':
                outputFile.write(',')
    outputFile.close()


def createGraphAllAverages(inputFile):
    wide_df = pd.read_csv(inputFile)
    fig = px.bar(wide_df, x="subreddit",y=['joy', 'life-affirming', 'courage', 'surprise', 'peaceful', 'guilt', 'hostility', 'sadness', 'fear', 'mortality'],
                                         color_discrete_sequence=px.colors.qualitative.Plotly_r,
                                         title="Emotional Analysis of Reddit Data")
    fig.show()

#createGraphAllAverages('/mnt/linuxlab/home/r21vxquin/reddit-data-collector/Formatted Output Data/averages.csv')
createGraphAllAverages('/mnt/linuxlab/home/r21vxquin/reddit-data-collector/Averages/averages.csv')