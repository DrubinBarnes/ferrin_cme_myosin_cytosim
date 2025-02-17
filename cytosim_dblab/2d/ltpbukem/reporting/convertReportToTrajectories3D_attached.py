
import os 
import numpy as np
import subprocess
from glob import glob
import scipy
import csv

# move to the "Report" folder (e.g. for this particular expt)
# should have a list of text files

# can directly report here in one script (or a function...).

## run "reportFiberProperties.py" or make a function version with one input as "reportFolder".
## and run "reportMultiple3D_current.py"


# choose which objects to report.

reportSingle   = 1
reportArp      = 1
reportClusters = 1
reportFiber    = 1
reportFiberEnds = 1

dimensions = 3
# this is for 3D. getting the Z position.

import sys

if len(sys.argv)>1:
    reportFolder = sys.argv[1]

else:
    reportFolder = 'spin90_x30_output'


reportPath = '/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/'+reportFolder

# first imort hip1R-bound singles
## import the hip1R info, including the list of which filaments are bound to hip1R over time. as a list of some kind.

if reportSingle == 1:

    os.chdir(reportPath+'/single/')

    myDir = os.getcwd()

    # get the parent path and the folder current name.

    (pathBeg, folderName) = os.path.split(myDir)

    # find the Hip1R-bound files

    hip1RFiles = glob('*hip1RPosition*')

    allDistances = {}
    allTimes = {}
    allBoundHip1RperTime={} # number bound Hip1R vs time
    allBoundSinglePerTime={} # number bound Hip1R vs time
    allArpInsideCylinderPerTime = {}
    allArpAngles = {}
    # distribution of branch angles (fim or arp) at last time point each simulation.
    branchAnglesLastTimepoint = {}

    eachArpAngle = []
    lastArpAnglesDegrees = []
    n = 0

    # z0 = -0.4  # resting equilibrium position of the bead. it may start further in.

    # initialize

    curClassNbs = []
    curSingleIDs = []
    curBoundStates = []

    curXs = []
    curYs = []
    curZs = []

    curHip1RForcesX = []
    curHip1RForcesY = []
    curHip1RForcesZ = []

    curHip1RboundFilamentIDs = []
    curHip1RboundFilamentDirXs = []
    curHip1RboundFilamentDirYs = []
    curHip1RboundFilamentDirZs = []
    curHip1RboundFilament_Distances_Attachment_PlusEnd = []

    curHip1RboundFilamentDirFromPlusEndXs = []
    curHip1RboundFilamentDirFromPlusEndYs = []
    curHip1RboundFilamentDirFromPlusEndZs = []

    for textFile in hip1RFiles:

        # open file
        datafile = open(textFile, 'r')


        frames = []
        times  = []

       # Go through each line and filter for whether it's a new time point or a new object (protein).

        for line in datafile:
            line = line.strip()
            if line.startswith('% frame'):
                curFrame = int(line[8:])
                frames.append(int(line[8:]))
                # reset list for each time point (marked by #)

                curClassNbs = []
                curSingleIDs = []
                curBoundStates = []

                curXs = []
                curYs = []
                curZs = []

                curHip1RForcesX = []
                curHip1RForcesY = []
                curHip1RForcesZ = []

                curHip1RboundFilamentIDs = []
                curHip1RboundFilamentDirXs = []
                curHip1RboundFilamentDirYs = []
                curHip1RboundFilamentDirZs = []
                curHip1RboundFilament_Distances_Attachment_PlusEnd = []
                curHip1RboundFilamentDirFromPlusEndXs = []
                curHip1RboundFilamentDirFromPlusEndYs = []
                curHip1RboundFilamentDirFromPlusEndZs = []

            if line.startswith('% time'):
                # add time information
                times.append(float(line[7:]))

            if line.startswith('%'):
                ()
            elif len(line)==0:
                ()
            else:
                sline = line.split()

                curClass   = int(sline[0])
                curID      = int(sline[1])
                boundState = int(sline[2])

                curX = float(sline[3])
                curY = float(sline[4])
                curZ = float(sline[5])

                curForceX = float(sline[6])
                curForceY = float(sline[7])
                curForceZ = float(sline[8])

                if boundState == 1:
                    curHip1RBoundFilamentID   = float(sline[9])
                    curHip1RboundFilamentDirX = float(sline[10])
                    curHip1RboundFilamentDirY = float(sline[11])
                    curHip1RboundFilamentDirZ = float(sline[12])
                    # Abscissa (PLUS_END) which seems to be distance between attachment site and plus end.
                    curHip1RboundFilament_Distance_Attachment_PlusEnd = float(sline[14])
                    curHip1RboundFilamentDirFromPlusEndX = float(sline[15])
                    curHip1RboundFilamentDirFromPlusEndY = float(sline[16])
                    curHip1RboundFilamentDirFromPlusEndZ = float(sline[17])
                else:
                    curHip1RBoundFilamentID   = float('nan')
                    curHip1RboundFilamentDirX = float('nan')
                    curHip1RboundFilamentDirY = float('nan')
                    curHip1RboundFilamentDirZ = float('nan')
                    curHip1RboundFilament_Distance_Attachment_PlusEnd = float('nan')
                    curHip1RboundFilamentDirFromPlusEndX = float('nan')
                    curHip1RboundFilamentDirFromPlusEndY = float('nan')
                    curHip1RboundFilamentDirFromPlusEndZ = float('nan')
                    # can make this a loop for all the singles. or a library?

                curClassNbs.append(curClass)
                curSingleIDs.append(curID)
                curBoundStates.append(boundState)

                curXs.append(curX)
                curYs.append(curY)
                curZs.append(curZ)

                curHip1RForcesX.append(curForceX)
                curHip1RForcesY.append(curForceY)
                curHip1RForcesZ.append(curForceZ)

                curHip1RboundFilamentIDs.append(curHip1RBoundFilamentID)
                curHip1RboundFilamentDirXs.append(curHip1RboundFilamentDirX)
                curHip1RboundFilamentDirYs.append(curHip1RboundFilamentDirY)
                curHip1RboundFilamentDirZs.append(curHip1RboundFilamentDirZ)

                curHip1RboundFilament_Distances_Attachment_PlusEnd.append(curHip1RboundFilament_Distance_Attachment_PlusEnd)

                curHip1RboundFilamentDirFromPlusEndXs.append(curHip1RboundFilamentDirFromPlusEndX)
                curHip1RboundFilamentDirFromPlusEndYs.append(curHip1RboundFilamentDirFromPlusEndY)
                curHip1RboundFilamentDirFromPlusEndZs.append(curHip1RboundFilamentDirFromPlusEndZ)

            if line.startswith('% end'):
                # make a text file for each time point
                hip1RinfoCurrentTimept = np.array(
                    [curClassNbs, curSingleIDs, curBoundStates, curXs, curYs, curZs, curHip1RForcesX, curHip1RForcesY, curHip1RForcesZ, curHip1RboundFilamentIDs,
                     curHip1RboundFilamentDirXs, curHip1RboundFilamentDirYs, curHip1RboundFilamentDirZs, curHip1RboundFilament_Distances_Attachment_PlusEnd, curHip1RboundFilamentDirFromPlusEndXs, curHip1RboundFilamentDirFromPlusEndYs, curHip1RboundFilamentDirFromPlusEndZs])
                # would be nicer as a table to prevent indexing errors. or print a legend for good measure

                np.savetxt(pathBeg + '/' + str(folderName) + '/' + str(reportFolder) + '_hip1R_sim' + str(n).zfill(3) + 'frame' + str(curFrame).zfill(3) + '.txt', hip1RinfoCurrentTimept)


        print(textFile)
        print(str(n))
        hip1RinfoLegend = ('Class_number', 'single_ID', 'bound_state', 'X', 'Y', 'Z', 'forceX', 'forceY', 'forceZ', 'boundFilament_ID', 'boundFilament_dirX', 'boundFilament_dirY', 'boundFilament_dirZ', 'boundFilament_abscissa_PlusEnd', 'boundFilament_DirFromPlusEndX', 'boundFilament_DirFromPlusEndY', 'boundFilament_DirFromPlusEndZ')
        myFile1 = open('hip1RLegend.txt', 'w')
        for item in hip1RinfoLegend:
            myFile1.write("%s \n" % item)
        myFile1.close()

        # hip1RinfoLegend = np.array('Class_number single_ID' 'bound_state' 'X' 'Y' 'Z' 'forceX' 'forceY' 'forceZ' 'boundFilament_ID' 'boundFilament_dirX' 'boundFilament_dirY' 'boundFilament_dirZ''')
        # I could write this to file... fornow I'll just ocpy it over to matlab and notes.
        # np.savetxt(pathBeg + '/' + str(folderName) + 'hip1R_legend.txt', hip1RinfoLegend)

        n = n + 1

