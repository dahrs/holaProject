#!/usr/bin/python
#-*- coding:utf-8 -*-

import json, codecs, random, shutil, os
from tqdm import tqdm
import pandas as pd
import numpy as np
import networkx as nx

import utilsOs, utilsString


##################################################################################
#TOOL FUNCTIONS
##################################################################################


def getDataFrameFromArgs(df1arg, df2arg=None):
	'''
	we chech if 'df1arg' and 'df2arg' are string paths or pandas dataframes
	'''
	#df1
	if type(df1arg) != str: # or type(df1arg) != unicode:
		df1 = df1arg
	else:
		df1 = pd.read_csv(df1arg, sep=u'\t')
	#df2
	if df2arg == None:
		return df1
	elif type(df2arg) != str: # or type(df2arg) != unicode:
		df2 = df2arg
	else:
		df2 = pd.read_csv(df2arg, sep=u'\t')
	return df1, df2


##################################################################################
#GRAPH FILES MAKER (EDGE_LIST and NODE_LIST) in O(n^2) where n is the nb of skills
##################################################################################


def edgeListTemp(pathInput, pathTempFile, lowercaseItAll=False):
	'''
	takes the linkedin data and makes a temporary file that is an edge list of (columns):
		- jobNode(source)
		- skillNode(target)
	It's only a temporary file because we still need to erase doubles, 
	to make the weight (count coreference of skills) and count how 
	many times the job titles appeared
	'''
	#we open a temp file
	outputTempFile = utilsOs.createEmptyFile(pathTempFile) #don't specify that the headerLine is 'Source \t Target'

	with open(pathInput) as jsonFile:
		#we read the original json file line by line
		jsonData = jsonFile.readline()
		while jsonData:
			jsonDict = json.loads(jsonData)
			#if there are experiences
			if u'experiences' in jsonDict:
				#reliable job-skill correspondence if we only have one job title
				if len(jsonDict[u'experiences']) == 1:
					if u'function' in jsonDict[u'experiences'][0]:
						jobTitle = jsonDict[u'experiences'][0][u'function']
						if lowercaseItAll != False:
							jobtitle = jobTitle.lower()
						if u'skills' in jsonDict:
							for skillDict in jsonDict[u'skills']:
								skill = skillDict[u'name']
								if lowercaseItAll != False:
									skill = skill.lower()
								outputTempFile.write(u'{0}\t{1}\n'.format(jobTitle, skill))
								#outputTxt.write(u'{0}\t{1}\n'.format(jobTitle, skill))
			jsonData = jsonFile.readline()
	#closing the file	
	outputTempFile.close()


def edgeListDump(pathTempFile, pathOutput):
	'''
	opens the temp file containing the extracted linkedin data and makes an edge list of (columns):
		- jobNode(source)
		- skillNode(target)	
		- weight(coreference) 
		- nbOfTimesJobTitleAppeared
	
	[in a further function we might want to add keywords (non stop-words most common tokens for each jobtitle)]
	'''
	skillCorefDict = {}
	jobTitleCorefDict = {}
	lastJobTitle = None
	lineSet = set()

	#open the output file
	outputTxt = utilsOs.createEmptyFile(pathOutput, headerLine=u'Source\tTarget\tWeight\tWeight1')
	#we browse the data once to get the weight and nbOfTimesJobTitleAppeared data

	with codecs.open(pathTempFile, u'r', encoding=u'utf8') as tempData:
		dataLine = tempData.readline()
		while dataLine:
			dataList = dataLine.replace(u'\n', u'').split(u'\t')
			if len(dataList) > 1:
				#count the skills coref
				skillCorefDict[dataList[1]] = skillCorefDict.get(dataList[1], 0) + 1
				#count the repetitions of job titles
				if dataList[0] != lastJobTitle:
					jobTitleCorefDict[dataList[0]] = jobTitleCorefDict.get(dataList[0], 0) + 1
					lastJobTitle = dataList[0]
				#we add the line to the set
				lineSet.add(dataLine)
			#get to the next line
			dataLine = tempData.readline()
	#we browse the data a second time to dump it
	for dataLine in lineSet:
		dataList = dataLine.replace(u'\n', u'').split(u'\t')
		#we write 2 possible edge weights: skill coreference & skill coreference*jobtitle coreference
		outputTxt.write(u'{0}__s\t{1}__t\t{2}\t{3}\n'.format(dataList[0], dataList[1], skillCorefDict[dataList[1]], skillCorefDict[dataList[1]]*jobTitleCorefDict[dataList[0]]))

	#closing the file	
	outputTxt.close()


def nodeListIdType(pathEdgeListFile, pathNodeFileOutput):
	'''
	opens the temp file containing the extracted linkedin data and makes a node list of (columns):
		- id(same as label)
		- label(jobTitle / skill node)	
		- type(source or target; 2 for source 1 for target) #the job title is always the source, the skill is always the target
	'''
	jobTitleSet = set()
	skillSet = set()

	#open the output file
	outputTxt = utilsOs.createEmptyFile(pathNodeFileOutput, headerLine=u'Id\tLabel\tNodeType')

	with codecs.open(pathEdgeListFile, u'r', encoding=u'utf8') as edgeData:
		dataLine = edgeData.readline()
		while dataLine:
			dataList = dataLine.replace(u'\n', u'').split(u'\t')
			if len(dataList) > 1:
				#add to the jobTitle (source) set
				jobTitleSet.add(dataList[0])
				#add to the skill (target) set
				skillSet.add(dataList[1])
			#get to the next line
			dataLine = edgeData.readline()
	#browse the data sets to dump them
	for jobTitle in jobTitleSet:
		outputTxt.write(u'{0}\t{1}\t{2}\n'.format(jobTitle, jobTitle.replace(u'__s', u''), 2)) #id's '_s' means 'source', 2 means 'source'
	for skill in skillSet:
		outputTxt.write(u'{0}\t{1}\t{2}\n'.format(skill, skill.replace(u'__t', u''), 1)) #id's '_t' means 'target', 1 means 'target'


##################################################################################
#GET ADJACENCY
##################################################################################


def getNodeAdjacency(nodeName, edgeList, bothWays=True): ###########################################################
	'''
	given a node, searchs for the adjacent nodes to it
	'''
	adjacencyList = []
	#add all nodes adjacent to the source nodes
	for edge in edgeList:
		if edge[0] == nodeName:
			adjacencyList.append(edge[1])
	#if the nodeName is not a source node, browse all the target nodes and append the source nodes to the adjacency list
	#or if bothways is true, it means the graph is not directed so there is no difference between source and target nodes
	if len(adjacencyList) == 0 or bothways == True:
		for edge in edgeList:
			if edge[1] == nodeName:
				adjacencyList.append(edge[0])
	return adjacencyList


