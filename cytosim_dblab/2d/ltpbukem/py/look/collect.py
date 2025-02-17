#!/usr/bin/env python
#
# collect.py
#
# copyright F. Nedelec, 2007--2015


"""
Synopsis:
    
    Rename files or folders using a pattern containing consecutive numbers.
    Existing files will not be overwritten, and the index in the file name
    will be incremented automatically for each file.
    
Syntax:
    
    collect.py [--copy] PATTERN [index] FILE_NAMES
    
Examples:
    
    "collect.py image%04i.png image*.png"  will rename images as: image0000.png, image0001.png, etc.
    "collect.py --copy image%04i.png 1 run*/image.png"  will copy the images, starting from index 1
    
    
    F. Nedelec, 2012--2015.
"""


import sys, shutil, os


#------------------------------------------------------------------------


def move(paths, pattern, idx):
    """rename files using consecutive numbers"""
    import os
    res = []
    for src in paths:
        while idx < 100000:
            dst = pattern % idx
            idx += 1
            if dst == src:
                res.append(dst)
                break
            if not os.path.exists(dst):
                os.rename(src, dst)
                res.append(dst)
                print("%s -> %s" % (src, dst))
                break
    return res


def copy_recursive(src, dst):
    """Copy directory recursively"""
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    elif os.path.isdir(src):
        try:
            os.mkdir(dst)
        except OSError:
            pass
        files = os.listdir(src)
        for f in files:
            s = os.path.join(src, f)
            d = os.path.join(dst, f)
            copy_recursive(s, d)


def copy(paths, pattern, idx):
    """move files to 'root????' where '????' are consecutive numbers"""
    res = []
    for src in paths:
        while idx < 100000:
            dst = pattern % idx
            idx += 1
            if not os.path.exists(dst):
                copy_recursive(src, dst)
                res.append(dst)
                print("%s -> %s" % (src, dst))
                break
    return res


#------------------------------------------------------------------------


def command(args):
    """rename files"""
    paths = []
    idx = 0
    
    do_copy = False
    if args[0] == '-c' or args[0] == '--copy':
        do_copy = True
        args.pop(0);
    
    pattern = args.pop(0);
    
    if os.path.isfile(pattern):
        print("Error: first argument should be the pattern used to build output file name")
        return 1
    
    if args[0].isdigit():
        idx = int(args[0])
        args.pop(0);
    
    for arg in args:
        if os.path.isfile(arg) or os.path.isdir(arg):
            paths.append(arg)
        else:
            print("Error: '%s' is not a file or directory" % arg)
            return 1
    
    try:
        if do_copy:
            copy(paths, pattern, idx)
        else:
            move(paths, pattern, idx)
    except IOError as e:
        print("Error: "+str(e))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1]=='help':
        print(__doc__)
    else:
        command(sys.argv[1:])