# Arp angle, position

n = 0

if reportArp == 1:

    os.chdir(reportPath + '/Arp/')

    myDir = os.getcwd()

    # get the parent path and the folder current name.

    (pathBeg, folderName) = os.path.split(myDir)

    # find the Hip1R-bound files

    arpAngleFiles = glob('*ArpBranchAngle*')
    arpPosFiles = glob('*ArpPositionAngle*')

    eachArpAngle = []
    lastArpAnglesDegrees = []
    n = 0

    # z0 = -0.4  # resting equilibrium position of the bead. it may start further in.

    # initialize

    curArpClasses = []
    curArpIDs = []
    curBoundFiber1IDs = []
    curBoundDistancesAlongFiber1 = []
    curBoundFiber2IDs = []
    curArpAngles = []

    for textFile in arpAngleFiles:

        # open file
        datafile = open(textFile, 'r')

        frames = []
        times = []

        # Go through each line and filter for whether it's a new time point or a new object (protein).

        for line in datafile:
            line = line.strip()
            if line.startswith('% frame'):
                curFrame = int(line[8:])
                frames.append(int(line[8:]))
                # reset list for each time point (marked by #)


                curArpClasses = []
                curArpIDs = []
                curBoundFiber1IDs = []
                curBoundDistancesAlongFiber1 = []
                curBoundFiber2IDs = []
                curBoundDistancesAlongFiber2 = []
                curArpAngles = []

            if line.startswith('% time'):
                # add time information
                times.append(float(line[7:]))

            if line.startswith('%'):
                ()
            elif len(line) == 0:
                ()
            else:
                sline = line.split()

                curClass = int(sline[0])
                curArpID = int(sline[1])
                boundFiber1ID = int(sline[2])
                boundDistanceAlongFiber1 = float(sline[3])
                boundFiber2ID = int(sline[4])
                boundDistanceAlongFiber2 = float(sline[5])

                curArpAngle = float(sline[6]) # in cosTheta

                # add to current list for this time point of (cosine of) branch angles

                curArpClasses.append(curClass)
                curArpIDs.append(curArpID)
                curBoundFiber1IDs.append(boundFiber1ID)
                curBoundDistancesAlongFiber1.append(boundDistanceAlongFiber1)
                curBoundFiber2IDs.append(boundFiber2ID)
                curBoundDistancesAlongFiber2.append(boundDistanceAlongFiber2)
                curArpAngles.append(curArpAngle)

                ## will need to set for different classes if there is more than one couple saved.


            if line.startswith('% end'):
                # make a text file for each time point
                arpBranchInfoCurrentTimept = np.array([curArpClasses, curArpIDs, curBoundFiber1IDs, curBoundDistancesAlongFiber1, curBoundFiber2IDs, curBoundDistancesAlongFiber2, curArpAngles])

                # would be nicer as a table to prevent indexing errors. printing a legend for good measure

                np.savetxt(
                    pathBeg + '/' + str(folderName) + '/' + str(reportFolder) + '_Arp23Branches_sim' + str(n).zfill(
                        3) + 'frame' + str(curFrame).zfill(3) + '.txt', arpBranchInfoCurrentTimept)

        print(textFile)
        print(str(n))
        arpInfoLegend = (
        'Class_number', 'arp_ID', 'fiber1_bound_ID', 'fiber1_abscissa', 'fiber2_bound_ID', 'fiber2_abscissa', 'arpAngleCos')
        myFile3 = open('arpInfoLegend.txt', 'w')
        for item in arpInfoLegend:
            myFile3.write("%s \n" % item)
        myFile3.close()

        n = n + 1

