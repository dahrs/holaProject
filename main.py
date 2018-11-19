#!/usr/bin/python
#-*- coding:utf-8 -*-

import dataFormater
import extractor
import stats
import utilsOs, utilsStats, utilsString, utilsGraph


def mainActionsOnto(listOfActions, sampleData=False, 
	linkedInData=u'/u/kessler/LBJ/data/2016-09-15/fr/anglophone/candidats.json',
	environment=u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/'):
	'''
	Launches the different actions to make, process and analyse the 
	automatically learned ontology of jobtitles and skills.
	If we want to use the sample data instead of the whole data we 
	need to specify so in the sampledata arg.
	The list of actions must include only ints and floats representing
	the function we want to call:
		- 0 : make the language ressources
		- 1 : make the linkedIn job sets and dicts
			- 1.1 : make the ontologies job sets and dicts
		- 2 : make the linkedIn job-skill edge and node list
		- 3 : clean the graph files (edge and node lists)
		- 4 : modularize the graph files (edge and node lists) into communities
		- 5 : trim the graph files (edge and node lists)
		- 6 : infer the community names using ESCO's domain names
		- 7 : tweak the config.json and index.html graph files (sigma.js output from the gephi software)
		- 8 : get the ontoQA metrics
		- 9.1 : make the sample file for the human annotation
		- 9.2 : make the human annotation
	'''
	if environment[-1] != u'/':
		environment = u'{0}/'.format(environment)
	##################################################################################
	#CALLING FUNCT FROM utilsString.py TO MAKE THE LANGUAGE RESSOURCES
	##################################################################################
	if 0 in listOfActions:
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

	##################################################################################
	#CALLING FUNCT FROM dataFormater.py TO MAKE THE ONTOLOGIES/LINKEDIN JOB SETS AND DICTIONARIES
	##################################################################################
	if 1 in listOfActions:
		pathInput = linkedInData
		pathOutput = u'{0}sample100milFunctions/'.format(environment)
		#we make a sample tsv file of 100000 job titles + description
		#and also a json file containig all the needed information of the sample LinkedIn profiles
		dataFormater.makeSampleFileHavingNJobTitles(pathInput, pathOutput, 100000, True)
	if 1.1 in listOfActions:
		#we open the taxonomies json dicts (trees) 
		esco = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/escoTree.json')
		hrm = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/hrmTree.json')
		isco = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/iscoTreeNatural.json')
		soc = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/socTreeNatural.json')
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
		
		#we transform those dicts into sets (so we can compare them on the same level, without hierarchy)
		grandHacheSet = dataFormater.makeJobSetFromOnto(True, hrm, isco, soc)
		escoSet = dataFormater.makeJobSetFromOnto(True, esco)
		
		#we load the linkedin job titles as a set
		#linkedInPathInput = u'/u/kessler/LBJ/data/2016-09-15/fr/anglophone/candidats.json'
		linkedInPathOutput = environment
		#linkedInSet = dataFormater.makeJobSetFromLinkedIn(linkedInPathInput, lowercaseItAll=True, pathOutput=linkedInPathOutput)
		linkedInPathInput = u'{0}sample7millionFunctions/listOfJobs.linkedIn'.format(environment)
		linkedInSet = dataFormater.loadJobSetFromFile(linkedInPathInput, n=1000000)

		#we print the results so we can make very superficial stats
		print('hache ', len(grandHacheSet))
		print('esco ', len(escoSet))
		print('intersection ', len(escoSet.intersection(grandHacheSet)))

		print('linkedIn ', len(linkedInSet))
		print('intersection esco ', len(escoSet.intersection(linkedInSet)))
		print('intersection hache ', len(linkedInSet.intersection(grandHacheSet)))
	
	##################################################################################
	#CALLING FUNCT FROM dataFormater.py TO MAKE THE LINKEDIN JOB-SKILL EDGE LIST AND NODE LIST
	##################################################################################
	if 2 in listOfActions:
		pathInputSample = linkedInData
		pathOutputToEdgeListFile = u'{0}edgeListWeight.tsv'.format(environment)
		pathOutputToNodeListFile = u'{0}nodeListType.tsv'.format(environment)
		dataFormater.linkedInJobSkillEdgeAndNodeList(pathInputSample, pathOutputToEdgeListFile, pathOutputToNodeListFile, lowercaseItAll=True)

	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO CLEAN THE GRAPH FILES
	##################################################################################
	if 3 in listOfActions:
		#clean the content, supressing language intruders and over-specific job titles
		edgeFilePathInput = u'{0}edgeListWeight.tsv'.format(environment)
		nodeFilePathInput = u'{0}nodeListType.tsv'.format(environment)
		edgeFilePathOutput = u'{0}edgeListWeightCleaned.tsv'.format(environment)
		nodeFilePathOutput = u'{0}nodeListCleaned.tsv'.format(environment)
	
		utilsGraph.ontologyContentCleaning(u'en', edgeFilePathInput, nodeFilePathInput, edgeFilePathOutput, nodeFilePathOutput)
	
	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO MODULARIZE THE EDGE AND NODE LISTS
	##################################################################################
	if 4 in listOfActions:
		edgeFilePath = u'{0}edgeListWeightCleanedNoHeader.tsv'.format(environment)
		nodeFilePath = u'{0}nodeListCleaned.tsv'.format(environment)
		nodeFilePathOutput = u'{0}nodeListCleanedModularized.tsv'.format(environment)

		nodeDf, dendrogram = utilsGraph.modularizeLouvain(edgeFilePath, nodeFilePath, nodeFilePathOutput)
		
		#STATS previsualization of modularity result
		###utilsGraph.getModularityPercentage(outputFilePath)
	
	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO TRIM THE GRAPH FILES
	##################################################################################
	#structure cleaning or trimming of isolated and hapax nodes
	if 5 in listOfActions:
		edgeFilePathInput = u'{0}edgeListWeightCleaned.tsv'.format(environment)
		nodeFilePathInput = u'{0}nodeListCleanedModularized.tsv'.format(environment)
		edgeFilePathOutput = u'{0}edgeListWeightCleanedTrimmed.tsv'.format(environment)
		nodeFilePathOutput = u'{0}nodeListCleanedModularizedTrimmed.tsv'.format(environment)
		
		corefDictPath = u'{0}corefDict.json'.format(environment)

		utilsGraph.ontologyStructureCleaning(edgeFilePathInput, nodeFilePathInput, corefDictPath, edgeFilePathOutput, nodeFilePathOutput)

	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO INFER THE COMMUNITIES NAMES
	##################################################################################
	if 6 in listOfActions:
		nodeFile = u'{0}nodeListCleanedModularizedTrimmed.tsv'.format(environment)
		outputNodeFile = u'{0}nodeListCleanedModularizedTrimmedInfered.tsv'.format(environment)
		utilsGraph.getCommunityNameInferences(nodeFile, outputNodeFile)

		#pretty print a table of the inference and a sample of the job titles
		###utilsGraph.printCommunityInferenceHeaders(outputNodeFile)
	
	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO TWEAK THE CONFIG.JSON AND INDEX.HTML GRAPH FILES
	##################################################################################
	if 7 in listOfActions:
		pathToGraphExportEnvironment = u'./testsGephi/gephiExportSigma0/springLayoutAndModularityPythonLouvain/wholeReCleanedModularizedMoreTrimmedInfered/network/'
		utilsGraph.modifyConfigAndIndexFiles(pathToGraphExportEnvironment)

	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO GET THE ONTOQA METRICS
	##################################################################################
	if 8 in listOfActions:
		#ESCO
		edgeFilePath = u'./001ontologies/ESCO/v1.0.2/edgeAndNodeList/ESCOedgeList.tsv'
		nodeFilePath = u'./001ontologies/ESCO/v1.0.2/edgeAndNodeList/ESCOnodeList.tsv'
		utilsGraph.ontoQA(edgeFilePath, nodeFilePath, verbose=True)
		 
		#Our ontology from all english FR candidates
		edgeFilePath = u'{0}edgeListWeightCleanedTrimmed.tsv'.format(environment)
		nodeFilePath = u'{0}nodeListCleanedModularizedTrimmedInfered.tsv'.format(environment)
		utilsGraph.ontoQA(edgeFilePath, nodeFilePath, verbose=True)

	##################################################################################
	#CALLING FUNCT FROM utilsGraph.py TO MAKE THE HUMAN EVALUATION
	##################################################################################
	edgeFileInput = u'{0}edgeListWeightCleanedTrimmed.tsv'.format(environment)
	nodeFileInput = u'{0}nodeListCleanedModularizedTrimmedInfered.tsv'.format(environment)
	outputEdgeFilePath = u'./009humanAnnotation/sampleEdge1000ForHumanEval.tsv'
	outputNodeFilePath = u'./009humanAnnotation/sampleNode1000ForHumanEval.tsv'
	corefDictPath = u'{0}corefDict.json'.format(environment)

	#make the sample file
	if 9.1 in listOfActions:
		utilsGraph.getSampleForHumanEvaluation(edgeFileInput, nodeFileInput, 1000, outputEdgeFilePath, outputNodeFilePath)
	#launch the evaluation interface
	if 9.2 in listOfActions:
		utilsGraph.humanAnnotatorInterface(outputEdgeFilePath, outputNodeFilePath, corefDictPath, nameOfEvaluator='David', listOfEvaluationsToBeLaunched=[0,1,2,3])



"""
testing
"""
if __name__ == '__main__': 
	
	mainActionsOnto([9.2], 
		sampleData=False, 
		linkedInData=u'/u/kessler/LBJ/data/2016-09-15/fr/anglophone/candidats.json',
		environment=u'./002data/candidats/2016-09-15/fr/anglophone/')


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

