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


	def getReliableJobTitles(self, jobAndPitchFilePath, lang=u'en', outputPath=None):
		'''
		Make a set containing the job titles that might be considered more reliable:
		- having less than 3 tokens
		- not being the right language (job + pitch)
		- not having acronyms
		- present more than once (no hapax)
		- not having ampersand (&) or slash (/) signs
		'''
		candidatesDict = {}
		plainWords = re.compile(ur'(\b\w+\b)')
		#we look at the job title file line by line (job by job)
		with codecs.open(jobAndPitchFilePath, 'r', encoding='utf8') as openedFile:
			for line in openedFile:
				job = line.split(u'\t')[0]
				#not having ampersand (&) or slash (/ \) signs
				if u'&' not in job or u'/' not in job or u'\\' not in job:
					lineTokenList = re.findall(plainWords, job.replace(u'/', u' '))
					#having less than 3 tokens
					if len(lineTokenList) <= 3:
						#discard the ones that have accronyms
						if utilsString.findAcronyms(job) != None:
							candidatesDict[line.lower()] = candidatesDict.get(line.lower(),0)+1
		setOfReliableJobs = set()
		#if it's present more than once then add it to the set
		for line in candidatesDict:
			job = line.split(u'\t')[0]
			pitch = line.split(u'\t')[1]
			if candidatesDict[line] > 1:
				#try to guess the language (job title and corresponding pitch) and if it doesn't match do not take it into account
				#if there is no pitch it's discarded
				if u'NA' not in line and lang == utilsString.englishOrFrench(line, u'./utilsString/en.json', u'./utilsString/fr.json'):
					setOfReliableJobs.add(job)
		#dump the output if the output path is specified
		if outputPath != None:
			utilsOs.dumpRawLines(setOfReliableJobs, outputPath, addNewline=False, rewrite=True)
		return setOfReliableJobs


setOfReliableJobs = (ruleBasedExtractor().getReliableJobTitles(u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/job+pitch.tsv', lang=u'en', outputPath=u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/reliableJobTitles.txt'))
for x in setOfReliableJobs:
	print(x)