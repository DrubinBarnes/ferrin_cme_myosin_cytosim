import IPython
from tabulate import tabulate
import math
import numpy as np
import pandas as pd
import os
import shutil
import subprocess
from subprocess import Popen
import datetime
import matplotlib.pyplot as plt  # plotting
import seaborn as sns  # nicer plotting
from decimal import Decimal
from matplotlib.colors import LogNorm
from matplotlib.colors import SymLogNorm
from scipy.stats import binned_statistic_2d

def test_func():
    print('test3')

def find_directories():
    output_dirs = []
    config_dirs = []

    for d in next(os.walk('simulations/'))[1]:
        for f in os.listdir('simulations/'+d):
            if f.endswith('.cym'):
                config_dirs.append(d)
                break
        for sd in next(os.walk('simulations/'+d))[1]:
            if sd.endswith('output') or sd.startswith('run'):
                output_dirs.append(d)
                break


    return(output_dirs, config_dirs)

def report_sims(working_dir, output_dirs, config_dirs, cytosim_dir,
                report, replace_movies):
    os.chdir(working_dir)

    solid_allruns_allparams = dict()
    properties_allruns_allparams = dict()
    configs_allruns_allparams = dict()
    single_hip1r_allruns_allparams = dict()
    single_membrane_myosin_allruns_allparams = dict()
    fiber_forces_allruns_allparams = dict()
    fiber_tensions_allruns_allparams = dict()
    fiber_clusters_allruns_allparams = dict()
    fiber_ends_allruns_allparams = dict()
    rundirs_allparams = dict()

    total_runs = 0

    # config = open(config_sweep, 'r')
    # config_lines = config.readlines()
    # config.close()

    for output_dir in output_dirs:
    #for output_dir in [output_dirs[0]]:
        config_dir = output_dir.replace('_output', '')
        if config_dir in config_dirs:
            config_exists = 'yes'
        else:
            config_exists = 'no'
        configs_allruns = dict()
        solid_allruns = dict()
        single_hip1r_allruns = dict()
        single_membrane_myosin_allruns = dict()
        fiber_cluster_allruns = dict()
        properties_allruns = dict()
        fiber_forces_allruns = dict()
        fiber_tensions_allruns = dict()
        fiber_ends_allruns = dict()
        rundirs = []
        #subprocess.call(['bash', os.path.join(cytosim_dir,'../modProperties.sh'), os.path.join('simulations/',output_dir)])
        for rundir in os.listdir('simulations/' + output_dir):
        #for rundir in [os.listdir('simulations/' + output_dir)[0]]:
        #for rundir in ['output01_0000']:
            reportdir = 'simulations/'+output_dir+'/'+rundir
            run_num = rundir.split('_')[0][-4:]
            conf_file = 'simulations/'+config_dir+'/'+config_dir+run_num+'.cym'
            if rundir.startswith('output') or rundir.startswith('run') and 'properties.cmo' in os.listdir(reportdir):
                if config_exists == 'yes':
                    conf = open(conf_file, 'r')
                    configs_allruns[rundir] = conf.readlines()
                    conf.close()
                os.chdir(reportdir)
                if report == 'yes':
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                    'solid', 'output=solid.txt'])
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                    'single:hip1r', 'output=single_hip1r.txt'])
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                'single:membrane_myosin', 'output=single_membrane_myosin.txt'])
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                    'fiber:forces', 'output=fiber_forces.txt'])
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                'fiber:ends', 'output=fiber_ends.txt'])
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                'fiber:clusters', 'output=fiber_clusters.txt'])
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                'fiber:tensions', 'output=fiber_tensions.txt'])
                solid = open('solid.txt', 'r')
                solid_allruns[rundir] = solid.readlines()
                solid.close()
                single_hip1r = open('single_hip1r.txt', 'r')
                single_hip1r_allruns[rundir] = single_hip1r.readlines()
                single_hip1r.close()
                single_membrane_myosin = open('single_membrane_myosin.txt', 'r')
                single_membrane_myosin_allruns[rundir] = single_membrane_myosin.readlines()
                single_membrane_myosin.close()
                fiber_cluster = open('fiber_clusters.txt', 'r')
                fiber_cluster_allruns[rundir] = fiber_cluster.readlines()
                fiber_cluster.close()
                fiber_forces = open('fiber_forces.txt', 'r')
                fiber_forces_allruns[rundir] = fiber_forces.readlines()
                fiber_forces.close()
                fiber_tensions = open('fiber_tensions.txt', 'r')
                fiber_tensions_allruns[rundir] = fiber_tensions.readlines()
                fiber_tensions.close()
                fiber_ends = open('fiber_ends.txt', 'r')
                fiber_ends_allruns[rundir] = fiber_ends.readlines()
                fiber_ends.close()
                properties = open('properties.cmo', 'r')
                properties_allruns[rundir] = properties.readlines()
                properties.close()
                rundirs.append(rundir)
                total_runs += 1
                #print ('finished reporting ' + output_dir + ' ' + rundir)
                if replace_movies == 'yes':
                    if 'movie.mp4' in os.listdir('.'):
                        os.remove('movie.mp4')
                    #%run -i cytosim_dir+'make_movie.py' cytosim_dir+'bin/play'
                    subprocess.call(['python', os.path.join(cytosim_dir,'../make_movie.py'),
                                    os.path.join(cytosim_dir,'bin/play')])
                    print ('finished making video of ' + output_dir + ' ' + rundir)
                os.chdir(working_dir)
        rundirs_allparams[output_dir] = rundirs
        solid_allruns_allparams[output_dir] = solid_allruns
        single_hip1r_allruns_allparams[output_dir] = single_hip1r_allruns
        single_membrane_myosin_allruns_allparams[output_dir] = single_membrane_myosin_allruns
        fiber_forces_allruns_allparams[output_dir] = fiber_forces_allruns
        fiber_clusters_allruns_allparams[output_dir] = fiber_cluster_allruns
        fiber_tensions_allruns_allparams[output_dir] = fiber_tensions_allruns
        fiber_ends_allruns_allparams[output_dir] = fiber_ends_allruns
        properties_allruns_allparams[output_dir] = properties_allruns
        configs_allruns_allparams[output_dir] = configs_allruns
        print ('finished reporting ' + output_dir)

    return(
        solid_allruns_allparams,
        properties_allruns_allparams,
        configs_allruns_allparams,
        single_hip1r_allruns_allparams,
        single_membrane_myosin_allruns_allparams,
        fiber_forces_allruns_allparams,
        fiber_clusters_allruns_allparams,
        fiber_tensions_allruns_allparams,
        fiber_ends_allruns_allparams,
        rundirs_allparams,
        total_runs
    )

