#!/usr/bin/python
#-*- coding:utf-8 -*-

import json, codecs, random
from tqdm import tqdm
import pandas as pd
import numpy as np
import utilsOs


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
			else:
				print(111111, dataList)
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
			else:
				print(111111, dataList)
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

def getNodeAdjacencyDf(nodeId, edgeDf):
	'''
	returns a data frame of the edges where the nodeId appears
	and the type of the nodes adjacent to it ('Source' if nodeId is 'Target' and vice-versa)
	'''
	#if the node id is marked as source
	if nodeId[-3:] == u'__s':
		nodeDf = edgeDf.loc[edgeDf[u'Source'] == nodeId]
		typeAdjacentNodes = u'Target'
	#if the node id is marked as target
	elif nodeId[-3:] == u'__t':
		nodeDf = edgeDf.loc[edgeDf[u'Target'] == nodeId]
		typeAdjacentNodes = u'Source'
	#if the node id is not marked and we don't know if it's a source or a target we explore all possibilities
	else:
		nodeDf = edgeDf.loc[edgeDf[u'Source'] == nodeId]
		typeAdjacentNodes = u'Target'
		if len(nodeDf[u'Source']) == 0:
			nodeDf = edgeDf.loc[edgeDf[u'Target'] == nodeId]
			typeAdjacentNodes = u'Source'
	return nodeDf, typeAdjacentNodes


def getReducedDf(df, columnName, detailList):
	'''	returns a reduced and specialized data frame	'''
	return df.loc[df[columnName].isin(detailList)]


def getSumOfAllWeights(df):
	'''	returns the variable sum of all edges in the data frame	'''
	return df[u'Weight'].sum()


def intersectOf2Df(df1, df2, columnNameInCommon):
	'''	returns the dataframe obtained after intersecting 2 dataframes	'''
	return pd.merge(df1, df2, how='inner', on=columnNameInCommon)


def unionOf2Df(df1, df2, columnNameInCommon):
	'''	returns the dataframe obtained after the union of 2 dataframes	'''
	return pd.merge(df1, df2, how='outer', on=columnNameInCommon)


def getSumOfWeightOfEdgesInCommunity(communityNodes, edgeDf):
	'''	both nodes of the edge must be in the community	'''
	sourceNodesDf = getReducedDf(edgeDf, u'Source', communityNodes)
	targetNodesDf = getReducedDf(edgeDf, u'Target', communityNodes)
	intersection = intersectOf2Df(sourceNodesDf, targetNodesDf, None)
	if len(intersection) == 0:
		return 0
	return getSumOfAllWeights(intersection)


def getSumOfWeightOfEdgesIncidentToCommunity(communityNodes, edgeDf):
	'''	both nodes of the edge must be in the community	'''
	sourceNodesDf = getReducedDf(edgeDf, u'Source', communityNodes)
	targetNodesDf = getReducedDf(edgeDf, u'Target', communityNodes)
	union = unionOf2Df(sourceNodesDf, targetNodesDf, None)
	return getSumOfAllWeights(union)


def getGainOfModularity(jCommunityNodes, edgeDf, iDf, iAdjacentType, m2):
	'''
	calculates the gain of modularity
	'''
	m2 = float(m2)
	#sum Of Weights Of Edges In C  = both nodes of the edge must be in the community
	sigmaIn = float(getSumOfWeightOfEdgesInCommunity(jCommunityNodes, edgeDf))
	#sum Of Weights Of Edges Incident To Nodes In C  = one node of the edge must be in the community
	sigmaTot = float(getSumOfWeightOfEdgesIncidentToCommunity(jCommunityNodes, edgeDf))
	#sum Of Weights Of Edges From I To Nodes In C = all the weights of edges having i and a node of the community
	kIin = float(getSumOfAllWeights( getReducedDf(iDf, iAdjacentType, jCommunityNodes) ))
	#sum Of Weights Of Edges Incident To Node I = all the weights of edges having i as one of their node
	kI = float(getSumOfAllWeights(iDf))
	gainModularity = float( ((sigmaIn + kIin)/m2)-(((sigmaTot+kI)/m2)**2) ) - ( (sigmaIn/m2)-((sigmaTot/m2)**2)-((kI/m2)**2) )
	return gainModularity


def updatingDicts(gainModularity, nodeId, communityId, nodesDict, communityDict):
	'''
	updates the dicts so every node has one community
	'''
	oldCommunityId = nodesDict[nodeId][1]
	#we change the node's community in the node dict
	nodesDict[nodeId][0] += gainModularity
	nodesDict[nodeId][1] = communityId
	#we delete the node from the list of the old community
	communityDict[oldCommunityId].remove(nodeId)
	#if the community is empty we delete it
	if len(communityDict[oldCommunityId]) == 1:
		del communityDict[oldCommunityId]
	#we add the node to its new community
	try:
		communityDict[communityId][0] += gainModularity
		communityDict[communityId].append(nodeId)
	except KeyError:
		###########################################
		#from time to time they might be a call to a node in the community dict that has just been changed so we obtain
		#a KeyError, whenever we encounter that problem we pass since it will be solved in the next step of the loop
		print(2222222221111111, 'keyerror updating dict  ', communityId)
	return nodesDict, communityDict


