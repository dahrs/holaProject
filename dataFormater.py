#!/usr/bin/python
#-*- coding:utf-8 -*-


import json, codecs, nltk
import utilsOs


##################################################################################
#LINKEDIN JOB DATA FORMATING
##################################################################################


def getJobData(profile, dictJobTitlesData={}):
	'''
	Saves the function's information in a dict
	'''
	skillDict = {}
	if u'experiences' in profile:
		for experience in profile[u'experiences']:
			dataDict = {}
			#if there is a job title in the profile
			if u'function' in experience:
				function = experience[u'function']
				#if it's the first time we have encountered this job title
				#we save the function data to the dict
				if function not in dictJobTitlesData:
					listFunction = nltk.word_tokenize(function)
					#coreference
					dataDict[u'nbCoreferenceJobTitleInCorpus'] = 1#how many times we encountered the same function in the corpus
					#tokens
					dataDict[u'tokens'] = listFunction
					dataDict[u'nbOfTokens'] = len(listFunction)
					#pos
					dataDict[u'pos'] = nltk.pos_tag(listFunction)
					#alternative names
					dataDict[u'alternativeNames'] = [function.lower(), function.upper(), (function.lower()).capitalize()]
					if u'missions' in experience:
						dataDict[u'description'] = [(experience[u'missions']).replace(u'\n', u' ').replace(u'\t', u' ').replace(u'\r', u' ')]
					#pitch
					if u'personalBranding_pitch' in profile:
						dataDict[u'pitch'] = [(profile[u'personalBranding_pitch']).replace(u'\n', u' ').replace(u'\t', u' ').replace(u'\r', u' ')]
					else:
						dataDict[u'pitch'] = []
					#skills
					if u'skills' in profile:
						for skill in profile[u'skills']:
							skillDict[skill[u'name']] = 1
							skillDict[skill[u'name'].lower()] = 1
							skillDict[skill[u'name'].upper()] = 1
							skillDict[skill[u'name'].capitalize()] = 1
					dataDict[u'possibleSkills'] = skillDict			
					#we save the function info
					dictJobTitlesData[function] = dataDict
				#if there is a duplicate
				else:
					dictJobTitlesData = manageDuplicates(function, profile, dictJobTitlesData)
	#we return the dict
	return dictJobTitlesData


def manageDuplicates(function, profile, dictJobTitlesData):
	'''
	if there is a duplicate in the dict, we add the data to the existing one
	'''
	emptyList = []
	#we save the function data to the dict
	dictJobTitlesData[function][u'nbCoreferenceJobTitleInCorpus'] += 1#how many times we encountered the same function in the corpus
	#if the profile has data for job description
	if u'missions' in profile[u'experiences']:
		dictJobTitlesData[function][u'description'].append((profile[u'experiences'][u'missions']).replace(u'\n', u' ').replace(u'\t', u' ').replace(u'\r', u' '))
	#pitch
	if u'personalBranding_pitch' in profile:
		(dictJobTitlesData[function].get(u'pitch', emptyList)).append((profile[u'personalBranding_pitch']).replace(u'\n', u' ').replace(u'\t', u' ').replace(u'\r', u' '))
	#skills
	if u'skills' in profile:
		for skill in profile[u'skills']:
			dictJobTitlesData[function][u'possibleSkills'][skill[u'name']] = dictJobTitlesData[function][u'possibleSkills'].get(skill[u'name'], 0) + 1			
			if skill[u'name'] != skill[u'name'].lower():
				dictJobTitlesData[function][u'possibleSkills'][skill[u'name'].lower()] = dictJobTitlesData[function][u'possibleSkills'].get(skill[u'name'].lower(), 0) + 1			
			if skill[u'name'] != skill[u'name'].upper():
				dictJobTitlesData[function][u'possibleSkills'][skill[u'name'].upper()] = dictJobTitlesData[function][u'possibleSkills'].get(skill[u'name'].upper(), 0) + 1			
			if skill[u'name'] != skill[u'name'].capitalize():
				dictJobTitlesData[function][u'possibleSkills'][skill[u'name'].capitalize()] = dictJobTitlesData[function][u'possibleSkills'].get(skill[u'name'].capitalize(), 0) + 1
	return dictJobTitlesData


