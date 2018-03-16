#!/usr/bin/python
#-*- coding:utf-8 -*-


import json, codecs, nltk
import utilsOs

##################################################################################
#JOB DATA FORMATING
##################################################################################


def addJobData(profile, dictJobTitlesData={}):
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
				#if we have it's the first time we have encountered this job title
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

def dumpJobTitleAndDescription(jsonDict, pathOutputFile='./job+pitch.tsv'):
	'''
	Saves the basic linkedIn job data in a tsv file
	each line shows:
	- one job title (or variant)
	- its description(s) / personal pitch(es) / NA (non applicable)
	'''
	#file of job titles names (and optional description)
	with utilsOs.createEmptyFile(pathOutputFile) as outputJobtitles:
		for jobTitle, jobData in jsonDict.iteritems():
			#only the job title
			if addJobDescription == False:
				content = u'%s\n' %(jobTitle)
			#job title + description
			else:
				#if there is one or multiple specific description of the job
				try:
					content = u'%s\t%s\n' %(jobTitle, u' _#####_ '.join(jobData[u'description']))
				except KeyError:
					#if there is one or multiple personal pitches that might give us an idea of what is the job
					try:
						content = u'%s\t%s\n' %(jobTitle, u' _#####_ '.join(jobData[u'pitch']))
					#if there is nothing then it's Non Applicable
					except KeyError:
						content = u'%s\t%s\n' %(jobTitle, u'NA')
			#dumping to file
			outputJobtitles.write(content)
	return


##################################################################################
#LINKEDIN DATA SAMPLE MAKER
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
				dictJobTitlesData = addJobData(jsonLine, dictJobTitlesData)

	#dumping dict content in json
	utilsOs.dumpDictToJsonFile(dictJobTitlesData, pathOutputFile=u'%sjobTitlesDataDict.json'%(pathOutput))

	#SIMPLIFIED DATA dumping job title (and optional dexcription) to a file
	dumpJobTitleAndDescription(jsonDict, pathOutputFile=u'./job+pitch.tsv')
	
	#closing the files
	outputJson.close()
	return None






##################################################################################
#QUICK COMMANDS
##################################################################################


pathInput = u'/u/kessler/LBJ/data/2016-09-15/fr/anglophone/candidats.json'
pathOutput = u'/u/alfonsda/Documents/DOCTORAT_TAL/004projetOntologie/002data/candidats/2016-09-15/fr/anglophone/sample100milFunctions2/'

#we make a sample tsv file of 100000 job titles + description
#and also a json file containig all the needed information of the sample LinkedIn profiles
makeSampleFileHavingNJobTitles(pathInput, pathOutput, 100000)
