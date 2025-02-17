import os 
import numpy as np
import subprocess
from glob import glob
import scipy

# move to the "Report" folder (e.g. for this particular expt)
# should have a list of text files

# for now just get the lengths at teh last time point. and save as a vector. 

#last_time_point = '99' 

dimensions = 3 # number of dimensions

targetFiberClass = 1 # 0 should be actin, 1 mother actin? but sometimes I'm removing mother actin. will have to toggle that.

import sys
# print "This is the name of the script: ", sys.argv[0]
# print "Number of arguments: ", len(sys.argv)
# print "The arguments are: " , str(sys.argv)

if len(sys.argv)>1:
    runSubdirectory = sys.argv[1]

else:
    runSubdirectory = 'varyCp_Lp_fixedNucleator'

# print "runsubdirectory is now "+runSubdirectory

# runHeader = 'output04'
runHeader = 'output' # for all files that start with "output"

# reportPath = '/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/crosslinking_lengths_inVitro'
# reportPath = '/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/crosslinking_lengths_inVitro'
reportPath = '/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reports/crosslinking_lengths_endo'

os.chdir(reportPath+'/Fiber/')

myDir = os.getcwd()

# get the parent path and the folder current name. 

(pathBeg, folderName) = os.path.split(reportPath)

#os.chdir('/Users/mathewakamatsu/Documents/EMBL modeling course 2015/Practicals/pushvesicles/stiffness0/')
#os.chdir('/Users/mathewakamatsu/Documents/EMBL modeling course 2015/Practicals/pushvesicles/stiffness1/')

#datafile = open('solidzero.txt', 'r')

# find the files

reportFiles = glob('*.txt')

allDistances = {}
allTimes = {}
allBoundHip1RperTime={} # number bound Hip1R vs time
allLengths = {}

allNetForces={}
allForcesMagnitude = {}

allFiberEndNumbers = {}
allFiberLengths = {}

allFiberXs = {}
allFiberYs = {}
allFiberZs = {}

allFiberDirectionsX = {}
allFiberDirectionsY = {}
allFiberDirectionsZ = {}


allFiberEndXs = {}
allFiberEndYs = {}
allFiberEndZs = {}

allFiberEndDirectionsX = {}
allFiberEndDirectionsY = {}
allFiberEndDirectionsZ = {}

allFiberEndForcesX = {}
allFiberEndForcesY = {}
allFiberEndForcesZ = {}

allMeanFilamentLengths = {}
allStdFilamentLengths = {}

allLastTimeptFilamentLengths = {}

n = 0 # for fiberPRop
m = 0 # for fiberEnds
p = 0 # for fiberCLusters
for textFile in reportFiles:
    
    # open file
    datafile = open(textFile, 'r')
