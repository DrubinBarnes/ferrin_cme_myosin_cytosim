# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 19:38:51 2017

@author: mathewakamatsu
"""
    
# this program will look for "run" folders within your current directory and then put them in "reports" folder (assuming it's in the same parent folder)
# change the name of "curname" to name the text file. 

# to report arp2/3 branch angle

# curName  = 'crosslinkRates_1to20'
# curName  = 'crosslinking_lengths_inVitro'
# curName  = 'crosslinking_lengths_endo'
# curName  = 'binding_varyKon_length'
# curName  = 'arpVary_0-1000_output'
# curName  = 'nucleationVary_output'
# curName  = '3D_repat24x_noCrosslinking'
# curName  = '3D_repat24x_plusCrosslinking'
# curName  = 'motherFilament_bind1000_2'
# curName  = 'springStiffnessVary'
curName  = 'spin90_example'

# set runHeader based on folder name of the simulation output.

# runSubdirectory ='crosslinkRates_3D_1to20/'
# runSubdirectory ='crosslinks_lengths_inVitro/'
# runSubdirectory ='capLinkSweep_Output/'
# runSubdirectory = 'binding_varyKon_length_output/'
# runSubdirectory = 'arpVary_0-1000_output/'
# runSubdirectory = 'nucleationRate_vary_output/'
# runSubdirectory = '3D_repeat24x_noCrosslinking_output/'
# runSubdirectory = '3D_repeat24x_plusCrosslinking_output/'
# runSubdirectory = 'motherFilament_bind1000_output2/'
# runSubdirectory = 'arpVary_noxlink_localMother_output/'
# runSubdirectory = 'springStiffnessVary_output/'
runSubdirectory = 'spin90_example/'

runHeader = 'output'

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
os.chdir(myDir+'/'+runSubdirectory)

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

if os.path.exists(myDir+'/reports/'+curName+'/'):
    print('Overwriting an existing folder.')
    
else:

    os.mkdir(myDir+'/reports/'+curName+'/')
# the following should let you run fiber Or this program in either order.
if os.path.exists(myDir + '/reports/' + curName + '/' + 'bead/'):
    print('Overwriting an existing Fiber folder.')

else:
    os.mkdir(myDir+'/reports/'+curName+'/'+'bead/')
    os.mkdir(myDir+'/reports/'+curName+'/'+'Arp/')
    os.mkdir(myDir+'/reports/'+curName+'/'+'solid/')
    os.mkdir(myDir + '/reports/' + curName + '/' + 'single/')
n = 0

for line in runSubdirs:

    runDir = myDir+'/'+runSubdirectory+line
    
    print(runDir)

    os.chdir(runDir)

    hipArg1 = 'single:all' 
    hipArg2 = 'output=../../reports/'+curName+'/bead/'+curName+'bead'+str(n).zfill(3)+'.txt'

    solidArg1 = 'solid'
    solidArg2 = 'output=../../reports/'+curName+'/solid/'+curName+'solidPosition'+str(n).zfill(3)+'.txt'
    
    arpArg1 = 'couple:all'
    arpArg2 = 'output=../../reports/'+curName+'/Arp/'+curName+'ArpPosition'+str(n).zfill(3)+'.txt'
    
    arpArg3 = 'couple:bridge'
    arpArg4 = 'output=../../reports/'+curName+'/Arp/'+curName+'ArpBranchAngle'+str(n).zfill(3)+'.txt'

    singleArg1 = 'single:all'
    singleArg2 = 'output=../../reports/'+curName+'/single/'+curName+'singlePosition'+str(n).zfill(3)+'.txt'


    myOutput  = subprocess.call([reportPath, hipArg1, hipArg2])
    myOutput2 = subprocess.call([reportPath, arpArg1, arpArg2])
    myOutput3 = subprocess.call([reportPath, arpArg3, arpArg4])
    myOutput4 = subprocess.call([reportPath, solidArg1, solidArg2])

    myOutput5 = subprocess.call([reportPath, singleArg1, singleArg2])
    
    n=n+1
    
print('results are in reports/'+curName+'/')

#for runVal in 

 #   bin/report run000*/objects.cym single:all output:repatBeads.txt