def report_fiber_ends(working_dir, output_dirs, config_dirs, cytosim_dir,
                report, replace_movies):
    os.chdir(working_dir)

    properties_allruns_allparams = dict()
    configs_allruns_allparams = dict()
    fiber_ends_allruns_allparams = dict()
    rundirs_allparams = dict()

    total_runs = 0

    for output_dir in output_dirs:
        config_dir = output_dir.replace('_output', '')
        if config_dir in config_dirs:
            config_exists = 'yes'
        else:
            config_exists = 'no'
        configs_allruns = dict()
        properties_allruns = dict()
        fiber_ends_allruns = dict()
        rundirs = []
        for rundir in os.listdir('simulations/' + output_dir):
            reportdir = 'simulations/'+output_dir+'/'+rundir
            run_num = rundir.split('_')[0][-4:]
            conf_file = 'simulations/'+config_dir+'/'+config_dir+run_num+'.cym'
            if rundir.startswith('output') or rundir.startswith('run') and 'properties.cmo' in os.listdir(reportdir):
                if config_exists == 'yes':
                    conf = open(conf_file, 'r')
                    configs_allruns[rundir] = conf.readlines()
                    conf.close()
                os.chdir(reportdir)
                if report == 'yes':
                    subprocess.call([os.path.join(cytosim_dir, 'bin/report'),
                                'fiber:ends', 'output=fiber_ends.txt'])
                fiber_ends = open('fiber_ends.txt', 'r')
                fiber_ends_allruns[rundir] = fiber_ends.readlines()
                fiber_ends.close()
                properties = open('properties.cmo', 'r')
                properties_allruns[rundir] = properties.readlines()
                properties.close()
                rundirs.append(rundir)
                total_runs += 1
                if replace_movies == 'yes':
                    if 'movie.mp4' in os.listdir('.'):
                        os.remove('movie.mp4')
                    subprocess.call(['python', os.path.join(cytosim_dir,'../make_movie.py'),
                                    os.path.join(cytosim_dir,'bin/play')])
                    print ('finished making video of ' + output_dir + ' ' + rundir)
                os.chdir(working_dir)
        rundirs_allparams[output_dir] = rundirs
        fiber_ends_allruns_allparams[output_dir] = fiber_ends_allruns
        properties_allruns_allparams[output_dir] = properties_allruns
        configs_allruns_allparams[output_dir] = configs_allruns
        print ('finished reporting ' + output_dir)

    return(
        properties_allruns_allparams,
        configs_allruns_allparams,
        fiber_ends_allruns_allparams,
        rundirs_allparams,
        total_runs
    )

