# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:32:15 2021

@author: erikv
"""
from sklearn.tree import DecisionTreeClassifier
import listReader as lr
#training data
boards = lr.read('boards.txt')
labels = lr.read('labels.txt')
clf=DecisionTreeClassifier()
trainPix = boards[0:90000]
trainLab = labels[0:90000]
clf.fit(trainPix,trainLab)
## testing data
testPix = boards [90000:]
testLab= labels [90000:]
testLen=len(testLab)
p=clf.predict(testPix)
count=0
for i in range(testLen):
    if p[i]==testLab[i]:count+=1
print ((count/testLen)*100) ## neural network accuracy