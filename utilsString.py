#!/usr/bin/python
#-*- coding:utf-8 -*-

import re, codecs, nltk
from langdetect import detect


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


def fromHexToDec(hexCode):
	'''
	transforms a unicode hexadecimal code given in string form
	into a decimal code as an integral
	'''
	if type(hexCode) is int:
		return hexCode
	#delete all possible unicode affixes given to the hex code
	hexCode = hexCode.lower().replace(u' ', u'')
	for affix in [u'u+', u'u', u'u-']:
		hexCode = hexCode.replace(affix, u'')
	return int(hexCode, 16)


def unicodeCodeScore(string, countSpaces=False, unicodeBlocksList=[(0, 128)]):
	'''
	Returns a normalized score of the proportion of
	characters between the integer-code block-frontiers 
	over all the characters of the word.
	(the element of the list can be a tuple or a list if 
	we want a start and an end frontier, or it can be a
	string or an integral if we want to add only one 
	specific code)
	e.g., 
		for an ascii frontier(U+0-U+128) == unicodeBlocksList=[(0, 128)] :
			'touche' = 1.0 
			'touché' = 0.833333			
			'ключ' = 0.0
		for an ascii frontier (U+0-U+128) + the french loan-character 'é' (U+00E9) == unicodeBlocksList=[(0, 128), [201] :
			'touche' = 1.0 
			'touché' = 1.0			
			'ключ' = 0.0
		for an cyrilic frontier (U+0400-U+04FF) == unicodeBlocksList=[[1024, 1279], ('0500', '052F'), 1280] :
			'touche' = 0.0 
			'touché' = 0.0
			'ключ' = 1.0
	'''
	totalOfAcceptedChars = 0
	acceptedUnicodeCodes = set()
	#delete spaces if needed
	if countSpaces == False:
		string = string.replace(u' ', u'')
	#make a list of accepted unicode codes 
	for frontierElement in unicodeBlocksList:
		#if the element is a lone code
		if type(frontierElement) is int or type(frontierElement) is str :
			#if the code is in hexadecimal, transform to decimal code and add it to the accepted set
			acceptedUnicodeCodes.add(fromHexToDec(frontierElement))
		#if the element is only one code
		elif len(frontierElement) == 1:	
			#if the code is in hexadecimal, transform to decimal code and add it to the accepted set
			acceptedUnicodeCodes.add(fromHexToDec(frontierElement[0]))
		#if the element is 2 codes (start and end)
		elif len(frontierElement) == 2:	
			#if the frontiers are in hexadecimal, transform to decimal code and union the set of all intervals between the start and end frontier
			acceptedUnicodeCodes = acceptedUnicodeCodes.union(set(range(fromHexToDec(frontierElement[0]), fromHexToDec(frontierElement[1])+1)))
		#if it's bigger than 2, it's not taken into account
	#verify if the characters of the strings are in the accepted set
	for char in string:
		if ord(char) in acceptedUnicodeCodes:
			totalOfAcceptedChars += 1
	return float(totalOfAcceptedChars) / float(len(string))


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


def naiveRegexTokenizer(string, caseSensitive=True, eliminateEnStopwords=False, language=u'english'):
	'''
	returns the token list using a very naive regex tokenizer
	'''
	plainWords = re.compile(r'(\b\w+\b)', re.UNICODE)
	tokens = re.findall(plainWords, string.replace(u'\r', u'').replace(u'\n', u' '))
	#if we don't want to be case sensitive
	if caseSensitive != True:
		tokens = [tok.lower() for tok in tokens]
	#if we don't want the stopwords
	if eliminateEnStopwords != False:
		tokens = removeStopwords(tokens, language=language)
	return tokens


def naiveStemmer(string, caseSensitive=True, eliminateEnStopwords=False, language=u'english'):
	'''
	returns the stemmed token list using nltk
	where a stem is a word of a sentence converted to its non-changing portions
	possible stemmer argument options are 'snowball', 'lancaster', 'porter'
	'''
	from nltk.tokenize import word_tokenize
	from nltk.stem.snowball import SnowballStemmer as stemmer
	#tokenize
	tokens = word_tokenize(string)
	#if we don't want to be case sensitive
	if caseSensitive != True:
		tokens = [tok.lower() for tok in tokens]
	#if we don't want the stopwords
	if eliminateEnStopwords != False:
		tokens = removeStopwords(tokens, language=language)
	#get stems
	stems = [stemmer(language).stem(tok) for tok in tokens]
	return tokens