#datafile = open('solid1.txt', 'r')
    if 'FiberProp' in  textFile:
        print('found a FiberProp file')
        print(textFile)
        frames = []
        times  = []
        fiberXs = {}
        fiberYs = {}
        fiberZs = {}
        fiberLengths = {}
        fiberDirectionsX = {}
        fiberDirectionsY = {}
        fiberDirectionsZ = {}
        
        meanFilamentLengths = []
        stdFilamentLengths  = []
        #distances = {}
    #    ydistance = []
    #    ystd = []
    #    meanYperTime = []
    #    stdYperTime  = [] # per hip1r
    #    boundHip1RperTime = []
    #    curLengths =[]
    # force (opposite directions will cancel each other)
    #    forcesNet=[]    
    #    forcesNetPositive = []
        # force magnitude (absolute value of forces on Hip1Rs)
    #    forcesMagnitude=[]   
    #    curLocalMagnitudeForces = []
    #    totalForcesLocalMagnitudePerTime =[]
    #    y0 = 2.89 #position vesicle starts  
       # y0 = 2.93 # equiplibrium position of vesicle   
        
        for line in datafile:
            line = line.strip()
            if line.startswith('%'):            
                if line.startswith('% frame'): 
                    curFrame = int(line[8:])
                    frames.append(int(line[8:]))
    #                reset per-timpoint values at each new time point (marked by %)  
                    curFibersX =[]
                    curFibersY = []
                    curFibersZ = []
                    curDirectionsX = []
                    curDirectionsY = []
                    curDirectionsZ = []
                    curFiberLengths = []

                if line.startswith('% time'):
                    times.append(float(line[7:]))   
                if line.startswith('% end'): # sum up the prev meanYs. 
                    ()
                    fiberLengths['frame'+str(curFrame).zfill(3)] = curFiberLengths 
                    fiberXs['frame'+str(curFrame).zfill(3)] = curFibersX  
                    fiberYs['frame'+str(curFrame).zfill(3)] = curFibersY  
                    fiberDirectionsX['frame'+str(curFrame).zfill(3)] = curDirectionsX  
                    fiberDirectionsY['frame'+str(curFrame).zfill(3)] = curDirectionsY  
                    
                    meanFilamentLength=np.mean(curFiberLengths)
                    stdFilamentLength = np.std(curFiberLengths)
                    
                    meanFilamentLengths.append(meanFilamentLength)
                    stdFilamentLengths.append(stdFilamentLength)
                    
                    if dimensions == 3:
                        fiberZs['frame'+str(curFrame).zfill(3)] = curFibersZ
                        fiberDirectionsZ['frame'+str(curFrame).zfill(3)] = curDirectionsZ  
                    
                    

            elif len(line)==0:
        #        print('break')
                ()
            else:
                sline = line.split()
               # print(sline[1])
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
                elif dimensions == 2: # haven't tested 2D yet
                    curDirectionX = float(sline[5])
                    curDirectionY = float(sline[6])

                # store the data JUST for the starget fiber class (usually actin)            
                if curClassID == targetFiberClass:            
                    curFiberLengths.append(curLength)
                    curFibersX.append(curFiberX)
                    curFibersY.append(curFiberY)                
                    curDirectionsX.append(curDirectionX)
                    curDirectionsY.append(curDirectionY)
                    if dimensions==3:
                        curFibersZ.append(curFiberZ)                    
                        curDirectionsZ.append(curDirectionZ)
                

        allTimes['sim'+str(n).zfill(3)]=times
        allFiberLengths['sim'+str(n).zfill(3)]=fiberLengths
        allFiberXs['sim'+str(n).zfill(3)]=fiberXs
        allFiberYs['sim'+str(n).zfill(3)]=fiberYs
        allFiberZs['sim'+str(n).zfill(3)]=fiberZs
        allFiberDirectionsX['sim'+str(n).zfill(3)]=fiberDirectionsX
        allFiberDirectionsY['sim'+str(n).zfill(3)]=fiberDirectionsY
        allFiberDirectionsZ['sim'+str(n).zfill(3)]=fiberDirectionsZ
        
        allMeanFilamentLengths['sim'+str(n).zfill(3)]= meanFilamentLengths
        allStdFilamentLengths['sim'+str(n).zfill(3)]= stdFilamentLengths

        allLastTimeptFilamentLengths['sim'+str(n).zfill(3)]=curFiberLengths

    
        print(str(n))
        n=n+1
        
                
        
    if 'FiberEnds' in  textFile:
        print('found a FiberEnds file')
        # Note: here I am reporting for PLUS end of fiber. 
        # try to just reset the relevant variables
        frames = []
        times  = []
        fiberEndNumbers = {}        
        fiberXs = {}
        fiberYs = {}
        fiberZs = {}
        fiberLengths = {}
        fiberDirectionsX = {}
        fiberDirectionsY = {}
        fiberDirectionsZ = {}
        
        meanFilamentLengths = []
        stdFilamentLengths  = []

        
        for line in datafile:
            line = line.strip()
            if line.startswith('%'):            
                if line.startswith('% frame'): 
                    curFrame = int(line[8:])
                    frames.append(int(line[8:]))
    #                reset per-timpoint values at each new time point (marked by %)  
                    curFiberNumbers=[]                    
                    curFibersX =[]
                    curFibersY = []
                    curFibersZ = []
                    curDirectionsX = []
                    curDirectionsY = []
                    curDirectionsZ = []