def props_configs(output_dirs, rundirs_allparams, properties_allruns_allparams, configs_allruns_allparams):
    properties_list = []
    config_list = []

    for output_dir in output_dirs:
        properties_dict_allruns = dict()
        config_dict_allruns = dict()
        # for line in config_lines:
        #     if 'x =' in line:
        #         membrane_myosins = line.strip().strip('[[ x = [').strip('] ]]').split(', ')
        #     if 'y =' in line:
        #         myosins_radius = line.strip().strip('[[ y = [').strip('] ]]').split(', ')

        for rundir in rundirs_allparams[output_dir]:
            properties = properties_allruns_allparams[output_dir][rundir]
            conf = configs_allruns_allparams[output_dir][rundir]
            properties_dict = dict()
            config_dict = dict()
            # added this because not all properites have these parameters set, which
            # messes up the dataframe later
            properties_dict['internalize.cym_viscosity'] = 1
            properties_dict['blobneck_viscosity'] = 1
            properties_dict['bud_viscosity'] = 1
            config_dict['bud_viscosity'] = 1
            config_dict['blobneck_viscosity'] = 1
            for line in properties:
                if 'set' in line:
                    obj = line.strip().split(' ')[-1]
                if '=' in line:
                    line = line.strip().split(' = ')
                    param = line[0].strip()
                    val = line[-1].strip(';')
                    if val.isnumeric() == True:
                        val = float(val)
                    properties_dict[obj+'_'+param] = val

            for line in conf:
                if line.strip().startswith('%'):
                    continue
                if '%' in line:
                    line = line.split('%')[0]
                if 'set' in line:
                    obj = line.strip().split(' ')[-1]
                if '=' in line:
                    line = line.strip().split(' = ')
                    param = line[0].strip()
                    val = line[-1].strip(';')
                    if val.isnumeric() == True:
                        val = float(val)
                    config_dict[obj+'_'+param] = val
                if 'new' in line:
                    line = line.strip().split(' ')
                    obj = line[-1]
                    val = line[1]
                    # if type(val) != int:
                    #     val = 1
                    config_dict[obj+'_number'] = val

            # properties_dict['unbinding_rate'] = properties_dict['unbinding'].split(' ')[0].strip(',')
            # properties_dict['unbinding_force'] = properties_dict['unbinding'].split(' ')[-1]
            if 'actin_catastrophe_rate' in config_dict.keys():
                config_dict['actin_catastrophe_rate'] = float(config_dict['actin_catastrophe_rate'].split(',')[0])
            if 'bud_confine' in config_dict.keys():
                config_dict['bud_confine'] = float(config_dict['bud_confine'].split(',')[1])
                properties_dict['bud_confine'] = float(properties_dict['bud_confine'].split(',')[1])
            if 'membrane_myosin_position' in config_dict.keys():
                config_dict['membrane_myosin_zoffset'] = float(config_dict['membrane_myosin_position'].split(' ')[-5])+0.4
            properties_dict_allruns[rundir] = properties_dict
            config_dict_allruns[rundir] = config_dict
            # print 'finished reading ' + output_dir + ' ' + rundir + ' properties'

        properties_df = pd.DataFrame.from_dict(properties_dict_allruns, orient = 'index')
        properties_list.append(properties_df)
        config_df = pd.DataFrame.from_dict(config_dict_allruns, orient = 'index')
        config_list.append(config_df)

    properties_allparams = pd.concat(properties_list, keys = output_dirs,
                                names = ['param_sweep', 'run'])

    config_allparams = pd.concat(config_list, keys = output_dirs,
                                names = ['param_sweep', 'run'])

    return(properties_allparams, config_allparams)

