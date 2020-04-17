import os
from os import listdir
from os.path import isfile, join
	
####	The goal of this script is to read through folders, detect which EXR files are supposed to go together based on their names, and then merge them together


def main():
	# Get the current directory
	srcDirectory = dirPath()

	# Get the list of directories in the current one
	dirList = listdirectories()

	# Print infos
	startInfos(srcDirectory, dirList)

	# Splitting by folders
	fileList = getFolderFiles(srcDirectory, dirList)

	# Splitting by dots to get the frames and extensions
	fileListPoints = splitPoints(fileList)
	# This definition returns a lits following this syntax:
	#### [[['Shot_Shape20_leoLayer_SET_LGT_A,B,G,R_filtered', '0105', 'exr'], ['Shot_Shape20_leoLayer_SET_LGT_A,B,G,R_filtered', '0145', 'exr']], [['Shot_Shape20_leoLayer_SET_LGT_dirSpec_filtered', '0105', 'exr'], ['Shot_Shape20_leoLayer_SET_LGT_dirSpec_filtered', '0145', 'exr']]]
	# The frame of each exr is positioned at:
	# fileListPoint[channel][numberOfExrsInTheChannel][1]
	# we still need to split [channel][numberOfExrsInTheChannel][0] to find the specific name of the said channel in the exr
	# Therefore we need to split the last two "_" charaters to separate filtered and the channel in different lists items

	fileListUnderscores = splitUnderscores(fileListPoints)
	# Returns a list with the renderpass as the second item of the list 
	
	separatedList = listseparation(fileListUnderscores)
	# returns a list with the following syntax
	# separatedList[current][0] = Layer+AOV
	# separatedList[current][1] = layer
	# separatedList[current][2] = filtered
	# separatedList[current][3] = frame number (<f4>)
	# separatedList[current][4] = exr

	groupedlists = listsgrouping(separatedList)
	# Returns a list grouped by render layer but containing all of the render frames, which still need to be separated

	joblist = listframes(groupedlists)

	outputJson(joblist, dirList, srcDirectory)

	modBlenderBatcher(srcDirectory)


def dirPath():
	directoryPath = (os.path.dirname(os.path.realpath(__file__)))
	return(directoryPath)

def listdirectories():
	directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
	return(directories)
	
def startInfos(srcDirectory, dirList):
	print("\nThe folder being processed is:")
	print(srcDirectory)
	print("\nThe following renderpasses have been detected:")

	current = 0
	for i in dirList:
		print (dirList[current])
		current += 1

def getFolderFiles(srcDirectory, dirList):
	allFilesList = []
	current = 0
	for i in dirList:
		onlyfiles = [f for f in listdir(srcDirectory +"\\" + str(dirList[current])) if isfile(join(srcDirectory +"\\" + str(dirList[current]), f))]
		allFilesList.append(onlyfiles)
		current += 1
	return(allFilesList)

def splitPoints(fileList):
	current = 0
	for i in fileList:
		subCurrent = 0
		for i in fileList[current]:
			split = fileList[current][subCurrent].split(".")
			fileList[current][subCurrent] = split
			subCurrent += 1
		current += 1
	return(fileList)

def splitUnderscores(fileListPoints):
	current = 0
	for i in fileListPoints:
		subCurrent = 0
		for i in fileListPoints[current]:
			split = (fileListPoints[current][subCurrent][0]).split("_")
			# Formatting the split to separate necessary naming conventions
			split = (("_".join(split[:-2])), split[len(split)-2], split[len(split)-1])
			# Replacing the list with the splitted naming convention
			fileListPoints[current][subCurrent][0] = split
			subCurrent += 1
		current += 1
		
	return(fileListPoints)

def listseparation(fileListUnderscores):
	current = 0
	listSeparated = []
	for i in fileListUnderscores:
		subCurrent = 0
		for i in fileListUnderscores[current]:
			templist = [(fileListUnderscores[current][subCurrent][0][0]),(fileListUnderscores[current][subCurrent][0][1]),(fileListUnderscores[current][subCurrent][0][2]),(fileListUnderscores[current][subCurrent][1]),(fileListUnderscores[current][subCurrent][2])]
			listSeparated.append(templist)
			subCurrent += 1
		current += 1
	return(listSeparated)

def listsgrouping(separatedList):
	# Making a list of the different render layers (items[0])
	current = 0
	layerlist = []
	for i in separatedList:
		if (separatedList[current][0]) not in layerlist:
			layerlist.append(separatedList[current][0])
		current += 1

	print("\nThe following layers have been detected:")
	current = 0
	for i in layerlist:
		print(layerlist[current])
		current += 1

	# Creating a list containing as many empty li0sts as tehre are layers
	groupedlist = []
	for i in layerlist:
		groupedlist.append([])

	# Appending the separatedlist with the corresponding layer list
	current = 0
	for i in separatedList:
		subCurrent = 0
		for i in layerlist:
			#print("Comparing ", layerlist[subCurrent], " to ", separatedList[current][0])
			if separatedList[current][0] == layerlist[subCurrent]:
				groupedlist[subCurrent].append(separatedList[current])
				
			subCurrent += 1
		current += 1
		
	return(groupedlist)
	

