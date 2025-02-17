
import os 
import numpy as np
import subprocess
from glob import glob
import scipy

# move to the "Report" folder (e.g. for this particular expt)
# should have a list of text files

# this may only work for"arpsbead" rather tha n"hip1r.txt"

#x y z coord of where arps start. 

innerCylinderCoords = [0,0,-2]
innerCylinderRadius = 0.15 # in um. 
 
dimensions = 3 # number of dimensions

# this is for 3D. getting the Z position.

import sys

if len(sys.argv)>1:
    reportFolder = sys.argv[1]

else:
    reportFolder = 'spin90_x30_output'

reportPath = '/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/'+reportFolder

os.chdir(reportPath+'/solid/')

myDir = os.getcwd()

# get the parent path and the folder current name. 

(pathBeg, folderName) = os.path.split(myDir)

reportSolidPosition = 1
plotSolidPosition   = 0

# find the files

reportFiles = glob('*.txt')

#allDistances = {}
#allBoundHip1RperTime={} # number bound Hip1R vs time
#allArpInsideCylinderPerTime = {}
#allArpAngles = {}
distancesEachSimulation = {}
timesEachSimulation = {}
times = []

n = 0

# iterate through each text file

for textFile in reportFiles:
    
    # open file
    datafile = open(textFile, 'r')
#datafile = open('solid1.txt', 'r')
    
   
    
    # y0 = 1.7  # equilibirum position of vesicle  (2D)
    z0 = -0.4 # resting equilibrium position of the bead (3D). it may start further in.
    
    
    if 'solidPosition' in  textFile:
        print('found a solidPosition file')
        
        if reportSolidPosition>0:        
            
            frames = []
            times  = []
            distances = []
#            curXs = []
#            curYs = []
            
#            curXsInBounds = []
#            curYsInBounds = []
#            curZsInBounds = []
            #distances = {}
#            ydistance = []
#            ystd = []
            xPerTime = []
            yPerTime = []
            zPerTime = []
#            stdYperTime  = [] 
#            stdZperTime  = []
            
#            boundHip1RperTime = []
        
#            arpInsideCylinderPerTime = []            
            
            # iterate through each line in the current text file. 
            for line in datafile:
                line = line.strip()
                if line.startswith('%'):            
                    if line.startswith('% frame'):
                        curframe = int(line[8:])
                        frames.append(int(line[8:])) 
#                        curZs = [] # reset mean Y value for each time point (marked by #)  
#                        curXs = []
#                        curYs = []
                        
#                        curXsInBounds = []
#                        curYsInBounds = []
#                        curZsInBounds = []
#                        
                        curBoundStates = []
                    if line.startswith('% time'):
                        times.append(float(line[7:]))   
#                    if line.startswith('% end'): # sum up the prev meanYs.
                               
#                        if dimensions == 3:
                            
#                            stdZperTime.append(np.std(curZs[:]))
#                        boundHip1RperTime.append(sum(curBoundStates))
#                        arpInsideCylinderPerTime.append(len(curZsInBounds))
                        
                elif len(line)==0:
            #        print('break')
                    ()
                else:
                    sline = line.split()
                   # print(sline[1])
                    curID = int(sline[1]) 
                    # for point_0. I set this as the "vesicle"
                    if dimensions==2:
                        curX = float(sline[4])
                        curY = float(sline[5])
                        curDistance= curY-y0
                        xPerTime.append(curX)
                        yPerTime.append(curY)
                    elif dimensions==3:
                        curX = float(sline[5])
                        curY = float(sline[6])
                        curZ = float(sline[7])
                        curDistance = z0-curZ # zo-z bc they are both negative
                        xPerTime.append(curX)
                        yPerTime.append(curY)
                        zPerTime.append(curZ)
                    distances.append(curDistance)
                # convert position to distance from equilibrium position
                
#                if dimensions == 2:
#                    distances = np.transpose(np.subtract(yPerTime, y0))
#                elif dimensions == 3:
#                    distances = np.transpose(np.subtract(zPerTime, z0))
                distancesEachSimulation['sim'+str(n).zfill(3)]=distances

        timesEachSimulation['sim'+str(n).zfill(3)]=times
        print(times[-1])
#    
#    if 'ArpPosition' in  textFile:
#        allArpInsideCylinderPerTime['sim'+str(n)]=arpInsideCylinderPerTime
#        print('found an ArpsPosition file')
#    else:
#    # here I could add the status of wheter each hip1R is bound or not. (to correlate with position over time)    
#        allBoundHip1RperTime['sim'+str(n)]=boundHip1RperTime
        print(str(textFile))
        np.savetxt(pathBeg + '/' + str(folderName) + 'distances_track' + str(n).zfill(3)+'.txt', distancesEachSimulation['sim'+str(n).zfill(3)])
        print(str(n))
        n=n+1