def solid_positions(output_dirs, rundirs_allparams, solid_allruns_allparams):
    solid_list = []

    for output_dir in output_dirs:
        solid_outputs_allruns = []
        rundirs = rundirs_allparams[output_dir]
        for rundir in rundirs:
            all_lines = solid_allruns_allparams[output_dir][rundir]
            timepoints = []
            outputs = []
            for line in all_lines:
                line = line.strip()
                if line.startswith('%'):
                    if line.startswith('% time'):
                        time = float(line.split(' ')[-1])
                        timepoints.append(time)
                        solids = {}
                    elif line.startswith('% end'):
                        df = pd.DataFrame.from_dict(solids, orient = 'index')
                        outputs.append(df)
                        # print 'finished parsing ' + rundir + ' timepoint ' + str(time)
                elif len(line.split()) > 0:
                    [solid_class, solid_id, centroid_x, centroid_y, centroid_z,
                    point_x, point_y, point_z, idk1, idk2, idk3] = line.split()
                    solids[int(solid_id)] = {'xpos': float(point_x), 'ypos' : float(point_y),
                                        'zpos' : float(point_z)}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                    names = ['time', 'id'])
            # all_outputs = all_outputs.swaplevel('time','id',axis=0).sort_index()
            solid_outputs_allruns.append(all_outputs)

        all_solid_outputs_allruns = pd.concat(solid_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])

        all_solid_outputs_allruns['internalization'] = all_solid_outputs_allruns['zpos'] + 0.4
        solid_list.append(all_solid_outputs_allruns)

        print('finished parsing ' + output_dir)

    solid_allparams = pd.concat(solid_list, keys = output_dirs,
                                names = ['param_sweep', 'run', 'time', 'id'])

    return(solid_allparams)

def all_hip1r(output_dirs, rundirs_allparams, single_hip1r_allruns_allparams):
    hip1r_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        single_hip1r_outputs_allruns = []
        for rundir in rundirs:
            single_all_lines = single_hip1r_allruns_allparams[output_dir][rundir]
            timepoints = []
            outputs = []
            for line in single_all_lines:
                line = line.strip()
                if line.startswith('%'):
                    if line.startswith('% time'):
                        time = float(line.split(' ')[-1])
                        timepoints.append(time)
                        singles = {}
                    elif line.startswith('% end'):
                        df = pd.DataFrame.from_dict(singles, orient = 'index')
                        outputs.append(df)
                        # print 'finished parsing ' + rundir + ' timepoint ' + str(time)
                elif len(line.split()) > 0:
                    [single_class, single_id, state, xpos, ypos, zpos, xforce, yforce, zforce, fiber_id, direction, abscissa, abscissa_plus, dir_from_plus] = line.split()[:14]
                    singles[int(single_id)] = {'state' : int(state), 'fiber_id' : int(fiber_id),
                                            'xpos': float(xpos), 'single_id' : int(single_id),
                                            'ypos' : float(ypos), 'zpos': float(zpos),
                                            'xforce' : float(xforce), 'yforce' : float(yforce),
                                            'zforce': float(zforce), 'abscissa' : float(abscissa),
                                            'direction' : float(direction)}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                names = ['time', 'id'])
            # all_outputs = all_outputs.swaplevel('time','id',axis=0).sort_index()
            all_outputs['scalar_force'] = np.sqrt(np.square(all_outputs['xforce']) +
                                                np.square(all_outputs['yforce']) +
                                                np.square(all_outputs['zforce']))
            all_outputs['rpos'] = np.sqrt(np.square(all_outputs['xpos']) +
                                        np.square(all_outputs['ypos']))

            single_hip1r_outputs_allruns.append(all_outputs)


        all_single_hip1r = pd.concat(single_hip1r_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])

        # bound_hip1r = all_single_hip1r.loc[all_single_hip1r['state'] == 1]
        hip1r_list.append(all_single_hip1r)

        print('finished parsing ' + output_dir)

    hip1r_allparams = pd.concat(hip1r_list, keys = output_dirs,
                                names = ['param_sweep', 'run', 'time', 'id'])

    return(hip1r_allparams)