#                        curFiberLengths = []

                if line.startswith('% time'):
                    times.append(float(line[7:]))   
                if line.startswith('% end'): # sum up the prev meanYs. 
                    ()
#                        fiberLengths['frame'+str(curFrame).zfill(3)] = curFiberLengths 
                    fiberXs['frame'+str(curFrame).zfill(3)] = curFibersX  
                    fiberYs['frame'+str(curFrame).zfill(3)] = curFibersY  
                    fiberDirectionsX['frame'+str(curFrame).zfill(3)] = curDirectionsX  
                    fiberDirectionsY['frame'+str(curFrame).zfill(3)] = curDirectionsY  
                    fiberEndNumbers['frame'+str(curFrame).zfill(3)] = curFiberNumbers     
#                        meanFilamentLength=np.mean(curFiberLengths)
#                        stdFilamentLength = np.std(curFiberLengths)
                        
#                        meanFilamentLengths.append(meanFilamentLength)
#                        stdFilamentLengths.append(stdFilamentLength)
                    
                    if dimensions == 3:
                        fiberZs['frame'+str(curFrame).zfill(3)] = curFibersZ
                        fiberDirectionsZ['frame'+str(curFrame).zfill(3)] = curDirectionsZ  
                    
                    
            elif len(line)==0:
        #        print('break')
                ()
            else:
                sline = line.split()
               # print(sline[1])
                curClassID = int(sline[0])
                curFiberNumber = int(sline[1])
#                    curLength = float(sline[2])
                # this is for PLUS end. 
                
                
                
                if dimensions == 3:
                    curFiberX = float(sline[11])
                    curFiberY = float(sline[12])                        
                    curFiberZ = float(sline[13])
                    curDirectionX = float(sline[14])
                    curDirectionY = float(sline[15])
                    curDirectionZ = float(sline[16])
                elif dimensions == 2: # haven't tested 2D yet
                    curFiberX = float(sline[9])
                    curFiberY = float(sline[10])                                
                    curDirectionX = float(sline[11])
                    curDirectionY = float(sline[12])
         
                if curClassID == targetFiberClass:            
#                        curFiberLengths.append(curLength)
                    curFiberNumbers.append(curFiberNumber)                    
                    curFibersX.append(curFiberX)
                    curFibersY.append(curFiberY)                
                    curDirectionsX.append(curDirectionX)
                    curDirectionsY.append(curDirectionY)
                    if dimensions==3:
                        curFibersZ.append(curFiberZ)                    
                        curDirectionsZ.append(curDirectionZ)
#                allTimes['sim'+str(n).zfill(3)]=times
#                allFiberLengths['sim'+str(n).zfill(3)]=fiberLengths
        allFiberEndNumbers['sim'+str(m).zfill(3)]=fiberEndNumbers
        allFiberEndXs['sim'+str(m).zfill(3)]=fiberXs
        allFiberEndYs['sim'+str(m).zfill(3)]=fiberYs
        allFiberEndZs['sim'+str(m).zfill(3)]=fiberZs
        allFiberEndDirectionsX['sim'+str(m).zfill(3)]=fiberDirectionsX
        allFiberEndDirectionsY['sim'+str(m).zfill(3)]=fiberDirectionsY
        allFiberEndDirectionsZ['sim'+str(m).zfill(3)]=fiberDirectionsZ
#                            

        print(str(m))
        m=m+1

