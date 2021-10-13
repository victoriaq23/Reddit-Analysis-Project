#!/usr/bin/env python
# coding: utf-8
#author: Victoria Quin
#this file is used to collect Reddit data from Pushshift

# In[ ]:


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


# In[ ]:


#three functions below are used to generate a pushshift URL which can be used to obtain Reddit data in JSON format

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
        

#print(makeURL(1, 2021, 'news'))
# generalURL = makeURLGeneral('comment', 'news')
# generalURL = (makeURLAfter(generalURL, 1, 2021))
# generalURL = makeURLBefore(generalURL, 1, 2021)

# print(generalURL)


# In[ ]:


#collecting information from Pushshift JSON Files
resps = requests.get('https://api.pushshift.io/reddit/comment/search/?subreddit=news&after=2021-01-01&before=2021-02-01')
print(resps.headers.get('content-type'))
numPosts = 0
#creates pushshift URL using int inputs startMonth and year and String inputs specifying subreddit and whether
#it is collecting submissions (posts) or comments
#gathers and returns data from all pushshift JSON files parsed as an array of dictionaries (?)

def downloadFromURL(startMonth, year, postOrComment, subreddit):
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
            
#monthData = downloadFromURL(1, 2021, 'comment', 'news') 
#print('last epoch should be less than or equal to 1612137600')
#print(monthData)


# In[ ]:


# # Open JSON file
# JSONFile = 'TEST_newsJan2021Comments.json' #REPLACE name with file name here 

# with open(JSONFile) as dataFile: 
#     textDictionary = json.load(dataFile)

# textDictionary = textDictionary.get('data')

#isPosts = False #change to False if reading from comment file

#NOTE: want to keep selftext and title for posts, body in comments
def toArray(dictionaryArray, isPosts):
    global numPosts
    textArray = []
    for array in dictionaryArray:
        for dictionary in array:
            numPosts += 1
            if(isPosts):
                textArray.append(dictionary.get('title'))
                if not dictionary.get('selftext') == '':
                    textArray.append(dictionary.get('selftext'))
            else:
                    textArray.append(dictionary.get('body'))
            
    return textArray
    
#dataArray = toArray(textDictionary)
#print(dataArray)
# dataArray = toArray(monthData, True)
# print(dataArray)
# In[ ]:


#remove emojis from collected raw data
#function removeEmojis takes in an array of Strings as an input and returns the same array of Strings with emojis removed
def removeEmojis(textArray):
    tempArray = []
    for text in textArray:
        for word in text:
            if(word in emoji.UNICODE_EMOJI['en']):
                text = text.replace(word, '')
        tempArray.append(text)
        
    print('emojis removed')
    return tempArray

# dataArrayEmojiless = removeEmojis(dataArray)
# print(dataArrayEmojiless)


# In[ ]:


#remove links from collected raw data
#function removeLinks takes in an array of Strings as an input and returns the same array of Strings with links removed
def removeLinks(textArray):
    tempArray = []
    for text in textArray:      
        pattern = re.compile('(https:\/\/|http:\/\/)\S+')
        tempArray.append(pattern.sub('', text))
    
    print('links removed')
    return tempArray

# dataArrayLinkless = removeLinks(dataArrayEmojiless)
# print(dataArrayLinkless)


# In[ ]:
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

# dataTokenized = tokenize(dataArrayLinkless)
#print(dataTokenized)


# In[ ]:


#filtering out stopwords 
def removeStopwords(textArray):
    textArray =  [word for word in textArray if word not in stopwords.words('english')]
    
    print('stopwords removed')
    return textArray

#dataCleaned = removeStopwords(dataTokenized)
#print(dataCleaned)


# In[ ]:


def writeToCSV(fileName, textArray):
    filePath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/redditData/' + fileName
    with open(filePath, 'w') as csvFile:
        for sentence in textArray:
            csvFile.write(sentence + ',')
            
    print('csv file created')
    #csvFile.close()
    
#writeToCSV('newsCommentsJanuary1st2021.csv', dataCleaned)


# In[ ]:
def main(startMonth, year, postOrComment, subreddit, isPost, fileName):
    t0 = time.time()
    
    monthData = downloadFromURL(startMonth, year, postOrComment, subreddit) 
    dataArray = toArray(monthData, isPost)
    dataArrayEmojiless = removeEmojis(dataArray)
    dataArrayLinkless = removeLinks(dataArrayEmojiless)
    #dataTokenized = tokenize(dataArrayLinkless)
    #dataCleaned = removeStopwords(dataTokenized)
    writeToCSV(fileName, dataArrayLinkless)
    
    t1 = time.time()
    global numPosts
    print(f"{t1-t0} seconds to download {numPosts} posts")
    filePath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/' + fileName
    with open(filePath, 'a') as csvFile:
        csvFile.write(f"{t1-t0} seconds to download {numPosts} posts")
    csvFile.close()

#main(1, 2018, 'submission', 'news', True, 'Jan2018NewsPosts.csv')
# main(3, 2020, 'submission', 'worldnews', True, 'Mar2020worldnewsPosts.csv')
# main(1, 2019, 'submission', 'dankmemes', True, 'Mar2019dankmemesPosts.csv')
# #main(1, 2019, 'submission', 'unpopularopinion', True, 'Jan2019unpopularopinionPosts.csv')
# main(1, 2019, 'submission', 'mildlyinteresting', True, 'Jan2019mildlyinterestingPosts.csv')

#main(1, 2019, 'comment', 'AskReddit', False, 'Jan2019AskRedditComments.csv')
#main(1, 2019, 'submission', 'news', True, 'Jan2019NewsPosts.csv')
#main(1, 2018, 'comment', 'news', False, 'Jan2018NewsComments.csv')
main(1, 2019, 'comment', 'Memes', False, 'Jan2019MemesComments.csv')
main(3, 2019, 'comment', 'dankmemes', False, 'Mar2019dankmemesComments.csv')