## arp position.

n = 0

if reportArp == 1:

    os.chdir(reportPath + '/Arp/')

    myDir = os.getcwd()

    # get the parent path and the folder current name.

    (pathBeg, folderName) = os.path.split(myDir)

    # find the Hip1R-bound files

    # arpAngleFiles = glob('*ArpBranchAngle*')
    arpPosFiles = glob('*ArpPosition*')

    eachArpAngle = []
    lastArpAnglesDegrees = []
    n = 0

    # z0 = -0.4  # resting equilibrium position of the bead. it may start further in.

    # initialize

    curArpClasses = []
    curArpIDs = []
    curBoundFiber1IDs = []
    curBoundDistancesAlongFiber1 = []
    curBoundFiber2IDs = []
    curArpAngles = []

    for textFile in arpPosFiles:

        # open file
        datafile = open(textFile, 'r')

        frames = []
        times = []

        # Go through each line and filter for whether it's a new time point or a new object (protein).

        for line in datafile:
            line = line.strip()
            if line.startswith('% frame'):
                curFrame = int(line[8:])
                frames.append(int(line[8:]))
                # reset list for each time point (marked by #)


                curArpClasses = []
                curArpIDs = []
                curBoundStates1 = []
                curBoundStates2 = []
                curArpXs = []
                curArpYs = []
                curArpZs = []

            if line.startswith('% time'):
                # add time information
                times.append(float(line[7:]))

            if line.startswith('%'):
                ()
            elif len(line) == 0:
                ()
            else:
                sline = line.split()

                curClass = int(sline[0])
                curArpID = int(sline[1])
                curBoundState1 = int(sline[2])
                curBoundState2 = int(sline[3])
                curArpX = float(sline[4])
                curArpY = float(sline[5])
                curArpZ = float(sline[6])

                # add to current list for this time point of (cosine of) branch angles

                curArpClasses.append(curClass)
                curArpIDs.append(curArpID)
                curBoundStates1.append(curBoundState1)
                curBoundStates2.append(curBoundState2)
                curArpXs.append(curArpX)
                curArpYs.append(curArpY)
                curArpZs.append(curArpZ)

                ## will need to set for different classes if there is more than one couple saved.


            if line.startswith('% end'):
                # make a text file for each time point
                arpPositionInfoCurrentTimept = np.array([curArpClasses, curArpIDs, curBoundStates1, curBoundStates2, curArpXs, curArpYs, curArpZs])

                # would be nicer as a table to prevent indexing errors. printing a legend for good measure

                np.savetxt(
                    pathBeg + '/' + str(folderName) + '/' + str(reportFolder) + '_Arp23Position_sim' + str(n).zfill(
                        3) + 'frame' + str(curFrame).zfill(3) + '.txt', arpPositionInfoCurrentTimept)

        print(textFile)
        print(str(n))
        arpInfoLegend = (
        'Class_number', 'arp_ID', 'bindingState1', 'bindingState2', 'arpX', 'arpY', 'arpZ')
        myFile4 = open('arpPosLegend.txt', 'w')
        for item in arpInfoLegend:
            myFile4.write("%s \n" % item)
        myFile4.close()

        n = n + 1


## clusters
n = 0
os.chdir(reportPath + '/Fiber/')

myDir = os.getcwd()

# get the parent path and the folder current name.

(pathBeg, folderName) = os.path.split(myDir)

# find the Hip1R-bound files

clusterFiles = glob('*FiberClusters*')

