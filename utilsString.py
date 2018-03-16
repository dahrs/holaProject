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
	acronyms = re.compile(r'((?<![A-Z])(([A-Z][\.][&]?){2,}|([A-Z][&]?){2,5})(?![a-z])(?=\b)+)')
	'''
	#we make the regex of acronyms, all uppercase tokens and plain tokens
	acronyms = re.compile(r'((?<![A-Z])(([A-Z]([\.]|[&])?){2,4})(?![a-z])(?=(\b|\n))+)')
	upperTokens = re.compile(r'(\b([A-Z0-9&-][\.]?)+\b)')
	plainTokens = re.compile(r'(\b\w+\b)')
	#if the whole sent is all in caps then we discard it
	if len(re.findall(plainTokens, string)) != len(re.findall(upperTokens, string)) and len(re.findall(plainTokens, string)) >= 2:
		return re.findall(acronyms, string)
	return None


def naiveRegexTokenizer(string):
	'''
	returns the token list using a very naive regex tokenizer
	'''
	plainWords = re.compile(r'(\b\w+\b)', re.UNICODE)
	return re.findall(plainWords, string)


##################################################################################
#LANGUAGE
##################################################################################

def englishOrFrench(string):
	'''guesses the language of a string between english and french'''
	#presence of french specific diacriticals
	diacriticals = [u'à', u'â', u'è', u'é', u'ê', u'ë', u'ù', u'û', u'ô', u'î', u'ï', u'ç', u'œ']
	for char in diacriticals:
		if char in string:
			return u'fr'
	#ngram detection
	string = string.replace(u'\n', u' ').replace(u'\r', u'')
	unkNgramDict = trigramDictMaker(string)
	frenchScore = langDictComparison(unkNgramDict, utilsOs.openJsonFileAsDict(u'./utilsString/fr3gram.json'))
	englishScore = langDictComparison(unkNgramDict, utilsOs.openJsonFileAsDict(u'./utilsString/en3gram.json'))
	#token detection
	unkTokendict = tokenDictMaker(string)
	frenchScore += langDictComparison(unkTokendict, utilsOs.openJsonFileAsDict(u'./utilsString/frTok.json'))
	englishScore += langDictComparison(unkTokendict, utilsOs.openJsonFileAsDict(u'./utilsString/enTok.json'))
	if frenchScore < englishScore:
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
	takes a string, makes a dict of 4grams with their cooccurrence
	'''
	quadrigramDict = {}
	for i in range(len(string)-3):
		quadrigramDict[string[i:i+4]] = quadrigramDict.get(string[i:i+4],0.0)+1.0
	return quadrigramDict


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
		outputFilePath = utilsOs.safeFilePath(inputFilePath.replace(inputFilePath.split(u'/')[-1], 'quadrigrams.json'))
	utilsOs.dumpDictToJsonFile(quadrigramDict, outputFilePath)
	return quadrigramDict


def tokenDictMaker(string):
	'''
	takes a string, makes a dict of tokens with their cooccurrence
	'''
	tokenDict = {}
	for token in naiveRegexTokenizer(string):
		tokenDict[token] = tokenDict.get(token, 0.0)+1.0
	return tokenDict


def tokenDictMakerFromFile(inputFilePath, outputFilePath=None):
	'''
	takes a corpus file, makes a dict of tokens with their cooccurrence
	and dumps the result in a json file
	'''
	tokenDict = {}
	stringList = utilsOs.readAllLinesFromFile(inputFilePath, True)
	for string in stringList:
		tokenList = naiveRegexTokenizer(string.replace(u'/', u' '))
		for token in tokenList:
			tokenDict[token] = tokenDict.get(token,0.0)+(1.0/len(stringList))
			#we also add the lowercase version if there is an uppercase in the token
			if any(c.isupper() for c in token):
				tokenDict[token.lower()] = tokenDict.get(token.lower(),0.0)+(1.0/len(stringList))
	if outputFilePath == None:
		outputFilePath = utilsOs.safeFilePath(inputFilePath.replace(inputFilePath.split(u'/')[-1], 'tokens.json'))
	utilsOs.dumpDictToJsonFile(tokenDict, outputFilePath)
	return tokenDict


##################################################################################
#COMPARISONS AND EVALUATIONS
##################################################################################

def langDictComparison(dictUnk,dictLang):
	'''compares 2 dictionnaries and returns the distance between its keys'''
	distance=0
	maxUnk = max(dictUnk.values())
	for key in dictUnk:
		distance+=abs((dictUnk[key]/maxUnk) - dictLang.get(key,0))
	return distance


##################################################################################
#QUICK COMMANDS
##################################################################################

#trigramDictMakerFromFile(u'./utilsString/en.txt', u'./utilsString/en3gram.json')
#trigramDictMakerFromFile(u'./utilsString/fr.txt', u'./utilsString/fr3gram.json')
#quadrigramDictMakerFromFile(u'./utilsString/en.txt', u'./utilsString/en4gram.json')
#quadrigramDictMakerFromFile(u'./utilsString/fr.txt', u'./utilsString/fr4gram.json')
#tokenDictMakerFromFile(u'./utilsString/en.txt', u'./utilsString/enTok.json')
#tokenDictMakerFromFile(u'./utilsString/fr.txt', u'./utilsString/frTok.json')
