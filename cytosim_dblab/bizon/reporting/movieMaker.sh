#!/bin/bash
# try to add something here 
echo "adding display params"

# input='ab'

# insert='setzz'

# expecting a 

cd "$1"

# to iterate over dif folders

for d in */ ; do
	cd "$d"
	echo "$d"
	
	# check if the simul:display is already present

	if grep -Fq simul:display properties.cmo
	then
		echo "display text already inserted"
	else
		
	sed -i.tmp 's|set space 0 cell|set simul:display *\
	{\
	zoom           = 1.5;\
	focus          = -0.012 -0.0 -0.25;\
	rotation       = -0.54 -0.5 -0.45 0.5;\
	window_size    = 1300, 800;\
	couple_select  = 7;\
	point_size     = 8;\
	}\
	set space 0 cell|' properties.cmo
	echo "added display text"
	# change blue filaments to white. this isn't necessary for it to run.
	sed -i.tmp '
		/display        = (line = 5, 2/ c\
		display        = (line = 5, 1; point = 1; end_style = 5; rainbow = 0.01);
		' properties.cmo
	echo "changed filament color"
	fi
	cd ..
done

cd ..
# run movie maker
echo "making movies"

py/look/make_movie.py bin/play lazy=0 $1/output*

# sed 's/$input/$insert\n$input/' myText.txt>myTex2t.txt