for textFile in clusterFiles:

    # open file
    datafile = open(textFile, 'r')

    if reportClusters == 1:
        print('found a cluster file')

        frames = []
        times = []

        # Go through each line and filter for whether it's a new time point or a new object (protein).

        # initalize
        curNbFibers = []
        curFiberNumbers = []
        clusterIDsTimept = []
        nbFibersTimept = []
        fiberNumbersTimept = []

        for line in datafile:
            line = line.strip()
            if line.startswith('%'):
                ()
            elif len(line) == 0:
                ()
            else:
                sline = line.split()
                curClusterID = int(sline[0])
                curNbFibers = int(sline[1])
                # sline[2] sould be a colon
                curFiberNumbers = sline[3:]

                clusterIDsTimept.append(curClusterID)
                nbFibersTimept.append(curNbFibers)
                fiberNumbersTimept.append(curFiberNumbers)  # will this work bc lists different size?

            if line.startswith('% frame'):
                curFrame = int(line[8:])
                print(curFrame)
                frames.append(int(line[8:]))
                #                reset per-timpoint values at each new time point (marked by %)
                clusterIDsTimept = []
                nbFibersTimept = []
                fiberNumbersTimept = []

            if line.startswith('% time'):
                times.append(float(line[7:]))

            if line.startswith('% end'):  # save each timept as a text file.

                # save cluster numbers for each time point.
                # this could probably be one matrix with NaNs in the gaps.

                clusterFile = open('clusterIDs_sim'+str(n).zfill(3)+'frame'+str(curFrame).zfill(3)+'.txt', 'w')
                for item in clusterIDsTimept:
                    clusterFile.write("%s \n" % item)

                # write it to a file
                myFile = open('filamentIDsInCluster_sim'+str(n).zfill(3)+'frame'+str(curFrame).zfill(3)+'.txt', 'w')
                for item in fiberNumbersTimept:
                    myFile.write("%s \n" % item)
                    # myFile.write(item '\n')

                # clusterInfoCurrentTimept = np.array([clusterIDsTimept, fiberNumbersTimept])

                # would be nicer as a table to prevent indexing errors. or print a legend for good measure

                # np.savetxt(pathBeg + '/' + str(reportFolder) + '_clusters_sim' + str(n).zfill(3) + 'frame' + str(curFrame).zfill(3) + '.txt', clusterInfoCurrentTimept)

        myFile.close()
        clusterFile.close()
        # print(textFile)
        # print(str(n))
        # hip1RinfoLegend = (
        # 'Class_number single_ID bound_state X Y Z forceX forceY forceZ boundFilament_ID boundFilament_dirX boundFilament_dirY boundFilament_dirZ')
        # hip1RinfoLegend = np.array('Class_number single_ID' 'bound_state' 'X' 'Y' 'Z' 'forceX' 'forceY' 'forceZ' 'boundFilament_ID' 'boundFilament_dirX' 'boundFilament_dirY' 'boundFilament_dirZ''')
        # I could write this to file... fornow I'll just ocpy it over to matlab and notes.
        # np.savetxt(pathBeg + '/' + str(folderName) + 'hip1R_legend.txt', hip1RinfoLegend)

        n = n + 1

## fiber prop

# reportPath = '/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/crosslinking_lengths_endo'
#
# os.chdir(reportPath + '/Fiber/')
#
# myDir = os.getcwd()

# get the parent path and the folder current name.

# (pathBeg, folderName) = os.path.split(reportPath)

reportFiles = glob('*FiberProp*')

#target class. right now 0 is actin.

targetFiberClass = 0

#
# allDistances = {}
# allTimes = {}
# allBoundHip1RperTime = {}  # number bound Hip1R vs time
# allLengths = {}
#
# allNetForces = {}
# allForcesMagnitude = {}
#
# allFiberEndNumbers = {}
# allFiberLengths = {}
#
# allFiberXs = {}
# allFiberYs = {}
# allFiberZs = {}
#
# allFiberDirectionsX = {}
# allFiberDirectionsY = {}
# allFiberDirectionsZ = {}
#
# allFiberEndXs = {}
# allFiberEndYs = {}
# allFiberEndZs = {}
#
# allFiberEndDirectionsX = {}
# allFiberEndDirectionsY = {}
# allFiberEndDirectionsZ = {}
#
# allFiberEndForcesX = {}
# allFiberEndForcesY = {}
# allFiberEndForcesZ = {}
#
# allMeanFilamentLengths = {}
# allStdFilamentLengths = {}
#
# allLastTimeptFilamentLengths = {}
n = 0  # for fiberProp