# report fiber clusters

    if 'FiberClusters' in  textFile:
        print('found a FiberClusters file')
        # Note: here I am reporting for PLUS end of fiber. 
        # try to just reset the relevant variables
        frames = []
        times  = []
        fiberEndNumbers = {}        
        fiberXs = {}
        fiberYs = {}
        fiberZs = {}
        fiberLengths = {}
        fiberDirectionsX = {}
        fiberDirectionsY = {}
        fiberDirectionsZ = {}
        
        meanFilamentLengths = []
        stdFilamentLengths  = []

        
        for line in datafile:
            line = line.strip()
            if line.startswith('%'):            
                if line.startswith('% frame'): 
                    curFrame = int(line[8:])
                    frames.append(int(line[8:]))
    #                reset per-timpoint values at each new time point (marked by %)  
                    curNbFibers = []                    
                    curFiberNumbers=[]
                    clusterIDsTimept = []
                    nbFibersTimept = []
                    fiberNumbersTimept = []              
#                    curFibersX =[]
#                    curFibersY = []
#                    curFibersZ = []
#                    curDirectionsX = []
#                    curDirectionsY = []
#                    curDirectionsZ = []
#                        curFiberLengths = []

                if line.startswith('% time'):
                    times.append(float(line[7:]))   
                if line.startswith('% end'): # sum up the prev meanYs. 
                    ()
#                        fiberLengths['frame'+str(curFrame).zfill(3)] = curFiberLengths 
                    # HERE is where you put the cluster number, etc in for each time point and aave it.                     
#                    fiberXs['frame'+str(curFrame).zfill(3)] = curFibersX  
#                    fiberYs['frame'+str(curFrame).zfill(3)] = curFibersY  
#                    fiberDirectionsX['frame'+str(curFrame).zfill(3)] = curDirectionsX  
#                    fiberDirectionsY['frame'+str(curFrame).zfill(3)] = curDirectionsY  
#                    fiberEndNumbers['frame'+str(curFrame).zfill(3)] = curFiberNumbers     
#                        meanFilamentLength=np.mean(curFiberLengths)
#                        stdFilamentLength = np.std(curFiberLengths)
                        
#                        meanFilamentLengths.append(meanFilamentLength)
#                        stdFilamentLengths.append(stdFilamentLength)
                    
#                    if dimensions == 3:
##                        fiberZs['frame'+str(curFrame).zfill(3)] = curFibersZ
#                        fiberDirectionsZ['frame'+str(curFrame).zfill(3)] = curDirectionsZ  
                    
                    
            elif len(line)==0:
        #        print('break')
                ()
            else:
                sline = line.split()
                
               # print(sline[1])
                curClusterID = int(sline[0])
                curNbFibers = int(sline[1])
                # sline[2] sould b ea colon
                curFiberNumbers = sline[3:]

                clusterIDsTimept.append(curClusterID)
                nbFibersTimept.append(curNbFibers)
                fiberNumbersTimept.append(curFiberNumbers) # will this work bc lists different size?
#                    curLength = float(sline[2])
                # this is for PLUS end. 
                
                
#                
#                if dimensions == 3:
#                    curFiberX = float(sline[11])
#                    curFiberY = float(sline[12])                        
#                    curFiberZ = float(sline[13])
#                    curDirectionX = float(sline[14])
#                    curDirectionY = float(sline[15])
#                    curDirectionZ = float(sline[16])
#                elif dimensions == 2: # haven't tested 2D yet
#                    curFiberX = float(sline[9])
#                    curFiberY = float(sline[10])                                
#                    curDirectionX = float(sline[11])
#                    curDirectionY = float(sline[12])
#         
#                if curClassID == targetFiberClass:            
##                        curFiberLengths.append(curLength)
#                    curFiberNumbers.append(curFiberNumber)                    
#                    curFibersX.append(curFiberX)
#                    curFibersY.append(curFiberY)                
#                    curDirectionsX.append(curDirectionX)
#                    curDirectionsY.append(curDirectionY)
#                    if dimensions==3:
#                        curFibersZ.append(curFiberZ)                    
#                        curDirectionsZ.append(curDirectionZ)
#                allTimes['sim'+str(n).zfill(3)]=times
#                allFiberLengths['sim'+str(n).zfill(3)]=fiberLengths
#        allFiberEndNumbers['sim'+str(m).zfill(3)]=fiberEndNumbers
#        allFiberEndXs['sim'+str(m).zfill(3)]=fiberXs
#        allFiberEndYs['sim'+str(m).zfill(3)]=fiberYs
#        allFiberEndZs['sim'+str(m).zfill(3)]=fiberZs
#        allFiberEndDirectionsX['sim'+str(m).zfill(3)]=fiberDirectionsX
#        allFiberEndDirectionsY['sim'+str(m).zfill(3)]=fiberDirectionsY
#        allFiberEndDirectionsZ['sim'+str(m).zfill(3)]=fiberDirectionsZ
## for a given simulation (default last right now):
        print(str(p))       
        p = p+1    
                     
