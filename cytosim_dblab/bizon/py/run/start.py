#!/usr/bin/env python
# Start simulations in parallel.
# F. Nedelec

"""
    Start simulations in parallel.
    For each given config file, a new directory 'run????' is created in the current directory,
    and the simulation are started. The scripts returns without waiting for completion.

Syntax:

    start.py [executable] [repeat] [script.py] config-file [more-config-files]
    
    script.py if specified should provide a function parse(input, output)
        You may use: pre_config.py

    The default executable is 'sim', but it is possible to specify another one.

    
    F. Nedelec, 05.2007, 03.2010, 09.2012, 04.2013
"""

try:
    import sys, os, tempfile
    import go_sim_lib
except ImportError:
    sys.stderr.write("  Error: could not load necessary python modules\n")
    sys.exit()


#------------------------------------------------------------------------

def executable(arg):
    return os.path.isfile(arg) and os.access(arg, os.X_OK)


def run(exe, conf, root, preconf, repeat):
    """
    start simulations in parallel without waiting for completion
    """
    # generate config file:
    if preconf:
        wdir = tempfile.mkdtemp('', 'start.', '.')
    else:
        wdir = ''
    files = go_sim_lib.make_config(conf, preconf, repeat, wdir)

    if not files:
        out.write("Error: could not generate config files\n")
        sys.exit()

    # start simulations in parallel:
    for conf in files:
        try:
            (i, d) = go_sim_lib.start(exe, conf, root)
        except go_sim_lib.Error as e:
            out.write("Simulation could not be started: %s\n" % e)
        print("> process %i started in %-20s" %(i, d))


def command(args):
    """
    Info
    """
    exe = os.path.abspath('sim')
    preconf = ''
    repeat  = 1
    files   = []
    
    for arg in args:
        if arg.isdigit():
            repeat = int(arg)
        elif os.path.isfile(arg) and arg.endswith('.py'):
            preconf = arg
        elif os.path.isfile(arg) and '.cym' in arg:
            files.append(arg)
        elif executable(arg):
            exe = os.path.abspath(arg)
        else:
            sys.stderr.write("Error: unexpected argument `%s'\n" %arg)
            sys.exit()
    
    if not files:
        sys.stderr.write("You should specify a config file on the command line\n")
        sys.exit()
    
    if not executable(exe):
        sys.stderr.write("  Error:  please specify the executable\n")
        sys.exit()
    
    cnt = 0
    while os.path.exists('run%04i' % cnt):
        cnt = cnt+1
    
    for file in files:
        root = 'run%04i' % cnt
        run(exe, file, root, preconf, repeat)
        cnt = cnt+1



#------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1]=='help':
        print(__doc__)
    else:
        command(sys.argv[1:])


