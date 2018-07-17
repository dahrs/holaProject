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
	return occDict, groupDict, relDict


def makeEscoTree(occUsList, occUkList, groupList, relList):
	''''''
	escoTree = {}
	emptyDict = {}
	occDict, groupList, relDict = makeReferenceDict(occUsList, occUkList, groupList, relList)
	for occup in occDict:
		jobVariants = occDict[occup][u'alternative']
		#we swim up the tree from the leaf to the root (hierarchy list from child to parent)
		listHierarchy = [occup]
		while listHierarchy[-1] in relDict:
			listHierarchy.append(relDict[listHierarchy[-1]])
		#we browse from root to leaf and make the final tree
		escoTree = (finalTree(list(reversed(listHierarchy)), occDict, groupList, relDict, escoTree))
	#tree dumping root-to-leaf
	with codecs.open(u'./escoTree.json', u'wb', encoding=u'utf8') as dictFile:
		json.dump(escoTree, dictFile)
	return escoTree


def finalTree(listHierarchy, occDict, groupList, relDict, tree):
	node = listHierarchy[0]
	if node in groupList:
		nodeName = u'{0}___{1}'.format(groupList[node][u'code'], groupList[node][u'groupName'])
	else:
		nodeName = u'{0}___{1}'.format(occDict[node][u'code'], occDict[node][u'jobTitle'])
	#we browse the immediate childs if we don't find a match we go one level below
	for child in tree:
		#if we find a nodeName that matches we go one level below
		if child == nodeName:
			tree[child] = finalTree(listHierarchy[1:], occDict, groupList, relDict, tree[child])
	dictToMerge = makeSubtree(list(reversed(listHierarchy)), occDict, groupList)
	#if we find the divergent level
	#and we are in a leaf level
	if type(tree) is list and type(dictToMerge) is list:
		tree = tree + dictToMerge
	#we don't update if it's in a level where the key already exists
	elif dictToMerge.keys()[0] in tree:
		pass
	#if we have something new, we update the dicts
	else:
		tree.update(dictToMerge)
	return tree


def makeSubtree(listHierarchy, occDict, groupList):
	'''
	given a hierarchy list (from parent to child), makes a tree containing all values od the hierarchy
	'''
	tempDict = {}
	for url in listHierarchy:
		nodeName = u'{0}___{1}'.format(groupList[url][u'code'], groupList[url][u'groupName']) if url in groupList else u'{0}___{1}'.format(occDict[url][u'code'], occDict[url][u'jobTitle'])
		if url in occDict:
			tempDict = occDict[url][u'alternative']
		elif type(tempDict) is list:
			tempDict = {nodeName: tempDict}
		else:
			tempDict = {nodeName: dict(tempDict)}
	return tempDict




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

catCounter = 0
clasCounter = 0
groupCounter = 0
subGroupCounter = 0
unitCounter = 0
for cat in escoTree:
	catCounter += 1
	for clas in escoTree[cat]:
		clasCounter += 1
		for group in escoTree[cat][clas]:
			groupCounter += 1
			for subGroup in escoTree[cat][clas][group]:
				subGroupCounter += 1
				for unit in escoTree[cat][clas][group][subGroup]:
					unitCounter += 1
print('categ: ', catCounter)
print('class: ', clasCounter)
print('group: ', groupCounter)
print('subgroup: ', subGroupCounter)
print('unit: ', unitCounter)