def all_myosin(output_dirs, rundirs_allparams, single_membrane_myosin_allruns_allparams):
    membrane_myosin_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        single_membrane_myosin_outputs_allruns = []
        for rundir in rundirs:
            single_all_lines = single_membrane_myosin_allruns_allparams[output_dir][rundir]
            timepoints = []
            outputs = []
            for line in single_all_lines:
                line = line.strip()
                if line.startswith('%'):
                    if line.startswith('% time'):
                        time = float(line.split(' ')[-1])
                        timepoints.append(time)
                        singles = {}
                    elif line.startswith('% end'):
                        df = pd.DataFrame.from_dict(singles, orient = 'index')
                        outputs.append(df)
                        # print 'finished parsing ' + rundir + ' timepoint ' + str(time)
                elif len(line.split()) > 0:
                    [single_class, single_id, state, xpos, ypos, zpos, xforce, yforce, zforce,
                    fiber_id, xdirection, ydirection, zdirection, abscissa] = line.split()[:14]
                    singles[int(single_id)] = {'state' : int(state), 'fiber_id' : int(fiber_id),
                                            'xpos': float(xpos), 'single_id' : int(single_id),
                                            'ypos' : float(ypos), 'zpos': float(zpos),
                                            'xforce' : float(xforce), 'yforce' : float(yforce),
                                            'zforce': float(zforce), 'abscissa' : float(abscissa),
                                            'xdirection' : float(xdirection), 'ydirection' : float(ydirection),
                                            'zdirection' : float(zdirection)}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                names = ['time', 'id'])
            # all_outputs = all_outputs.swaplevel('time','id',axis=0).sort_index()
            all_outputs['scalar_force'] = np.sqrt(np.square(all_outputs['xforce']) +
                                                np.square(all_outputs['yforce']) +
                                                np.square(all_outputs['zforce']))
            all_outputs['rpos'] = np.sqrt(np.square(all_outputs['xpos']) +
                                        np.square(all_outputs['ypos']))

            single_membrane_myosin_outputs_allruns.append(all_outputs)

        all_single_membrane_myosin = pd.concat(single_membrane_myosin_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])

        # bound_membrane_myosin = all_single_membrane_myosin.loc[all_single_membrane_myosin['state'] == 1]
        membrane_myosin_list.append(all_single_membrane_myosin)

        print('finished parsing ' + output_dir)

    membrane_myosin_allparams = pd.concat(membrane_myosin_list, keys = output_dirs,
                                names = ['param_sweep', 'run', 'time', 'id'])

    return(membrane_myosin_allparams)

