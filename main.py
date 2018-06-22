#!/usr/bin/python
#-*- coding:utf-8 -*-

import dataFormater
import extractor
import stats
import utilsOs, utilsStats, utilsString, utilsGraph

"""
testing
"""
if __name__ == '__main__': 

	##################################################################################
	#CALLING FUNCT FROM utilsString.py TO MAKE THE LANGUAGE RESSOURCES
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
	#CALLING FUNCT FROM dataFormater.py TO MAKE THE ONTOLOGIES/LINKEDIN JOB SETS AND DICTIONARIES
	##################################################################################
	'''
	pathInput = u'/u/kessler/LBJ/data/2016-09-15/fr/anglophone/candidats.json'
	pathOutput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/'

	#we make a sample tsv file of 100000 job titles + description
	#and also a json file containig all the needed information of the sample LinkedIn profiles
	dataFormater.makeSampleFileHavingNJobTitles(pathInput, pathOutput, 100000, True)
	'''
	'''
	#we open the taxonomies json dicts (trees) 
	esco = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/escoTree.json')
	hrm = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/hrmTree.json')
	isco = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/iscoTreeNatural.json')
	soc = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/socTreeNatural.json')
	'''
	'''
	#we make sets out of the taxonomies
	escoSet = dataFormater.dfsExtractor(esco, set(), lowercaseItAll=True)
	hrmSet = dataFormater.dfsExtractor(hrm, set(), lowercaseItAll=True)
	iscoSet = dataFormater.dfsExtractor(isco, set(), lowercaseItAll=True)
	socSet = dataFormater.dfsExtractor(soc, set(), lowercaseItAll=True)
	#we dump the sets in json form (so we can analyse them more easely with jq)
	dataFormater.dumpSetToJson(escoSet, u'./jsonJobTaxonomies/escoSet.json')
	dataFormater.dumpSetToJson(hrmSet, u'./jsonJobTaxonomies/hrmSet.json')
	dataFormater.dumpSetToJson(iscoSet, u'./jsonJobTaxonomies/iscoSet.json')
	dataFormater.dumpSetToJson(socSet, u'./jsonJobTaxonomies/socSet.json')
	'''

	'''
	#we transform those dicts into sets (so we can compare them on the same level, without hierarchy)
	grandHacheSet = dataFormater.makeJobSetFromOnto(True, hrm, isco, soc)
	escoSet = dataFormater.makeJobSetFromOnto(True, esco)
	
	#we load the linkedin job titles as a set
	#linkedInPathInput = u'/u/kessler/LBJ/data/2016-09-15/fr/anglophone/candidats.json'
	linkedInPathOutput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/'
	#linkedInSet = dataFormater.makeJobSetFromLinkedIn(linkedInPathInput, lowercaseItAll=True, pathOutput=linkedInPathOutput)
	linkedInPathInput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample7millionFunctions/listOfJobs.linkedIn'
	linkedInSet = dataFormater.loadJobSetFromFile(linkedInPathInput, n=1000000)

	#we print the results so we can make very superficial stats
	print('hache ', len(grandHacheSet))
	print('esco ', len(escoSet))
	print('intersection ', len(escoSet.intersection(grandHacheSet)))

	print('linkedIn ', len(linkedInSet))
	print('intersection esco ', len(escoSet.intersection(linkedInSet)))
	print('intersection hache ', len(linkedInSet.intersection(grandHacheSet)))
	'''


	##################################################################################
	#CALLING FUNCT FROM dataFormater.py TO MAKE THE LINKEDIN JOB-SKILL EDGE LIST FOR GRAPH MAKING
	##################################################################################
	'''
	#from the 100 000 sample with doubles
	pathInputSample = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/sample.json'
	pathOutputToEdgeListFile = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListWeight.tsv'
	pathOutputToNodeListFile = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListType.tsv'
	dataFormater.linkedInJobSkillEdgeAndNodeList(pathInputSample, pathOutputToEdgeListFile, pathOutputToNodeListFile, lowercaseItAll=True)
	

	#from all english FR candidates
	pathInputSample = u'/u/kessler/LBJ/data/2016-09-15/fr/anglophone/candidats.json'
	pathOutputToEdgeListFile = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/edgeListWeight.tsv'
	pathOutputToNodeListFile = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/nodeListType.tsv'
	dataFormater.linkedInJobSkillEdgeAndNodeList(pathInputSample, pathOutputToEdgeListFile, pathOutputToNodeListFile, lowercaseItAll=True)
	''' 

	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO MAKE THE GRAPH EDGES AND NODES FILES
	##################################################################################
	
	#from the 100 000 sample
	edgeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListWeight.tsv'
	nodeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListType.tsv'
	outputFilePath=u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListTypeModularity.tsv'

	nodesDict, communityDict = utilsGraph.modularize(edgeFilePath, nodeFilePath, 150, outputFilePath)
	#STATS previsualization of modularity result
	utilsGraph.getModularityPercentage(outputFilePath)
	
	#from all english FR candidates
	edgeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/edgeListWeight.tsv'
	nodeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/nodeListType.tsv'
	outputFilePath=u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/nodeListTypeModularity.tsv'

	nodesDict, communityDict = utilsGraph.modularize(edgeFilePath, nodeFilePath, 150, outputFilePath)
	#STATS previsualization of modularity result
	utilsGraph.getModularityPercentage(outputFilePath)
	''' '''


	##################################################################################
	#CALLING FUNCT FROM extractor.py TO MAKE REALIABLE JOB TITLES
	##################################################################################
	'''
	#make file of reliable job titles using rule-based code
	(extractor.ruleBasedExtractor().getReliableJobTitles(u'./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/job+pitch.tsv', lang=u'en', outputPath=u'./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/reliableJobTitles.txt'))
	
	#make file of reliable job titles using Zack Soliman's code
	extractor.jobTitleExtractorZack().getJobsZackExtracted('./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/jobTitles.txt', outputPath='./002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/zackReliableJobs.txt')
	''' 

	##################################################################################
	#CALLING FUNCT FROM stats.py TO MAKE STATS ON THE PROJECT
	##################################################################################

	'''
	#linked in sample 100 000
	pathToFile = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/jobTitles.txt'
	lineList = utilsOs.readAllLinesFromFile(pathToFile, noNewLineChar=True, asStringNotUnicode=False)
	distribDict = utilsStats.tokenDistribution(lineList)
	print('LINKED IN')
	for k, v in distribDict.items():
		print('de longueur tok :', k, '  il y a :', v[0])

	#esco distribution
	esco = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/escoTree.json')
	escoSet = dataFormater.dfsExtractor(esco, set(), lowercaseItAll=True)
	distribDict = utilsStats.tokenDistribution(escoSet)
	print('ESCO')
	for k, v in distribDict.items():
		print('de longueur tok :', k, '  il y a :', v[0])
	'''