##################################################################################
#RANDOM WALK
##################################################################################

def randomWalk(edgeDf, nodeDf):
	'''
	takes 2 pandas dataframes as main arguments:
	an edgeList and nodeList with the following columns:
	- edge list:
		- Source, Target, Weight, etc.
	- node list:
		- Id, Label, etc.
	'''
	#get a random node where to begin the random walk
	#get the adjacency list of the randomly chosen node
	#randomly choose if we want to move or not
		#randomly choose where we want to move, if we want to move
	return


##################################################################################
#MODULARITY
##################################################################################

def nodeDfCleaner(nodeDf):
	''' cleans all the node dataframe from NaN values in the modularity class '''
	#return nodeDf.loc[nodeDf[u'modularity_class'] != float(u'nan')]
	return nodeDf.dropna()


def formatModularityValue(dendroPartitionDict, nodeDf, nameOfModularityColumn, nameOfPreviousModCol):
	'''
	modifies the values of the modularity dict so it has the wanted 
	string format for the modularity column
	'''
	if nameOfPreviousModCol not in nodeDf.columns:
		for key, val in dendroPartitionDict.items():
			dendroPartitionDict[key] = str(val)
	else:
		column = nodeDf[u'Id'].map(dendroPartitionDict)
		for key, val in list(dendroPartitionDict.items()):
			#get index of previous (more general) modularity community number
			try:
				previousIndex = column[nodeDf[u'Id']==key].index.tolist()[0]
				#apply changes
				dendroPartitionDict[key] = u'{0}.{1}'.format(nodeDf[nameOfPreviousModCol][previousIndex], str(val))
			#if the previous column is empty (it doesn<t exist)
			except IndexError:
				del dendroPartitionDict[key]
				#dendroPartitionDict[key] = str(val)			
	return dendroPartitionDict


def modularize(edgeGraph, nodeDf):
	'''
	uses the original code of the louvain algorithm to give modularity to a graph
	'''
	import community #downloaded and installed from https://github.com/taynaud/python-louvain
	#compute the best partition
	dendrogram = community.generate_dendrogram(edgeGraph, weight='weight')
	for indexPartition in list(reversed(range(len(dendrogram)))):
		dendroPartitionDict = community.partition_at_level(dendrogram, indexPartition) #dendroPartitionDict = community.best_partition(graph)
		nameOfModularityColumn = u'Community_Lvl_{0}'.format(str(len(dendrogram)-indexPartition-1))
		#name a possible previous modularity column (needed to format the column values)
		nameOfPreviousModCol = u'Community_Lvl_{0}'.format(str(len(dendrogram)-indexPartition-2))
		#add a column to the node data frame so we can add the community values
		if nameOfModularityColumn not in nodeDf.columns:
			nodeDf[nameOfModularityColumn] = np.nan	
		#apply the wanted format to the content of the dict
		dendroPartitionDict = formatModularityValue(dendroPartitionDict, nodeDf, nameOfModularityColumn, nameOfPreviousModCol)
		#add the community values to the node data frame
		nodeDf[nameOfModularityColumn] = nodeDf[u'Id'].map(dendroPartitionDict)
	#making sure all 'modularity_class' NaN were deleted 
	return nodeDfCleaner(nodeDf), dendrogram


def modularizeLouvain(edgeFilePath, nodeFilePath, outputFilePath=None):
	'''
	uses the original code of the louvain algorithm to give modularity to a graph on multiple levels
	downloaded from https://github.com/taynaud/python-louvain
	documentation at: http://python-louvain.readthedocs.io/en/latest/api.html
	official website: https://perso.uclouvain.be/vincent.blondel/research/louvain.html
	'''
	#open the edge list as a networkx graph
	edgeGraph = nx.read_weighted_edgelist(edgeFilePath, delimiter='\t')
	#open the node list as a data frame	
	nodeDf = pd.read_csv(nodeFilePath, sep=u'\t')
	#get the louvain modularity algorithm result in the form of a completed node data frame
	nodeDf, dendrogram = modularize(edgeGraph, nodeDf)
	#dumps the dataframe with the modularization data
	if outputFilePath != None:
		nodeDf.to_csv(outputFilePath, sep='\t', index=False)
	return nodeDf, dendrogram


def modularizeSubCommunities(edgeFilePath, nodeFilePath, outputFilePath):
	'''
	reapplies a second time the louvain algorithm to each individual 
	sub-community obtained from the louvain algorithm
	'''
	#open the edge list as a data frame	
	edgeDf = pd.read_csv(edgeFilePath, sep=u'\t')
	#open the node list as a data frame	
	nodeDf = pd.read_csv(nodeFilePath, sep=u'\t')
	#modularize
	nodeDf, dendrogram = modularizeFurther(edgeDf, nodeDf, nameOfCommunityColumn=u'Community_Lvl_0', nameOfNewCommunityColumn=u'Community_Lvl_1', outputFilePath=outputFilePath)
	return nodeDf, dendrogram


def modularizeFurther(edgeDf, nodeDf, nameOfCommunityColumn, nameOfNewCommunityColumn, outputFilePath=None):
	'''
	recalculates the modularity for each community already in existence (adds one level of modularization)
	returns a node data frame with 
	'''
	#get the list of community ids
	communityList = list(set(nodeDf[nameOfCommunityColumn].tolist()))
	#for each community reapply the louvain algorithm
	for community in communityList:
		communityNodeDf = nodeDf.loc[nodeDf[nameOfCommunityColumn] == community]
		#select all the edges that have a community node as a source (we leave behind all the community nodes that are 'targets')
		selectiveEdgeDf = edgeDf.loc[edgeDf[u'Source'].isin(communityNodeDf[u'Id'].tolist())]
		#use the reduced edge list to make the graph
		communityGraph = nx.from_pandas_edgelist(selectiveEdgeDf, u'Source', u'Target', edge_attr=u'Weight')
		#further modularization
		subCommunityDf, dendrogram = modularize(communityGraph, communityNodeDf, nameOfModularityColumn=nameOfNewCommunityColumn)
		if nameOfNewCommunityColumn not in nodeDf.columns:
			nodeDf[nameOfNewCommunityColumn] = np.nan
		#add the Community_Lvl_1 value to the whole node data frame in the form : community_lvl_0 . community_lvl_1 (i.e., 1245.00015)
		for index in subCommunityDf.index:
			nodeDf.loc[index, nameOfNewCommunityColumn] = nodeDf.loc[index, nameOfCommunityColumn] + (subCommunityDf.loc[index, nameOfNewCommunityColumn] / 10000)
	#dumps the dataframe with the modularization data
	if outputFilePath != None:
		nodeDf.to_csv(outputFilePath, sep='\t', index=False)
	return nodeDf, dendrogram


