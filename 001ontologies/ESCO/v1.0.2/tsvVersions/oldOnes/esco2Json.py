#!/usr/bin/python
#-*- coding:utf-8 -*-

import json, codecs, pprint
#import ete3
from collections import defaultdict

#this is a sloppy job, to be commented, organized and prettyfied when I have the time

##################################################################################
#TREE MAKING
##################################################################################

def tree(): return defaultdict(tree) #tree creator


def makeReferenceDict(occUsList, occUkList, groupList, relList):
	occDict = {}
	groupDict = {}
	relDict = {}
	#occupations en-uk
	for occUk in occUkList:
		elemList = occUk.split(u'\t')
		occDict[elemList[1]] = {
			u'code': elemList[2], 
			u'jobTitle': elemList[3].replace(u'"', u''),
			u'alternative': [e for e in (elemList[4].replace(u'"', u'')).split(u', ') if e != u''],
			u'description': elemList[5]}
	#occupations en-us
	for occUs in occUsList:
		elemList = occUs.split(u'\t')
		if elemList[1] in occDict:
			occDict[elemList[1]][u'alternative'].append(elemList[3].replace(u'"', u''))
			occDict[elemList[1]][u'alternative'] = list(set(occDict[elemList[1]][u'alternative'] + [e for e in (elemList[4].replace(u'"', u'')).split(u', ') if e != u'']))
	#groups
	for group in groupList:
		elemList = group.split(u'\t')
		groupDict[elemList[1]] = {
			u'code': elemList[2], 
			u'groupName': elemList[3].replace(u'"', u''),
			u'alternative': [e for e in (elemList[4].replace(u'"', u'')).split(u', ') if e != u''],
			u'description': elemList[5]}
	#relations
	for rel in relList:
		elemList = rel.split(u'\t')
		#child as key, parent as value
		relDict[elemList[1]] = elemList[3]
	return occDict, groupList, relDict


def makeEscoTree(occUsList, occUkList, groupList, relList):
	''''''
	escoTree = {}
	emptyDict = {}
	occDict, groupList, relDict = makeReferenceDict(occUsList, occUkList, groupList, relList)
	for occup in occDict:
		#we swim up the tree from the leaf to the root
		listHierarchy = [occup]
		while listHierarchy[-1] in relDict:
			listHierarchy.append(relDict[listHierarchy[-1]])
		#we browse from root to leaf and make the final tree
		tempTree = {}
		###################tree in tree build final tree
		for node in listHierarchy:
			if node == listHierarchy[0]:
				tempTree[node] = occDict[node]
			else:
				interTree = {}
				tempTree[]
			escoTree[node] = tempTree[node]
	#tree dumping root-to-leaf
	with codecs.open(u'./escoTree.json', u'wb', encoding=u'utf8') as dictFile:
		json.dump(escoTree, dictFile)


def populateFinalTree(node, valueDict, finalTree={}):
	if finalTree == {}:
		return finalTree[node] = valueDict
	




def dfs(start, finalTree, grouptree, relTree, leafVariants=None):
	newTree = {}
	#if start is a branch/leaf node
	if start in relTree:
		parent = relTree[start]
		#if start is leaf
		if leafVariants != None:
			return newTree[parent] = leafVariants ###############
			#populate final tree
			###### for for for
		#if start is branch

		newTree[start] = {}
		for nextN in tree[start]:
			if nextN not in visited:
				newTree[start][nextN] = dfs(tree, nextN, visited)
		return newTree[start]

	#if start is the root
	return None


##################################################################################
#OPEN THE DATA FILE
##################################################################################

def openEscoSpecialFile(pathToFile, lineHeader):
	with codecs.open(pathToFile, u'r', encoding='utf8') as openedFile:
		newLinesList = []
		linesList = openedFile.readlines()[1:]
		for indexL, line in enumerate(linesList):
			if line[:len(lineHeader)] == lineHeader:
				newLinesList.append(line.replace(u'\n', u', '))
			elif indexL+1 != len(linesList) and linesList[indexL+1][:len(lineHeader)] != lineHeader and linesList[indexL+1] != u'':
				newLinesList[-1] = u'{0}{1}'.format(newLinesList[-1], (line.replace(u'\n', u', ')).replace(u'"', u''))
			else:
				newLinesList[-1] = u'{0}{1}'.format(newLinesList[-1], (line.replace(u'\n', u'')).replace(u'"', u''))
	return newLinesList


def openEscoFile(pathToFile):
	with codecs.open(pathToFile, u'r', encoding='utf8') as openedFile:
		linesList = openedFile.readlines()
		linesList = [(e.replace(u'\n', u'').replace(u'\r', u'')) for e in linesList]
	return linesList[1:]


##################################################################################
#QUICK COMMANDS
##################################################################################

occUsList = openEscoSpecialFile('./occupations_en-us.csv', u'Occupation')
occUkList = openEscoSpecialFile('./occupations_en.csv', u'Occupation')
groupList = openEscoSpecialFile('./ISCOGroups_en.csv', u'ISCOGroup')
relList = openEscoFile('./broaderRelationsOccPillar.csv')
escoTree = makeEscoTree(occUsList, occUkList, groupList, relList)
'''
catCounter = 0
clasCounter = 0
groupCounter = 0
unitCounter = 0
for cat in escoTree:
	catCounter += 1
	for clas in escoTree[cat]:
		clasCounter += 1
		for group in escoTree[cat][clas]:
			groupCounter += 1
			for unit in escoTree[cat][clas][group]:
				unitCounter += 1
print('categ: ', catCounter)
print('class: ', clasCounter)
print('group: ', groupCounter)
print('unit: ', unitCounter)
'''