##################################################################################
#SIMPLIFIED DATA DUMPING
##################################################################################

def dumpJobTitleAndDescription(jsonDict, pathOutputFile='./job+pitch.tsv', addJobDescription=False):
	'''
	Saves the basic linkedIn job data in a tsv file
	each line shows:
	- one job title (or variant)
	- its description(s) / personal pitch(es) / NA (non applicable)
	'''
	#file of job titles names (and optional description)
	with utilsOs.createEmptyFile(pathOutputFile) as outputJobtitles:
		for jobTitle, jobData in jsonDict.items():
			#only the job title
			if addJobDescription == False:
				content = u'%s\n' %(jobTitle)
			#job title + description
			else:
				#if there is one or multiple specific description of the job
				if u'description' in jobData and len(jobData[u'description']) > 0:
					content = u'%s\t%s\n' %(jobTitle, u' _#####_ '.join(jobData[u'description']))
				else:
					#if there is one or multiple personal pitches that might give us an idea of what is the job
					if u'pitch' in jobData and len(jobData[u'pitch']) > 0:
						content = u'%s\t%s\n' %(jobTitle, u' _#####_ '.join(jobData[u'pitch']))
					#if there is nothing then it's Non Applicable
					else:
						content = u'%s\t%s\n' %(jobTitle, u'NA')
			#dumping to file
			outputJobtitles.write(content)
	return


def dumpSetToJson(aSet, pathOutput):
	'''
	Mixes all given taxonomies/ontologies 
	and returns a set of their content
	regardless of the hierarchy (flattens jobtitle at same level)
	'''
	jsonDict = {}
	for elem in aSet:
		jsonDict[elem] = None
	utilsOs.dumpDictToJsonFile(jsonDict, pathOutput)
	return


##################################################################################
#JOB SET MAKER FROM TAXONOMY/ONTOLOGY (flatten the tree so we can compare them on the same level)
##################################################################################

def makeJobSetFromOnto(lowercaseItAll, *argv):
	'''
	Mixes all given taxonomies/ontologies 
	and returns a set of their content
	regardless of the hierarchy (flattens jobtitle at same level)
	'''
	allSet = set()
	for taxoonto in argv:
		allSet = dfsExtractor(taxoonto, allSet, lowercaseItAll)
	return allSet


##################################################################################
#TAXONOMY BROWSING TOOLS (from the uniformed json taxonomy format we made)
##################################################################################

def dfsExtractor(tree, setNodes, lowercaseItAll=False):
	'''
	depth first search of uniformized taxonomy tree
	key:	code___name of job or category
	'''
	if len(tree) == 0:
		return None
	elif type(tree) is dict:
		for node, dictNode in tree.items():
			if u'___' in node:
				#we do not take the code into account
				name = node.split(u'___')[1]
				#if we want all in lowercase
				if lowercaseItAll == True:
					name = name.lower()
				#we add to the set
				setNodes.add(name)
				result = dfsExtractor(dictNode, setNodes, lowercaseItAll)
				#we add to the set
				if result != None:
					setNodes = setNodes.union(result)
			else:
				result = dfsExtractor(dictNode, setNodes, lowercaseItAll)
				if result != None:
					setNodes = setNodes.union(result)
	elif type(tree) is list:
		for name in tree:
			setNodes.add(name)
	return setNodes


##################################################################################
#DICTIONARY SAMPLE MAKER FROM LINKEDIN DATA
##################################################################################