def naiveEnLemmatizer(string, caseSensitive=True, eliminateEnStopwords=False):
	'''
	returns the lemmatized token list using nltk
	where a lemma is a word of a sentence converted to its dictionnary standard form
	works only for english text
	'''
	from nltk.tokenize import word_tokenize
	from nltk import WordNetLemmatizer
	lemmatizer = WordNetLemmatizer()
	#tokenize
	tokens = word_tokenize(string)
	#if we don't want to be case sensitive
	if caseSensitive != True:
		tokens = [tok.lower() for tok in tokens]
	#if we don't want the stopwords
	if eliminateEnStopwords != False:
		tokens = removeStopwords(tokens, language=u'english')
	#get lemmas
	lemmas = [lemmatizer.lemmatize(tok) for tok in tokens]
	return tokens


def tokenizeAndExtractSpecificPos(string, listOfPosToReturn, caseSensitive=True, eliminateEnStopwords=False):
	'''
	using nltk pos tagging, tokenize a string and extract the
	tokens corresponding to the specified pos
	The pos labels are:	
		- cc coordinating conjunction
		- cd cardinal digit
		- dt determiner
		- in preposition/subordinating conjunction
		- j adjective
		- n noun
		- np proper noun
		- p pronoun
		- rb adverb
		- vb verb
	'''
	posDict = {u'cc': [u'CC'], u'cd': [u'CD'], u'dt': [u'DT', u'WDT'], u'in': [u'IN'], u'j': [u'JJ', u'JJR', u'JJS'], u'n': [u'NN', u'NNS'], u'np': [u'NNP', u'NNPS'], u'p': [u'PRP', u'PRP$', u'WP$'], u'rb': [u'RB', u'RBR', u'RBS', u'WRB'], u'vb': [u'MD', u'VB', u'VBD', u'VBG', u'VBN', u'VBZ']}
	listPos = []
	#tokenize
	tokens = nltk.word_tokenize(string)
	#we replace the general pos for the actual nltk pos
	for generalPos in listOfPosToReturn:
		listPos = listPos + posDict[generalPos]
	#pos tagging
	tokensPos = nltk.pos_tag(tokens)
	#reseting the tokens list
	tokens = []
	#selection of the pos specified tokens
	for tupleTokPos in tokensPos:
		#if they have the right pos
		if tupleTokPos[1] in listPos:
			tokens.append(tupleTokPos[0])
	#if we don't want to be case sensitive
	if caseSensitive != True:
		tokens = [tok.lower() for tok in tokens]
	#if we don't want the stopwords
	if eliminateEnStopwords != False:
		tokens = removeStopwords(tokens, language='english')
	return tokens


def indicator2in1(string):
	'''
	detects if a string has '/', '\', ',', ':', ';', ' - ' and '&' between words
	if it does it returns true, otherwise it returns false
	'''
	#we make the regex of 2 in 1 substrings
	twoInOneSubstring = re.compile(r'([\w]{2,}([\s|\t]?)&([\s|\t]?)[\w]{2,})|([\w]+([\s|\t]?)(\\|\/|,|:|;)([\s|\t]?)[\w]+)|([\w]+[\s]+-[\s]*[\w]+)|([\w]+-[\s]+[\w]+)')
	#if we find at least one substring indicating a 2 in 1, return true
	if len(re.findall(twoInOneSubstring, string)) != 0:
		return True
	return False


def indicator3SameLetters(string):
	'''
	detects if the string contains a substring composed ot the same 3 characters or more (type of characters limited)
	'''
	#we make the regex of 3 same letters
	threeCharRepetition = re.compile(r'(a){3,}|(b){3,}|(c){3,}|(d){3,}|(e){3,}|(f){3,}|(g){3,}|(h){3,}|(i){3,}|(j){3,}|(k){3,}|(l){3,}|(m){3,}|(n){3,}|(o){3,}|(p){3,}|(q){3,}|(r){3,}|(s){3,}|(t){3,}|(u){3,}|(v){3,}|(w){3,}|(x){3,}|(y){3,}|(z){3,}|(,){3,}|(\.){3,}|(:){3,}|(;){3,}|(\?){3,}|(!){3,}|(\'){3,}|(\"){3,}|(-){3,}|(\+){3,}|(\*){3,}|(\/){3,}|(\\){3,}|(\$){3,}|(%){3,}|(&){3,}|(@){3,}|(#){3,}|(<){3,}|(>){3,}|(\|){3,}')
	#if we find at least one substring indicating a 2 in 1, return true
	if len(re.findall(threeCharRepetition, string.lower())) != 0:
		return True
	return False


