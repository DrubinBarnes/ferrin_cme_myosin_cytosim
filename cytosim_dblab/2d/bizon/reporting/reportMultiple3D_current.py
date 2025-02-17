# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 19:38:51 2017

@author: mathewakamatsu
"""
    
# this program will look for "run" folders within your current directory and then put them in "reports" folder (assuming it's in the same parent folder)
# change the name of "curname" to name the text file. 

# FORMAT: reportMultiple3D_current [folder_name]

#[folder_name] is an optional input so you don't have to choose which folder in this script

# set runHeader based on folder name of the simulation output.
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

dimensionality = 3


import os 
import numpy as np
import subprocess
from glob import glob
#os.chdir('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim 2017/cytosim-master/')


# os.chdir('/Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/')
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
    # exeDir = myDir+'/bin3d'
    exeDir = myDir+'/bin'

os.chdir(exeDir)
reportPath = os.path.abspath('report')

if os.path.exists(myDir+'/reports/'+runSubdirectory+'/'):
    print('Overwriting an existing folder.')
    
else:

    os.mkdir(myDir+'/reports/'+runSubdirectory+'/')
# the following should let you run fiber Or this program in either order.
if os.path.exists(myDir + '/reports/' + runSubdirectory + '/' + 'bead/'):
    print('Overwriting an existing Fiber folder.')

else:
    os.mkdir(myDir+'/reports/'+runSubdirectory+'/'+'bead/')
    os.mkdir(myDir+'/reports/'+runSubdirectory+'/'+'Arp/')
    os.mkdir(myDir+'/reports/'+runSubdirectory+'/'+'solid/')
    os.mkdir(myDir + '/reports/' + runSubdirectory + '/' + 'single/')
n = 0

for line in runSubdirs:

    runDir = myDir+'/'+runSubdirectory+'/'+line
    
    print(runDir)

    os.chdir(runDir)

    hipArg1 = 'single:all' 
    hipArg2 = 'output=../../reports/'+runSubdirectory+'/bead/'+runSubdirectory+'bead'+str(n).zfill(3)+'.txt'

    solidArg1 = 'solid'
    solidArg2 = 'output=../../reports/'+runSubdirectory+'/solid/'+runSubdirectory+'solidPosition'+str(n).zfill(3)+'.txt'
    
    arpArg1 = 'couple:all'
    arpArg2 = 'output=../../reports/'+runSubdirectory+'/Arp/'+runSubdirectory+'ArpPosition'+str(n).zfill(3)+'.txt'
    
    arpArg3 = 'couple:bridge'
    arpArg4 = 'output=../../reports/'+runSubdirectory+'/Arp/'+runSubdirectory+'ArpBranchAngle'+str(n).zfill(3)+'.txt'

    singleArg1 = 'single:all'
    singleArg2 = 'output=../../reports/'+runSubdirectory+'/single/'+runSubdirectory+'singlePosition'+str(n).zfill(3)+'.txt'

    singleArg3 = 'single:hip1r'
    singleArg4 = 'output=../../reports/'+runSubdirectory+'/single/'+runSubdirectory+'hip1RPosition'+str(n).zfill(3)+'.txt'


    myOutput  = subprocess.call([reportPath, hipArg1, hipArg2])
    myOutput2 = subprocess.call([reportPath, arpArg1, arpArg2])
    myOutput3 = subprocess.call([reportPath, arpArg3, arpArg4])
    myOutput4 = subprocess.call([reportPath, solidArg1, solidArg2])

    myOutput5 = subprocess.call([reportPath, singleArg1, singleArg2])
    myOutput6 = subprocess.call([reportPath, singleArg3, singleArg4])

    n=n+1
    
print('results are in reports/'+runSubdirectory+'/')

#for runVal in 

 #   bin/report run000*/objects.cym single:all output:repatBeads.txt