def listframes(groupedlists):
	current = 0
	frameLists = []

	# Creating a list containing all of the different frames for later comparison
	for i in groupedlists:
		subCurrent = 0
		for i in groupedlists[current]:
			if groupedlists[current][subCurrent][3] not in frameLists:
				frameLists.append(groupedlists[current][subCurrent][3])
			subCurrent += 1
		current += 1

	current = 0
	print("\nThe following frames have been detected:")
	for i in frameLists:
		print (frameLists[current])
		current += 1

	currentJob = 1
	current = 0
	current2 = 0
	subCurrent = 0
	var = []
	currentIndex = 1
	currentJobIndex = 0 
	"""	
	print("\n")
	print(groupedlists[1][0][3])
	print(len(frameLists))
	"""
	for i in frameLists:
		current = 0
		var.append("jobID#" + str(currentJob)) 
		var.append(frameLists[subCurrent])
		for i in groupedlists:
			current2 = 0
			for i in groupedlists[current]:
				## Uncomment the following for debugging only
				"""
				print("grouped list index :          ",current)
				print("current exr in grouped list : ",current2)
				print("current frame in list :       ",subCurrent)
				print("\n")
				"""
				if frameLists[subCurrent] == (groupedlists[current][current2][3]):
					var.append(groupedlists[current][current2])
				current2 += 1
			current += 1
		subCurrent += 1
		currentJob += 1
		currentIndex += 2
		currentJobIndex += 2

	
	numberofjobs = (len(var))
	current = 0
	subCurrent = -1
	joblist = []
	for i in var:
		#print(var[current])
		if type(var[current]) is list:
			if var[current][0] == var[current - 1][0]:
				joblist[subCurrent].append(var[current])
				#print(var[current], " - ", var[current - 1])
			else:
				joblist.append(var[current])
				subCurrent += 1
		current += 1

	"""
	print("\n")
	current = 0
	for i in joblist:
		print(joblist[current])
		current += 1
	
	"""
	return(joblist)

def outputJson(joblist, dirList, srcDirectory):
	
	# mergine the first elements of the lists which are strings in a single list of theses strings
	current = 0
	for i in joblist:
		templist = [(joblist[current][0]), (joblist[current][1]), (joblist[current][2]), (joblist[current][3]), (joblist[current][4])]
		joblist[current][0] = templist
		joblist[current].pop(1)
		joblist[current].pop(1)
		joblist[current].pop(1)
		joblist[current].pop(1)
		current += 1

	# Adding the directories at the start of the exrs and checking if the files exist within the directories 

	current = 0
	for i in joblist:
		subCurrent = 0
		for i in joblist[current]:
			current2 =  0
			tempvar = (joblist[current][subCurrent][0] + "_" + joblist[current][subCurrent][1] + "_" + joblist[current][subCurrent][2] + "." + joblist[current][subCurrent][3] + "." + joblist[current][subCurrent][4])
			for i in dirList:
				if dirList[current2] in tempvar:
					testfile = (dirList[current2] + "/" + tempvar)
					# tests if the file exists
					if os.path.isfile(testfile):
					    # Append the folder if the file exists (to avoid duplicates with indirect and indirect names)
						joblist[current][subCurrent].insert(0, dirList[current2])	
				current2 += 1
			subCurrent += 1
		current += 1

	# Writing the file out
	f = open("exrMergingList.json", "w+")
	
	current = 0
	for i in joblist:
		line = (str(joblist[current]) + "\n")
		f.write(line)
		current += 1
	# Adding the absolute path to the denoised intel folde
	line = (srcDirectory)
	f.write(line)

	f.close()

	
	
def modBlenderBatcher(srcDirectory):
	jsonFile = srcDirectory + "\\" +"exrMergingList.json"
	jsonVar = jsonFile.replace("\\", "\\\\")
	
	blenderBackgroundFile = "C:\\Denoiser\\EXR_MERGE\\exrMerge_toBlender_v001.py"
	#     jsonPath = ("C:\\Users\\Administrateur\\Desktop\\mergeExrLayers\\exrMergingList.json")
	a_file = open(blenderBackgroundFile, "r")
	list_of_lines = a_file.readlines()
	list_of_lines[49] = ('    jsonPath = ("' +str(jsonVar) +'")\n')

	a_file = open(blenderBackgroundFile, "w")
	a_file.writelines(list_of_lines)
	a_file.close()

	os.system('start C:\\Denoiser\\EXR_MERGE\\blender_executable\\blender.exe --background --factory-startup --python C:\\Denoiser\\EXR_MERGE\\exrMerge_toBlender_v001.py')




if __name__ == "__main__":
	main()