def isItGibberish(string, gibberishTreshold=0.49, exoticCharSensitive=False):
	'''
	Detect if the string is composed of mostly gibberish (non-alphanumerical symbols)
	and repetition of the same letter.
	it returns true if the gibberish treshold is surpassed, false otherwise
	if exoticCharSensitive is False, it will treat non-latin-based characters as gibberish too
	'''
	nonGibberishCharsList = []
	latinExtChars = set( list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123)) + list(range(192, 215)) + list(range(216, 247)) + list(range(248, 384)) + list(range(536, 540)))
	symbolsChars = set( list(range(0, 48)) + list(range(58, 65)) + list(range(91, 97)) + list(range(123, 192)) + [215, 247, 884, 885, 894, 903] )
	#detect if there is a repetition of the same 3 letters
	if indicator3SameLetters(string) == True:
		return True
	string = string.replace(u' ', u'')
	#treat non-latin-based characters as gibberish too
	if exoticCharSensitive == False:
		#detect accepted characters, append non-acepted to list
		for char in string:
			if ord(char) in latinExtChars:
				nonGibberishCharsList.append(char)	
	#treat non-latin-based characters as an alphabet
	else:
		#detect non accepted characters
		for char in string:
			if ord(char) not in symbolsChars:
				nonGibberishCharsList.append(char)
	#calculate the ratio of non-gibberish in the string
	nonGibberishRatio = float(len(nonGibberishCharsList))/float(len(string))
	if (1.0-nonGibberishRatio) >= gibberishTreshold:
		#for very small labels, symbols are not that uncommon, so we do not apply the same rigor
		if len(string) <= 4:
			if (1.0-nonGibberishRatio) == 0.0:
				return True
			return False
		return True
	return False
		
	

##################################################################################
#LANGUAGE
##################################################################################

def englishOrFrench(string):
	'''guesses the language of a string between english and french'''
	import utilsOs
	from langdetect.lang_detect_exception import LangDetectException
	#if the string is only made of numbers and non alphabetic characters we return 'unknown'
	if re.fullmatch(re.compile(r'([0-9]|-|\+|\!|\#|\$|%|&|\'|\*|\?|\.|\^|_|`|\||~|:|@)+'), string) != None:
		return u'unknown'
	#if more than 30% of the string characters is outside the ascii block and the french block, then it must be another language and we return 'unknown'
	if unicodeCodeScore(string, countSpaces=False, unicodeBlocksList=[[0, 255]]) < 0.7:
		return u'unknown'
	#if the string has a presence of unicode characters of french specific diacritics
	diacritics = [192, 194, [199, 203], 206, 207, 212, 140, 217, 219, 220, 159, 224, 226, [231, 235], 238, 239, 244, 156, 250, 251, 252, 255]
	if unicodeCodeScore(string, countSpaces=False, unicodeBlocksList=diacritics) > 0.0:
		return u'fr'
	#putting the string in lowercase improves the language detection functions
	string = string.lower()
	#use langdetect except if it returns something else than "en" or "fr", if the string is too short it's easy to mistake the string for another language
	try:
		lang = detect(string)
		if lang in [u'en', u'fr']:
			return lang
	#if there is an encoding or character induced error, we try the alternative language detection
	except LangDetectException:
		pass 
	#alternative language detection
	#token detection
	unkTokendict = tokenDictMaker(string)
	#ngram char detection
	unkNgramDict = trigramDictMaker(string.replace(u'\n', u' ').replace(u'\r', u''))
	#if the obtained dict is empty, unable to detect (probably just noise)
	if len(unkTokendict) == 0 or len(unkNgramDict) == 0:
		return u'unknown'
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
	import utilsOs
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
	import utilsOs
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
	import utilsOs
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

def langDictComparison(dictUnk, dictLang):
	'''
	compares 2 dictionnaries and returns the distance between 
	its keys (using the scores in the values)
	'''
	distance=0
	weight = 1
	#get the greatest value so we can use it as a divisor
	maxUnk = float(max(dictUnk.values()))
	#we make the sum of all the distances
	for key in dictUnk:
		#distance calculation
		distance+=abs((dictUnk[key]/maxUnk) - dictLang.get(key,0))
	return distance