exptToExport = 0




# save the LAST time point filament lengths, separately for each simulation
for nn in range(0, n):
    # np.savetxt(pathBeg+'/'+str(folderName)+'lastTimeptAngles_protein'+str(bridgeClass)+'sim'+str(m).zfill(3)+'.txt', branchAnglesLastTimepoint['sim'+str(m)])
    np.savetxt(reportPath+'/'+str(folderName)+'lastTimeptFilamentLengths_'+'sim'+str(nn).zfill(3)+'.txt', allLastTimeptFilamentLengths['sim'+str(nn).zfill(3)])

# save the LAST time point cluster information. 
# i'm turing this off for now
#
# if os.path.exists(reportPath+'/'+str(folderName)+'fiberCluster/'):
#     print('Overwriting an existing folder.')
#
# else:
#
#     os.mkdir(reportPath+'/'+str(folderName)+'fiberCluster/')
#
# clustersLastTimePt = clusterIDsTimept
# nbFilamentsPerClusterLastTimept = nbFibersTimept
# filamentIDsLastTimept = fiberNumbersTimept



# create an output table for all filaments, with XYZ and dirXYZ. for ends first. later for filament middles too.


# make folder if doesn't exist

if os.path.exists(reportPath+'/'+str(folderName)+'fiberEnd/'):
    print('Overwriting an existing folder.')
    
else:

    os.mkdir(reportPath+'/'+str(folderName)+'fiberEnd/')


# right now just assume that "frames" did not change over different simulations.

exportFrameNumbers = frames

exportFiberEndNumbers=allFiberEndNumbers['sim'+str(exptToExport).zfill(3)]
exportFiberEndXs=allFiberEndXs['sim'+str(exptToExport).zfill(3)]
exportFiberEndYs=allFiberEndYs['sim'+str(exptToExport).zfill(3)]
exportFiberEndZs=allFiberEndZs['sim'+str(exptToExport).zfill(3)]
exportFiberEndDirectionsX=allFiberEndDirectionsX['sim'+str(exptToExport).zfill(3)]
exportFiberEndDirectionsY=allFiberEndDirectionsY['sim'+str(exptToExport).zfill(3)]
exportFiberEndDirectionsZ=allFiberEndDirectionsZ['sim'+str(exptToExport).zfill(3)]

exportFiberEndProperties = {}
allExportFiberEndProperties = {}
for curFrame in exportFrameNumbers:

#    print(curFrame)
    # identify the number of filaments

#    curNbFibers = len(exportFiberEndNumbers['frame'+str(curFrame).zfill(3)])
    
    #exportFiberEndPropertiesCurFrame = newTable(curNbFibers,7)
    
    # make an x by 6 set of lists, where n is the number of filaments.     
    # order is as above: fiberNumber, end_x y z, end direction_x y z
