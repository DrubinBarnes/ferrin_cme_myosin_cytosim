#!/bin/bash
echo "modifying display params"

# this script lets you replace lines in the "properties.cmo" subfolders
# e.g. on the focus, actin filament color. 
# currently focus & zoom for larger size simulations.

# expecting an argument for which folder it is
# could include an error message
cd "$1"

# to iterate over dif folders

for d in */ ; do
	cd "$d"
	echo "$d"
	
	# check if the simul:display is already present

	if grep -Fq simul:display properties.cmo
	then
		echo "replacing display text"
		# zoom (larger sim)
		sed -i.tmp '
		/zoom/ c\
		 zoom 	= 1.5
		' properties.cmo
		# focus (larger sim)
		sed -i.tmp '
		/focus/ c\
		focus   = -0.012 -0.0 -0.25;
		' properties.cmo
		# rotation (larger sim)
		sed -i.tmp '
		/rotation/ c\
		rotation   = -0.54 -0.5 -0.45 0.5;
		' properties.cmo

		# actin blue to white
		sed -i.tmp '
		/display        = (line = 5, 2/ c\
		display        = (line = 5, 1; point = 1; end_style = 5; rainbow = 0.01);
		' properties.cmo

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
	echo "inserted display text"
	fi
	cd ..
done

cd ..
# run movie maker
echo "making movies"

py/look/make_movie.py bin/play lazy=0 $1/output*

# sed 's/$input/$insert\n$input/' myText.txt>myTex2t.txt