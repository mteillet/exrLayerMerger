# This script is an example of how you can run blender from the command line
# (in background mode with no interface) to automate tasks
#
# Example usage for this test.
#  blender --background --factory-startup --python $HOME/background_job.py -- \
#          --text="Hello World" \
#          --render="/tmp/hello" \
#          --save="/tmp/hello.blend"
#
# Notice:
# '--factory-startup' is used to avoid the user default settings from
#                     interfering with automated scene generation.
#
# '--' causes blender to ignore all following arguments so python can use them.
#
# See blender --help for details.


import bpy
import ast
import os.path
import time


def main():    
    exrsLists = jsonInterpreter()
    jobDir = exrsLists[0]
    jobExrPath = exrsLists[1]
    jobFrame = exrsLists[2]
    outputPath = exrsLists[3]
    numberOfJobs = exrsLists[4]
    outputName = exrsLists[5]
    exrName = exrsLists[6]
    passType = exrsLists[7]

    testSingleFrame = ["1"]

    current = 0
    for i in jobExrPath:
        exrOut = executeJob(jobFrame[current], jobDir[current], jobExrPath[current], current, numberOfJobs, outputPath, outputName, exrName[current], passType[current])
        while not os.path.exists(exrOut):
            time.sleep(1)
            print("wait")
        current += 1
    
    

def jsonInterpreter():
    ### Variables
    jsonPath = ("C:\\Users\\Administrateur\\Desktop\\mergeExrLayers\\exrMergingList.json")
    
    jsonList = []

    with open(jsonPath) as jp:
        line = jp.readline()
        while line:
            line = jp.readline()
            try:
                jsonList.append(ast.literal_eval(line))
            except:
                jsonList.append(line)

    
    # Assigning variables based on the content of the json file
    lines = len(jsonList)
    jobs = lines - 1
    rootDirectory = jsonList[lines - 2]

    numberOfJobs = 0
    current = 0
    exrPaths = []
    exrDir = []
    exrFrame = []
    outputPath = []
    outputBaseName = []
    exrName = []
    passType = []
    for i in jsonList:
        current2 = 0
        jobPaths = []
        jobDir = []
        jobFrame = []
        output = []
        outputName = []
        exrNametemp = []
        passTypeTemp = []
        for i in jsonList[current]:
            try:
                jobPaths.append(rootDirectory + "\\" + jsonList[current][current2][0] + "\\" + jsonList[current][current2][1] + "_" +  jsonList[current][current2][2] + "_" +  jsonList[current][current2][3] + "." + jsonList[current][current2][4] + "." + jsonList[current][current2][5])
                jobFrame.append(jsonList[current][current2][4])
                jobDir.append(rootDirectory + "\\" + jsonList[current][current2][0] + "\\")
                output.append(rootDirectory + "\\")
                outputName.append(jsonList[current][current2][1])
                exrNametemp.append(jsonList[current][current2][1] + "_" +  jsonList[current][current2][2] + "_" +  jsonList[current][current2][3] + "." + jsonList[current][current2][4] + "." + jsonList[current][current2][5])
                passTypeTemp.append(jsonList[current][current2][0])
            except:
                pass
            current2 += 1
        if jobPaths != []:
            numberOfJobs += 1
            # Registering the real path of the exrs of jobs in the exrPaths list
            exrPaths.append(jobPaths)
            exrFrame.append(jobFrame[0])
            exrDir.append(jobDir)
            outputPath.append(output[0])
            outputBaseName.append(outputName)
            exrName.append(exrNametemp)
            passType.append(passTypeTemp)
            #print("Job number#" + str(numberOfJobs))
            #print(jobPaths)
        current += 1


    return(exrDir, exrPaths, exrFrame, outputPath, numberOfJobs, outputBaseName, exrName , passType)

def executeJob(jobFrame, jobDir, jobExrPath, current, numberOfJobs, outputPath, outputName, exrName, passType):
    print("Processing job " + str(current) + " out of " + str(numberOfJobs) )

    ####    BLENDER CODE    ####
    
    # Set the blender scene to use the nodes 
    bpy.context.scene.use_nodes = True

    # set the node tree context
    tree = bpy.context.scene.node_tree


    # delete the default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)


    # Add file output node in blender scene
    outputNode = tree.nodes.new(type='CompositorNodeOutputFile')
    outputNode.location = 300, 0
    outputNode.format.file_format = 'OPEN_EXR_MULTILAYER'
    # Removing the default image input of the outputNode
    outputNode.layer_slots.remove(outputNode.inputs[0])
    # Setting the output directory of the base
    outputStr = (str(outputPath[0]) + str(outputName[current][0]) + "_mergedExr.")
    outputNode.base_path = outputStr
    
    
    current2 = 0
    imgNodeList = []
    nodePosOffset = 0
    for i in jobExrPath:
        # add input to the output node
        outputNode.layer_slots.new(str(passType[current2]))
        # Add image node
        imgNode = tree.nodes.new(type='CompositorNodeImage')
        # Add to list for future referencing
        imgNodeList.append(imgNode)

        # Set variables for image import
        passName = (passType[current2])
        rootDirectory = (jobDir[current2])
        exrFilePath = (jobFrame)
        name = (exrName[current2])
        # Open image in blender
        img = bpy.ops.image.open(filepath=exrFilePath, directory=rootDirectory, files=[{"name":(name), "name":(name)}], show_multiview=False)
        # Loading image in the current imgNode
        imgNode.image = bpy.data.images[(name[:63])]
        # Getting the image resolution
        imgResolution = imgNode.image.size[:]
        # Avoiding node overlay if you need to see it as in the Blender GUI 
        imgNode.location = 0, nodePosOffset
        nodePosOffset += 300
        current2 += 1
        
    # Setting the image resolution
    print("Image resolution is : " + str(imgResolution[0]) + " by " + str(imgResolution[1]))
    bpy.context.scene.render.resolution_x = (imgResolution[0])
    bpy.context.scene.render.resolution_y = (imgResolution[1])
    bpy.context.scene.render.resolution_percentage = 100


    #Shot_Shape20_masterLayer_SET_LGT_beauty_EnvMain_filtered.0105.e

    # Linking each image node to the ouput node
    links = tree.links
    current = 0

    for i in jobExrPath:
        link = links.new(imgNodeList[current].outputs[0], outputNode.inputs[current])
        current += 1
    
    # Setting the correct frame
    bpy.context.scene.frame_current = int(jobFrame)


    # Rendering    
    bpy.ops.render.render(write_still=True)

    # returning exrOutToCheck if it exists
    exrOut = outputStr + jobFrame + ".exr"
    return(exrOut)


    


if __name__ == "__main__":
    main()