if reportFiber == 1:

    for textFile in reportFiles:

        # open file
        datafile = open(textFile, 'r')
        if 'FiberProp' in textFile:
            print('found a FiberProp file')
            print(textFile)
            frames = []
            times = []
            fiberXs = {}
            fiberYs = {}
            fiberZs = {}
            fiberLengths = {}
            fiberDirectionsX = {}
            fiberDirectionsY = {}
            fiberDirectionsZ = {}

            # meanFilamentLengths = []
            # stdFilamentLengths = []

            for line in datafile:
                line = line.strip()
                if line.startswith('% frame'):
                    curFrame = int(line[8:])
                    frames.append(int(line[8:]))
                    #                reset per-timpoint values at each new time point (marked by %)

                    curFiberNumbers = []
                    curFiberLengths = []
                    curFibersX = []
                    curFibersY = []
                    curFibersZ = []
                    curDirectionsX = []
                    curDirectionsY = []
                    curDirectionsZ = []

                if line.startswith('% time'):
                    times.append(float(line[7:]))

                if line.startswith('%'):
                    ()
                elif len(line) == 0:
                    ()
                else:
                    sline = line.split()
                    curClassID = int(sline[0])
                    curFiberNumber = int(sline[1])
                    curLength = float(sline[2])

                    curFiberX = float(sline[3])
                    curFiberY = float(sline[4])

                    if dimensions == 3:
                        curFiberZ = float(sline[5])
                        curDirectionX = float(sline[6])
                        curDirectionY = float(sline[7])
                        curDirectionZ = float(sline[8])
                    elif dimensions == 2:  # haven't tested 2D yet
                        curDirectionX = float(sline[5])
                        curDirectionY = float(sline[6])

                    # store the data JUST for the target fiber class (usually actin)
                    if curClassID == targetFiberClass:
                        curFiberNumbers.append(curFiberNumber)
                        curFiberLengths.append(curLength)
                        curFibersX.append(curFiberX)
                        curFibersY.append(curFiberY)
                        curDirectionsX.append(curDirectionX)
                        curDirectionsY.append(curDirectionY)
                        if dimensions == 3:
                            curFibersZ.append(curFiberZ)
                            curDirectionsZ.append(curDirectionZ)

                if line.startswith('% end'):# sum up and save text file for each time point.
                    ()
                    fiberinfoCurrentTimept = np.array([curFiberNumbers, curFiberLengths, curFibersX, curFibersY, curFibersZ, curDirectionsX, curDirectionsY, curDirectionsZ])

                    np.savetxt(pathBeg + '/' + str(folderName) + '/' + str(reportFolder) + '_fibers_sim' + str(n).zfill(3) + 'frame' + str(curFrame).zfill(3) + '.txt', fiberinfoCurrentTimept)
        print(str(n))
        n = n + 1

    # write legend
    fiberLegend = ['fiberNumber', 'fiberLength', 'FiberX', 'FiberY', 'fiberZ', 'fiberDirectionX', 'fiberDirectionY', 'fiberDirectionZ']

    myFile = open('fiberLegend.txt', 'w')
    for item in fiberLegend:
        myFile.write("%s \n" % item)
    myFile.close()
    # would be nicer as a table to prevent indexing errors. or print a legend for good measure

    # fiberLengths['frame' + str(curFrame).zfill(3)] = curFiberLengths
                    # fiberXs['frame' + str(curFrame).zfill(3)] = curFibersX
                    # fiberYs['frame' + str(curFrame).zfill(3)] = curFibersY
                    # fiberDirectionsX['frame' + str(curFrame).zfill(3)] = curDirectionsX
                    # fiberDirectionsY['frame' + str(curFrame).zfill(3)] = curDirectionsY
                    #
                    # meanFilamentLength = np.mean(curFiberLengths)
                    # stdFilamentLength = np.std(curFiberLengths)
                    #
                    # meanFilamentLengths.append(meanFilamentLength)
                    # stdFilamentLengths.append(stdFilamentLength)
                    #
                    # if dimensions == 3:
                    #     fiberZs['frame' + str(curFrame).zfill(3)] = curFibersZ
                    #     fiberDirectionsZ['frame' + str(curFrame).zfill(3)] = curDirectionsZ

            # allTimes['sim' + str(n).zfill(3)] = times
            # allFiberLengths['sim' + str(n).zfill(3)] = fiberLengths
            # allFiberXs['sim' + str(n).zfill(3)] = fiberXs
            # allFiberYs['sim' + str(n).zfill(3)] = fiberYs
            # allFiberZs['sim' + str(n).zfill(3)] = fiberZs
            # allFiberDirectionsX['sim' + str(n).zfill(3)] = fiberDirectionsX
            # allFiberDirectionsY['sim' + str(n).zfill(3)] = fiberDirectionsY
            # allFiberDirectionsZ['sim' + str(n).zfill(3)] = fiberDirectionsZ
            #
            # allMeanFilamentLengths['sim' + str(n).zfill(3)] = meanFilamentLengths
            # allStdFilamentLengths['sim' + str(n).zfill(3)] = stdFilamentLengths
            #
            # allLastTimeptFilamentLengths['sim' + str(n).zfill(3)] = curFiberLengths





## fiber ends

reportFiles = glob('*FiberEnds*')

#target class. right now 0 is actin.

targetFiberClass = 0
m = 0 # for fiberEnds

fiberEndLegend = ['fiberNumber', 'fiberPlusEndState', 'FiberPlusEndX', 'FiberPlusEndY', 'fiberPlusEndZ', 'fiberPlusEndDirectionX', 'fiberPlusEndDirectionY', 'fiberPlusEndDirectionZ']