def getModularityPercentage(nodeFilePathWithModularity, communityColumnHeader=u'Community_Lvl_0'):
	'''
	opens the node list tsv file and calculates the percentage of communities
	'''
	communityDict = {}
	resultDict = {}
	nodeDf = getDataFrameFromArgs(nodeFilePathWithModularity)

	#remaking a community dict
	for nodeIndex, nodeRow in nodeDf.iterrows():
		modCommunity = nodeRow[communityColumnHeader]
		if modCommunity in communityDict:
			communityDict[modCommunity].append(nodeRow[u'Label'])
		else:
			communityDict[modCommunity] = [nodeRow[u'Label']]
	#calculation
	for idKey, communityValue in communityDict.items():
		resultDict[idKey] = (float(len(communityValue)) / float(len(nodeDf)))
	#printing in order
	for v,k in (sorted( ((v,k) for k,v in resultDict.items()), reverse=True)):
		print('community {0} normalized score: {1}'.format(k, v))
		#if v > 0.01:
		#	print(55555555555, communityDict[k])
	return resultDict


##################################################################################
#MODULARITY DOMAIN NAME GUESSING USING BAG OF WORDS
##################################################################################


def fillBagOfWords(bowSet, jobTitleList, occupationsDf):
	'''
	Takes an empty of full set and fills it with the job title and description bag of words
	'''
	#adding the job titles to the bag of words
	for jobTitle in jobTitleList:
		bowSet = bowSet.union(set(utilsString.tokenizeAndExtractSpecificPos(jobTitle, [u'n', u'np', u'j'], caseSensitive=False, eliminateEnStopwords=True)))
	#adding the description(s) to the bag of words
	selectiveEscoDf = occupationsDf.loc[occupationsDf['preferredLabel'].isin(jobTitleList)]
	if selectiveEscoDf.empty:
		return bowSet
	for rowIndex, row in selectiveEscoDf.iterrows():
		#adding the alternative label(s) to the bag of words
		try:
			bowSet = bowSet.union(set(utilsString.tokenizeAndExtractSpecificPos(row['altLabels'].replace(u'\n', u' '), [u'n', u'np', u'j'], caseSensitive=False, eliminateEnStopwords=True)))
		#if the row value is an int or float
		except AttributeError:
			pass
		#adding the description(s) to the bag of words
		bowSet = bowSet.union(set(utilsString.tokenizeAndExtractSpecificPos(row['description'], [u'n', u'np', u'j'], caseSensitive=False, eliminateEnStopwords=True)))
	return bowSet


