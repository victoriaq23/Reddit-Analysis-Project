#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 15:57:11 2021

@author: r21vxquin
** code for neural net adapted from code written by Usman Malik in the 
*** following article: 
    https://stackabuse.com/python-for-nlp-multi-label-text-classification-with-keras
"""

from numpy import array
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dropout, Dense
from tensorflow.keras.layers import Flatten, LSTM
from tensorflow.keras.layers import GlobalMaxPooling1D
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Concatenate

import pandas as pd
import numpy as np
import re
import tensorflow as tf

import nltk
from nltk.corpus import stopwords

import matplotlib.pyplot as plt

from numpy import array
from numpy import asarray
from numpy import zeros

from tensorflow.keras.utils import plot_model

import csv


inputFile = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/allDataMore.csv'
#inputFile = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/AllDataWithConceptNet/allDataFormat2.csv'
word_data = pd.read_csv(inputFile)

#print(word_data.shape)


labels = ['courage', 'fear', 'guilt', 'hostility', 'joy', 'life-affirming',
          'mortality', 'peaceful', 'sadness', 'surprise']

word_data_labels = word_data[labels]

fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 10
fig_size[1] = 8
plt.rcParams["figure.figsize"] = fig_size

word_data_labels.sum(axis=0).plot.bar()


def preprocess_text(sen):
    # Remove punctuations and numbers
    sentence = re.sub('[^a-zA-Z]', ' ', str(sen))

    # Single character removalkeras.layers.merge
    sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', str(sentence))

    # Removing multiple spaces
    sentence = re.sub(r'\s+', ' ', str(sentence))
    
    tempSentenceArray = sentence.split()
    newSentence = []
    #print(tempSentenceArray)
    for word in tempSentenceArray:
        try:
            word.encode(encoding='utf-8').decode('ascii') #removes foreign characters
        except UnicodeDecodeError:
            continue
        else:
            if word not in stopwords.words('english'):
                newSentence.append(word.lower())
            #print(newSentence)
    if len(newSentence) >= 1:
        sentence = ' '.join(str(word) for word in newSentence)
    #print(sentence)
    return sentence

X = []
sentences = list(word_data["word"])
for sen in sentences:
    # if(isinstance(sen, str)):
    #     print(sen)
    #     X.append(preprocess_text(sen))
    #print(str(sen))
    X.append(preprocess_text(str(sen)))

y = word_data_labels.values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(X_train)

X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)

vocab_size = len(tokenizer.word_index) + 1

maxlen = 50

X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

embeddings_dictionary = dict()

glove_file = open('/mnt/linuxlab/home/r21vxquin/Documents/glove.6B/glove.6B.100d.txt', encoding="utf8")

for line in glove_file:
    records = line.split()
    word = records[0]
    vector_dimensions = asarray(records[1:], dtype='float32')
    embeddings_dictionary[word] = vector_dimensions
glove_file.close()

embedding_matrix = zeros((vocab_size, 100))
for word, index in tokenizer.word_index.items():
    embedding_vector = embeddings_dictionary.get(word)
    if embedding_vector is not None:
        embedding_matrix[index] = embedding_vector

deep_inputs = Input(shape=(maxlen,))
embedding_layer = Embedding(vocab_size, 100, weights=[embedding_matrix], trainable=False)(deep_inputs)
LSTM_Layer_1 = LSTM(128)(embedding_layer)
dense_layer_1 = Dense(10, activation='relu')(LSTM_Layer_1)
dense_layer_2 = Dense(10, activation='softmax')(dense_layer_1)
model = Model(inputs=deep_inputs, outputs=dense_layer_2)
#model.add(Dense(10, activation='softmax'))
# sgd = tf.keras.optimizers.SGD(learning_rate=0.0001)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])

print(model.summary())
plot_model(model, to_file='model_plot4a.png', show_shapes=True, show_layer_names=True)
#plot_model(model, to_file='model_plot4a.png', show_shapes=True, show_layer_names=True)

history = model.fit(X_train, y_train, batch_size=64, epochs=10, verbose=1, validation_split=0.2)

score = model.evaluate(X_test, y_test, verbose=1)

print("Test Score:", score[0])
print("Test Accuracy:", score[1])

import matplotlib.pyplot as plt

plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])

plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])

plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

# txt = ["A WeWork shareholder has taken the company to court over the near-$1.7bn (£1.3bn) leaving package approved for ousted co-founder Adam Neumann."]
# processed_text = preprocess_text(txt)
# seq = tokenizer.texts_to_sequences(processed_text)
# padded = pad_sequences(seq, maxlen=maxlen)
# pred = model.predict(padded)
# print(pred, labels[np.argmax(pred)])

#%% functions in this cell used to run predictions 
import os
import time

n = 5
inputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/redditData/'
outputPath = '/mnt/linuxlab/home/r21vxquin/reddit-data-collector/OutputData/'

def readAnalyzeFile(inputFileName):
    t0 = time.time()
    with open(inputPath + inputFileName + '.csv', 'r') as inputfile:
        allText = inputfile.read()
        allTextArray = allText.split(',')
        allData = []
        for line in allTextArray:
            result = []
            if 'seconds to download' in line:
                break
            processed_text = preprocess_text([line])
            seq = tokenizer.texts_to_sequences([processed_text])
            padded = pad_sequences(seq, maxlen=maxlen)
            pred = model.predict(padded)
            result.append(list(pred.flatten()))
            print(str(processed_text) + ' pred: ' + str(np.argmax(pred))) 
            indices = pred.flatten().argsort()[-n:][::-1]
            print(indices)
            for index in indices:
                result.append(labels[index] + ':' + str(pred.flatten()[index]))
            allData.append(result)
    
    
    outputFileName = inputFileName + 'results.csv'
    with open(outputPath + outputFileName, 'w') as outputfile:
        totals = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        totalTexts = 0
        for dataArray in allData:
            totalTexts += 1
            weights = dataArray[0]
            for i in range(0, 10):
                totals[i] += weights[i]
            outputfile.write(str(dataArray) + '\n')
        averages = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        for i in range(0, 10):
            averages[i] = totals[i] / totalTexts
        sortedAverages = dict(sorted(averages.items(), key=lambda item: item[1]))
        avgIndices = []
        for i in range(5, 10):
            avgIndices.append(list(sortedAverages.keys())[i])
        outputfile.write(str(sortedAverages) + ',')
        for index in avgIndices:
            outputfile.write(labels[index] + ':' + str(averages[index]) + ',')
    outputfile.close()
    
    t1 = time.time()
    print(f"{t1-t0} seconds to analyze and create file")
    print(str(outputFileName) + ' created')
    
    with open(outputPath + outputFileName, 'a') as outputfile:
        outputfile.write(f"{t1-t0} seconds to create file")
    outputfile.close()
            

def main():
    for file in os.listdir(inputPath):
        inputFileName = str(file)[:-4]
        #print(FileNotFoundError())
        #inputFilePath = inputPath + file
        readAnalyzeFile(inputFileName)

#main()
# readAnalyzeFile('Jan2018NewsPosts')
# readAnalyzeFile('Jan2019MemesComments')
readAnalyzeFile('Jan2019MemesPosts')
# readAnalyzeFile('Jan2019mildlyinterestingComments')
readAnalyzeFile('Jan2019mildlyinterestingPosts')
readAnalyzeFile('Jan2019NewsPosts2')
# readAnalyzeFile('Jan2019NewsComments')
# readAnalyzeFile('Jan20192meirl4meirlComments')