if reportFiberEnds == 1:

    for textFile in reportFiles:

        # open file
        datafile = open(textFile, 'r')
        # if 'FiberEnds' in textFile:
        #     print('found a FiberEnds file')
        print(textFile)
        frames = []
        times = []
        # fiberXs = {}
        # fiberYs = {}
        # fiberZs = {}
        # fiberLengths = {}
        # fiberDirectionsX = {}
        # fiberDirectionsY = {}
        # fiberDirectionsZ = {}

        # Note: here I am reporting for PLUS end of fiber.
        # try to just reset the relevant variables
        frames = []
        times = []
        fiberEndNumbers = {}
        fiberXs = {}
        fiberYs = {}
        fiberZs = {}
        fiberLengths = {}
        fiberDirectionsX = {}
        fiberDirectionsY = {}
        fiberDirectionsZ = {}

        # meanFilamentLengths = []
        # stdFilamentLengths = []

        for line in datafile:
            line = line.strip()
            if line.startswith('% frame'):
                curFrame = int(line[8:])
                frames.append(int(line[8:]))
                #                reset per-timpoint values at each new time point (marked by %)
                curFiberEndNumbers = []
                curFiberEndsX = []
                curFiberEndsY = []
                curFiberEndsZ = []
                curDirectionEndsX = []
                curDirectionEndsY = []
                curDirectionEndsZ = []
                curFiberPlusEndStates = []
            # curFiberLengths = []

            if line.startswith('% time'):
                times.append(float(line[7:]))

            if line.startswith('%'):
                ()
            elif len(line) == 0:
                ()
            else:
                sline = line.split()
                curClassID = int(sline[0])
                curFiberEndNumber = int(sline[1])
                # this is for PLUS end.
                curFiberPlusEndState = float(sline[10])
                if dimensions == 3:
                    curFiberEndX = float(sline[11])
                    curFiberEndY = float(sline[12])
                    curFiberEndZ = float(sline[13])
                    curDirectionEndX = float(sline[14])
                    curDirectionEndY = float(sline[15])
                    curDirectionEndZ = float(sline[16])
                elif dimensions == 2:  # haven't tested 2D yet
                        curFiberEndX = float(sline[9])
                        curFiberEndY = float(sline[10])
                        curDirectionEndX = float(sline[11])
                        curDirectionEndY = float(sline[12])

                if curClassID == targetFiberClass:
                    #                        curFiberLengths.append(curLength)
                    curFiberEndNumbers.append(curFiberEndNumber)
                    curFiberPlusEndStates.append(curFiberPlusEndState)
                    curFiberEndsX.append(curFiberEndX)
                    curFiberEndsY.append(curFiberEndY)
                    curDirectionEndsX.append(curDirectionEndX)
                    curDirectionEndsY.append(curDirectionEndY)
                    if dimensions == 3:
                        curFiberEndsZ.append(curFiberEndZ)
                        curDirectionEndsZ.append(curDirectionEndZ)
                        #                allTimes['sim'+str(n).zfill(3)]=times
                        #                allFiberLengths['sim'+str(n).zfill(3)]=fiberLengths
            if line.startswith('% end'):  # sum up the prev meanYs.
                ()
                # Here I could make a dictionary of all the time points and all the simulations.
                # for now I'm exporting each time point as a text file.
                #                        fiberLengths['frame'+str(curFrame).zfill(3)] = curFiberLengths
                # fiberXs['frame' + str(curFrame).zfill(3)] = curFibersX
                # fiberYs['frame' + str(curFrame).zfill(3)] = curFibersY
                # fiberDirectionsX['frame' + str(curFrame).zfill(3)] = curDirectionsX
                # fiberDirectionsY['frame' + str(curFrame).zfill(3)] = curDirectionsY
                # fiberEndNumbers['frame' + str(curFrame).zfill(3)] = curFiberNumbers
                #                        meanFilamentLength=np.mean(curFiberLengths)
                #                        stdFilamentLength = np.std(curFiberLengths)

                #                        meanFilamentLengths.append(meanFilamentLength)
                #                        stdFilamentLengths.append(stdFilamentLength)

                if dimensions == 3:
                    # fiberZs['frame' + str(curFrame).zfill(3)] = curFibersZ
                    # fiberDirectionsZ['frame' + str(curFrame).zfill(3)] = curDirectionsZ

               # fiberEndsinfoTable = np.array([fiberEndLegend, np.transpose(curFiberEndNumbers), np.transpose(curFiberPlusEndStates)])
                    # fiberEndsinfoTable = np.array(['fiberNumber', curFiberEndNumbers], ['plusEndState', curFiberPlusEndStates])

                    # , curFiberEndsX, curFiberEndsY, curFiberEndsZ, curDirectionEndsX, curDirectionEndsY, curDirectionEndsZ])])
                    # fiberEndsinfoTable = np.array([curFiberEndNumbers, curFiberPlusEndStates, curFiberEndsX, curFiberEndsY, curFiberEndsZ, curDirectionEndsX, curDirectionEndsY, curDirectionEndsZ])

                    # add legend
                    # newFiberEndsinfoTable = np.insert(fiberEndsinfoTable, 1, fiberEndLegend, axis=1)

                    ## this legend (determined above) needs to be the same order as the rest of the array in the following table!

                    # fiberEndLegend =                     ['fiberNumber', 'fiberPlusEndState', 'FiberPlusEndX', 'FiberPlusEndY', 'fiberPlusEndZ', 'fiberPlusEndDirectionX', 'fiberPlusEndDirectionY', 'fiberPlusEndDirectionZ']

                    fiberEndsinfoCurrentTimept = np.array([curFiberEndNumbers, curFiberPlusEndStates, curFiberEndsX, curFiberEndsY, curFiberEndsZ, curDirectionEndsX, curDirectionEndsY, curDirectionEndsZ])
                    np.savetxt(pathBeg + '/' + str(folderName) + '/' + str(reportFolder) + '_fiberEnds_sim' + str(m).zfill(3) + 'frame' + str(curFrame).zfill(3) + '.txt', fiberEndsinfoCurrentTimept)
                    # myFile2 = open('fiberEndInfo.txt', 'w')
                    # for item in fiberEndsinfoTable:
                    #     myFile2.write("%s \n" % item)
                    # myFile2.close()
                    # with open('test_file.csv', 'w') as csvfile:
                    #     writer = csv.writer(csvfile)
                    #     [writer.writerow(r) for r in fiberEndsinfoTable]
        # allFiberEndNumbers['sim' + str(m).zfill(3)] = fiberEndNumbers
        # allFiberEndXs['sim' + str(m).zfill(3)] = fiberXs
        # allFiberEndYs['sim' + str(m).zfill(3)] = fiberYs
        # allFiberEndZs['sim' + str(m).zfill(3)] = fiberZs
        # allFiberEndDirectionsX['sim' + str(m).zfill(3)] = fiberDirectionsX
        # allFiberEndDirectionsY['sim' + str(m).zfill(3)] = fiberDirectionsY
        # allFiberEndDirectionsZ['sim' + str(m).zfill(3)] = fiberDirectionsZ
        # advance to next simulation

        print(str(m))
        m = m + 1


# fiberEndLegend = ['fiberNumber', 'fiberPlusEndState', 'FiberPlusEndX', 'FiberPlusEndY', 'fiberPlusEndZ', 'fiberPlusEndDirectionX', 'fiberPlusEndDirectionY', 'fiberPlusEndDirectionZ']
#
# # fiberEndLegend = ['fiberNumber', 'FiberPlusEndX', 'FiberPlusEndY', 'fiberPlusEndZ', 'fiberPlusEndDirectionX', 'fiberPlusEndDirectionY', 'fiberPlusEndDirectionZ']
#
myFile2 = open('fiberEndLegend.txt', 'w')
for item in fiberEndLegend:
    myFile2.write("%s \n" % item)