#    exportFiberEndPropertiesCurFrame = [exportFiberEndNumbers.values()[curFrame], exportFiberEndXs.values()[curFrame], exportFiberEndYs.values()[curFrame],  exportFiberEndZs.values()[curFrame],  exportFiberEndDirectionsX.values()[curFrame], exportFiberEndDirectionsY.values()[curFrame], exportFiberEndDirectionsZ.values()[curFrame]]
    exportFiberEndPropertiesCurFrame = [exportFiberEndNumbers['frame'+str(curFrame).zfill(3)], exportFiberEndXs['frame'+str(curFrame).zfill(3)], exportFiberEndYs['frame'+str(curFrame).zfill(3)],  exportFiberEndZs['frame'+str(curFrame).zfill(3)],  exportFiberEndDirectionsX['frame'+str(curFrame).zfill(3)], exportFiberEndDirectionsY['frame'+str(curFrame).zfill(3)], exportFiberEndDirectionsZ['frame'+str(curFrame).zfill(3)]]
    
    # convert lists to n by 6 array.
    
    exportFiberEndPropertiesCurrFrameArray = np.transpose(np.asarray(exportFiberEndPropertiesCurFrame))
    
    allExportFiberEndProperties['frame'+str(curFrame).zfill(3)] =exportFiberEndPropertiesCurrFrameArray    
    
    # save each array as a text file for each time point. 
    np.savetxt(reportPath+'/'+str(folderName)+'fiberEnd/frame'+str(curFrame)+'FiberEndProperties.txt', exportFiberEndPropertiesCurrFrameArray)


# this will work for the simulation chosen above

#For a given cluster, e.g. those over 5 filaments in laneght, store the ID of the filaments.

# then for each filament, read out the important stuff. 

# x y z

# x y z dir 

# then for end too. 

# then for all the clusters, not just the large ones. 
n = 0
lastTimePoint = frames[-1]
curFrame = lastTimePoint

lastTimepointExportFiberEndNumbers=exportFiberEndNumbers['frame'+str(curFrame).zfill(3)]
lastTimepointExportFiberEndXs=exportFiberEndXs['frame'+str(curFrame).zfill(3)]
lastTimepointExportFiberEndXs=exportFiberEndYs['frame'+str(curFrame).zfill(3)]
lastTimepointExportFiberEndZs=exportFiberEndZs ['frame'+str(curFrame).zfill(3)]
lastTimepointExportFiberEndDirectionsX=exportFiberEndDirectionsX['frame'+str(curFrame).zfill(3)]
lastTimepointExportFiberEndDirectionsY=exportFiberEndDirectionsY['frame'+str(curFrame).zfill(3)]
lastTimepointExportFiberEndDirectionsZ=exportFiberEndDirectionsZ['frame'+str(curFrame).zfill(3)]
#
## THIS is where I might try to quantify cluster size, properties
#minClusterSize = 5
#for cluster in clustersLastTimePt:
#    if nbFilamentsPerClusterLastTimept[n]>minClusterSize:
#        curFilamentIDs = filamentIDsLastTimept[n]
#        
#        for filament in curFilamentIDs:
#            curFilIndex = lastTimepointExportFiberEndNumbers.index(filament)
#            
#    n = n+1   
#        

# make an x by 6 array, where n is the number of filaments. 

# ideally everything not filled in would be a NaN or a " "





# caluclate meana nd std
#distancesArray=allDistances.values()
#allBoundHip1RArray = allBoundHip1RperTime.values()
#allForcesMagnitudeArray = allForcesMagnitude.values()
#allNetForcesArray = allNetForces.values()

#allFiberLengths = np.transpose(allLengths.values()) # this will be fine if they're all the same nb fibers.
#allFiberLengths = allLengths.values() # this will be fine if they're all the same nb fibers.

# remove simluations that didn't finish. 
#n=0
#allLengths=[] # the name would need to be changed to keep using this. 
#for line in distancesArray:
#    allLengths.append(len(line))
#    n=n+1
#maxTimeLength = max(allLengths)

