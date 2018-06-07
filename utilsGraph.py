#!/usr/bin/python
#-*- coding:utf-8 -*-

import json, codecs, random
import pandas as pd
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
	outputTempFile = utilsOs.createEmptyFile(pathTempFile, headerLine=u'jobNode\tskillNode')

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
								#######################DOUBLES to be suppressed later
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
	outputTxt = utilsOs.createEmptyFile(pathOutput, headerLine=u'jobNode\tskillNode\tweight\tnbOfTimesJobTitleAppeared')
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
		outputTxt.write(u'{0}\t{1}\t{2}\t{3}\n'.format(dataList[0], dataList[1], skillCorefDict[dataList[1]], jobTitleCorefDict[dataList[0]]))

	#closing the file	
	outputTxt.close()


def nodeListIdType(pathEdgeListFile, pathNodeFileOutput):
	'''
	opens the temp file containing the extracted linkedin data and makes an edge list of (columns):
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
		outputTxt.write(u'{0}\t{1}\t{2}\n'.format(jobTitle, jobTitle, 2)) #2 means 'source'
	for skill in skillSet:
		outputTxt.write(u'{0}\t{1}\t{2}\n'.format(skill, skill, 1)) #1 means 'target'


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


def getSumOfEdgesInCommunity(nodeId, communityId, nodesDict, communityDict, edgeDf):
	'''
	searches what community does the nodeId belongs
	returns the variables sum of edges weights necessary to calculate the gain of modularity
	'''
	sumOfWeightsOfEdgesInC = 0
	sumOfWeightsOfEdgesIncidentToNodesInC = 0
	sumOfWeightsOfEdgesFromIToNodesInC = 0
	sumOfWeightsOfEdgesIncidentToNodeI = 0

	iDf, iAdjacentType = getNodeAdjacencyDf(nodeId, edgeDf)

	communityNodes = communityDict[communityId][1:]
	dejaVus = set()
	for cNode in communityNodes:
		#if the weight has not already been added to the sum of weights
		if cNode not in dejaVus:
			dejaVus.add(cNode)
			#we get the data frame containing the c node
			communityDf, cNodeAdjacentType = getNodeAdjacencyDf(cNode, edgeDf)

			#sumOfWeightsOfEdgesIncidentToNodesInC  = one node of the edge must be in the community
			sumOfWeightsOfEdgesIncidentToNodesInC = getSumOfAllWeights(communityDf)
			#sumOfWeightsOfEdgesInC  = both nodes of the edge must be in the community
			sumOfWeightsOfEdgesInC = getSumOfAllWeights( getReducedDf(communityDf, cNodeAdjacentType, communityNodes) )
			#sumOfWeightsOfEdgesIncidentToNodeI = all the weights of edges having i as one of their node
			sumOfWeightsOfEdgesIncidentToNodeI = getSumOfAllWeights(iDf)
			#sumOfWeightsOfEdgesInC = all the weights of edges having i and a node of the community
			sumOfWeightsOfEdgesFromIToNodesInC = getSumOfAllWeights( getReducedDf(iDf, iAdjacentType, communityNodes) )
	return sumOfWeightsOfEdgesInC, sumOfWeightsOfEdgesIncidentToNodesInC, sumOfWeightsOfEdgesFromIToNodesInC, sumOfWeightsOfEdgesIncidentToNodeI


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
	communityDict[communityId][0] += gainModularity
	communityDict[communityId].append(nodeId)
	return nodesDict, communityDict


def modularize(edgeDf, nodeDf, maxCommunities):
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
	BibTex	@MISC{Blondel08fastunfolding,
    author = {Vincent D Blondel and Jean-loup Guillaume and Renaud Lambiotte and Etienne Lefebvre},
    title = {Fast unfolding of communities in large networks}, year = {2008}}
	'''
	nodesDict = {}
	communityDict = {}
	#basic attribution of communities (to each node)
	for nodeIndex in range(len(nodeDf)):
		nodeId = nodeDf.iloc[nodeIndex][u'Id']
		#nodeId = id of the node, nodeIndex = id of the community, 0 = basic modularity score
		nodesDict[nodeId] = [0, nodeIndex]
		communityDict[nodeIndex] = [0, nodeId]
	repetitionCounter = [0, None]

	#calculation of the gain of modularity
	m2 = getSumOfAllWeights(edgeDf) * 2
	while len(communityDict) > maxCommunities:
		#we loop on each node of the dataframe
		for nodeIndex, nodeRow in nodeDf.iterrows():
			#we save for each node the stronges change based on the modularity gain
			changeToBeMade = [0, None]
			#we loop on every remaining community
			for communityId in communityDict:
				#FORMULA TAKEN FROM https://arxiv.org/pdf/0803.0476.pdf
				sigmaIn, sigmaTot, kIin, kI = getSumOfEdgesInCommunity(nodeRow[u'Id'], communityId, nodesDict, communityDict, edgeDf)
				gainModularity = ( ((sigmaIn + kIin)/m2)-(((sigmaTot+kI)/m2)**2) ) - ( (sigmaIn/m2)-((sigmaTot/m2)**2)-((kI/m2)**2) )
				#each node can only belong to one community so if the gain of modularity is the same as a preexisting one it gets discarded (could be improved)
				if gainModularity > changeToBeMade[0]:
					changeToBeMade = [gainModularity, communityId]
			#if there is a significant change to be made
			if changeToBeMade[1] != None:
				nodesDict, communityDict = updatingDicts(changeToBeMade[0], nodeRow[u'Id'], changeToBeMade[1], nodesDict, communityDict)

		#we use a counter to avoid infinite loops of variations of modules without ever obtsining less than the maxCommunities
		if len(communityDict) == repetitionCounter[1]:
			repetitionCounter[0] += 1
		else:
			repetitionCounter[1] = len(communityDict)
		#repetition limit
		if repetitionCounter[0] >= 99:
			break
	return nodesDict, communityDict

#edgeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/testsGephi/oldOnes/myGraphEdgeList.tsv'
#nodeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/testsGephi/oldOnes/myGraphNodeList.tsv'
edgeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/edgeList_TargetSourceWeight.tsv'
nodeFilePath = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions/nodeListType.tsv'
	
edgeDf = pd.read_csv(edgeFilePath, sep=u'\t')
nodeDf = pd.read_csv(nodeFilePath, sep=u'\t')

nodesDict, communityDict = modularize(edgeDf, nodeDf, 11382)
print(333333, len(communityDict), communityDict)