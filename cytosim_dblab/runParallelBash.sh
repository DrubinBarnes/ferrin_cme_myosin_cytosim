#!/bin/bash
# Job name:
#
# Account:
#SBATCH --account=fc_cytosim
# # Partition:
#SBATCH --partition=savio2
#
# Tasks per node
#
# Nodes
#
# Wall clock limit:
#SBATCH --time=72:00:00
#
# Mail type:
#SBATCH --mail-type=all
#
# Mail user:
#SBATCH --mail-user=ferrinm@berkeley.edu
# Export environmental variables
#SBATCH --export=ALL
## Command(s) to run
# just to test it out
# echo "$1 input 1"
# echo "$2 input 2"
# echo "$3 input 3"
# ./cytosimParallelBash.sh 
# module load intel openmpi
# module load blas lapack intel/2016.4.072 openmpi
module load intel/2016.4.072 openmpi blas lapack
echo "$SLURM_NTASKS tasks total"
# all except first node run with this on
# LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/global/home/users/ferrinm/libraries/
# export LD_LIBRARY_PATH
ht_helper.sh -t cytosimParallelBash.sh -r $SLURM_NTASKS