def makeSampleFileHavingNJobTitles(pathInput, pathOutput, n=1000000, addJobDescription=False):
	'''
	takes the real linkedIn data and makes a samble containing how
	many profiles necesary to achieve N functions (jobtitles)
	'''
	dictJobTitlesData = {}
	#sample of all candidates data
	outputJson = utilsOs.createEmptyFile(u'%ssample.json' %(pathOutput))
	
	#we read the original json file line by line
	with codecs.open(pathInput, u'r', encoding=u'utf8') as jsonFile:
		while len(dictJobTitlesData) < n:
			jsonData = jsonFile.readline()
			#we dump each line into the sample file
			outputJson.write(jsonData.replace(u'\r', ''))
			#we make a dict out of the string line
			jsonLine = utilsOs.convertJsonLineToDict(jsonData)
			if jsonLine != None:
				#we dump each job title into the jobtitle file
				dictJobTitlesData = getJobData(jsonLine, dictJobTitlesData)

	#dumping dict content in json
	utilsOs.dumpDictToJsonFile(dictJobTitlesData, pathOutputFile=u'%sjobTitlesDataDict.json'%(pathOutput))

	#SIMPLIFIED DATA dumping job title (and optional dexcription) to a file
	dumpJobTitleAndDescription(dictJobTitlesData, u'%sjob+pitch.tsv'%(pathOutput), addJobDescription)
	
	#closing the files
	outputJson.close()
	return None


##################################################################################
#JOB SET MAKER FROM LINKEDIN PROFILES
##################################################################################

def makeJobSetFromLinkedIn(pathInput, lowercaseItAll=False, pathOutput=None, n=float('inf')):
	'''
	makes a set of jobs taken from linkedIn profiles 
		IF a "pathOutput" is given we save the set as a txt file
		of one job per line 
		IF an "n" argument is given it makes a samble containing how
		many profiles necesary to achieve N functions (jobtitles)
	'''
	jobSet = set()
	#open the file
	if pathOutput != None:
		outputTxt = utilsOs.createEmptyFile(u'%slistOfJobs.linkedIn' %(pathOutput))
	#we read the original json file line by line
	with open(pathInput) as jsonFile:
		#if we want to make a sample n must be an int otherwise it will keep going until eof
		jsonData = jsonFile.readline()
		while jsonData and len(jobSet) < n:
			jobDict = getJobData(json.loads(jsonData))
			#we add the job titles
			jobsToAdd = set(jobDict.keys())
			#if we want them lowercased
			if lowercaseItAll != False:
				jobsToAdd = set([e.lower() for e in jobsToAdd])
			#we dump each job title into the txt file
			if pathOutput != None:
				for jobTitle in jobsToAdd:
					outputTxt.write(u'{0}\n'.format(jobTitle))
			#adding to the set
			jobSet = jobSet.union(jobsToAdd)
			#nextLine
			jsonData = jsonFile.readline()
	#closing the file	
	if pathOutput != None:
		outputTxt.close()
	return jobSet


def loadJobSetFromFile(pathInput, n=float('inf')):
	'''
	loads a txt file having one job per line as a set 
	'''
	jobSet = set()
	with codecs.open(pathInput, u'r', encoding=u'utf8') as txtFile:
		line = txtFile.readline()
		while line and len(jobSet) < n:
			job = line.split(u'\n')[0]
			jobSet.add(job)
	return jobSet


##################################################################################
#EDGE LIST MAKER IN O(n^2) where n is the nb of skills
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


			



def linkedInJobSkillEdgeList(pathEdgeFileInput, pathEdgeFileOutput, pathNodeFileOutput, lowercaseItAll=False):
	'''
	takes the linkedin data and makes an edge list of (columns):
		- jobNode(source)
		- skillNode(target)	
		- weight(coreference) 
		- nbOfTimesJobTitleAppeared
	
	[in a further function we might want to add keywords (non stop-words most common tokens for each jobtitle)]
	'''
	pathTempFile = u'./temp.txt'
	
	#we populate the temp file
	edgeListTemp(pathEdgeFileInput, pathTempFile, lowercaseItAll)
	#we populate the final output file
	edgeListDump(pathTempFile, pathEdgeFileOutput)
	#we populate the node list (defining each node as source or target)
	nodeListIdType(pathEdgeFileOutput, pathNodeFileOutput)