#n=0
#fullDistancesArray = []
#nbBoundVsTime = []
#for line in distancesArray:
#    if(len(line)==maxTimeLength):
#        fullDistancesArray.append(line)
#        n=n+1
#    
#n=0
#fullBoundHip1RArray =[]
#for line in allBoundHip1RArray:
#        if(len(line)==maxTimeLength):
#            fullBoundHip1RArray.append(line)
#            n=n+1
#
#n=0
#fullForcesMagnitudeArray = []
#for line in allForcesMagnitudeArray:
#    if(len(line)==maxTimeLength):
#        fullForcesMagnitudeArray.append(line)
#        n=n+1
#n=0
#fullNetForcesArray = []
#for line in allNetForcesArray:
#    if(len(line)==maxTimeLength):
#        fullNetForcesArray.append(line)
#        n=n+1       
#        
#meanBoundHip1RvsTime=np.mean(fullBoundHip1RArray,axis=0)
#stdBoundHip1RvsTime=np.std(fullBoundHip1RArray,axis=0)

# special case to not count the first track
#distancesArrayExceptFirst = distancesArray[1:]
#meanDistancesBetweenTracks = np.mean(distancesArrayExceptFirst, axis=0)

#meanDistancesBetweenTracks = np.mean(fullDistancesArray,axis=0)
#stdDistancesBetweenTracks = np.std(fullDistancesArray,axis=0)
#
#meanForcesMagnitudePerTime = np.mean(fullForcesMagnitudeArray,axis=0)
#stdForcesMagnitudePerTime  = np.std(fullForcesMagnitudeArray,axis=0)
#
#meanNetForcesPerTime = np.mean(fullNetForcesArray,axis=0)
#stdNetForcesPerTime  = np.std(fullNetForcesArray,axis=0)
#

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
        
#from matplotlib import pyplot as plt
#        
#def makescatter(times, amounts, title, rows, columns, subplot):
#    plt.subplot(rows, columns, subplot)
#    plt.scatter(times, amounts)
#    plt.title(title)
#    plt.axis([0, max(times), -0.5, 0.2])
#    plt.xlabel('Time (s)')
#    plt.ylabel('Distance (micron)')
#
#def makeerrorbar(times, amounts, ystds, title, rows, columns, subplot):
#    plt.subplot(rows, columns, subplot)
#    plt.errorbar(times, amounts, yerr=ystds)
#    plt.title(title)
#    plt.axis([0, max(times), -0.5, 0.15])
#    plt.xlabel('Time (s)')
#    plt.ylabel('Distance (micron)')
#    
#    
#def makescatterBound(times, amounts, title, rows, columns, subplot):
#    plt.subplot(rows, columns, subplot)
#    plt.scatter(times, amounts)
#    plt.title(title)
#    plt.axis([0, max(times), -5, 25])
#    plt.xlabel('Time (s)')
#    plt.ylabel('Number Hip1R bound')
#   
#def makeerrorbarBound(times, amounts, ystds, title, rows, columns, subplot):
#    plt.subplot(rows, columns, subplot)
#    plt.errorbar(times, amounts, yerr=ystds)
#    plt.title(title)
#    plt.axis([0, max(times), -5, 25])
#    plt.xlabel('Time (s)')
#    plt.ylabel('Number Hip1R bound')
#    
#    
#def makescatterForce(times, amounts, title, rows, columns, subplot):
#    plt.subplot(rows, columns, subplot)
#    plt.scatter(times, amounts)
#    plt.title(title)
#    plt.axis([0, max(times), -15, 15])
#    plt.xlabel('Time (s)')
#    plt.ylabel('Force on bead (pN)')
#   
#def makeerrorbarForce(times, amounts, ystds, title, rows, columns, subplot):
#    plt.subplot(rows, columns, subplot)
#    plt.errorbar(times, amounts, yerr=ystds)
#    plt.title(title)
#    plt.axis([0, max(times), -15, 15])
#    plt.xlabel('Time (s)')
#    plt.ylabel('Force on bead (pN)')
##makescatter(times, y1, 'testSolid', 1, 6, 1)
##makescatter(times, y2, 'testSolid', 1, 6, 2)
##makescatter(times, y3, 'testSolid', 1, 6, 3)
##makescatter(times, y4, 'testSolid', 1, 6, 4)
##makescatter(times, y5, 'testSolid', 1, 6, 5)
##makescatter(times, y6, 'testSolid', 1, 6, 6)
#
##plot each bead position over time    
#    
#n=0
#for tracks in fullDistancesArray:
#    makescatter(times,fullDistancesArray[n],'bead distance', 3,2,1)
#    n=n+1
#    
##plot std and mean bt the tracks for one condition
#    
#makeerrorbar(times,meanDistancesBetweenTracks,stdDistancesBetweenTracks, 'bead distance',3,2,2)
#
#n=0
#for tracks in fullBoundHip1RArray:
#    makescatterBound(times, fullBoundHip1RArray[n], 'bound Hip1R', 3,2,3)
#    n=n+1
#    
#makeerrorbarBound(times, meanBoundHip1RvsTime, stdBoundHip1RvsTime, 'bound Hip1R',3,2,4)
#
##n=0
##for tracks in fullForcesMagnitudeArray:
##    makescatterForce(times, fullForcesMagnitudeArray[n], 'total force on Hip1Rs', 3,2,5)
##    n=n+1
##    
##makeerrorbarForce(times, meanForcesMagnitudePerTime, stdForcesMagnitudePerTime, 'total force on Hip1Rs',3,2,6)
#
#n=0
#for tracks in fullNetForcesArray:
#    makescatterForce(times, fullNetForcesArray[n], 'net force on Hip1Rs', 3,2,5)
##    makescatterForce(times, fullForcesMagnitudeArray[n], 'total force on Hip1Rs', 3,2,5)
#    n=n+1
#    
##makeerrorbarForce(times, meanForcesMagnitudePerTime, stdForcesMagnitudePerTime, 'total force on Hip1Rs',3,2,6)
#makeerrorbarForce(times, meanNetForcesPerTime, stdNetForcesPerTime, 'total force on Hip1Rs', 3,2,6)
 
