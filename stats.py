#!/usr/bin/python
#-*- coding:utf-8 -*-


import utilsOs


##################################################################################
#ESCO STATS
##################################################################################


def savingToDict(dictionnary, labelList, description):
	'''
	'''
	if len(labelList) != 0:
		for label in labelList:
			dictionnary[label.lower()] = description
	return dictionnary


def printEscoSkills(escoFile, verbose=False):
	'''
	'''
	#first we make an esco dict containing all lowercased names of skills as keys
	escoSkillsDict = {}
	descriptionWaitingList = []

	for i, line in enumerate(escoFile):
		lineList = line.split(u',')
		if i == 0:
			pass
		#start of csv Line
		elif line[0:24] == u'KnowledgeSkillCompetence':
			#prefered, alternative labels and description on the same line
			if len(lineList) > 6:
				#description
				description = (u','.join(lineList[6:(len(lineList))])).replace(u'"', u'').replace(u'\r', u'').replace(u'\n', u'')
				if description == u'':
					description = None
				#saving to dict
				escoSkillsDict = savingToDict(escoSkillsDict, [lineList[4]] + [lineList[5].replace(u'"', u'')], description)
			#prefered and first alternative label on the same line
			else:
				#adding to the descriptionWaitingList until we find the description
				descriptionWaitingList.append(lineList[4])
				descriptionWaitingList.append((lineList[5].replace(u'"', u'')).replace(u'\n', u''))
		#rest of csv line
		elif len(lineList) == 1:
			#adding to the descriptionWaitingList until we find the description
			descriptionWaitingList.append(lineList[0].replace(u'\n', u''))
		#end of the csv line with last alternative skill and description
		else:
			#description
			description = (u','.join(lineList[1:(len(lineList))])).replace(u'"', u'')
			if description == u'':
				description = None
			#adding the last skill to the descriptionWaitingList
			descriptionWaitingList.append(lineList[0].replace(u'"', u''))
			#saving to dict with no description
			escoSkillsDict = savingToDict(escoSkillsDict, descriptionWaitingList, description)
			#erasing the descriptionWaitingList
			descriptionWaitingList = []
	if verbose == True:
		for key in escoSkillsDict:
			print(key)
	return escoSkillsDict


def printEscoJobs(escoFile, verbose=False):
	'''
	'''
	#first we make an esco dict containing all lowercased names of jobs as keys
	escoJobsDict = {}
	descriptionWaitingList = []

	for i, line in enumerate(escoFile):
		lineList = line.split(u',')
		if i == 0:
			pass
		#start of csv Line
		elif line[0:10] == u'Occupation,':
			#prefered, alternative labels and description on the same line
			if len(lineList) > 5:
				#description
				description = (u','.join(lineList[5:(len(lineList))])).replace(u'"', u'').replace(u'\r', u'').replace(u'\n', u'')
				if description == u'':
					description = None
				#saving to dict
				escoJobsDict = savingToDict(escoJobsDict, [lineList[3]] + [lineList[4].replace(u'"', u'')], description)
			#prefered and first alternative label on the same line
			else:
				#adding to the descriptionWaitingList until we find the description
				descriptionWaitingList.append(lineList[3])
				descriptionWaitingList.append((lineList[4].replace(u'"', u'')).replace(u'\n', u''))
		#rest of csv line
		elif len(lineList) == 1:
			#adding to the descriptionWaitingList until we find the description
			descriptionWaitingList.append(lineList[0].replace(u'\n', u''))
		#end of the csv line with last alternative skill and description
		else:
			#description
			description = (u','.join(lineList[1:(len(lineList))])).replace(u'"', u'')
			if description == u'':
				description = None
			#adding the last skill to the descriptionWaitingList
			descriptionWaitingList.append(lineList[0].replace(u'"', u''))
			#saving to dict with no description
			escoJobsDict = savingToDict(escoJobsDict, descriptionWaitingList, description)
			#erasing the descriptionWaitingList
			descriptionWaitingList = []
	if verbose == True:
		for key in escoJobsDict:
			print(key)
	return escoJobsDict
