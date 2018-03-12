#!/usr/bin/python
#-*- coding:utf-8 -*-

import re, codecs
import utilsOs


##################################################################################
#ENCODING
##################################################################################

def toUtf8(stringOrUnicode):
	'''
	Returns the argument in utf-8 encoding
	Unescape html entities???????
	'''
	typeArg = type(stringOrUnicode)
	if typeArg is unicode:
		return stringOrUnicode.encode(u'utf8').decode(u'utf8', u'replace')
	elif typeArg is str:
		return stringOrUnicode.decode(u'utf8')




##################################################################################
#REGEX
##################################################################################


def findAcronyms(string):
	'''
	Returns the acronyms found in the string.
	variant : 
	acronyms = re.compile(ur'((?<![A-Z])(([A-Z][\.][&]?){2,}|([A-Z][&]?){2,5})(?![a-z])(?=\b)+)')
	'''
	#we make the regex of acronyms, all uppercase tokens and plain tokens
	acronyms = re.compile(ur'((?<![A-Z])(([A-Z]([\.]|[&])?){2,4})(?![a-z])(?=(\b|\n))+)')
	upperTokens = re.compile(ur'(\b([A-Z0-9&-][\.]?)+\b)')
	plainTokens = re.compile(ur'(\b\w+\b)')
	#if the whole sent is all in caps then we discard it
	if len(re.findall(plainTokens, string)) != len(re.findall(upperTokens, string)) and len(re.findall(plainTokens, string)) >= 2:
		return re.findall(acronyms, string)
	return None


##################################################################################
#LANGUAGE
##################################################################################

def englishOrFrench(string, enJsonPath, frJsonPath):
	'''guesses the language of a string'''
	diacriticals = [u'à', u'â', u'è', u'é', u'ê', u'ë', u'ù', u'û', u'ô', u'î', u'ï', u'ç', u'œ']
	for char in diacriticals:
		if char in string:
			return u'fr'
	string = string.replace(u'\n', u' ').replace(u'\r', u'')
	unkTrigramDict = quadrigramDictMaker(string)
	if langDictComparison(unkTrigramDict,utilsOs.openJsonFileAsDict(frJsonPath)) < langDictComparison(unkTrigramDict,utilsOs.openJsonFileAsDict(enJsonPath)):
		return u'fr'
	return u'en'


##################################################################################
#SPECIAL DICTS
##################################################################################

def trigramDictMaker(string):
	'''
	takes a string, makes a dict of 3grams with their cooccurrence
	'''
	trigramDict = {}
	for i in range(len(string)-2):
		trigramDict[string[i:i+3]] = trigramDict.get(string[i:i+3],0.0)+1.0
	return trigramDict


def quadrigramDictMaker(string):
	'''
	takes a string, makes a dict of 3grams with their cooccurrence
	'''
	trigramDict = {}
	for i in range(len(string)-3):
		trigramDict[string[i:i+4]] = trigramDict.get(string[i:i+4],0.0)+1.0
	return trigramDict


def trigramDictMakerFromFile(inputFilePath, outputFilePath=None):
	'''
	takes a corpus file, makes a dict of 3grams with their cooccurrence
	and dumps the result in a json file
	'''
	trigramDict = {}
	stringList = utilsOs.readAllLinesFromFile(inputFilePath, True)
	langString = u' '.join(stringList)
	for i in range(len(langString)-2):
		trigramDict[langString[i:i+3]] = trigramDict.get(langString[i:i+3],0.0)+(1.0/len(stringList))
	if outputFilePath == None:
		outputFilePath = utilsOs.safeFilePath(inputFilePath.replace(inputFilePath.split(u'/')[-1], 'trigrams.json'))
	utilsOs.dumpDictToJsonFile(trigramDict, outputFilePath)
	return trigramDict


def quadrigramDictMakerFromFile(inputFilePath, outputFilePath=None):
	'''
	takes a corpus file, makes a dict of 4grams with their cooccurrence
	and dumps the result in a json file
	'''
	quadrigramDict = {}
	stringList = utilsOs.readAllLinesFromFile(inputFilePath, True)
	langString = u' '.join(stringList)
	for i in range(len(langString)-3):
		quadrigramDict[langString[i:i+4]] = quadrigramDict.get(langString[i:i+4],0.0)+(1.0/len(stringList))
	if outputFilePath == None:
		outputFilePath = utilsOs.safeFilePath(inputFilePath.replace(inputFilePath.split(u'/')[-1], 'trigrams.json'))
	utilsOs.dumpDictToJsonFile(quadrigramDict, outputFilePath)
	return quadrigramDict


##################################################################################
#COMPARISONS AND EVALUATIONS
##################################################################################

def langDictComparison(dictUnk,dictLang):
	'''compares 2 dictionnaries and returns the distance between its keys'''
	distance=0
	for key in dictUnk:
		distance+=abs(dictUnk[key] - dictLang.get(key,0))
	return distance


#quadrigramDictMakerFromFile(u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/utilsString/en.txt', u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/utilsString/en.json')
#quadrigramDictMakerFromFile(u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/utilsString/fr.txt', u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/utilsString/fr.json')