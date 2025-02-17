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

	cd ..
done

cd ..


# sed 's/$input/$insert\n$input/' myText.txt>myTex2t.txt