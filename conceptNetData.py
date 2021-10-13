#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 14:45:02 2021
This file is used to generate a larger training dataset using ConceptNet
@author: r21vxquin
"""



import os
import json
import requests
import time
import csv



#takes in one of the original 60 words, creates a new file with all related
#words from concept net, takes down relation info and weight
#only keeps words that have a weight greater than or equal to 1.0
def getRelatedWords(word):
    currentURL = 'http://api.conceptnet.io/c/en/' + word
    connectedWords = []
    
    while True:
        jsonData = requests.get(currentURL)
        time.sleep(1)
        try:
            jsonText = jsonData.json()
        except json.decoder.JSONDecodeError:
            time.sleep(1)
            continue
        
        if 'edges' not in jsonText:
            break
        
        edgesArray = jsonText.get('edges')
        if len(edgesArray) == 0:
            break
        
        allWords = []
        for edge in edgesArray:
            wordDict = {'word': '', 'relation': '', 'weight': 0, 'originalWord': ''}
            language = edge['start']['language']
            relation = edge['rel']['label']
            unrelated = ['ObstructedBy', 'Antonym', 'DistinctFrom', 'NotCapableOf']
            weight = edge['weight']
            relatedWord = edge['start']['label']
            
            if(weight < 1):
                break
            
            print(relatedWord + ', ' + relation + ', ' + str(weight))
            if language == 'en' and relation not in unrelated and not relatedWord.lower() == word:
                if word not in allWords:
                    wordDict['word'] = relatedWord.replace(',', '')
                    wordDict['relation'] = relation
                    wordDict['weight'] = weight
                    wordDict['originalWord'] = word
                    
                    connectedWords.append(wordDict)
                    allWords.append(relatedWord)
        
        pageInfo = jsonText.get('view')
        moreResults = "There are more results. Follow the 'nextPage' link for more."
        if pageInfo == None:
            break
        try:
            if not pageInfo['comment'] == moreResults:
                break
        except KeyError:
            break
        
        currentURL = 'http://api.conceptnet.io' + pageInfo['nextPage']
    return connectedWords

# NOTE: the two commented lines (77 and 78) are used for testing purposes
# moveRelated = getRelatedWords('move')
# print(moveRelated)

# main method reads in all words from a single text file and writes to a new 
# file with all words related to the original words (generated with ConceptNet)
def main():
    allWords = []
    with open('/mnt/linuxlab/home/r21vxquin/reddit-data-collector/word_results.txt', 
              'r') as readFile:
        allLines = readFile.readlines()
        for line in allLines:
            allWords.append(line[:line.find(' =')])
    readFile.close()
    print(allWords)
    print(len(allWords))
    
    filepath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/ConceptNet Data'
    for word in allWords:
        print(word)
        wordData = getRelatedWords(word)
        with open(filepath + '/' + word + '.csv', 'w') as newFile:
            newFile.write('word,weight,relation\n')
            for edge in wordData:
                newFile.write(edge['word'] + ',' + str(edge['weight']) +
                          ',' + edge['relation'] + '\n')
        newFile.close()
        print('file for words related to ' + word + ' created')
#main()

#************ the following methods were used for re-formatting my text files 
# ****************************************************************************
def addToDirectory():
    directoryPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/CSVAll/'
    CNDirectory = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/ConceptNet Data/'
    outputDirectory = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/'
    for file in os.listdir(directoryPath):
        fileData = []
        emotion = file[:file.find('.')]
        inputPath = directoryPath + emotion + '.csv'
        with open(inputPath, newline='') as csvfile:
            fileReader = csv.reader(csvfile)
            next(fileReader)
            for line in fileReader:
                fileData.append(line)
        csvfile.close()
        print(fileData)
        
        for wordArray in fileData:
            currentWord = wordArray[0]
            emotion = wordArray[2]
            relatedWords = []
            allWords = []
            
            with open(CNDirectory + currentWord + '.csv', newline='') as wordfile:
                csvReader = csv.reader(wordfile)
                next(csvReader)
                for line in csvReader:
                    wordData = []
                    if line[0].lower() not in allWords:
                        allWords.append(line[0].lower())
                        wordData.append(line[0].lower())
                        if float(line[1]) >= 2:
                            wordData.append(wordArray[1])
                        else:
                            wordData.append(str((int(wordArray[1]) / 2)))
                        wordData.append(wordArray[2])
                        relatedWords.append(wordData)
            wordfile.close()
            #print(relatedWords)
            
            with open(outputDirectory + emotion + '.csv', 'a') as outputfile:
                for wordArray in relatedWords:
                    outputfile.write(wordArray[0] + ',' + wordArray[1] + ',' +
                                     wordArray[2] + '\n')
            outputfile.close()
            print('file for ' + emotion + ' updated')
            
            
                
#addToDirectory()

def mergeFiles():
    directory = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/'
    allWords = []
    for file in os.listdir(directory):
        filepath = directory + file
        with open(filepath, newline='') as csvfile:
            fileReader = csv.reader(csvfile)
            next(fileReader)
            for line in fileReader:
                allWords.append(line)
        csvfile.close()
    print(allWords)
    for wordArray in allWords:
        print(wordArray)
        if len(wordArray) == 3:
            with open(directory + 'allData.csv', 'a') as outputfile:
                outputfile.write(wordArray[0] + ',' + wordArray[1] + ',' +
                                 wordArray[2] + '\n')
                print(wordArray[0] + ' added to file')
            outputfile.close()

#mergeFiles()

def getMoreWords():
    inputFile = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/allDataFormat2.csv'
    #inputFile = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/shortDataTest.csv'
    outputFile = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/allDataMore.csv'
    #outputFile = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/shortDataTest.csv'
    originalWords = []
    with open('/mnt/linuxlab/home/r21vxquin/reddit-data-collector/word_results.txt', 
              'r') as readFile:
        allLines = readFile.readlines()
        for line in allLines:
            originalWords.append(line[:line.find(' =')])
    readFile.close()
    
    allWords = []
    allData = {}
    with open(inputFile, newline='') as csvfile:
        filereader = csv.reader(csvfile)
        next(filereader)
        for line in filereader:
            if line[0] not in originalWords:
                allWords.append(line[0])
                allData[line[0]] = line[1:]
    csvfile.close()
    print('All data:')
    print(allData)
    
    newWords = {}
    for word in allWords:
        relatedWords = getRelatedWords(word)
        for newWordDict in relatedWords:
            if newWordDict['word'] not in allWords and newWordDict['word'] not in newWords.keys():
                wordArray = []
                # wordArray.append(newWordDict['word'])
                weights = allData[newWordDict['originalWord']]
                print('weights')
                print(weights)
                print(newWordDict) 
                if float(newWordDict['weight']) >= 2:
                    newWeights = [float(weight) / 2 for weight in weights]
                else:
                    newWeights = [float(weight) / 4 for weight in weights]
                wordArray.append(newWeights)
                newWords[newWordDict['word']] = newWeights
                
    with open(outputFile, 'a') as outputfile:
        for word in newWords.keys():
            outputfile.write(word + ',')
            for weight in newWords[word][:-1]:
                outputfile.write(str(weight) + ',')
            outputfile.write(str(newWords[word][-1]) + '\n')

    outputfile.close()
    
getMoreWords()
        