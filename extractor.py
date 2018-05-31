#!/usr/bin/python
#-*- coding:utf-8 -*-

import re, codecs, utilsString, utilsOs
from nltk import pos_tag
from nltk.corpus import stopwords


class ruleBasedExtractor():
	'''
	'''
	def __init__(self):
		pass


	def reliableFilter1(self, jobAndPitchFilePath):
		'''
		Rule based filter for all information that needs to analyze
		the raw line of the candidate job title, pitch, etc:
		- not having ampersand (&) or slash (/) signs
		- having less than 3 tokens
		- not having acronyms
		'''
		candidatesDict = {}
		#we look at the job title file line by line (job by job)
		for line in openedFile:
			job = line.split(u'\t')[0]
			#not having ampersand (&) or slash (/ \) signs or brackets (()[]{}) and punctuation (, . ! ?)
			if re.search(r'(&|/|\\|\(|\)|\[|\]|\{|\}|\.|,|\!|\?)', job) == None:
				jobTokenList = utilsString.naiveRegexTokenizer(job.replace(u'/', u' '))
				#having less than 3 tokens
				if len(jobTokenList) <= 3:
					#discard the ones that have accronyms
					if utilsString.findAcronyms(job) != None:
						candidatesDict[line.lower()] = candidatesDict.get(line.lower(),0)+1
		return candidatesDict


	def reliableFilter2(self, candidatesDict, lang, includeJobsWithNApitch):
		'''
		Rule based filter for all information that needs to analyze
		the lines after passing through one first filter:
		- present more than once (no hapax)
		- being the right language (en/fr in both 'job' and 'pitch')
		'''
		setOfReliableJobs = set()
		#if it's present more than once then add it to the set
		for line in candidatesDict:
			job = line.split(u'\t')[0]
			pitch = line.split(u'\t')[1]
			#we might not want to include empty pitchs (that helps to identify the language)
			processIt = False if pitch != 'na\n' and includeJobsWithNApitch != True else True
			#if it's present more than once
			if candidatesDict[line] > 1 and processIt == True:
				#try to guess the language (job title and corresponding pitch) and if it doesn't match do not take it into account
				if lang == utilsString.englishOrFrench(line):
					setOfReliableJobs.add(job)
		return setOfReliableJobs


	def getReliableJobTitles(self, jobAndPitchFilePath, lang=u'en', outputPath=None, includeJobsWithNApitch=True):
		'''
		Make a set containing the job titles that might be considered more reliable:
		filter 1:
			- having less than 3 tokens
			- not having ampersand (&) or slash (/) signs
			- not having acronyms
		filter 2:
			- present more than once (no hapax)
			- being the right language (en/fr in both 'job' and 'pitch')
		'''
		with codecs.open(jobAndPitchFilePath, 'r', encoding='utf8') as openedFile:
			candidatesDict = self.reliableFilter1(openedFile)
		setOfReliableJobs = self.reliableFilter2(candidatesDict, lang, includeJobsWithNApitch)

		#dump the output if the output path is specified
		if outputPath != None:
			utilsOs.dumpRawLines(setOfReliableJobs, outputPath, addNewline=True, rewrite=True)
		return setOfReliableJobs