myFile2.close()
# for m in range(0, n):
#     np.savetxt(pathBeg + '/' + str(folderName) + 'singlesBoundVsTime_sim' + str(m).zfill(3) + '.txt', allBoundSinglePerTime['sim' + str(m).zfill(3)])
print('made it')

# import cluster info, make a running list over time of which filaments are in what cluster.

# import fiber info (this should be below?) and report length_filametns.

# import fiberEnd info (this is below already), get dir and position of plus end.



#     elif 'ArpBranchAngle' in textFile:
#         print('found an ArpsBranchAngle file')
#
# # clear the variables you're going to append versus timepoint
#         frames = []
#         meanArpAngleVsTime = []
#         stdArpAngleVsTime  = []
#         times = []
#         curClass = [] # initialize it
#         for line in datafile:
#             line = line.strip()
#             if line.startswith('%'):
#                 if line.startswith('% frame'):
#                     curframe = int(line[8:])
#                     frames.append(int(line[8:]))
#                     curArpAngles = [] # reset arp angle time point (marked by #)
#
#                 if line.startswith('% time'):
#                     times.append(float(line[7:]))
#                 if line.startswith('% end'): # sum up the prev meanYs.
#                     # sline = line.split()
#                     # just save for the current protein (fimbrin or arp)
#                     if curClass==bridgeClass:
#
#                         # calculate angles for this timepoint in radian
#
#                         curArpAnglesRadian = np.arccos(curArpAngles)
#
#                         # convert radian to degrees
#
#                         curArpAnglesDegrees  = np.degrees(curArpAnglesRadian)
#                         lastArpAnglesDegrees = []
#                         lastArpAnglesDegrees = curArpAnglesDegrees
#     #                    eachArpAngle.append(curArpAnglesDegrees)
#
#                         # calculate mean branch angle at this tme point (defined here for degrees)
#
#                         meanArpAngleCurrentTimepoint=np.mean(curArpAnglesDegrees,axis=0)
#                         meanArpAngleVsTime.append(meanArpAngleCurrentTimepoint)
#                         # calculate std branch angle at this time point
#
#                         stdArpAngleCurrentTimepoint = np.std(curArpAnglesDegrees,axis=0)
#                         stdArpAngleVsTime.append(stdArpAngleCurrentTimepoint)
#
#                         # store all the branch angles in a dictionary (for a given experiment) (defined here for degrees)
#
#                         allArpAngles['time'+str(curframe).zfill(3)] = curArpAnglesDegrees
#
#
#             elif len(line)==0:
#         #        print('break')
#                 ()
#             else:
#                 sline = line.split()
#                 curClass = int(sline[0])
#
#                # print(sline[1])
#                 # branch angle (as a cosine value) for an individual arp (defined as a bridge)
#                 curArpAngle = float(sline[6])
#
#                 # add to current list for this time point of (cosine of) branch angles
#                 curArpAngles.append(curArpAngle)
#                 # every arp angle (including multipl)
#                 eachArpAngle.append(curArpAngle)
#
        # eachArpAngleDegrees = np.degrees(np.arccos(eachArpAngle))
        # branchAngleLastTimepoint=np.degrees(np.arccos(curArpAngles))
        # eachArpAngleDegrees = np.degrees(np.arccos(eachArpAngle))
        # branchAngleLastTimepoint=lastArpAnglesDegrees

    # if reportArpPosition>0:
    #     allDistances['sim'+str(n)]=meanZperTime

#    
#    if 'ArpPosition' in  textFile:
#        allArpInsideCylinderPerTime['sim'+str(n)]=arpInsideCylinderPerTime
#        print('found an ArpsPosition file')
#    else:
#    # here I could add the status of wheter each hip1R is bound or not. (to correlate with position over time)    
#        allBoundHip1RperTime['sim'+str(n)]=boundHip1RperTime



# save bound over time




# save distribution of branch angles at last time point each simulation

# currently protein0 is fimbrin, protein1 is arp.
# m = 0

    # m=m+1


# caluclate meana nd std

# if reportArpPosition>0:
#     distancesArray=allDistances.values()
#     #allBoundHip1RArray = allBoundHip1RperTime.values()
#     allArpInsideCylinderPeTimeArray=allArpInsideCylinderPerTime.values()
#
#     # remove simluations that didn't finish.
#     n=0
#     allLengths=[]
#     for line in distancesArray:
#         allLengths.append(len(line))
#         n=n+1
#     maxTimeLength = max(allLengths)
    
    # n=0
    # fullDistancesArray = []
    # nbBoundVsTime = []
    # for line in distancesArray:
    #     if(len(line)==maxTimeLength):
    #         fullDistancesArray.append(line)
    #         n=n+1
    #
    # n=0
    # fullBoundHip1RArray =[]
    # for line in allBoundHip1RArray:
    #         if(len(line)==maxTimeLength):
    #             fullBoundHip1RArray.append(line)
    #             n=n+1
    #
    # n=0
    #
    # fullArpInsideCylinderpPerTimeArray =[]
    # for line in allArpInsideCylinderPeTimeArray:
    #         if(len(line)==maxTimeLength):
    #             fullArpInsideCylinderpPerTimeArray.append(line)
    #             n=n+1
    #
    #
    # meanBoundHip1RvsTime=np.mean(fullBoundHip1RArray,axis=0)
    # stdBoundHip1RvsTime=np.std(fullBoundHip1RArray,axis=0)
    #
    # meanArpInsideCylinderPerTime=np.mean(fullArpInsideCylinderpPerTimeArray, axis=0)
    # stdArpInsideCylinderPerTime=np.std(fullArpInsideCylinderpPerTimeArray, axis = 0)
    #
    # special case to not count the first track
    #distancesArrayExceptFirst = distancesArray[1:]
    #meanDistancesBetweenTracks = np.mean(distancesArrayExceptFirst, axis=0)
    
    # meanDistancesBetweenTracks = np.mean(fullDistancesArray,axis=0)
    # stdDistancesBetweenTracks = np.std(fullDistancesArray,axis=0)


