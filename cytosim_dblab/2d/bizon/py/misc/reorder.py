#!/usr/bin/env python
#
# copyright F. Nedelec, 2012

"""
     Rename files
    
Syntax:

     reorder.py [files]
      
Example:

     reorder.py image*.png
     
     will rename all the image files as:
     image0000.png, image0001.png, etc.

March 19 2012 by F. Nedelec.
"""

try:
    import sys, os
except ImportError:
    sys.stderr.write("  Error: could not load necessary python modules\n")
    sys.exit()

#------------------------------------------------------------------------

def rename(files):
    """rename files using consecutive numbers"""
    res = []
    cnt = 0
    for file in files:
        [main, ext] = os.path.splitext(file)
        root = main.rstrip('0123456789')
        name = file
        while cnt <= 9999:
            name = root + '%04i' % cnt + ext
            cnt += 1
            if name == file:
                break
            if not os.path.exists(name):
                os.rename(file, name)
                print("%s -> %s" % ( file, name ))
                break
        res.append(name)
    return res

#------------------------------------------------------------------------


def command(args):
    files = []
    
    for arg in args:
        if os.path.isfile(arg) or os.path.isdir(arg):
            files.append(arg)
        else:
            print("ignored '%s' on command line" % arg)
        
    try:
        rename(files)
    except IOError as e:
        print("Error: "+str(e))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1]=='help':
        print(__doc__)
    else:
        command(sys.argv[1:])


