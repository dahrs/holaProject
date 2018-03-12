#!/usr/bin/python
#-*- coding:utf-8 -*-


import os, codecs

##################################################################################
#FOLDERS
##################################################################################

def emptyTheFolder(directoryPath, fileExtensionOrListOfExtensions=u'*'):
	'''
	Removes all files corresponding to the specified file(s) extension(s).
	If the fil estension is '*' the function will remove all files except
	the system files (ie: '.p', '.java', '.txt') and folders
	'''
	#we first delete the content of the folder to make place to the new content
	try:
		if type(fileExtensionOrListOfExtensions) is list:
			filelist = []
			for extension in fileExtensionOrListOfExtensions:
				fileExtensionList = [file for file in os.listdir(directoryPath) if file.endswith(".%s" %(fileExtensionOrListOfExtensions)) ]
				filelist = filelist + fileExtensionList
		#the '*' implies we want all files deleted
		elif fileExtensionOrListOfExtensions == u'*':
			filelist = [file for file in os.listdir(directoryPath)]
		else:
			filelist = [file for file in os.listdir(directoryPath) if file.endswith(u".%s" %(fileExtensionOrListOfExtensions)) ]
		#we delete the files
		for file in filelist:
			os.remove(directoryPath + file)
	except OSError:
		pass


##################################################################################
#FILES
##################################################################################

def createEmptyFile(filePath):
	'''
	we dump an empty string to make sure the file is empty
	and we return the handle to the ready to append file
	'''
	openFile = codecs.open(filePath, u'w', encoding=u'utf8')
	openFile.write(u'')
	openFile.close()
	openFile = codecs.open(filePath, 'a', encoding='utf8')
	return openFile


def theFileExists(directoryPath, nameOfFile, fileExtension=None):
	'''
	Returns false if the file does not exists at the directory
	and returns true if the file exists
	'''
	#if the path is correctly written at the end
	if directoryPath[-1] !=u'/':
		directoryPath = u'%s/' %(directoryPath)
	#all extensions
	if fileExtension == None:
		filelist = os.listdir(directoryPath)
		for file in filelist:
			splittedFileName = file.split('.')
			#if there was more than one '.'
			if len(splittedFileName) > 2:
				splittedFileName = ['.'.join(splittedFileName[:len(splittedFileName)-1])]
			#if the file exists
			for nb in range(100):
				if u'%s_%s' %(nameOfFile, unicode(nb)) == toUtf8(splittedFileName[0]) or u'%s_%s' %(noTroublesomeName(nameOfFile), unicode(nb)) == toUtf8(splittedFileName[0]):
					return True
		#if the file never appeared
		return False
	#exclusive extension
	else:
		return os.path.isfile(u'%s%s.%s' %(directoryPath, nameOfFile, fileExtension))


def readAllLinesFromFile(pathToFile):
	'''
	Returns a list containing all the lines in the file
	'''
	openedFile = codecs.open(pathToFile, 'r', encoding='utf8')
	linesList = openedFile.readlines()
	openedFile.close()

	#if linesList is None we return and empty list
	if linesList == None:
		linesList = []
	return linesList


def dumpRawLines(listOfRawLines, filePath, addNewline=True): 
	'''
	Dumps a list of raw lines in a a file 
	so the Benchmark script can analyse the results
	'''
	folderPath = u'/'.join((filePath.split(u'/'))[:-1]+[''])
	if not os.path.exists(folderPath):
		os.makedirs(folderPath)
	#we dump an empty string to make sure the file is empty
	openedFile = codecs.open(filePath, 'w', encoding='utf8')
	openedFile.write('')
	openedFile.close()
	openedFile = codecs.open(filePath, 'a', encoding='utf8')
	#we dump every line of the list
	for line in listOfRawLines:
		if addNewline == True:
			openedFile.write(u'%s\n' %(line))
		else:
			openedFile.write(u'%s' %(line))
	openedFile.close()
	return None


def dumpDictToJsonFile(aDict, pathOutputFile='./dump.json'):
	'''
	save dict content in json file
	'''
	import json
	#to avoid overwriting the name may change
	pathOutputFile = safeFilePath(pathOutputFile)
	#dumping
	dictFile = codecs.open(pathOutputFile, u'wb', encoding=u'utf8')
	json.dump(aDict, dictFile)
	dictFile.close()
	return None


