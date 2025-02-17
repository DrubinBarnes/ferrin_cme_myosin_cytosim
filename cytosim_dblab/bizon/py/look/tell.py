#!/usr/bin/env python
#
#
#
# F. Nedelec, Jan 24th, 2008, March 2010, July 2014

"""
    Print parameters from multiple files in column format
    
Syntax:
    
    tell.py parameter-names [directories/files]

"""


import sys, os
sep = ','


def format_value(val):
    if type(val) is str:
        return val
    if type(val) is dict:
        r = ""
        s = "{ "
        for k in sorted(val):
            r += s + str(k) + " = " + format_value(val[k])
            s = "; "
        return r + "; }"
    try:
        r = ""
        s = ""
        for k in val:
            r += s + format_value(k)
            s = ", "
        return r
    except:
        return str(val)


def column_width(table):
    """calculate the width of the stuff"""
    w = []
    for line in table:
        for i in xrange(len(line)):
            while i >= len(w):
                w.append(0)
            v = len(format_value(line[i]))
            if v > w[i]:
                w[i] = v
    return w


def format_table(table):
    """print table in tidy column format"""
    width = column_width(table)
    indx = range(len(width))
    res = ""
    for line in table:
        spc = ""
        val = ""
        for i in indx:
            if not line[i]:
                v = "-"+sep
            else:
                v = format_value(line[i])+sep
            val += v.ljust(width[i]+5)
        res += val.rstrip(sep+" ") + "\n"
    return res


def config_file(arg):
    """return name of probable config-file"""
    if os.path.isdir(arg):
        file = os.path.join(arg, 'config.cym')
        if os.path.isfile(file):
            return file
    if os.path.isfile(arg):
        return arg
    return ""


def find_any(str, chars):
    r = len(str)
    for c in chars:
        x = str.find(c)
        if x >= 0 and x < r:
            r = x
    return r


def find_value(file, key):
    """find value corresponding to key. Multiple values are concatenated"""
    val = []
    for line in file:
        inx = line.find(key)
        if inx >= 0:
            r = line.find('=', inx)
            if r > inx:
                e = find_any(line, '\n,;}%')
                v = line[r+1:e].strip()
                val.append(v)
    return val



def tell(files, keys):
    """print parameter from multiple files in columns"""
    res=[]
    line = ['%% file']
    line.extend(keys)
    res.append(line)
    
    for f in files:
        try:
            file = open(f, "r")
            vals = []
            for key in keys:
                file.seek(0)
                vals.append(find_value(file, key))
            file.close()
            line = [f]
            line.extend(vals)
            res.append(line)
        except IOError:
            continue
    return res;


#------------------------------------------------------------------------

def command(args):
    """print parameter from multiple files in columns"""
    paths = []
    keys = []
    for arg in args:
        if os.path.exists(arg):
            if arg.endswith('.cym') or os.path.isdir(arg):
                paths.append(arg)
        else:
            keys.append(arg)
    
    if not paths:
        print(__doc__)
        return

    files = []
    for p in paths:
        files.append(config_file(p))
    
    table = tell(files, keys)
    print(format_table(table))



if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=='help':
        print(__doc__)
    else:
        command(sys.argv[1:])



