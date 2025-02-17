#!/usr/bin/env python
#
# get_data.py
#
# simple extraction of data from files
#
# copyright F. Nedelec, Jan 2011 - 2012

"""
    Visit given run directories, and print data to standard output

Syntax:

    get_data.py DIRECTORIES
    
Example:

    get_data run???? > data.txt

Description:

    This script must be customized for any meaningful application,
    but it should be a useful template to start from.
    Please make a copy of the script with a different name.
    
    

F. Nedelec, Aug 2011 - 2012
"""

import sys, os

#------------------------------------------------------------------------

def find_value(file, key):
    """
    Find values corresponding to 'key' in the file.
    Multiple values are concatenated.
    """
    val = ""
    for line in file:
        inx = line.find(key)
        if inx >= 0:
            r = line.find('=', inx)
            if r > inx:
                v = line[r+1:].strip()
                if len(val):
                    val += '|' + v
                else:
                    val = v
    return val


def get_cell(file, ii, jj):
    """
    Extract the jj-th word from line ii
    If jj is an array, the corresponding values will be concatenated
    """
    if len(jj) == 0:
        return '';
    cnt = 0
    for line in file:
        cnt = cnt + 1
        if cnt == ii:
            s = line.split()
            val = s[jj[0]]
            for n in jj[1:]:
                val = ' ' + s[n] 
            return val
    return ''


#------------------------------------------------------------------------

def get_data(path):
    """ 
    This extracts one parameter from the config file,
    and two values read from 'fibers.txt'
    """
    #print get_val('config.cym', [73], [8]),
    try:
        f = open(path+'/config.cym', 'r')
        print find_value(f, 'viscosity')
    except IOError as e:
        print(e)

    try:
        f = open(path+'/fibers.txt', 'r')
        get_cell(f, 2, [3,4])
    except IOError as e:
        print(e)

#------------------------------------------------------------------------

def command(files):
    for f in files:
        if os.path.isdir(f):
            get_data(f)
        else:
            sys.stderr.write("The argument `"+f+" is not a directory and was ignored\n")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1]=='help':
        print(__doc__)
    else:
        command(sys.argv[1:])