def deleteTheFile(directoryPath, nameOfFile, fileExtension):
	'''
	Removes all files corresponding to the given name and the specified file(s) extension(s).
	'''	
	#if the path is correctly written at the end
	if directoryPath[-1] !=u'/':
		directoryPath = u'%s/' %(directoryPath)

	#preparing to dump into file
	for char in [u' ', u'_', u'/', u'\\', u':', u'…', u'。', u';', u',', u'.', u'>', u'<', u'?', u'!', u'*', u'+', u'(', u')', u'[', u']', u'{', u'}', u'"', u"'", u'=']:
		nameOfFile = nameOfFile.replace(char, u'_')
	#we change the iri code if there is one
	if u'%' in nameOfFile or '%' in nameOfFile:
		nameOfFile = iriToUri(nameOfFile)

	#we make a list of all the possible names of the files to be deleted
	fileNamesToBeDeleted = []
	namePlusExt = u'%s.%s' %(nameOfFile, fileExtension)

	fileNamesToBeDeleted.append(namePlusExt)
	fileNamesToBeDeleted.append(noTroublesomeName(namePlusExt))
	for nb in range(10):
		fileNamesToBeDeleted.append(u'%s_%s.%s' %(nameOfFile, unicode(nb), fileExtension))
		fileNamesToBeDeleted.append(u'%s_%s.%s' %(noTroublesomeName(nameOfFile), unicode(nb), fileExtension))

	#we make a list of all extension-like 
	try:
		#we catch all corresponding names
		if type(fileExtension) is unicode:	
			filelist = [toUtf8(file) for file in os.listdir(directoryPath) if file.endswith(".%s" %(fileExtension.encode('utf8'))) ]
		elif type(fileExtension) is str:
			filelist = [toUtf8(file) for file in os.listdir(directoryPath) if file.endswith(".%s" %(fileExtension)) ]
		
	except OSError:
		filelist = []

	#we make a list of the intersection between the 2 lists
	intersection = list(set(fileNamesToBeDeleted) & set(filelist))
	#we delete the files
	for file in intersection:
		os.remove(directoryPath + file)


def deleteFileContent(pathToFile, openAnAppendFile=False):
	'''
	Deletes a file's content without deleting the file by 
	writing an empty string into it.
	It returns the object corresponding to the file.
	If the openAnAppendFile is not False, it will return the
	object corresponding to an openend and append file
	'''
	openedFile = codecs.open(pathToFile, 'w', encoding='utf8')
	openedFile.write('')
	openedFile.close()
	if openAnAppendFile != False:
		openedFile = codecs.open(pathToFile, 'a', encoding='utf8')
	return openedFile


##################################################################################
#NAMES AND PATHS
##################################################################################

def noTroublesomeName(string):
	'''
	Transforms the name into a non-troublesome name
	'''
	for char in [u' ', u' ', u'_', u'/', u'\\', u':', u';', u',', u'.', u'>', u'<', u'?', u'!', u'*', u'+', u'(', u')', u'[', u']', u'{', u'}', u'"', u"'", u'=']:
		string = string.replace(char, u'_')
	#we change the iri code if there is one
	if u'%' in string:
		string = iriToUri(string)
	return string
	

def noTroublesomeNameAndNoDoubleUnderscore(string):
	'''
	Transforms the name into a non-troublesome name
	'''
	for char in [u' ', u' ', u'_', u'/', u'\\', u':', u';', u',', u'.', u'>', u'<', u'?', u'!', u'*', u'+', u'(', u')', u'[', u']', u'{', u'}', u'"', u"'", u'=']:
		string = string.replace(char, u'_')

	#we change the iri code if there is one
	if u'%' in string:
		string = iriToUri(string)
		#if there is still a '%' char we replace it
		if u'%' in string:
			string = string.replace(u'%', u'_') 

	if len(string) > 0:
		#we replace all double underscore by a single underscore
		if u'__' in string:
			string.replace(u'__', u'_')
		#if there is an underscore at the begining and at the end of the name, we delete it
		if string[0] == u'_':
			string = string[1:]
		if len(string) > 0 and string[-1] == u'_':
			string = string[:-1]
	return string


def safeFilePath(outputFilePath):
	fileName = noTroublesomeName(outputFilePath.split(u'/')[-1])
	folderPath = outputFilePath.replace(fileName, u'')
	if u'.' in fileName:
		fileExtension = None
	else:
		fileExtension = fileName.split(u'.')[-1]
		fileName = fileName.replace(u'.%s' %(fileExtension), u'')
	nb = 1
	if theFileExists(folderPath, fileName, fileExtension) == True:
		fileName = u'%s_%s' %(fileName, nb)
		while theFileExists(folderPath, fileName, fileExtension) == True:
			fileName = fileName.replace(u'_%s' %(str(nb)), u'_%s' %(str(nb+1)))
			nb += 1
	return u'%s%s.%s' %(folderPath, fileName, fileExtension)