def modularize(edgeFilePath, nodeFilePath, maxCommunities, outputFilePath=u'./nodeDf.tsv'):
	'''
	takes 2 pandas objects as main arguments:
	an edgeList and nodeList with the following columns:
	- edge list:
		- Source, Target, Weight, etc.
	- node list:
		- Id, Label, etc.
	it starts by giving a community id to each node then it calculates the modularity gain of moving each node to
	the next community and if there is a gain the communities get fusioned
	#https://arxiv.org/pdf/0803.0476.pdf
	'''
	nodesDict = {}
	communityDict = {}

	edgeDf = pd.read_csv(edgeFilePath, sep=u'\t')
	nodeDf = pd.read_csv(nodeFilePath, sep=u'\t')

	#add a column to the nodeDf so we can add a modularity class
	nodeDf[u'modularity_class'] = np.nan

	#each node in the network is assigned to its own community
	for nodeIndex, nodeRow in nodeDf.iterrows():
		nodeId = nodeRow[u'Id']
		#nodeId = id of the node, 0 = basic modularity score, nodeIndex1 = id of the community, nodeIndex2 = index of the df for easy find
		nodesDict[nodeId] = [0, nodeIndex, nodeIndex]
		communityDict[nodeIndex] = [0, nodeId]
	repetitionCounter = [0, None]

	#calculation of the gain of modularity
	m2 = getSumOfAllWeights(edgeDf) * 2
	while len(communityDict) > maxCommunities:
		print(11111111111111111111111111, len(communityDict))
		#we loop on every remaining community
		for iNodesList in tqdm(list(communityDict.values())):
			for iNode in iNodesList[1:]:
				#we save for each node the stronges change based on the modularity gain
				changeToBeMade = [0, None]
				iDf, iAdjacentType = getNodeAdjacencyDf(iNode, edgeDf)
				#the change in modularity is calculated for removing i from its own community and 
				#moving it into the community of each neighbor j of i
				for jIndex, jRow in iDf.iterrows():
					###########################################
					#from time to time they might be a call to a node in the community dict that has just been changed so we obtain
					#a KeyError, whenever we encounter that problem we pass it since it will be solved in the next step of the loop
					try:
						jCommunityNodes = communityDict[nodesDict[jRow[iAdjacentType]][1]]
						#louvain modularity gain formula
						gainModularity = getGainOfModularity(jCommunityNodes, edgeDf, iDf, iAdjacentType, m2)

						#each node can only belong to one community so if the gain of modularity is the same as a preexisting one it gets discarded (could be improved)
						if gainModularity > changeToBeMade[0]:
							newCommunityOfI = nodesDict[jRow[iAdjacentType]][1]
							changeToBeMade = [gainModularity, iNode, newCommunityOfI]
					except KeyError:
						print(2222222233333333, 'keyerrors  ', nodesDict[jRow[iAdjacentType]][1])
						pass
				#if there is a significant change to be made
				if changeToBeMade[1] != None :
					nodesDict, communityDict = updatingDicts(changeToBeMade[0], changeToBeMade[1], changeToBeMade[2], nodesDict, communityDict)
					nodeDf.at[nodesDict[changeToBeMade[1]][2], u'modularity_class'] = changeToBeMade[2]

		#we use a counter to avoid infinite loops of variations of modules without ever obtsining less than the maxCommunities
		if len(communityDict) == repetitionCounter[1]:
			repetitionCounter[0] += 1
		else:
			repetitionCounter[0] = 0
			repetitionCounter[1] = len(communityDict)
		#repetition limit
		if repetitionCounter[0] >= 10:
			break
	#dumps the dataframe with the modularization data
	nodeDf.to_csv(outputFilePath, sep='\t')
	return nodesDict, communityDict


def getModularityPercentage(nodeFilePathWithModularity):
	'''
	opens the node tsv file and calculates the percentage of communities
	'''
	communityDict = {}
	resultDict = {}
	nodeDf = pd.read_csv(nodeFilePathWithModularity, sep=u'\t')

	#remaking a community dict
	for nodeIndex, nodeRow in nodeDf.iterrows():
		modCommunity = nodeRow[u'modularity_class']
		if modCommunity in communityDict:
			communityDict[modCommunity].append(nodeRow[u'Label'])
		else:
			communityDict[modCommunity] = [nodeRow[u'Label']]
	#calculation
	for idKey, communityValue in communityDict.items():
		resultDict[idKey] = (float(len(communityValue)) / float(len(nodeDf)))
	#printing in order
	for v,k in (sorted( ((v,k) for k,v in resultDict.items()), reverse=True)):
		print(44444444444444444444444, 'community {0} normalized score: {1}'.format(k, v))
		if v > 0.01:
			print(55555555555, communityDict[k])
	return resultDict




edgeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/testsGephi/oldOnes/edgeListWeight.tsv'
nodeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/testsGephi/oldOnes/nodeListType.tsv'
outputFilePath=u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/testsGephi/oldOnes/nodeListTypeModularity.tsv'

#edgeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeListWeight.tsv'
#nodeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListType.tsv'
#outputFilePath=u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListTypeModularity.tsv'

nodesDict, communityDict = modularize(edgeFilePath, nodeFilePath, 150, outputFilePath)
#print(nodesDict)
#print(communityDict)
#STATS previsualization of modularity result
getModularityPercentage(outputFilePath)