#distancesArray=np.array(n,allDistances[sim0].length)
#for tracks in allDistances:
#    distancesArray[1]=allDistances['sim'+str(n)]
        
    
#allYs = np.array([n, allDistances[sim0].length()])

             
         
#        xs.append(curX)
#        ys.append(curY)
#        ydistance.append(curDistance)
#print(frames)
#print(times)
#print(xs)
#print(ys)
#import numpy as np
    
#for i in range(len(y1)):
#    curYdist = np.mean([y1[i], y2[i], y3[i], y4[i], y5[i], y6[i]])
#    curYstd = np.std([y1[i], y2[i], y3[i], y4[i], y5[i], y6[i]])    
#    ydistance.append(curYdist)
#    ystd.append(curYstd)

from matplotlib import pyplot as plt
        
def makescatter(times, amounts, title, rows, columns, subplot):
    plt.subplot(rows, columns, subplot)
    plt.scatter(times, amounts)
    plt.title(title)
    plt.axis([0, max(times), -0.5, 500])
    plt.xlabel('Time (s)')
    plt.ylabel('Number arp inside cylinder')

def makeerrorbar(times, amounts, ystds, title, rows, columns, subplot):
    plt.subplot(rows, columns, subplot)
    plt.errorbar(times, amounts, yerr=ystds)
    plt.title(title)
    plt.axis([0, max(times), -0.5, 500])
    plt.xlabel('Time (s)')
    plt.ylabel('Number arp inside cylinder')
    
  
def makeerrorbarAngle(times, amounts, ystds, title, rows, columns, subplot):
    plt.subplot(rows, columns, subplot)
    plt.errorbar(times, amounts, yerr=ystds)
    plt.title(title)
    plt.axis([0, max(times), 0, 200])
    plt.xlabel('Time (s)')
    plt.ylabel('Branch angle (degrees)')
    
def makescatterBound(times, amounts, title, rows, columns, subplot):
    plt.subplot(rows, columns, subplot)
    plt.scatter(times, amounts)
    plt.title(title)
    plt.axis([0, max(times), -5, 240])
    plt.xlabel('Time (s)')
    plt.ylabel('Number Hip1R bound')
   
def makeerrorbarBound(times, amounts, ystds, title, rows, columns, subplot):
    plt.subplot(rows, columns, subplot)
    plt.errorbar(times, amounts, yerr=ystds)
    plt.title(title)
    plt.axis([0, max(times), -5, 240])
    plt.xlabel('Time (s)')
    plt.ylabel('Number Hip1R bound')
    
#makescatter(times, y1, 'testSolid', 1, 6, 1)
#makescatter(times, y2, 'testSolid', 1, 6, 2)
#makescatter(times, y3, 'testSolid', 1, 6, 3)
#makescatter(times, y4, 'testSolid', 1, 6, 4)
#makescatter(times, y5, 'testSolid', 1, 6, 5)
#makescatter(times, y6, 'testSolid', 1, 6, 6)

#plot each bead position over time    

# if reportArpPosition>0:
#     n=0
#     for tracks in fullDistancesArray:
#         makescatter(times,fullArpInsideCylinderpPerTimeArray[n],'number arp inside cylinder', 2,1,1)
#         n=n+1
#
#     #plot std and mean bt the tracks for one condition
#
#     makeerrorbar(times,meanArpInsideCylinderPerTime,stdArpInsideCylinderPerTime, 'number arp inside cylinder',2,1,2)

#n=0
#for tracks in fullBoundHip1RArray:
#    makescatterBound(times, fullBoundHip1RArray[n], 'bound Hip1R', 2,2,3)
#    n=n+1
#    
#makeerrorbarBound(times, meanBoundHip1RvsTime, stdBoundHip1RvsTime, 'bound Hip1R', 2,2,4)


# plot branch angle over time (for one experiment)

# makeerrorbarAngle(times,meanArpAngleVsTime,stdArpAngleVsTime, 'Branch angle', 1,1,1)

# if reportArpPosition>0:
#
# # save mean and std with name
# #     np.savetxt(pathBeg+'/'+str(folderName)+' meanArpNbInsideCylinder.txt',meanArpInsideCylinderPerTime)
# #     np.savetxt(pathBeg+'/'+str(folderName)+' stdArpNbInsideCylinder.txt',stdArpInsideCylinderPerTime)
#
# np.savetxt(pathBeg+'/'+str(folderName)+' times.txt',times)
#
# np.savetxt(pathBeg+'/'+str(folderName)+' meanBranchAngles.txt',meanArpAngleVsTime)
# np.savetxt(pathBeg+'/'+str(folderName)+' stdBranchAngles.txt',stdArpAngleVsTime)
# # np.savetxt(pathBeg+'/'+str(folderName)+' eachBranchAngle.txt', eachArpAngleDegrees)
# #np.savetxt(pathBeg+'/'+str(folderName)+' meanBoundHip1RvsTime.txt', meanBoundHip1RvsTime)
# #np.savetxt(pathBeg+'/'+str(folderName)+' stdBoundHip1RvsTime.txt',  stdBoundHip1RvsTime)
#
# print('final branch angles: '+str(int(meanArpAngleVsTime[-1]))+'+/-'+str(int(stdArpAngleVsTime[-1]))+' degrees')