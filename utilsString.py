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
	try:
		if typeArg is str:
			return stringOrUnicode.decode(u'utf8')
		elif typeArg is unicode:
			return stringOrUnicode.encode(u'utf8').decode(u'utf8', u'replace')
	except AttributeError:
		return stringOrUnicode


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
	acronyms = re.compile(r'((?<![A-Z])(([A-Z]([\.]|[&])?){2,4})(?![a-z])(?=(\b|\n))+)') #2-4 uppercase characters that might be separated by . or & 
	upperTokens = re.compile(r'(\b([A-Z0-9&-][\.]?)+\b)')
	plainTokens = re.compile(r'(\b\w+\b)')
	#if the whole sent is all in caps then we discard it
	if len(re.findall(plainTokens, string)) != len(re.findall(upperTokens, string)) and len(re.findall(plainTokens, string)) >= 2:
		return re.findall(acronyms, string)
	return None


def removeStopwords(tokenList, language=u'english'):
	from nltk.corpus import stopwords		
	#stopwords
	to_remove = set(stopwords.words("english") + ['', ' ', '&'])
	return list(filter(lambda tok: tok not in to_remove, tokenList))


def naiveRegexTokenizer(string, caseSensitive=True, eliminateEnStopwords=False):
	'''
	returns the token list using a very naive regex tokenizer
	'''
	plainWords = re.compile(r'(\b\w+\b)', re.UNICODE)
	tokens = re.findall(plainWords, string)
	#if we don't want to be case sensitive
	if caseSensitive != True:
		tokens = [tok.lower() for tok in tokens]
	#if we don't want the stopwords
	if eliminateEnStopwords != False:
		tokens = removeStopwords(tokens, language='english')
	return tokens 


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
	#token detection
	unkTokendict = tokenDictMaker(string)
	#ngram char detection
	unkNgramDict = trigramDictMaker(string.replace(u'\n', u' ').replace(u'\r', u''))
	#if the obtained dict is empty, unable to detect (probably just noise)
	if len(unkTokendict) == 0 or len(unkNgramDict) == 0:
		return 'unknown'
	#token scores
	frenchTokScore = langDictComparison(unkTokendict, utilsOs.openJsonFileAsDict(u'./utilsString/frTok.json'))
	englishTokScore = langDictComparison(unkTokendict, utilsOs.openJsonFileAsDict(u'./utilsString/enTok.json'))
	#ngram scores
	frenchNgramScore = langDictComparison(unkNgramDict, utilsOs.openJsonFileAsDict(u'./utilsString/fr3gram.json'))
	englishNgramScore = langDictComparison(unkNgramDict, utilsOs.openJsonFileAsDict(u'./utilsString/en3gram.json'))
	#the smaller the string (in tokens), the more we want to prioritize the token score instead of the ngram score
	if len(unkTokendict) < 5:
		ratioNgram = float(len(unkTokendict))/10.0
		frenchTokScore = frenchTokScore * (1.0-ratioNgram)
		frenchNgramScore = frenchNgramScore * ratioNgram
		englishTokScore = englishTokScore * (1.0-ratioNgram)
		englishNgramScore = englishNgramScore * ratioNgram
	#we compare the sum of the language scores
	if (frenchTokScore+frenchNgramScore) < (englishTokScore+englishNgramScore):
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
	'''
	compares 2 dictionnaries and returns the distance between its keys
	'''
	distance=0
	maxUnk = max(dictUnk.values())
	for key in dictUnk:
		distance+=abs((dictUnk[key]/maxUnk) - dictLang.get(key,0))
	return distance
