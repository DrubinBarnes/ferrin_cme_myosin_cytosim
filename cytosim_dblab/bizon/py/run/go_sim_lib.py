#!/usr/bin/env python
#
# mini python library to run Cytosim
#  it is used by go_sim.py
#
# Copyright F. Nedelec, May 19th, 2007-2012
# Revised Dec. 2007; March 2010; Oct 2011, Feb. 2012, Sept 2012, June 2014

"""
 Functions to start cytosim and handle directory creation / copy,
 as necessary to run a simulation on a cluster

F. Nedelec, March 2010, May 2012, June 2014
"""

try:
    import os, shutil, exceptions, subprocess
except ImportError:
    import sys
    host = os.getenv('HOSTNAME', 'unknown')
    sys.stderr.write("Error: could not load python modules on %s\n" % host)
    sys.exit()


class Error( exceptions.Exception ):
    """go_sim.py exception class"""
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        return repr(self.value)

# default name of the config file:
config_name = 'config.cym'


#==========================  DIR/FILES HANDLING ==============================


def make_directory(path, n=0):
    """
    Create a new directory name????,
    where ???? is a 4-digit number greater than n
    """
    ndir = path
    
    if path[-1].isdigit():
        path = path + '_'
    
    while n < 10000:
        try:
            os.mkdir(ndir)
            #print("made " + name)
            return ndir
        except OSError:
            ndir = path + '%04i' % n
        n += 1
    
    raise Error, "failed to create new run directory on "+os.getenv('HOSTNAME', 'unknown')


def copy_recursive(src, dst):
    """Copy directory recursively"""
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    elif os.path.isdir(src):
        os.mkdir(dst)
        files = os.listdir(src)
        for f in files:
            s = os.path.join(src, f)
            d = os.path.join(dst, f)
            copy_recursive(s, d)


def move_directory(path, park, name):
    """Copy directory 'path' to park, under a similar name"""
    src = os.path.abspath(path)
    if src == os.path.abspath(park):
        return src
    dst = make_directory(os.path.join(park,name))
    if not dst:
        sys.stderr.write("Error: failed to park '%s'\n" % path)
        return src
    #print("moving directory( %s -> %s )" % (src, dst))
    copy_recursive(src, dst)
    from filecmp import dircmp
    dcmp = dircmp(src, dst)
    if dcmp.left_only or dcmp.diff_files:
        sys.stderr.write("Error: could not copy '%s' identically\n" % path)
    else:
        shutil.rmtree(src)
    return dst


def make_config(conf, preconf, repeat, dest):
    """
    Generate config files by running a preconf script,
    or simply repeat the name if ( repeat > 1 ) and preconf==''.
    """
    module = {}
    if preconf:
        try:
            module = __import__(preconf.rstrip('.py'))
        except:
            import imp
            module = imp.load_source('pre_config', preconf)
        if not module:
            raise Error, "could not load python module `"+preconf+"'"
    if module:
        print("Using " + preconf)
        # use preconf to generate a new config file:
        return module.parse(conf, {}, repeat, dest)
    else:
        res = []
        for x in xrange(repeat):
            res.extend([conf]);
        return res


#=======================  RUNNING THE SIMULATION  ==============================

def run_here(exe, args):
    """
    Start executable in current directory, and wait for completion.
    The executable should find its default configuration file.
    The standard output is redirected to file `out.txt',
        and the standard error to 'err.txt'.
    """
    outname = 'out.txt'
    errname = 'err.txt'
    outfile = open(outname, 'w')
    errfile = open(errname, 'w')
    # run simulation
    if not args:
        code = subprocess.call(exe, stdout=outfile, stderr=errfile)
    else:
        code = subprocess.call([exe]+args, stdout=outfile, stderr=errfile)
    outfile.close()
    errfile.close()
    
    # remove output files if empty:
    if os.path.isfile(outname) and not os.path.getsize(outname):
        os.remove(outname)
    if os.path.isfile(errname) and not os.path.getsize(errname):
        os.remove(errname)

    if code == 127:
        raise Error, "failed to run '%s'" % exe
    return code


def write_infoB(logfile, exe, args, pid):
    import time
    with open(logfile, "w") as f:
        f.write("host      %s\n" % os.getenv('HOSTNAME', 'unknown'))
        f.write("user      %s\n" % os.getenv('USER', 'unknown'))
        f.write("wdir      %s\n" % os.getcwd())
        f.write("exec      %s\n" % exe)
        f.write("args      %s\n" % args)
        f.write("pid       %s\n" % pid)
        f.write("start     %s\n" % time.asctime())


def write_infoA(logfile, val):
    import time
    with open(logfile, "a") as f:
        f.write("status    %s\n" % val)
        f.write("end       %s\n" % time.asctime())


def run_with_info(exe, args, logfile='log.txt'):
    """
    Write some diverse informations into info_file,
    and call run_here(exe, args)
    """
    write_infoB(logfile, exe, args, os.getpid())
    val = run_here(exe, args)
    write_infoA(logfile, val)



def run(exe, conf, name, args=['-']):
    """
    Run one simulation in a new sub directory and wait for completion.
    The config file 'conf' is copied to the subdirectory.
    Returns sub-directory in which `exe` was called.
    """
    if not os.path.isfile(conf):
        raise Error, "missing/unreadable config file"
    conf = os.path.abspath(conf);    
    cdir = os.getcwd()
    #use the /scratch directory on the LSF cluster:
    if os.environ.has_key('LSB_JOBID'):
        import tempfile
        wdir = tempfile.mkdtemp('', 'run.', '/scratch/ned')
    else:
        wdir = make_directory(name)
    os.chdir(wdir)
    shutil.copyfile(conf, config_name)
    run_with_info(exe, args)
    os.chdir(cdir)
    return wdir


def start(exe, conf, name, args=['-']):
    """
    Start simulation in a new sub directory, and return immediately.
    The config file `conf` is copied to the sub-directory.
    """
    if not os.path.isfile(conf):
        raise Error, "missing/unreadable config file"
    cdir = os.getcwd()
    wdir = make_directory(name)
    shutil.copyfile(conf, os.path.join(wdir,config_name))
    os.chdir(wdir)
    outfile = open('out.txt', 'w')
    errfile = open('err.txt', 'w')
    #start simulation, but do not wait for completion:
    pid = subprocess.Popen(['nohup', exe]+args, stdout=outfile, stderr=errfile).pid
    write_infoB('log.txt', exe, args, pid)
    os.chdir(cdir)
    return (pid, wdir)


