#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 14:07:02 2021

This file is a version of the JSONConverter.py file that uses multiprocessing
when cleaning the collected data with the goal of improving runtime
@author: r21vxquin
"""

import json
import csv

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

import emoji
import re

import requests
import time
from datetime import datetime, date
import calendar

from multiprocessing import Pool
import os


#makeURLGeneral takes in two String parameters, one specifying whether the user is currently trying to obtain 
#submission data or comment data, and the other specifying which subreddit to search; returns URL with this info
def makeURLGeneral(postOrComment, subreddit):
    url = 'https://api.pushshift.io/reddit/'
    url += postOrComment
    url += '/search/?'
    return url + 'subreddit=' + subreddit

#makeURLAfter takes in a String parameter which should be a valid pushshift URL, a starting month (represented by an 
#integer)that data should be collected from, and a year that data should be collected from; it returns the inputted 
#pushsift URL modified to have an $after attribute that corresponds to the inputted integers
def makeURLAfter(generalURL, startMonth, year):
    after = '&after=' + str(year) + '-'
    if(startMonth < 10):
        after += '0'
    after += str(startMonth) + '-01'
    return generalURL + after

#makeURLAfter takes in a String parameter which should be a valid pushshift URL, a starting month (represented by an 
#integer)that data should be collected from, and a year that data should be collected from; it returns the inputted 
#pushsift URL modified to have an $after attribute that corresponds to the inputted integers
def makeURLBefore(generalURL, startMonth, year):
    before = '&before='
    if(startMonth == 12):
        before+= str(year + 1) + '-' + '01-01'
    else:
        before+= str(year) + '-'
        if(startMonth < 10):
            before += '0'
        before += str(startMonth + 1) + '-01'
    return generalURL + before

numPosts = 0
def toArray(dictionaryArray, isPosts):
    global numPosts
    textArray = []
    #for array in dictionaryArray:
    for dictionary in dictionaryArray:
        numPosts += 1
        print(numPosts)
        if(isPosts):
            textArray.append(dictionary.get('title'))
            if not dictionary.get('selftext') == '':
                textArray.append(dictionary.get('selftext'))
        else:
                textArray.append(dictionary.get('body'))
     
    print('converted to array')
    return textArray

#remove emojis from collected raw data
#function removeEmojis takes in an array of Strings as an input and returns the same array of Strings with emojis removed
def removeEmojis(textArray):
    tempArray = []
    for text in textArray:
        for word in text:
            if(word in emoji.UNICODE_EMOJI['en']):
                text = text.replace(word, '')
        tempArray.append(text)
    print('removed emojis')
    return tempArray

#remove links from collected raw data
#function removeLinks takes in an array of Strings as an input and returns the same array of Strings with links removed
def removeLinks(textArray):
    tempArray = []
    for text in textArray:      
        pattern = re.compile('(https:\/\/|http:\/\/)\S+')
        tempArray.append(pattern.sub('', text))
    
    print('removed links')
    return tempArray

#tokenizing the text data
def tokenize(textArray):
    tokenizer = RegexpTokenizer('\w+')

    tokenizedText = []
    tokenizedArray = []
    
    for text in textArray:
        tokenized_item = tokenizer.tokenize(text)
        tokenizedText += tokenized_item
    
    for word in tokenizedText:
        try:
            word.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            continue
        else:
            tokenizedArray.append(word.lower())
    
    print('tokenized')
    return tokenizedArray


#filtering out stopwords 
def removeStopwords(textArray):
    textArray =  [word for word in textArray if word not in stopwords.words('english')]
    
    print('stopwords removed')
    return textArray


def writeToCSV(fileName, textArray):
    filePath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/' + fileName
    if os.path.isfile(filePath):
        csvFile = open(filePath, 'a')  
    else:
        print('csv file created') 
        csvFile = open(filePath, 'w')
        
    for sentence in textArray:
        csvFile.write(sentence)
        csvFile.write(',')
        print('sentence added to csv file')
    
         
    # csvFile.close()

def getURLs(year, startMonth, postOrComment, subreddit):
    counter = 0 #counts number of times new URL had to be generated
    allData = []
    
    startDate = date(year, startMonth, 1)
    previousEpoch = calendar.timegm(startDate.timetuple()) #converts startDate to a UTC timestamp
    
    print(previousEpoch)
    
    while True:
        currentURL = makeURLGeneral(postOrComment, subreddit)
        currentURL += '&after=' + str(previousEpoch)
        currentURL = makeURLBefore(currentURL, startMonth, year)
        #currentURL += '&before=' + str(year) + '-0' + str(startMonth) + '-02' #CHANGE BACK after testing **
        
        jsonData = requests.get(currentURL)
        time.sleep(.3) #sleep for .3 second, pushshift database has a rate limit
        
        try:
            jsonText = jsonData.json()
        except json.decoder.JSONDecodeError:
            time.sleep(1)
            continue
        
        if 'data' not in jsonText:
            break
        
        dictionaryArray = jsonText.get('data')
        if len(dictionaryArray) == 0:
            break
        
        allData.append(dictionaryArray)
        
        previousEpoch = dictionaryArray[len(dictionaryArray) - 1].get('created_utc')
        
        counter += 1
        print(counter)
        print(previousEpoch)
        
    return allData
    
def getURLData(dataArray):
    #print(dataArray)
    # rawData = requests.get(url)

    data = toArray(dataArray, False)
    print(numPosts)
    #print(data)
    
    dataCleaned = removeEmojis(data)
    print(dataCleaned)
    dataCleaned = removeLinks(dataCleaned)
    #dataCleaned = tokenize(dataCleaned)
    #dataCleaned = removeStopwords(dataCleaned)
    
    writeToCSV('Jan2020NewsCommentsFull.csv', dataCleaned)
    print('done')

    
    
    
def getAllURLData(allURLs):
    allData = []
    for data in allData:
        allData.append(getURLData(data))
    writeToCSV('TEST2Jan1stNewsPosts.csv', allData)
    
    
if __name__ == "__main__":
    t0 = time.time()
    allData = getURLs(2020, 1, 'comment', 'news')
    
    with Pool(processes=20) as pool: 
        pool.map(getURLData, allData)
        t1 = time.time()
        
    print(f"{t1-t0} seconds to download {len(allData)} urls")
    