# for most recent sim
fiberLengthsLastSimLastTimepoint = curFiberLengths
fiberDirectionsZLastSimLastTimepoint = curDirectionsZ
fiberZsLastSimLastTimepoint = curFibersZ

meanFiberLengthsLastSim = meanFilamentLengths
stdFiberLengthsLastSim  = stdFilamentLengths

# save mean and std with name
#np.savetxt(reportPath+'/'+str(folderName)+' allFiberLengths.txt',allFiberLengths)
#np.savetxt(pathBeg+'/'+str(folderName)+' stdDistance10beads.txt',stdDistancesBetweenTracks)
#np.savetxt(pathBeg+'/'+str(folderName)+' times.txt',times)

np.savetxt(reportPath+'/'+str(folderName)+' lastTimeptFiberLengths.txt', fiberLengthsLastSimLastTimepoint)
np.savetxt(reportPath+'/'+str(folderName)+' lastTimeptFiberDirectionsZ.txt', fiberDirectionsZLastSimLastTimepoint)
np.savetxt(reportPath+'/'+str(folderName)+' lastTimeptFiberZs.txt', fiberZsLastSimLastTimepoint)

np.savetxt(reportPath+'/'+str(folderName)+' lastTimeptMeanFiberLengths.txt', meanFiberLengthsLastSim)
np.savetxt(reportPath+'/'+str(folderName)+' lastTimeptStdFiberLengths.txt', stdFiberLengthsLastSim)


# what about lengths distribution over time, mean std

# save position, directions of filaments. 


#np.savetxt(pathBeg+'/'+str(folderName)+' meanBoundHip1RvsTime.txt', meanBoundHip1RvsTime)
#np.savetxt(pathBeg+'/'+str(folderName)+' stdBoundHip1RvsTime.txt',  stdBoundHip1RvsTime)
#
#np.savetxt(pathBeg+'/'+str(folderName)+' meanForceMagnitudevsTime.txt', meanForcesMagnitudePerTime)
#np.savetxt(pathBeg+'/'+str(folderName)+' stdForceMagnitudevsTime.txt', stdForcesMagnitudePerTime)