def get_fiber_forces(output_dirs, rundirs_allparams, fiber_forces_allruns_allparams):
    forces_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        fiber_forces_outputs_allruns = []
        for rundir in rundirs:
            single_all_lines = fiber_forces_allruns_allparams[output_dir][rundir]
            timepoints = []
            outputs = []
            for line in single_all_lines:
                line = line.strip()
                if line.startswith('%'):
                    if line.startswith('% time'):
                        time = float(line.split(' ')[-1])
                        timepoints.append(time)
                        singles = {}
                    elif line.startswith('% end'):
                        df = pd.DataFrame.from_dict(singles, orient = 'index')
                        outputs.append(df)
                        # print 'finished parsing ' + rundir + ' timepoint ' + str(time)
                elif len(line.split()) > 0:
                    [fiber_id, fiber_point, xpos, ypos, zpos,
                    xforce, yforce, zforce, idk1] = line.split()
                    singles[str(fiber_id)+'_'+str(fiber_point)] = {'fiber_id' : int(fiber_id),
                                                                'fiber_point' : int(fiber_point),
                                            'xpos': float(xpos), 'ypos' : float(ypos), 'zpos': float(zpos),
                                            'xforce' : float(xforce), 'yforce' : float(yforce),
                                            'zforce': float(zforce)}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                names = ['time', 'id'])
            # all_outputs = all_outputs.swaplevel('time','id',axis=0).sort_index()
            all_outputs['scalar_force'] = np.sqrt(np.square(all_outputs['xforce']) +
                                                np.square(all_outputs['yforce']) +
                                                np.square(all_outputs['zforce']))
            all_outputs['rpos'] = np.sqrt(np.square(all_outputs['xpos']) +
                                        np.square(all_outputs['ypos']))

            fiber_forces_outputs_allruns.append(all_outputs)

        all_fiber_forces = pd.concat(fiber_forces_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])

        forces_list.append(all_fiber_forces)

        print('finished parsing ' + output_dir)

    forces_allparams = pd.concat(forces_list, keys = output_dirs,
                                names = ['param_sweep', 'run', 'time', 'id'])

    return(forces_allparams)

def get_fiber_ends(output_dirs, rundirs_allparams, fiber_ends_allruns_allparams):
    ends_list = []
    for output_dir in [output_dirs[0]]:
        rundirs = rundirs_allparams[output_dir]
        fiber_ends_outputs_allruns = []
        for rundir in [rundirs[0]]:
            single_all_lines = fiber_ends_allruns_allparams[output_dir][rundir]
            timepoints = []
            outputs = []
            for line in single_all_lines:
                line = line.strip()
                if line.startswith('%'):
                    if line.startswith('% time'):
                        time = float(line.split(' ')[-1])
                        timepoints.append(time)
                        singles = {}
                    elif line.startswith('% end'):
                        df = pd.DataFrame.from_dict(singles, orient = 'index')
                        outputs.append(df)
                        #print('finished parsing ' + rundir + ' timepoint ' + str(time))
                elif len(line.split()) > 0:
                    [fiber_class, fiber_id, length, minus_state, minus_xpos, minus_ypos, minus_zpos,
                    minus_xdir, minus_ydir, minus_zdir, plus_state, plus_xpos, plus_ypos,
                    plus_zpos, plus_xdir, plus_ydir, plus_zir] = line.split()
                    singles[int(fiber_id)] = {'fiber_id' : int(fiber_id), 'length':float(length),
                                            'minus_state':int(minus_state), 'minus_xpos':float(minus_xpos),
                                            'minus_ypos':float(minus_ypos), 'minus_zpos':float(minus_zpos),
                                            'minus_xdir':float(minus_xdir), 'minus_ydir':float(minus_ydir),
                                            'minus_zdir':float(minus_zdir), 'plus_state':int(plus_state),
                                            'plus_xpos':float(plus_xpos), 'plus_ypos':float(plus_ypos),
                                            'plus_zpos':float(plus_zpos), 'plus_xdir':float(plus_xdir),
                                            'plus_ydir':float(plus_ydir), 'plus_zir':float(plus_zir),
                                            'growth':np.NaN}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                names = ['time', 'id'])
            if len(all_outputs) > 0:
                all_outputs['plus_rpos'] = np.sqrt(np.square(all_outputs['plus_xpos']) +
                                            np.square(all_outputs['plus_ypos']))

            lengths = dict()
            for i, timepoint in enumerate(timepoints):
                lengths[i] = all_outputs.loc[timepoint,'length']
                if i > 0:
                    all_outputs.loc[timepoint,'growth'] = list(lengths[i] - lengths[i-1])
                else:
                    all_outputs.loc[timepoint,'growth'] = list(lengths[i] - lengths[i])

            fiber_ends_outputs_allruns.append(all_outputs)


        all_fiber_ends = pd.concat(fiber_ends_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])
        ends_list.append(all_fiber_ends)
        print('finished parsing ' + output_dir)
    ends_allparams = pd.concat(ends_list, keys = output_dirs,
            names = ['param_sweep', 'run', 'time', 'id'])

    return(ends_allparams)

