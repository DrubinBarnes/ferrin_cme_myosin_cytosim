#!/bin/bash
python ~/google_drive/grad_school/db_lab/code/cytosim_dblab/ltpbukem/py/preconfig $1 "$2.cym.tpl"
# mkdir -p ~/google_drive/grad_school/db_lab/code/savio/simulations/$2
# mv "$2"0* ~/google_drive/grad_school/db_lab/code/savio/simulations/$2
mkdir $2
mv "$2"0* $2
echo "made and moved $2"
read -n1 -p "Do you want to send it up to the server? [Y/N] " answer
case $answer in
	Y | y) echo
		   echo "sending up to server"
		   
		   # scp -r ~/google_drive/grad_school/db_lab/code/savio/simulations/$2 ferrinm@dtn.brc.berkeley.edu:~/simulations/;;
       # scp -r $2 ferrinm@dtn.brc.berkeley.edu:~/simulations/;;
       scp -r $2 ferrinm@dtn.brc.berkeley.edu:/global/scratch/users/ferrinm/simulations/;;

	N | n) echo 
		   echo "goodbye"
	exit;;
esac

read -n1 -p "Do you want to visit the server? [Y/N] " answer
case $answer in
	Y | y) echo
		   echo "visiting server"
		   
		   ssh ferrinm@brc.berkeley.edu;;

	N | n) echo 
		   echo "goodbye"
	exit;;
esac

# this part doesn't show up once youre on the server
# read -n1 -p "Do you want to execute the simulation? [Y/N]" answer
# case $answer in
# 	Y | y) echo
# 		   read -p "type how many repeats of each cym file (ideally number of cym files x repeats is a multiple of 24)" answer2
# 		   ./savioParallelCym.sh $2 $answer2;;
		   

# 	N | n) echo 
# 		   echo "goodbye"
# 	exit;;
# esac