class jobTitleExtractorZack():
	'''
	Implements the job title extractor coded by Zack Soliman
	'''
	def __init__( self ):
		pass

	#stopwords
	to_remove = set(stopwords.words("english") + ['', ' ', '&'])
	#pattern of tokenizer splitters
	pattrn = re.compile(r"[-/,\.\\\/\s\&\"\']")	

	def getNgram_counts(self, jobFilePath, to_remove, pattrn):
		'''
		Makes a dict of every 1-, 2-, 3-gram in the 
		job source file
		'''
		ngram_counts = {}	
		with codecs.open(jobFilePath, 'r', encoding='utf8') as openedFile:
			for index, line in enumerate(openedFile):
				jobTitle = line.replace('\n', '')
				tokens = re.split(pattrn, jobTitle)
				tokens = list(filter(lambda tok: tok not in to_remove, tokens))
				for n in range(1,4):
					for ngram in self.get_ngrams(n, tokens):
						ngram_counts[ngram] = ngram_counts.get(ngram, 0)+1
		return ngram_counts


	def testZackExtractor(self, sentence, to_remove, pattrn):
		'''
		just a test, if we need to call the extractor multiple times we need to
		keep the ngram_counts dict in memory instead of making it over and over
		'''
		ngram_counts = self.getNgram_counts(u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/jobTitles.txt', to_remove, pattrn)
		return self.get_best(sentence, to_remove, pattrn, ngram_counts)


	def getJobsZackExtracted(self, jobFilePath, outputPath=None, to_remove=to_remove, pattrn=pattrn):
		'''
		extracts the most best jobs according to their co-reference 
		in decreasing order of ngram: 
			chief executive officer 
				IS BETTER THAN 
			chief officer 
				IS BETTER THAN 
			officer
		'''
		setOfJobs = set()
		#count jobs co-reference (counting the (1-4)-gram token words in the job title)
		ngram_counts = self.getNgram_counts(jobFilePath, to_remove, pattrn)
		#get best possibility
		with codecs.open(jobFilePath, 'r', encoding='utf8') as openedFile:
			for index, jobTitle in enumerate(openedFile):
				#ORIGINAL extractor bestOption = self.get_best(jobTitle, to_remove, pattrn, ngram_counts)
				bestOption = self.get_best_modified(jobTitle, to_remove, pattrn, ngram_counts) 
				#add the 'best' job name to the final set
				if bestOption != "<unk>":
					setOfJobs.add(bestOption)
		#dump the output if the output path is specified
		if outputPath != None:
			utilsOs.dumpRawLines(setOfJobs, outputPath, addNewline=True, rewrite=True)
		return setOfJobs


	def get_best_modified(self, s, to_remove, pattrn, ngram_counts, lang='en'):
		#only get something if it matches the language
		if lang == utilsString.englishOrFrench(s):
			tokens = re.split(pattrn, s)
			#in this modified version we add the french stopwords (since it might be noisy)
			to_remove.union(set(stopwords.words("french")))
			tokens = list(filter(lambda tok: tok not in to_remove, tokens))
			bigram = False
			trigram = False

			if len(tokens) == 0:
				return "<unk>"
			
			unigram = max(self.get_ngrams(1, tokens), key=lambda x: ngram_counts[x])
			if len(tokens) >= 2:
				bigram = max(self.get_ngrams(2, tokens), key=lambda x: ngram_counts[x])
			if len(tokens) >= 3:
				trigram = max(self.get_ngrams(3, tokens), key=lambda x: ngram_counts[x])

			#when not using a sample, we can augment the arbitrary coreference frontier ie:
			#if trigram and ngram_counts[trigram] > 100
			if trigram and ngram_counts[trigram] > 10:
				return " ".join(trigram)
			#when not using a sample, we can augment the arbitrary coreference frontier ie:
			#if trigram and ngram_counts[trigram] > 100
			elif bigram and ngram_counts[bigram] > 10:
				return " ".join(bigram)
			#add a very high score for unigrams for them to be considered results
			elif ngram_counts[unigram] > 100:
				return unigram[0]
		return "<unk>"
		

	####Zack Soliman's code##############################

	def get_best(self, s, to_remove, pattrn, ngram_counts):
		tokens = re.split(pattrn, s)
		tokens = list(filter(lambda tok: tok not in to_remove, tokens))
		bigram = False
		trigram = False

		if len(tokens) == 0:
			return "<unk>"

		unigram = max(self.get_ngrams(1, tokens), key=lambda x: ngram_counts[x])
		if len(tokens) >= 2:
			bigram = max(self.get_ngrams(2, tokens), key=lambda x: ngram_counts[x])
		if len(tokens) >= 3:
			trigram = max(self.get_ngrams(3, tokens), key=lambda x: ngram_counts[x])

		#when not using a sample, we can augment the arbitrary coreference frontier ie:
		#if trigram and ngram_counts[trigram] > 100
		if trigram and ngram_counts[trigram] > 10:
			return " ".join(trigram)
		#when not using a sample, we can augment the arbitrary coreference frontier ie:
		#if trigram and ngram_counts[trigram] > 100
		elif bigram and ngram_counts[bigram] > 10:
			return " ".join(bigram)
		else:
			return unigram[0]


	def get_ngrams(self, n, tokens):
		return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