def get_fiber_ends_2d(output_dirs, rundirs_allparams, fiber_ends_allruns_allparams):
    ends_list = []
    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        fiber_ends_outputs_allruns = []
        for rundir in rundirs:
            single_all_lines = fiber_ends_allruns_allparams[output_dir][rundir]
            timepoints = []
            outputs = []
            for line in single_all_lines:
                line = line.strip()
                if line.startswith('%'):
                    if line.startswith('% time'):
                        time = float(line.split(' ')[-1])
                        timepoints.append(time)
                        singles = {}
                    elif line.startswith('% end'):
                        df = pd.DataFrame.from_dict(singles, orient = 'index')
                        outputs.append(df)
                        #print('finished parsing ' + rundir + ' timepoint ' + str(time))
                elif len(line.split()) > 0:
                    [fiber_class, fiber_id, length, minus_state, minus_xpos, minus_ypos,
                    minus_xdir, minus_ydir, plus_state, plus_xpos, plus_ypos,
                    plus_xdir, plus_ydir] = line.split()
                    singles[int(fiber_id)] = {'fiber_id' : int(fiber_id), 'length':float(length),
                                            'minus_state':int(minus_state), 'minus_xpos':float(minus_xpos),
                                            'minus_ypos':float(minus_ypos), 'minus_xdir':float(minus_xdir),
                                            'minus_ydir':float(minus_ydir), 'plus_state':int(plus_state),
                                            'plus_xpos':float(plus_xpos), 'plus_ypos':float(plus_ypos),
                                            'plus_xdir':float(plus_xdir), 'plus_ydir':float(plus_ydir),}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                names = ['time', 'id'])
            if len(all_outputs) > 0:
                all_outputs['plus_rpos'] = np.sqrt(np.square(all_outputs['plus_xpos']) +
                                            np.square(all_outputs['plus_ypos']))

            fiber_ends_outputs_allruns.append(all_outputs)


        all_fiber_ends = pd.concat(fiber_ends_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])
        ends_list.append(all_fiber_ends)
        print('finished parsing ' + output_dir)
    ends_allparams = pd.concat(ends_list, keys = output_dirs,
            names = ['param_sweep', 'run', 'time', 'id'])

    return(ends_allparams)

def get_percentiles(output_dirs, rundirs_allparams_df, solid_allparams, properties_allparams):
    percentiles_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        percentiles_dict = dict()
        for run in rundirs:
            if run == 'empty':
                continue
            internalization = solid_allparams.loc[output_dir].loc[run]['internalization']*1000
            props = properties_allparams.loc[output_dir].loc[run]
            percentile = np.percentile(internalization, 95)
            percentiles_dict[run] = {'95_percentile_internalization':percentile}
        percentiles_df = pd.DataFrame.from_dict(percentiles_dict, orient='index')
        percentiles_list.append(percentiles_df)

    percentiles = pd.concat(percentiles_list, keys=output_dirs,
                        names=['param_sweep', 'run'])

    return(percentiles)

def get_actin_endpoints(output_dirs, rundirs_allparams_df, forces_allparams):
    actin_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        actin_dict = dict()
        for run in rundirs:
            if run == 'empty':
                continue
            actin_dict[run] = {'actin_points':forces_allparams.loc[(output_dir,run,15.0)].shape[0]}
        actin_df = pd.DataFrame.from_dict(actin_dict, orient='index')
        actin_list.append(actin_df)

    actin_endpoints = pd.concat(actin_list, keys=output_dirs,
                        names=['param_sweep', 'run'])

    return(actin_endpoints)