np.savetxt(pathBeg + '/' + str(folderName) + ' times.txt', times)

# caluclate meana nd std

# if reportSolidPosition>0:
#
#     [allKeys, allDistances]=sorted(distancesEachSimulation.items())
#     # allDistanes = distancesEachSimulationSorted.values()
#     timesSorted = sorted(timesEachSimulation.items())
#     allTimes    = timesSorted.values()
#     #allBoundHip1RArray = allBoundHip1RperTime.values()
#    allArpInsideCylinderPeTimeArray=allArpInsideCylinderPerTime.values()

# save each
#     m = 0
#     for m in range(0,n):
#         # np.savetxt(pathBeg + '/' + str(folderName) + 'distances_track' + str(n).zfill(3), allDistances[n])
#         curDistances =  distancesEachSimulation['sim'+str(m).zfill(3)]
#         np.savetxt(pathBeg + '/' + str(folderName) + 'distances_track' + str(m).zfill(3), curDistances)

        # n = n + 1

# the rest of this analysis I'm currently doing in matlab.
#
#     # remove simluations that didn't finish.
# n=0
# allLengths=[]
# for line in allDistances:
#     allLengths.append(len(line))
#     n=n+1
# maxTimeLength = max(allLengths)
#
# # just the simulations that completed
# n=0
# fullDistances = []
# fullTimes = []
# #    nbBoundVsTime = []
# for line in allDistances:
#     if(len(line)==maxTimeLength):
#         fullDistances.append(line)
#         n=n+1
# for line in allTimes:
#         if(len(line)==maxTimeLength):
#             fullTimes.append(line)
#             n=n+1
#
# #    n=0
# #    fullBoundHip1RArray =[]
# #    for line in allBoundHip1RArray:
# #            if(len(line)==maxTimeLength):
# #                fullBoundHip1RArray.append(line)
# #                n=n+1
# #
# #    n=0
# #
# #    fullArpInsideCylinderpPerTimeArray =[]
# #    for line in allArpInsideCylinderPeTimeArray:
# #            if(len(line)==maxTimeLength):
# #                fullArpInsideCylinderpPerTimeArray.append(line)
# #                n=n+1
# #
# #
# #    meanBoundHip1RvsTime=np.mean(fullBoundHip1RArray,axis=0)
# #    stdBoundHip1RvsTime=np.std(fullBoundHip1RArray,axis=0)
# #
# #    meanArpInsideCylinderPerTime=np.mean(fullArpInsideCylinderpPerTimeArray, axis=0)
# #    stdArpInsideCylinderPerTime=np.std(fullArpInsideCylinderpPerTimeArray, axis = 0)
#
#     # special case to not count the first track
#     #distancesArrayExceptFirst = distancesArray[1:]
#     #meanDistancesBetweenTracks = np.mean(distancesArrayExceptFirst, axis=0)
#
# meanDistancesBetweenTracks = np.mean(fullDistances,axis=0)
# stdDistancesBetweenTracks = np.std(fullDistances,axis=0)
#
# # take one full time array for plotting
# fullTime = fullTimes[0]
# #distancesArray=np.array(n,allDistances[sim0].length)
# #for tracks in allDistances:
# #    distancesArray[1]=allDistances['sim'+str(n)]
#
#
# #allYs = np.array([n, allDistances[sim0].length()])
#
#
#
# #        xs.append(curX)
# #        ys.append(curY)
# #        ydistance.append(curDistance)
# #print(frames)
# #print(times)
# #print(xs)
# #print(ys)
# #import numpy as np
#
# #for i in range(len(y1)):
# #    curYdist = np.mean([y1[i], y2[i], y3[i], y4[i], y5[i], y6[i]])
# #    curYstd = np.std([y1[i], y2[i], y3[i], y4[i], y5[i], y6[i]])
# #    ydistance.append(curYdist)
# #    ystd.append(curYstd)
#
# from matplotlib import pyplot as plt
#
# def makescatter(times, amounts, title, rows, columns, subplot):
#     plt.subplot(rows, columns, subplot)
#     plt.scatter(times, amounts)
#     plt.title(title)
#     plt.axis([0, max(times), -0.2, 0.1])
#     plt.xlabel('Time (s)')
#     plt.ylabel('Distance (micron)')
#
# def makeerrorbar(times, amounts, ystds, title, rows, columns, subplot):
#     plt.subplot(rows, columns, subplot)
#     plt.errorbar(times, amounts, yerr=ystds)
#     plt.title(title)
#     plt.axis([0, max(times), -0.2, 0.1])
#     plt.xlabel('Time (s)')
#     plt.ylabel('Distance (micron)r')
#
#
# def makeerrorbarAngle(times, amounts, ystds, title, rows, columns, subplot):
#     plt.subplot(rows, columns, subplot)
#     plt.errorbar(times, amounts, yerr=ystds)
#     plt.title(title)
#     plt.axis([0, max(times), 0, 200])
#     plt.xlabel('Time (s)')
#     plt.ylabel('Branch angle (degrees)')
#
# def makescatterBound(times, amounts, title, rows, columns, subplot):
#     plt.subplot(rows, columns, subplot)
#     plt.scatter(times, amounts)
#     plt.title(title)
#     plt.axis([0, max(times), -5, 240])
#     plt.xlabel('Time (s)')
#     plt.ylabel('Number Hip1R bound')
#
# def makeerrorbarBound(times, amounts, ystds, title, rows, columns, subplot):
#     plt.subplot(rows, columns, subplot)
#     plt.errorbar(times, amounts, yerr=ystds)
#     plt.title(title)
#     plt.axis([0, max(times), -5, 240])
#     plt.xlabel('Time (s)')
#     plt.ylabel('Number Hip1R bound')
#
# #makescatter(times, y1, 'testSolid', 1, 6, 1)
# #makescatter(times, y2, 'testSolid', 1, 6, 2)
# #makescatter(times, y3, 'testSolid', 1, 6, 3)
# #makescatter(times, y4, 'testSolid', 1, 6, 4)
# #makescatter(times, y5, 'testSolid', 1, 6, 5)
# #makescatter(times, y6, 'testSolid', 1, 6, 6)
#
# #plot each bead position over time
#
# if plotSolidPosition>0:
#     n=0
#     for tracks in allDistances:
#         makescatter(allTimes[n],allDistances[n], 'Vesicle distance', 2,1,1)
#         n=n+1
#
#     #plot std and mean bt the tracks for one condition
#
#     makeerrorbar(fullTime,meanDistancesBetweenTracks,stdDistancesBetweenTracks, '' ,2,1,2)
#
# #n=0
# #for tracks in fullBoundHip1RArray:
# #    makescatterBound(times, fullBoundHip1RArray[n], 'bound Hip1R', 2,2,3)
# #    n=n+1
# #
# #makeerrorbarBound(times, meanBoundHip1RvsTime, stdBoundHip1RvsTime, 'bound Hip1R', 2,2,4)
#
#
# # plot branch angle over time (for one experiment)
#
# #makeerrorbarAngle(times,meanArpAngleVsTime,stdArpAngleVsTime, 'Branch angle', 1,1,1)
# #
# #if reportArpPosition>0:
# #
#
# # save each distance
#
# # n=0
# # for tracks in allDistances:
# #     np.savetxt(pathBeg + '/' + str(folderName) + 'distances_track'+str(n).zfill(3), allDistances[n])
# #     n=n+1
#
# ## save mean and std with name
# #    np.savetxt(pathBeg+'/'+str(folderName)+' meanArpNbInsideCylinder.txt',meanArpInsideCylinderPerTime)
# #    np.savetxt(pathBeg+'/'+str(folderName)+' stdArpNbInsideCylinder.txt',stdArpInsideCylinderPerTime)
#
# np.savetxt(pathBeg+'/'+str(folderName)+' times.txt',fullTime)
#
# np.savetxt(pathBeg+'/'+str(folderName)+' meanDistance.txt',meanDistancesBetweenTracks)
# np.savetxt(pathBeg+'/'+str(folderName)+' stdDistance.txt',stdDistancesBetweenTracks)
# #np.savetxt(pathBeg+'/'+str(folderName)+' meanBoundHip1RvsTime.txt', meanBoundHip1RvsTime)
# #np.savetxt(pathBeg+'/'+str(folderName)+' stdBoundHip1RvsTime.txt',  stdBoundHip1RvsTime)
#
# #print('final branch angles: '+str(int(meanArpAngleVsTime[-1]))+'+/-'+str(int(stdArpAngleVsTime[-1]))+' degrees')
# print("final distance: %0.3f +/- %0.3f micron" % (meanDistancesBetweenTracks[-1], stdDistancesBetweenTracks[-1]))