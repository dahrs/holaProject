#!/usr/bin/python
#-*- coding:utf-8 -*-

import dataFormater
import extractor, zackExtractor
import stats
import utilsOs, utilsStats, utilsString

"""
testing
"""
if __name__ == '__main__': 

	##################################################################################
	#CALLING FUNCT FROM utilsString.py TO MAKE THE RESSOURCES
	##################################################################################
	'''
	#make ressource trigram dict in english and dump it
	trigramDictMakerFromFile(u'./utilsString/en.txt', u'./utilsString/en3gram.json')

	#make ressource trigram dict in french and dump it
	trigramDictMakerFromFile(u'./utilsString/fr.txt', u'./utilsString/fr3gram.json')

	#make ressource quadrigram dict in english and dump it
	quadrigramDictMakerFromFile(u'./utilsString/en.txt', u'./utilsString/en4gram.json')

	#make ressource quadrigram dict in french and dump it
	quadrigramDictMakerFromFile(u'./utilsString/fr.txt', u'./utilsString/fr4gram.json')

	#make ressource token dict in english and dump it
	tokenDictMakerFromFile(u'./utilsString/en.txt', u'./utilsString/enTok.json')

	#make ressource token dict in french and dump it
	tokenDictMakerFromFile(u'./utilsString/fr.txt', u'./utilsString/frTok.json')
	'''

	##################################################################################
	#CALLING FUNCT FROM extractor.py TO MAKE REALIABLE JOB TITLES
	##################################################################################
	'''
	#make file of reliable job titles using rule-based code
	(extractor.ruleBasedExtractor().getReliableJobTitles(u'./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/job+pitch.tsv', lang=u'en', outputPath=u'./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/reliableJobTitles.txt'))
	
	#make file of reliable job titles using Zack Soliman's code
	extractor.jobTitleExtractorZack().getJobsZackExtracted('./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/jobTitles.txt', outputPath='./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/zackReliableJobs.txt')
	''' 