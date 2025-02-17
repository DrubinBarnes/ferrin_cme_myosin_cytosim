# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 19:38:51 2017

@author: mathewakamatsu
"""
    
# this program will look for "run" folders within your current directory and then put them in "reports" folder (assuming it's in the same parent folder)
# change the name of "curname" to name the text file. 



#curName  = 'spin90_example'


# could turn this into a function with the name (and output folder) as different.

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
# runSubdirectory ='spin90_x30_output'
#
# runHeader = 'output008'


# set dimensinoality

dimensionality = 3

import os 
import numpy as np
import subprocess
from glob import glob
#os.chdir('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim 2017/cytosim-master/')


os.chdir('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/')
#os.chdir('/Users/mathewakamatsu/Downloads/cytogit.torque')

myDir = os.getcwd()

# make alist of folder names that include "run"


# move to subdirectory where current data are (including subfolders)
os.chdir(myDir+'/'+runSubdirectory+'/')

runSubdirs = []
subdirs = glob('*/')
for line in subdirs:
    if line.startswith(runHeader):    
        runSubdirs.append(line)
    
if dimensionality==2:
    # in 2D 
    exeDir = myDir+'/bin'
elif dimensionality == 3:
    # 3d (if that's how the folder is called )    
    exeDir = myDir+'/bin'

os.chdir(exeDir)
reportPath = os.path.abspath('report')

if os.path.exists(myDir+'/reports/'+runSubdirectory+'/'):
    print('Using an existing folder.')
    
else:

    os.mkdir(myDir+'/reports/'+curName+'/')
    
if os.path.exists(myDir+'/reports/'+runSubdirectory+'/'+'Fiber/'):
    print('Overwriting an existing Fiber folder.')
    
else:
    os.mkdir(myDir+'/reports/'+runSubdirectory+'/'+'Fiber/')
    
n = 0

for line in runSubdirs:

    runDir = myDir+'/'+runSubdirectory+'/'+line
    
    print(runDir)
    print(n)
    os.chdir(runDir)
    
    fiberArg1 = 'fiber'
    fiberArg2 = 'output=../../reports/'+runSubdirectory+'/Fiber/'+runSubdirectory+'FiberProp'+str(n).zfill(3)+'.txt'
    
    fiberArg3 = 'fiber:end'
    fiberArg4 = 'output=../../reports/'+runSubdirectory+'/Fiber/'+runSubdirectory+'FiberEnds'+str(n).zfill(3)+'.txt'
        
    fiberArg5 = 'fiber:force'
    fiberArg6 = 'output=../../reports/'+runSubdirectory+'/Fiber/'+runSubdirectory+'FiberForces'+str(n).zfill(3)+'.txt'

    fiberArg7 = 'fiber:tension'
    fiberArg8 = 'output=../../reports/'+runSubdirectory+'/Fiber/'+runSubdirectory+'FiberTensions'+str(n).zfill(3)+'.txt'

    fiberArg9 = 'fiber:clusters'
    fiberArg10= 'output=../../reports/'+runSubdirectory+'/Fiber/'+runSubdirectory+'FiberClusters'+str(n).zfill(3)+'.txt'



    myOutput  = subprocess.call([reportPath, fiberArg1, fiberArg2])
    myOutput2 = subprocess.call([reportPath, fiberArg3, fiberArg4])
    myOutput3 = subprocess.call([reportPath, fiberArg5, fiberArg6])
    myOutput4 = subprocess.call([reportPath, fiberArg7, fiberArg8])
    myOutput5 = subprocess.call([reportPath, fiberArg9, fiberArg10])

    n=n+1
    
print('results are in reports/'+runSubdirectory+'/')

#for runVal in 

 #   bin/report run000*/objects.cym single:all output:repatBeads.txt
