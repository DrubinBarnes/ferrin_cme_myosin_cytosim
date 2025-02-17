#!/usr/bin/env python
#
# battery_test.py
#
# copyright F. Nedelec, March 19 2011

"""
battery_test.py:

    run a battery of .cym files to check cytosim

Example - live:

    battery_test.py bin/play live cym/*.cym

Example - runs:

    battery_test.py bin/sim cym/*.cym
    make_image.py 'play frame=100 window_size=512,512' *_cym

F. Nedelec, March-June 2011 - Feb 2013
"""

import shutil, sys, os, subprocess

executable = 'cytosim'

#------------------------------------------------------------------------

def run_live(file):
    """run live test"""
    
    print file.center(100, '~')
    cmd = executable + ['live', file]
    val = subprocess.call(cmd)

    if val != 0:
        print('returned %i' % val)

#------------------------------------------------------------------------

def run(file):
    """run test in separate directory"""
    
    cdir = os.getcwd()
    name = os.path.split(file)[1]
    dname = "run-"+name.partition('.')[0];
    
    os.mkdir(dname)
    shutil.copyfile(file, os.path.join(dname, 'config.cym'))
    os.chdir(dname)
    print('\n->>>>>> RUN  '+file+'\n')
    
    cmd = executable + ['-']
    val = subprocess.call(cmd)
    
    if val != 0:
        print('returned %i' % val)
    
    os.chdir(cdir);

#------------------------------------------------------------------------

def command(args):
    
    global executable
    files = []
    live = False;
    err = sys.stderr;
    
    executable = args[0].split()
    if os.access(executable[0], os.X_OK):
        executable[0] = os.path.abspath(executable[0])
    else:
        err.write("Error: you must specify an executable on the command line\n")
        sys.exit()

    for arg in args[1:]:
        if os.path.isfile(arg):
            files.append(os.path.abspath(arg))
        elif arg=='live':
            live = True
        else:
            err.write("Ignored`"+arg+"' on the command line\n")


    if not files:
        print("You must specify config files!")
        sys.exit()

    if live:
        for f in files:
            run_live(f)
    else:
        for f in files:
            run(f)


#------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv)<2 or sys.argv[1]=='help':
        print(__doc__)
    else:
        command(sys.argv[1:])