def getJobOfferDescriptionDict(listOfPathToJobOfferFiles=[
		u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/jobsoffers/jobs_indeed-2016-06-17-noDup.json', 
		u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/jobsoffers/jobs_indeed-2016-02-25-noDup.json']):
	'''
	extracts the jobOffer name and description and returns a dictionary
	'''
	jobOfferDict = {}
	#for each 'jobOffer source path' open json as dict
	for jobOfferFilePath in listOfPathToJobOfferFiles:
		jobOfferDictTemp = {}
		with open(jobOfferFilePath) as jobOfferFile:
			jsonData = jobOfferFile.readline()
			while jsonData:
				jsonDict = json.loads(jsonData)
				#get the title and description alone
				jobOfferDictTemp[jsonDict[u'title']] = u'{0} {1}'.format(jobOfferDictTemp.get(jsonDict[u'title'], u''), jsonDict[u'description'].replace(u'\n', u' '))
				#get next line
				jsonData = jobOfferFile.readline()
		jobOfferDict.update(jobOfferDictTemp)
	return jobOfferDict


def addJobOfferDescriptionToBow(jobTitle, jobOfferDict, bowDict={}):
	'''
	returns a dict of matching the job title and a description taken from a job offer
	'''	
	#best match job offer name and length of stems in common with job title
	bestMatch = [None, 0, None]
	jobTitleStems = utilsString.naiveStemmer(jobTitle, caseSensitive=False, eliminateEnStopwords=True, language=u'english')
	#search for a match between the job title and the job offer posts
	for jobOffer in jobOfferDict.keys():
		jobOfferStems = utilsString.naiveStemmer(jobOffer, caseSensitive=False, eliminateEnStopwords=True, language=u'english')
		stemIntersection = set(jobTitleStems).intersection(set(jobOfferStems))
		#if we have more than 2/3 match between job title and job offer post and if we have a better match than bestMatch, we update bestMatch
		if len(stemIntersection) > round(len(jobTitleStems)*0.66) and len(stemIntersection) > round(len(jobOfferStems)*0.66) and len(stemIntersection) > bestMatch[1]:
			bestMatch[0] = jobOffer
			bestMatch[1] = len(stemIntersection)
			bestMatch[2] = stemIntersection
	#extract the description and make a bow
	if bestMatch[0] != None:
		description = jobOfferDict[bestMatch[0]]
	return None


def getEscoBowByLevel(escoTree):
	'''
	starting at level 0 : the most abstract job title domain,
	we make a bag of words of the job titles and added descriptions 
	contained in the domain
	e.g., 	0: 		a0 : bow of a1+a2
					b0: bow of b1+b2
				1: 		a1: bow of a1 ...
						a2: bow of a2 ...
						b1: bow of b1 ...
						b2: bow of b2 ...
	'''
	from nltk.corpus import stopwords
	bowsDict = {0:{}, 1:{}, 2:{}, 3:{}}
	#open a dataframe of all occupation data, ready to extract the description
	occupationsUkDf = pd.read_csv(u'./001ontologies/ESCO/v1.0.2/occupations_en.csv')
	occupationsUsDf = pd.read_csv(u'./001ontologies/ESCO/v1.0.2/occupations_en-us.csv')
	#browsing the esco tree by hand to add the bow in the 4 levels	
	with codecs.open(u'./001ontologies/ESCO/v1.0.2/occupations_en.csv', u'r', encoding=u'utf8') as escoFileForDescription:
		#level 0
		for domain1digit, value1digit in escoTree.items():
			bow0 = set()
			#level 1
			for domain2digit, value2digit in value1digit.items():
				bow1 = set()
				#level 2
				for domain3digit, value3digit in value2digit.items():
					bow2 = set()
					#when the job titles are at level 3
					if type(value3digit) is list:
						bow2 = fillBagOfWords(bow2, value3digit, occupationsUkDf)
						bow2 = fillBagOfWords(bow2, value3digit, occupationsUsDf)
					else:
						#level 3
						for domain4digit, value4digit in value3digit.items():
							bow3 = set()
							#when the job titles are at level 4
							bow3 = fillBagOfWords(bow3, value4digit, occupationsUkDf)	
							bow3 = fillBagOfWords(bow3, value4digit, occupationsUsDf)						
							#saving in the bow dict
							bowsDict[3][domain4digit] = bow3
							bow2 = bow2.union(bow3)
					#saving in the bow dict
					bowsDict[2][domain3digit] = bow2
					bow1 = bow1.union(bow2)
				#saving in the bow dict
				bowsDict[1][domain2digit] = bow1
				bow0 = bow0.union(bow1)
			#saving in the bow dict
			bowsDict[0][domain1digit] = bow0
	return bowsDict


def addPitchToBow(jobTitle, bowDict={}, jobPitchDict=None):
	'''
	add pitch tokens to bow if there is a pitch and if the job title has a pitch
	'''
	if jobTitle in jobPitchDict:
		#pitch
		if len(jobPitchDict[jobTitle][u'pitch']) != 0:
			for pitch in jobPitchDict[jobTitle][u'pitch']:
				for pitchToken in utilsString.naiveRegexTokenizer(pitch, caseSensitive=False, eliminateEnStopwords=True):
					bowDict[pitchToken] = bowDict.get(pitchToken, 0) + 1
		#missions
		if len(jobPitchDict[jobTitle][u'mission']) != 0:
			for mission in jobPitchDict[jobTitle][u'mission']:
				for missionToken in utilsString.naiveRegexTokenizer(mission, caseSensitive=False, eliminateEnStopwords=True):
					bowDict[missionToken] = bowDict.get(missionToken, 0) + 1
	return bowDict


def getOntologyBowByCommunity(nodeDf, columnToInferFrom):
	'''
	makes a bag of words composed of the job title names
	for each community in the ontology
	'''
	communityBagOfWords = {}
	communitiesSet = set(nodeDf[columnToInferFrom].tolist())

	#get the dict containing all jobtitles and pitches
	jobPitchDict = utilsOs.openJsonFileAsDict(u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/jobAndPitch.json')

	for community in communitiesSet:
		bowDict = {}
		#get a reduced df where the community column corresponds to the community value
		communityDf = nodeDf.loc[nodeDf[columnToInferFrom] == community]
		#make the bag of words set
		jobTitleList = communityDf['Label'].tolist()
		for jobTitle in jobTitleList:
			#save te coreference of each token in the community as a proxy of the relevance weight of each token for that specific community
			for jobToken in utilsString.naiveRegexTokenizer(jobTitle, caseSensitive=False, eliminateEnStopwords=True):
				bowDict[jobToken] = bowDict.get(jobToken, 0) + 1
			#add the linkedIn profiles pitch to the bow
			bowDict = addPitchToBow(jobTitle, bowDict, jobPitchDict)
			
		#save the bag of words to the dict
		communityBagOfWords[community] = bowDict
	return communityBagOfWords


def getCommunityNameInferences(nodeFileInput, outputFilePath):
	''' 
	using a bag of words on jobtitles of the same community and on
	job titles and descriptions from existing ontologies (ESCO)
	estimate what is the name of the community domain
	'''
	inferencesDict = {}
	#we chech if 'edgeFileInput' and 'nodeFileInput' are string paths or pandas dataframes
	nodeDf = getDataFrameFromArgs(nodeFileInput)
	#bag of words of the esco ontology
	escoTree = utilsOs.openJsonFileAsDict(u'./jsonJobTaxonomies/escoTree.json')
	escoTreeBagOfWords = getEscoBowByLevel(escoTree)
	#infer a name for each existing level of communities
	communityLevel = 0
	subClasses = set()	
	while u'Community_Lvl_{0}'.format(str(communityLevel)) in nodeDf.columns:
		columnToInferFrom = u'Community_Lvl_{0}'.format(str(communityLevel))
		communityLevel += 1
		#bag of words of the communities in our ontology
		communityBagOfWords = getOntologyBowByCommunity(nodeDf, columnToInferFrom)
		#add an empty column
		inferenceColumnName = u'Infered_Community_Name_Lvl_{0}'.format(columnToInferFrom.split(u'_')[-1])
		nodeDf[inferenceColumnName] = np.nan
		#comparing intersection between esco bow and the communities bow
		for community, communityBowDict in communityBagOfWords.items():
			#reset values of best intersection
			bestIntersection = {u'result': 0.0, u'set': None, u'name': u'00000000___'}
			for nb in reversed(range(1, 4)):
				for escoDomain, escoBow in escoTreeBagOfWords[nb].items():
					bowIntersectionScore = 0
					#we intersect the 2 bag of words
					bowIntersection = set(communityBowDict.keys()).intersection(escoBow)
					for token in bowIntersection:
						bowIntersectionScore += communityBowDict[token]
					#we evaluate if we are at the same level in the esco taxonomy. If we are still on the same level the score 
					#needed to replace the best intersection is simply the one > than the precedent, 
					#if we are one level upper, then the needed score is multiplied by a variable (to priorize staying in a 
					#lower, more specialized, ESCO level)
					if len(bestIntersection[u'name'].split(u'___')[0]) == len(escoDomain.split(u'___')[0]):
						multiplier = 1.0
					else:
						#multiplier = (4.6 - (nb * 1.2))
						multiplier = 1.5
					#if the score is greater, we replace the previous best intersection with the new intersection
					if bowIntersectionScore > bestIntersection['result']*multiplier or bestIntersection['result'] == 0.0:
						bestIntersection[u'result'] = bowIntersectionScore
						bestIntersection[u'set'] = bowIntersection
						bestIntersection[u'dict'] = communityBowDict
						bestIntersection[u'name'] = escoDomain
			#saving the information
			inferencesDict[community] = bestIntersection
			nodeDf[inferenceColumnName].loc[nodeDf[columnToInferFrom] == community] = str(bestIntersection['name'])
	#dump to file
	nodeDf.to_csv(outputFilePath, sep='\t', index=False)
	return inferencesDict


##################################################################################
#MODULARITY DOMAIN NAME GUESSING USING WORD EMBEDDINGS
##################################################################################


def avg_sentence_vector(sentence, modelFastText):
	#make an empty vector
	num_features = model.get_dimension()
	featureVec = np.zeros(num_features, dtype="float32")
	#tokenization
	words = word_tokenize(sentence)
	for word in words:
		#sum of the vector's values
		featureVec = np.add(featureVec, model.get_word_vector(word))
	featureVec = np.divide(featureVec, float(max(len(words),1)))
	return featureVec


def cosine_similarity(vec1, vec2):
	return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def getWordEmbeddingInference(semanticClassCluster):
	'''
	Follows the Patel and Ravichandran algorithm for automatically
	labelling semantic classes and returns a ranked list of semantic
	classes names
	'''
	#pathToModel = u'/data/rali5/Tmp/alfonsda/DOCTORAT_TAL/004projetOntologie/fastTextModel/crawl-300d-2M.vec'
	pathToModel = u'/data/rali5/Tmp/alfonsda/DOCTORAT_TAL/004projetOntologie/fastTextModel/wiki-news-300d-1M.vec'
	model = FastText()
	model.load_model(pathToModel)
	###################################################################
	###################################################################


##################################################################################
#ONTOLOGY CLEANING AND TRIMMING
##################################################################################

def wasteNodeElimination(edgeFileInput, nodeFileInput):
	'''
	Checks if every node in the node file appear in the edge file
	otherwise it eliminates it
	Checks if the nodes of every edge is in the node file
	otherwise the edge gets eliminated
	'''
	edgesToEliminate = []
	nodesToEliminate = []
	edgeDf, nodeDf = getDataFrameFromArgs(edgeFileInput, nodeFileInput)
	#browse edges if its nodes are not in the nodes list, prepare the lists of elements to drop
	for edgeIndex, edgeRow in (edgeDf.iterrows()):
		edgeSourceId = edgeRow[u'Source']
		edgeTargetId = edgeRow[u'Target']
		sourceNodesOfEdgesDf = nodeDf.loc[nodeDf[u'Id'] == edgeSourceId]
		targetNodesOfEdgesDf = nodeDf.loc[nodeDf[u'Id'] == edgeTargetId]
		if len(sourceNodesOfEdgesDf) == 0 or len(targetNodesOfEdgesDf) == 0:
			edgesToEliminate.append(edgeIndex)
	#drop the edges
	for edgeIndex in reversed(edgesToEliminate):
		edgeDf = edgeDf.drop(edgeDf.index[edgeIndex])
	#browse nodes if not in edges, prepare the lists of elements to drop
	for nodeIndex, nodeRow in list(nodeDf.iterrows()):
		nodeId = nodeRow['Id']
		edgesOfNodesDf = edgeDf.loc[edgeDf[u'Source'] == nodeId] & edgeDf.loc[edgeDf[u'Target'] == nodeId]
		if len(edgesOfNodesDf) == 0:
			nodesToEliminate.append(nodeIndex)
	#drop the nodes
	for nodeIndex in reversed(nodesToEliminate):
		nodeDf = nodeDf.drop(nodeDf.index[nodeIndex])
	#dumping the data frames to the same file where we opened them
	if type(edgeFileInput) == str and type(nodeFileInput) == str:
		edgeDf.to_csv(edgeFileInput, sep='\t', index=False)
		nodeDf.to_csv(nodeFileInput, sep='\t', index=False)	
	return edgeDf, nodeDf


def ontologyContentCleaning(languageOfOntology, edgeFilePathInput, nodeFilePathInput, edgeFilePathOutput=None, nodeFilePathOutput=None):
	'''
	NOTE: this function only cleans interlanguage intrusion between FRENCH and ENGLISH
	given an ontology (edge list and node list), removes:
		- all nodes detected to be in a different language that the language of the ontology
		- all over-specific nodes (having more than 5 tokens) 
	'''
	import langdetect
	rightLanguageNodes = []
	edgeDf = pd.read_csv(edgeFilePathInput, sep=u'\t')
	nodeDf = pd.read_csv(nodeFilePathInput, sep=u'\t')

	for nodeIndex, nodeRow in nodeDf.iterrows():
		label = nodeRow['Label']
		#detecting if the label is in english or french
		try:
			if utilsString.englishOrFrench(label) == languageOfOntology:
				#if the node is not over-specific
				if len(utilsString.naiveRegexTokenizer(label)) <= 5:
					#add the node id to the list of correct nodes
					rightLanguageNodes.append(nodeRow['Id'])
		except TypeError:
			#print(label, type(label))
			pass
	#get the dataframes containing the right nodes
	cleanedEdgeDf = edgeDf.loc[edgeDf[u'Source'].isin(rightLanguageNodes) & edgeDf[u'Target'].isin(rightLanguageNodes)]
	cleanedNodeDf = nodeDf.loc[nodeDf[u'Id'].isin(rightLanguageNodes)]
	#dumping the data frames
	if edgeFilePathOutput != None:
		cleanedEdgeDf.to_csv(edgeFilePathOutput, sep='\t', index=False)
		cleanedEdgeDf.to_csv(u'{0}NoHeader.tsv'.format(edgeFilePathOutput.split(u'.tsv')[0]), sep='\t', index=False, header=None)
	if nodeFilePathOutput != None:
		cleanedNodeDf.to_csv(nodeFilePathOutput, sep='\t', index=False)
	return cleanedEdgeDf, cleanedNodeDf


def remove1DegreeNodes(dictA, dictB):
	'''
	recursive function to remove all the less core-connected 
	nodes from the dicts representing the graph
	'''
	aOriginalSize = len(dictA)
	bOriginalSize = len(dictB)
	#remove job titles of degree 1 (with only one skill)
	for aKey, aList in dict(dictA).items():
		#if there is one (or less) skill for that job title
		if len(aList) <= 1:
			#to maintain consistency, delete the job title from the skill to jobs dict
			for bElem in list(aList):
				#delete the job title from the skill to jobs dict
				dictB[bElem].remove(aKey)
				#remove the keys in the dict with an empty list as value
				if len(dictB[bElem]) == 0:
					del dictB[bElem]
			#delete the dict entry from the job to skills dict
			del dictA[aKey]
	if len(dictA) != aOriginalSize and len(dictB) != bOriginalSize:
		dictB, dictA = remove1DegreeNodes(dictB, dictA)
	return dictA, dictB


def ontologyStructureCleaning(edgeFileInput, nodeFileInput, edgeFilePathOutput=None, nodeFilePathOutput=None):
	'''
	given an ontology (edge list and node list), removes:
		- all communities corresponding to less than 1% of the node
		- all independent and isolated skills and job titles:
			- all skills connected to only 1 job title
			- all job titles with only one skill
			- all job titles (and skills) whose skills are not connected to any other job titles
	'edgeFileInput' and 'nodeFileInput' can either be a string/unicode path to the a tsv file or a pandas dataframe
	'''
	#get dataframes
	edgeDf, nodeDf = getDataFrameFromArgs(edgeFileInput, nodeFileInput)
	#remove communities corresponding to less than 1% of the node
	communitiesSet = set(nodeDf['Community_Lvl_0'].tolist())
	copyCommunitiesSet = list(communitiesSet)
	for communityId in copyCommunitiesSet:
		#get a reduced df where the community column corresponds to the community id value
		communityDf = nodeDf.loc[nodeDf[u'Community_Lvl_0'] == communityId]
		if len(communityDf)/len(nodeDf) < 0.01:
			communitiesSet.remove(communityId)
	#save the trimmed df as the new node df
	nodeDf = nodeDf.loc[nodeDf[u'Community_Lvl_0'].isin(list(communitiesSet))]
	#make a dict of jobtitle to skills and a dict of skill to jobtitles
	jToSkillsDict = {}
	sToJobsDict = {}
	emptyList = []
	for edgeIndex, edgeRow in edgeDf.iterrows():
		jToSkillsDict[edgeRow[u'Source']] = list(set(jToSkillsDict.get(edgeRow[u'Source'], list(emptyList)) + [edgeRow[u'Target']]))
		sToJobsDict[edgeRow[u'Target']] = list(set(sToJobsDict.get(edgeRow[u'Target'], list(emptyList)) + [edgeRow[u'Source']]))
	#remove independent and isolated skills and job titles
	jToSkillsDict, sToJobsDict = remove1DegreeNodes(jToSkillsDict, sToJobsDict)
	#save the trimmed data frames as the new data frames
	nodeDf = nodeDf.loc[nodeDf[u'Id'].isin( list(jToSkillsDict.keys())+list(sToJobsDict.keys()) )]
	edgeDf = edgeDf.loc[edgeDf[u'Source'].isin(list(jToSkillsDict.keys())) & edgeDf[u'Target'].isin(list(sToJobsDict.keys()))]
	#dumping the data frames
	if edgeFilePathOutput != None:
		edgeDf.to_csv(edgeFilePathOutput, sep='\t', index=False)
	if nodeFilePathOutput != None:
		nodeDf.to_csv(nodeFilePathOutput, sep='\t', index=False)
	#we make sure there are no unconnected nodes
	wasteNodeElimination(edgeFilePathOutput, nodeFilePathOutput)
	return edgeDf, nodeDf


##################################################################################
#ONTOLOGY EVALUATION METRICS
##################################################################################

def ontoQA(edgeFilePath, nodeFilePath, verbose=True):
	'''
	given an ontology (edge list and node list) it calculates the ontoQA score
	the lists must contain certain column names:
	 - edge list: Source, Target
	 - node list: Id, Community_Lvl_0
	'''
	emptyDict = {}
	dataDict = {}
	metricsDict = {}
	#open the edge list as a data frame	
	edgeDf = pd.read_csv(edgeFilePath, sep=u'\t')
	#open the node list as a data frame	
	nodeDf = pd.read_csv(nodeFilePath, sep=u'\t')
	#make a dict for the class related data
	classes = set(nodeDf['Community_Lvl_0'].tolist())
	classDataDict = {k:dict(emptyDict) for k in classes}
	#count the number of subClasses (not counting the main, upper level, classes)
	nb = 1
	subClasses = set()
	while 'Community_Lvl_{0}'.format(str(nb)) in nodeDf.columns:
		subClasses = subClasses.union(set( nodeDf[ 'Community_Lvl_{0}'.format(str(nb)) ].tolist() ))
		nb += 1

	#get C, number of classes
	dataDict['C'] = len(classes)
	#get P', non-inheritance relationships (relation types) deducing the inexisting schema
	if 'esco' in edgeFilePath.lower():
		dataDict['P'] = 15 #hasSkill, conceptType, conceptUri, broaderUri, iscoGroup, preferredLabel, alternativeLabel, description, code, occupationUri, relationType, skillType, skillUri, reuseLevel
	else:
		dataDict['P'] = 11 #in an edge and node List it's 2!!!: hasSkill, hasSubclass #BUT can be grown to 11 by adding if put in a formal ontology form: hasSkill, conceptType, conceptUri, broaderUri, preferredLabel, occupationUri, relationType, skillUri, reuseLevel
	#get P', non-inheritance relations (instances)
	dataDict["P'"] = len(edgeDf)
	#get H, inheritance relationships
	dataDict['H'] = 1	 #isSubclassOf or broaderUri(in ESCO)
	#get Hs, number of subclasses
	dataDict['Hs'] = len(subClasses)	
	#get att, number of attributes
	dataDict['att'] = len(edgeDf) + len(nodeDf)
	#get CI, total number of instances
	dataDict['CI'] = len(nodeDf) + len(classes)
	#get class (C_i) dependent data (inst)
	for classId in classes:
		classDataDict[classId]['inst_nbClassInstances'] = len(nodeDf.loc[nodeDf['Community_Lvl_0'] == classId])
		#add a NIREL value of 0 in case there is an 'na' in the classes
		classDataDict[classId]['NIREL_nbRelOtherClass'] = 0
	#get class (C_i) dependent data (NIREL)
	for edgeIndex, edgeRow in edgeDf.iterrows():
		sourceClass = nodeDf.loc[nodeDf['Id'] == edgeRow['Source']]['Community_Lvl_0'].values
		targetClass = nodeDf.loc[nodeDf['Id'] == edgeRow['Target']]['Community_Lvl_0'].values
		try:
			if sourceClass != targetClass:
				#get NIREL(Cj), number of relationships instances of the class have with instances of other classes
				classDataDict[sourceClass[0]]['NIREL_nbRelOtherClass'] = classDataDict[sourceClass[0]].get('NIREL_nbRelOtherClass', 0) + 1 
			else:
				classDataDict[sourceClass[0]]['nbRelSameClass'] = classDataDict[sourceClass[0]].get('nbRelSameClass', 0) + 1 
		except IndexError:
			pass
	#open the edge list as a networkx graph to get the nb of connected components
	edgeGraph = nx.from_pandas_edgelist(edgeDf, u'Source', u'Target', edge_attr=u'Weight')
	#get CC, number of connected components
	dataDict['CC'] = nx.number_connected_components(edgeGraph)

	#calculating the ONTOQA METRICS:
	#RR - relationship richness
	metricsDict['RR'] = float(dataDict['P']) / float(dataDict['H']+dataDict['P'])
	#IR - inheritance richness
	metricsDict['IR'] = float(dataDict['Hs']) / float(dataDict['C'])
	#AR - attribute richness
	metricsDict['AR'] = float(dataDict['att']) / float(dataDict['C'])
	#CR - class richness
	##################unable to actually calculate it without having a preconceived schema of the ontology
	#Conn(C_i) - class connectivity 
	metricsDict['Conn'] = {}
	for classId, classData in classDataDict.items():
		try:
			metricsDict['Conn'][u'CLASS {0}'.format(classId)] = classData['NIREL_nbRelOtherClass']
		except KeyError:
			#print(classId, classData)
			pass
	#Imp(C_i) - class importance
	metricsDict['Imp'] = {}
	for classId, classData in classDataDict.items():
		metricsDict['Imp'][u'CLASS {0}'.format(classId)] = float(classData['inst_nbClassInstances']) / float(dataDict['CI'])
	#Coh - cohesion
	metricsDict[u'Coh'] = dataDict[u'CC']
	#RR(C_i) - relationship richness per class
	##################unable to actually calculate it without having a preconceived schema of the ontology
	if verbose == True:
		print(metricsDict)
	return metricsDict


##################################################################################
#TOOLS FOR HUMAN ONTOLOGY ANALYSIS AND EVALUATION
##################################################################################

def printCommunityInferenceHeaders(nodeFileInput):
	'''
	pretty prints an ASCII table containing the communities 
	header selection of a particular level of the ontology
	'''
	from prettytable import PrettyTable
	dataDict = {}
	#get the node dataframe
	nodeDf = getDataFrameFromArgs(nodeFileInput)
	#get the data from the node dataframe
	communityLevel = 0
	while u'Community_Lvl_{0}'.format(str(communityLevel)) in nodeDf.columns:
		nameOfCommunityColumn = u'Community_Lvl_{0}'.format(str(communityLevel))
		#empty dict
		dataDict[communityLevel] = {}
		#get the list of community ids for a specific level
		communityIdsList = list(set(nodeDf[nameOfCommunityColumn].tolist()))
		#save the data for each community
		for communityId in communityIdsList:
			communityNodeDf = nodeDf.loc[nodeDf[nameOfCommunityColumn] == communityId]
			#transform the ratio into string beacause prettytable has trouble with exponential numbers
			ratio = str(len(communityNodeDf)/len(nodeDf))
			if 'e-' in ratio:
				ratio = ratio.split('e-')
				ratio1 = '0' * (int(ratio[1])-1)
				ratio2 = ratio[0].replace('.', '')
				ratio = '0.{0}{1}'.format(ratio1, ratio2)
			#fill data dict with the data
			dataDict[communityLevel][communityId] = {
			'communityName': (communityNodeDf.head(1)['Infered_Community_Name_Lvl_{0}'.format(communityLevel)]).values[0] , 
			'ratioOfNodeInWholeDf': ratio, 
			'nbOfNodes': len(communityNodeDf), 
			'sample': communityNodeDf.head(10)['Label'].tolist()}
		communityLevel += 1
	#print one table per level
	for levelNb in sorted(dataDict.keys()):
		levelDataDict = dataDict[levelNb]
		#use prettytable to show the data in a human readable way
		table = PrettyTable()
		table.title = "LEVEL {0}".format(str(levelNb))
		table.field_names = ['Ratio', 'Infered Name', 'Sample']
		#insert the data as rows
		for communityId, data in levelDataDict.items():
			#cut the community name if it's too long
			if len(data['communityName']) > 20:
				segmentedCommunityName = []
				lastSeg = 0
				for nbSeg in range((len(data['communityName']) % 20)+2)[1:]:
					if nbSeg * 20 < len(data['communityName']):
						seg = nbSeg*20
					else:
						seg = len(data['communityName'])
					segmentedCommunityName.append(data['communityName'][lastSeg:seg])
					#hold place of last segmentation
					lastSeg = seg
				communityName = '\n'.join(segmentedCommunityName)
			else:
				communityName = data['communityName']
			#add the row data to the table
			table.add_row([data['ratioOfNodeInWholeDf'], communityName, '\n'.join(data['sample'] + [''])])
		#sort
		table.sortby = "Ratio"
		table.reversesort = True
		#printing
		print("LEVEL {0}".format(str(levelNb)))
		print(table)


def getSampleForHumanEvaluation(edgeFileInput, nodeFileInput, lengthOfSample=1000, outputEdgeFilePath=None, outputNodeFilePath=None):
	'''
	given a finished ontology in the form of an edge list and a node list
	return and dump a random sample in the form of an extended edge list
	'''
	setOfIndexes = set()
	#get dataframes
	edgeDf, nodeDf = getDataFrameFromArgs(edgeFileInput, nodeFileInput)
	#get a random list of indexes
	while len(setOfIndexes) < lengthOfSample:
		setOfIndexes.add(random.randint(0, len(edgeDf)))
	#get a reduced randomly chosen edge dataframe
	sampleEdgeDf = edgeDf.iloc[list(setOfIndexes)]
	#get the reduced node dataframe corresponding to the randomly chosen edge dataframe
	sampleNodeDf = nodeDf.loc[nodeDf[u'Id'].isin(sampleEdgeDf[u'Source'].tolist() + sampleEdgeDf[u'Target'].tolist())]
	#dumps the dataframes
	if outputEdgeFilePath != None:
		sampleEdgeDf.to_csv(outputEdgeFilePath, sep='\t', index=False)
	if outputNodeFilePath != None:
		(sampleNodeDf.sort_values(by=['Community_Lvl_1'])).to_csv(outputNodeFilePath, sep='\t', index=False)
	return sampleEdgeDf, sampleNodeDf.sort_values(by=['Community_Lvl_1'])


def humanAnnotatorInterface(sampleEdgeFileInput, sampleNodeFileInput, nameOfEvaluator='David'):
	'''
	terminal interface for human annotation
	3 types of annotation:
	 - edge relevance (is the skill relevant for that job title?)
	 - filter evaluation (is the node in the right language? is the node well written? must not show a named entity. must be coherent.)
	 - community/taxonomy evaluation (Sesame Street test: is this thing just like the others?)
	3 types of annotation:
	 - 0 : negative evaluation
	 - 1 : positive evaluation
	 - 2 : neutral/doubtful evaluation
	'''
	#get dataframe
	sampleEdgeDf, sampleNodeDf = getDataFrameFromArgs(sampleEdgeFileInput, sampleNodeFileInput)
	#print instructions
	print(u'3 types of annotation: 0 = negative eval, 1 = positive eval, 2 = doubtful eval\n')
	#edge Annotation
	print(u'EDGE ANNOTATION:\n')
	#add the columns preparing for the data
	sampleEdgeDf[u'edgeAnnotation'] = np.nan	
	for edgeIndex, edgeRow in sampleEdgeDf.iterrows():
		#print the edge
		print(u'{0} >>>> {1}'.format(edgeRow[u'Source'], edgeRow[u'Target']))
		#wait for annotator input
		annotatorInput = input(u'Annotation: ')
		#save the annotation
		sampleEdgeDf[u'edgeAnnotation'][edgeIndex] = int(annotatorInput)
		#clear the terminal before the next row
		utilsOs.moveUpAndLeftNLines(2, slowly=False)
	#dump the edge dataframe
	sampleEdgeDf.to_csv(u'{0}{1}.tsv'.format(sampleEdgeFileInput.split(u'.tsv')[0], nameOfEvaluator), sep='\t', index=False)

	#print instructions
	utilsOs.moveUpAndLeftNLines(3, slowly=False)
	print(u'must be: the right language... well written... not having a named entity... coherent.\n')
	#node annotation filter evaluation
	print(u'NODE ANNOTATION (filter evaluation):')
	print()
	#add the columns preparing for the data
	sampleNodeDf[u'nodeAnnotationFilter'] = np.nan	
	for nodeIndex, nodeRow in sampleNodeDf.iterrows():
		#print the edge
		print(nodeRow[u'Label'])
		#wait for annotator input
		annotatorInput = input(u'Annotation: ')
		#save the annotation
		sampleNodeDf[u'nodeAnnotationFilter'][nodeIndex] = int(annotatorInput)
		#clear the terminal before the next row
		utilsOs.moveUpAndLeftNLines(2, slowly=False)

	#node annotation taxonomy evaluation ###########################

	#dump the node dataframe
	sampleNodeDf.to_csv(u'{0}{1}.tsv'.format(sampleNodeFileInput.split(u'.tsv')[0], nameOfEvaluator), sep='\t', index=False)



	

##################################################################################
#CALIBRATION OF THE SIGMA.JS EXPORTATION OF THE GRAPH
##################################################################################

def modifyConfigAndIndexFiles(pathToTheExportationEnvironment):
	'''
	given the path to the sigma.js exportation environment (ending in 
	the folder "network/"), it changes the config.json file and the index.html
	file so they show the graph the way intended
	'''
	from shutil import copyfile
	#copying config.json file
	configContent = {"type": "network","version": "1.0","data": "data.json","logo": {"file": "","link": "","text": ""},"text": {"more": "","intro": "","title": ""},"legend": {"edgeLabel": "","colorLabel": "","nodeLabel": ""},"features": {"search": True,"groupSelectorAttribute": True,"hoverBehavior": "default"},"informationPanel": {"groupByEdgeDirection": True,"imageAttribute": False},"sigma": {"drawingProperties": {"defaultEdgeType": "curve","defaultHoverLabelBGColor": "#002147","defaultLabelBGColor": "#ddd","activeFontStyle": "bold","defaultLabelColor": "#000","labelThreshold": 999,"defaultLabelHoverColor": "#fff","fontStyle": "bold","hoverFontStyle": "bold","defaultLabelSize": 14},"graphProperties": {"maxEdgeSize": 2,"minEdgeSize": 2,"minNodeSize": 0.25,"maxNodeSize": 2.5},"mouseProperties": {"maxRatio": 20,"minRatio": 0.75}}}
	pathConfigJson = u'{0}config.json'.format(pathToTheExportationEnvironment)
	if utilsOs.theFileExists(pathConfigJson) == True:
		os.remove(pathConfigJson)
	utilsOs.dumpDictToJsonFile(configContent, pathConfigJson) 
	#copying the logo images
	srcRali = u'./testsGephi/gephiExportSigma0/rali.png'
	dstRali = u'./testsGephi/gephiExportSigma0/springLayoutAndModularityPythonLouvain/wholeCleanedModularizedTrimmedInfered/network/images/rali.png'
	srcUdem = u'./testsGephi/gephiExportSigma0/udem.png'
	dstUdem = u'./testsGephi/gephiExportSigma0/springLayoutAndModularityPythonLouvain/wholeCleanedModularizedTrimmedInfered/network/images/udem.png'
	copyfile(srcRali, dstRali)
	copyfile(srcUdem, dstUdem)
	#getting the color information from the data file
	colorCommunityDict = {}
	dataDict = utilsOs.openJsonFileAsDict(u'{0}data.json'.format(pathToTheExportationEnvironment))
	for nodeDict in dataDict[u'nodes']:
		try:
			if nodeDict[u'attributes'][u'community_lvl_0'] not in colorCommunityDict:
				colorCommunityDict[nodeDict[u'attributes'][u'community_lvl_0']] = u'\t\t\t<div style="color: {0};">● {1}</div>\n'.format(nodeDict[u'color'], nodeDict[u'attributes'][u'infered_community_name_lvl_0'])
			'''
			#####################################################
			#before I changed the names of the columns
			if nodeDict[u'attributes'][u'community'] not in colorCommunityDict:
				colorCommunityDict[nodeDict[u'attributes'][u'community']] = u'\t\t\t<div style="color: {0};">● {1}</div>\n'.format(nodeDict[u'color'], nodeDict[u'attributes'][u'infered_community_name'])
			'''
		except KeyError:
			pass
	#modifying the index.html file
	with open(u'{0}index.html'.format(pathToTheExportationEnvironment)) as indexFile:
		fileLines = indexFile.readlines()
		#to add the colors
		for index, line in enumerate(fileLines):
			if line == u'\t\t<dt class="colours"></dt>\n':
				indexDivisorCol = index + 1
				break
		fileLines = fileLines[:indexDivisorCol] + [u'\t\t<dd>\n'] + list(colorCommunityDict.values()) + [u'\t\t</dd>\n'] + fileLines[indexDivisorCol+1:]
		#to change the images and urls to rali and udem
		for index, line in enumerate(fileLines):
			if line == u'\t<a href="http://www.oii.ox.ac.uk" title="Oxford Internet Institute"><div id="oii"><span>OII</span></div></a>\n':
				indexDivisorImg = index + 1
				break
		fileLines = fileLines[:indexDivisorImg-1] + [u'\t<a href="http://rali.iro.umontreal.ca/rali/en" title="RALI laboratories"><div id="RALI"><span>RALI</span></div></a>\n', 
		u'\t<a href="http://www.umontreal.ca/en/" title="UdeM"><div id="UdeM"><span>UdeM</span></div></a>\n']  + fileLines[indexDivisorImg+2:]
	utilsOs.dumpRawLines(fileLines, u'{0}index.html'.format(pathToTheExportationEnvironment), addNewline=False, rewrite=True)
	#modifying the style.css file to point to the images
	with open(u'{0}css/style.css'.format(pathToTheExportationEnvironment)) as styleFile:
		fileLines = styleFile.readlines()
		fileLines = fileLines + [u'''#UdeM {\nwidth: 198px;\nheight: 81px;\nbackground-image: url('../images/udem.png');\nbackground-repeat: no-repeat;\ndisplay:inline-block;\n}\n\n#UdeM span {\n\tdisplay:none;\n}\n\n#RALI {\nwidth: 318px;\nheight: 75px;\nbackground-image: url('../images/rali.png');\nbackground-repeat: no-repeat;\ndisplay:inline-block;\nmargin-right:10px;\n\n}\n\n#RALI span {\n\tdisplay:none;\n}\n''']
	utilsOs.dumpRawLines(fileLines, u'{0}css/style.css'.format(pathToTheExportationEnvironment), addNewline=False, rewrite=True)




sampleEdgeFileInput = '/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/009humanAnnotation/sampleEdge1000ForHumanEval.tsv'
sampleNodeFileInput = '/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/009humanAnnotation/sampleNode1000ForHumanEval.tsv'
humanAnnotatorInterface(sampleEdgeFileInput, sampleNodeFileInput, nameOfEvaluator='David')