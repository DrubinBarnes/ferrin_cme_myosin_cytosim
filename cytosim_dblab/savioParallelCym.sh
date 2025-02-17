#!/bin/bash 
# file_ID=$(./iterateNumbers.sh $HT_TASK_ID) 

# input 1: folder where the cym files are
# input 2: number of repeats. 

# this is given by which partition we're using. each has a max nb jobs per node. This is for savio2.

maxTasksPerNode=24

# this part makes the folders, based on the number of .cym files and the number of repeats you want

# input argument should be folder_ID
folder_ID=$1  
echo $folder_ID'_output'

echo $# arguments

# second input argument is number of times you want to run the simulation

if [ $# -gt 1 ]
then
	nbRepeats=$2
else
	nbRepeats=1
fi
echo "$nbRepeats repeats"
# find the number of .cym files in the targed folder (folder_ID)

nbCyms=$(ls -1q "$folder_ID"/*.cym | wc -l)

echo I found $nbCyms cym files

# decide whether to make a new folder or not, and ask user if they want to overwrite an existing folder.

if [ -d "$folder_ID"_output ]
	then
	# echo "this folder already exists: $folder_ID . Remove this folder and its subfolders to continue! goodbye."
	read -n1 -p "this folder already exists: $folder_ID _output. Do you want to erase everything in this folder??? type N to safely leave. [Y/N] " answer
	case $answer in
		Y | y) echo
			   echo "erasing folder $folder_ID"
			   rm -r "$folder_ID"_output
			   mkdir "$folder_ID"_output;;
		N | n) echo 
			   echo "goodbye"
		exit;;
	esac
else

mkdir "$folder_ID"_output
fi

# make a new folder for each one: one per cym file, times the number of simulations. 


for ((i=0; i<$nbCyms; i++))
do
	file_ID=$(./iterateNumbers.sh $i)
	# echo $file_ID

	for ((j=0; j<$nbRepeats; j++))
	do
		repeatID=$(./iterateNumbers.sh $j)
		mkdir "$folder_ID"_output"/run"$file_ID"_"$repeatID 
	done
done

# export nbCyms and nbRepeats

# next is run bash script for slurm

# input 1 is name of folder (also name of job and name of cym file)
# input 2 is number of cyms total. I think calculate divisin over nodes in runparallel bash

totalNbSims=$(($nbRepeats*$nbCyms))

echo "$totalNbSims total simulations to run"

# here I could generate the task file directly.

# calculate how to divide the total number of tasks over 24-task nodes.

# echo $maxTasksPerNode 
# echo "$2 tasks total"

# calculate ceiling (number of tasks divided by max tasks per node, rounded up)
nbNodes=$((($totalNbSims+$maxTasksPerNode-1)/$maxTasksPerNode))


if [ $totalNbSims -le $maxTasksPerNode ]
then
	maxNbNodes=$totalNbSims
else
	maxNbNodes=$maxTasksPerNode
fi

# maxNbNodes=$(($maxTasksPerNode-$2))

echo "$nbNodes nodes used"
echo "$maxNbNodes tasks per node"

export folder_ID
export nbCyms
export nbRepeats
export maxNbNodes
export totalNbCyms
export nbNodes

# write variables to file so it works across multiple nodes
echo "echo $folder_ID" > folder_ID.sh
echo "echo $nbRepeats" > nbRepeats.sh

# load modules - not sure if necessary?
module load intel/2016.4.072 openmpi blas lapack 

# this step runs "runParallelBash.sh" and feeds in the total number of simulations to run.
# locally
# ./runParallelBash.sh $folder_ID $maxNbNodes $totalNbSims
# on SLURM (may need quotes in last 3 args)
sbatch --job-name=$folder_ID --ntasks-per-node=$maxNbNodes --nodes=$nbNodes runParallelBash.sh

#cd "$folder_ID"_output"/output_$file_ID" 
