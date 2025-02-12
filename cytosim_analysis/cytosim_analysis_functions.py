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
from scipy import stats
from scipy.stats import binned_statistic_2d
import textwrap
from scipy.signal import savgol_filter
from scipy.signal import find_peaks

def test_func():
    print('test3')

kB = 1.380649e-23 #J⋅K^−1
T = 303.15 #K
def ufpN_to_dnm(unbinding_force, kB=kB, T=T):
    if type(unbinding_force) == int:
        if unbinding_force == 0:
            distance = 0
        else:
            distance = (-kB * T / (unbinding_force*1E-12))*1E9
    else:
        distance = (-kB * T / (unbinding_force*1E-12))*1E9
        #distance.replace([np.inf, -np.inf], 0, inplace=True)
    return(distance)

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

def report_sims(working_dir, output_dirs, cytosim_dir, report):
    os.chdir(working_dir)
    for output_dir in output_dirs:
        for rundir in os.listdir('simulations/' + output_dir):
            reportdir = 'simulations/'+output_dir+'/'+rundir
            if rundir.startswith('output') or rundir.startswith('run') and 'properties.cmo' in os.listdir(reportdir):
                os.chdir(reportdir)
                if report == 'yes':
                    print('starting ' + reportdir)
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
                os.chdir(working_dir)
        print('finished reporting ' + output_dir)

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

def open_reports(reports, working_dir, output_dirs, config_dirs, cytosim_dir, replace_movies):
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
            #print('starting '+reportdir)
            if rundir.startswith('output') or rundir.startswith('run') and 'properties.cmo' in os.listdir(reportdir):
                if config_exists == 'yes':
                    conf = open(conf_file, 'r')
                    configs_allruns[rundir] = conf.readlines()
                    conf.close()
                os.chdir(reportdir)
                properties = open('properties.cmo', 'r')
                properties_allruns[rundir] = properties.readlines()
                properties.close()
                if 'solid' in reports:
                    solid = open('solid.txt', 'r')
                    solid_allruns[rundir] = solid.readlines()
                    solid.close()
                if 'single_hip1r' in reports:
                    single_hip1r = open('single_hip1r.txt', 'r')
                    single_hip1r_allruns[rundir] = single_hip1r.readlines()
                    single_hip1r.close()
                if 'single_membrane_myosin' in reports:
                    single_membrane_myosin = open('single_membrane_myosin.txt', 'r')
                    single_membrane_myosin_allruns[rundir] = single_membrane_myosin.readlines()
                    single_membrane_myosin.close()
                if 'fiber_cluster' in reports:
                    fiber_cluster = open('fiber_clusters.txt', 'r')
                    fiber_cluster_allruns[rundir] = fiber_cluster.readlines()
                    fiber_cluster.close()
                if 'fiber_forces' in reports:
                    fiber_forces = open('fiber_forces.txt', 'r')
                    fiber_forces_allruns[rundir] = fiber_forces.readlines()
                    fiber_forces.close()
                if 'fiber_tensions' in reports:
                    fiber_tensions = open('fiber_tensions.txt', 'r')
                    fiber_tensions_allruns[rundir] = fiber_tensions.readlines()
                    fiber_tensions.close()
                if 'fiber_ends' in reports:
                    fiber_ends = open('fiber_ends.txt', 'r')
                    fiber_ends_allruns[rundir] = fiber_ends.readlines()
                    fiber_ends.close()
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

def props_configs(output_dirs, rundirs_allparams_df, properties_allruns_allparams, configs_allruns_allparams):
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

def solid_positions(output_dirs, rundirs_allparams_df, solid_allruns_allparams):
    solid_list = []

    for output_dir in output_dirs:
        solid_outputs_allruns = []
        rundirs = rundirs_allparams_df.loc[output_dir]
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
            all_outputs['rpos'] = np.sqrt(np.square(all_outputs['xpos']) +
                                        np.square(all_outputs['ypos']))
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

def all_hip1r(output_dirs, rundirs_allparams_df, single_hip1r_allruns_allparams, solid_allparams):
    hip1r_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
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
                    [single_class, single_id, state, xpos, ypos, zpos,
             xforce, yforce, zforce, fiber_id, xdir, ydir, zdir, abscissa] = line.split()[:14]
                    singles[int(single_id)] = {'state' : int(state), 'fiber_id' : int(fiber_id),
                            'xpos': float(xpos), 'single_id' : int(single_id),
                            'ypos' : float(ypos), 'zpos': float(zpos),
                            'xforce' : float(xforce), 'yforce' : float(yforce),
                            'zforce': float(zforce), 'abscissa' : float(abscissa),
                            'xdir' : float(xdir), 'ydir' : float(ydir), 'zdir' : float(zdir)}

                    # [single_class, single_id, state, xpos, ypos, zpos, xforce, yforce, zforce, fiber_id, direction, abscissa, abscissa_plus, dir_from_plus] = line.split()[:14]
                    # singles[int(single_id)] = {'state' : int(state), 'fiber_id' : int(fiber_id),
                    #                         'xpos': float(xpos), 'single_id' : int(single_id),
                    #                         'ypos' : float(ypos), 'zpos': float(zpos),
                    #                         'xforce' : float(xforce), 'yforce' : float(yforce),
                    #                         'zforce': float(zforce), 'abscissa' : float(abscissa),
                    #                         'direction' : float(direction)}

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

    hip1r_allparams['xpos_rel'] = hip1r_allparams['xpos']-solid_allparams.reset_index(level='id', drop=True)['xpos']
    hip1r_allparams['ypos_rel'] = hip1r_allparams['ypos']-solid_allparams.reset_index(level='id', drop=True)['ypos']
    hip1r_allparams['rpos_rel'] = np.sqrt(np.square(hip1r_allparams['xpos_rel'])+
                                        np.square(hip1r_allparams['ypos_rel']))

    return(hip1r_allparams)

def all_myosin(output_dirs, rundirs_allparams_df, single_membrane_myosin_allruns_allparams):
    membrane_myosin_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        single_membrane_myosin_outputs_allruns = []
        for rundir in rundirs:
            if rundir == 'empty':
                continue
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
            if len(all_outputs) > 0:
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

def get_fiber_clusters(output_dirs, rundirs_allparams_df, fiber_clusters_allruns_allparams):
    clusters_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        fiber_clusters_outputs_allruns = []
        for rundir in rundirs:
            all_lines = fiber_clusters_allruns_allparams[output_dir][rundir]
            timepoints = []
            outputs = []
            for line in all_lines:
                line = line.strip()
                if line.startswith('%'):
                    if line.startswith('% time'):
                        time = float(line.split(' ')[-1])
                        timepoints.append(time)
                        fiber_clusters = {}
                    elif line.startswith('% end'):
                        df = pd.DataFrame.from_dict(fiber_clusters, orient = 'index')
                        outputs.append(df)
                        # print 'finished parsing ' + rundir + ' timepoint ' + str(time)
                elif len(line.split()) > 0:
                    [cluster_id, number_fibers] = line.split()[:2]
                    fiber_id_list = line.split(':')[-1].split()
                    fiber_clusters[int(cluster_id)] = {'cluster_id' : int(cluster_id),
                    'number_fibers' : int(number_fibers), 'fiber_id_list' : fiber_id_list}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                    names = ['time', 'id'])
            # all_outputs = all_outputs.swaplevel('time','id',axis=0).sort_index()
            fiber_clusters_outputs_allruns.append(all_outputs)

        all_fiber_clusters = pd.concat(fiber_clusters_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])

        clusters_list.append(all_fiber_clusters)

        print('finished parsing ' + output_dir)

    clusters_allparams = pd.concat(clusters_list, keys = output_dirs,
                                names = ['param_sweep', 'run', 'time', 'id'])

    return(clusters_allparams)

def get_fiber_forces(output_dirs, rundirs_allparams_df, fiber_forces_allruns_allparams):
    forces_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
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

def get_fiber_ends(output_dirs, rundirs_allparams_df, fiber_ends_allruns_allparams, solid_allparams):
    ends_list = []
    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
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
                    [fiber_class, fiber_id, length, minus_state, minus_xpos, minus_ypos, minus_zpos,
                    minus_xdir, minus_ydir, minus_zdir, plus_state, plus_xpos, plus_ypos,
                    plus_zpos, plus_xdir, plus_ydir, plus_zdir] = line.split()
                    singles[int(fiber_id)] = {'fiber_id' : int(fiber_id), 'length':float(length),
                                            'minus_state':int(minus_state), 'minus_xpos':float(minus_xpos),
                                            'minus_ypos':float(minus_ypos), 'minus_zpos':float(minus_zpos),
                                            'minus_xdir':float(minus_xdir), 'minus_ydir':float(minus_ydir),
                                            'minus_zdir':float(minus_zdir), 'plus_state':int(plus_state),
                                            'plus_xpos':float(plus_xpos), 'plus_ypos':float(plus_ypos),
                                            'plus_zpos':float(plus_zpos), 'plus_xdir':float(plus_xdir),
                                            'plus_ydir':float(plus_ydir), 'plus_zdir':float(plus_zdir),
                                            'growth':np.NaN}

            all_outputs = pd.concat(outputs, keys = timepoints,
                                names = ['time', 'id']).sort_index()
            if len(all_outputs) > 0:
                all_outputs['plus_rpos'] = np.sqrt(np.square(all_outputs['plus_xpos']) +
                                            np.square(all_outputs['plus_ypos']))

            lengths = dict()
            for i, timepoint in enumerate(timepoints):
                lengths[i] = all_outputs.loc[timepoint,'length']
                if i > 0:
                    check = 'good'
                    for fil in lengths[i-1].reset_index()['id']:
                        if fil not in np.array(lengths[i].reset_index()['id']):
                            check = 'bad'
                    if check == 'good':
                        growth = lengths[i] - lengths[i-1]
                        for fil in lengths[i].reset_index()['id']:
                            if fil not in np.array(lengths[i-1].reset_index()['id']):
                                growth.loc[fil] = lengths[i].loc[fil]
                        all_outputs.loc[timepoint,'growth'] = np.array(growth)
                else:
                    all_outputs.loc[timepoint,'growth'] = np.array(lengths[i])

            fiber_ends_outputs_allruns.append(all_outputs)


        all_fiber_ends = pd.concat(fiber_ends_outputs_allruns, keys = rundirs,
                                    names = ['run', 'time', 'id'])
        ends_list.append(all_fiber_ends)
        print('finished parsing ' + output_dir)
    ends_allparams = pd.concat(ends_list, keys = output_dirs,
            names = ['param_sweep', 'run', 'time', 'id'])

    ends_allparams['minus_xpos_rel'] = ends_allparams['minus_xpos']-solid_allparams.reset_index(level='id', drop=True)['xpos']
    ends_allparams['minus_ypos_rel'] = ends_allparams['minus_ypos']-solid_allparams.reset_index(level='id', drop=True)['ypos']
    ends_allparams['minus_rpos_rel'] = np.sqrt(np.square(ends_allparams['minus_xpos_rel'])+
                                        np.square(ends_allparams['minus_ypos_rel']))

    ends_allparams['plus_xpos_rel'] = ends_allparams['plus_xpos']-solid_allparams.reset_index(level='id', drop=True)['xpos']
    ends_allparams['plus_ypos_rel'] = ends_allparams['plus_ypos']-solid_allparams.reset_index(level='id', drop=True)['ypos']
    ends_allparams['plus_rpos_rel'] = np.sqrt(np.square(ends_allparams['plus_xpos_rel'])+
                                        np.square(ends_allparams['plus_ypos_rel']))

    return(ends_allparams)

def get_fiber_ends_2d(output_dirs, rundirs_allparams_df, fiber_ends_allruns_allparams):
    ends_list = []
    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
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

def actin_ends_analysis(output_dirs, rundirs_allparams_df, hip1r_allparams,
                        solid_allparams, clusters_allparams, ends_allparams):

    bound_hip1r = hip1r_allparams.loc[hip1r_allparams['state'] == 1]
    hip1r_clusters_ends_list = []
    fiber_ends_summary_list = []

    for output_dir in output_dirs:

        rundirs = rundirs_allparams_df.loc[output_dir]
        associated_fibers_allruns = []
        associated_ends_allruns = []
        summaries_allruns = []

        for rundir in rundirs:
            if rundir == 'empty':
                continue
            if rundir not in bound_hip1r.loc[output_dir].reset_index()['run'].unique():
                continue
            fiber_outputs = []
            end_outputs = []
            lengths = dict()
            growth = dict()
            summary = dict()
            timepoints = solid_allparams.loc[output_dir].loc[rundir].reset_index()['time']
            last_uncapped_fiber_ends = pd.DataFrame(
                {'id':np.NaN, 'growth':np.NaN, 'length':np.NaN},index=[0])
            for i, timepoint in enumerate(timepoints):
                if timepoint in bound_hip1r.loc[output_dir].loc[rundir].reset_index()['time'].unique():
                    bound_fibers = bound_hip1r.loc[output_dir].loc[rundir].loc[timepoint]['fiber_id']
                else:
                    bound_fibers = []
                internalization = solid_allparams.loc[output_dir].loc[rundir].loc[timepoint]['internalization'].max()
                clusters = clusters_allparams.loc[output_dir].loc[rundir].loc[timepoint]['fiber_id_list']
                #fiber_forces = all_fiber_forces.loc[output_dir].loc[rundir].loc[timepoint]
                fiber_ends = ends_allparams.loc[output_dir].loc[rundir].loc[timepoint]
                fibers = fiber_ends['fiber_id']
                bound_fiber_list = []

                for fiber in bound_fibers:
                    if fiber not in bound_fiber_list:
                        bound_fiber_list.append(fiber)

                associated_fiber_list = []

                for fiber in bound_fiber_list:
                    for cluster in clusters:
                        if str(fiber) in cluster:
                            for cluster_fiber in cluster:
                                if cluster_fiber not in associated_fiber_list:
                                    associated_fiber_list.append(cluster_fiber)

                uncapped_fiber_ends = fiber_ends.loc[fiber_ends['plus_state'] == 1]
                capped_fiber_ends = fiber_ends.loc[fiber_ends['plus_state'] == 4]
                growing_fiber_ends = fiber_ends.loc[fiber_ends['growth'] > 0.0]
                associated_fiber_ends = fiber_ends[fiber_ends['fiber_id'].astype('str')
                                                .isin(associated_fiber_list)]
                end_outputs.append(associated_fiber_ends)
                uncapped_associated_ends = associated_fiber_ends.loc[associated_fiber_ends['plus_state'] == 1]
                capped_associated_ends = associated_fiber_ends.loc[associated_fiber_ends['plus_state'] == 4]
                growing_associated_ends = associated_fiber_ends.loc[associated_fiber_ends['growth'] > 0.0]

                interval_uncapped_ends = uncapped_fiber_ends[
                    uncapped_fiber_ends['fiber_id'].isin(
                        last_uncapped_fiber_ends.reset_index()['id'])]
                interval_uncapped_associated_ends = interval_uncapped_ends[
                    interval_uncapped_ends['fiber_id'].astype('str').isin(associated_fiber_list)]
                last_uncapped_fiber_ends = uncapped_fiber_ends

                summary[timepoint] = {
                    'growth_total_mean':np.mean(fiber_ends['growth']),
                    'growth_total_median':np.median(fiber_ends['growth']),
                    'growth_total_std':np.std(fiber_ends['growth'], ddof=1),
                    'growth_total_sum':np.sum(fiber_ends['growth']),
                    'growth_uncapped_mean':np.mean(uncapped_fiber_ends['growth']),
                    'growth_uncapped_median':np.median(uncapped_fiber_ends['growth']),
                    'growth_uncapped_std':np.std(uncapped_fiber_ends['growth'], ddof=1),
                    'growth_uncapped_sum':np.sum(uncapped_fiber_ends['growth']),
                    'growth_capped_mean':np.mean(capped_fiber_ends['growth']),
                    'growth_capped_median':np.median(capped_fiber_ends['growth']),
                    'growth_capped_std':np.std(capped_fiber_ends['growth'], ddof=1),
                    'growth_capped_sum':np.sum(capped_fiber_ends['growth']),
                    'growth_growing_mean':np.mean(growing_fiber_ends['growth']),
                    'growth_growing_median':np.median(growing_fiber_ends['growth']),
                    'growth_growing_std':np.std(growing_fiber_ends['growth'], ddof=1),
                    'growth_growing_sum':np.sum(growing_fiber_ends['growth']),
                    'growth_associated_mean':np.mean(associated_fiber_ends['growth']),
                    'growth_associated_median':np.median(associated_fiber_ends['growth']),
                    'growth_associated_std':np.std(associated_fiber_ends['growth'], ddof=1),
                    'growth_associated_sum':np.sum(associated_fiber_ends['growth']),
                    'growth_associated_uncapped_mean':np.mean(uncapped_associated_ends['growth']),
                    'growth_associated_uncapped_median':np.median(uncapped_associated_ends['growth']),
                    'growth_associated_uncapped_std':np.std(uncapped_associated_ends['growth'], ddof=1),
                    'growth_associated_uncapped_sum':np.sum(uncapped_associated_ends['growth']),
                    'growth_associated_capped_mean':np.mean(capped_associated_ends['growth']),
                    'growth_associated_capped_median':np.median(capped_associated_ends['growth']),
                    'growth_associated_capped_std':np.std(capped_associated_ends['growth'], ddof=1),
                    'growth_associated_capped_sum':np.sum(capped_associated_ends['growth']),
                    'growth_associated_growing_mean':np.mean(growing_associated_ends['growth']),
                    'growth_associated_growing_median':np.median(growing_associated_ends['growth']),
                    'growth_associated_growing_std':np.std(growing_associated_ends['growth'], ddof=1),
                    'growth_associated_growing_sum':np.sum(growing_associated_ends['growth']),
                    'growth_interval_uncapped_mean':np.mean(interval_uncapped_ends['growth']),
                    'growth_interval_uncapped_median':np.median(interval_uncapped_ends['growth']),
                    'growth_interval_uncapped_std':np.std(interval_uncapped_ends['growth'], ddof=1),
                    'growth_interval_uncapped_sum':np.sum(interval_uncapped_ends['growth']),
                    'growth_interval_uncapped_associated_mean':np.mean(
                        interval_uncapped_associated_ends['growth']),
                    'growth_interval_uncapped_associated_median':np.median(
                        interval_uncapped_associated_ends['growth']),
                    'growth_interval_uncapped_associated_std':np.std(
                        interval_uncapped_associated_ends['growth']),
                    'growth_interval_uncapped_associated_sum':np.sum(
                        interval_uncapped_associated_ends['growth']),
                    'count_total':fibers.shape[0],
                    'count_uncapped':uncapped_fiber_ends.shape[0],
                    'count_capped':capped_fiber_ends.shape[0],
                    'count_growing':growing_fiber_ends.shape[0],
                    'count_associated':associated_fiber_ends.shape[0],
                    'count_associated_uncapped':uncapped_associated_ends.shape[0],
                    'count_associated_capped':capped_associated_ends.shape[0],
                    'count_associated_growing':growing_associated_ends.shape[0],
                    'count_interval_uncapped':interval_uncapped_ends.shape[0],
                    'count_interval_uncapped_associated':interval_uncapped_associated_ends.shape[0],
                    'mass_total':np.sum(fiber_ends['length']),
                    'mass_uncapped':np.sum(uncapped_fiber_ends['length']),
                    'mass_capped':np.sum(capped_fiber_ends['length']),
                    'mass_growing':np.sum(growing_fiber_ends['length']),
                    'mass_associated':np.sum(associated_fiber_ends['length']),
                    'mass_associated_uncapped':np.sum(uncapped_associated_ends['length']),
                    'mass_associated_capped':np.sum(capped_associated_ends['length']),
                    'mass_associated_growing':np.sum(growing_associated_ends['length']),
                    'mass_interval_uncapped':np.sum(interval_uncapped_ends['length']),
                    'mass_interval_uncapped_associated':np.sum(
                        interval_uncapped_associated_ends['length']),

                    'length_total_mean':np.mean(fiber_ends['length']),
                    'length_uncapped_mean':np.mean(uncapped_fiber_ends['length']),
                    'length_capped_mean':np.mean(capped_fiber_ends['length']),
                    'length_growing_mean':np.mean(growing_fiber_ends['length']),
                    'length_associated_mean':np.mean(associated_fiber_ends['length']),
                    'length_associated_uncapped_mean':np.mean(uncapped_associated_ends['length']),
                    'length_associated_capped_mean':np.mean(capped_associated_ends['length']),
                    'length_associated_growing_mean':np.mean(growing_associated_ends['length']),
                    'length_interval_uncapped_mean':np.mean(interval_uncapped_ends['length']),
                    'length_interval_uncapped_associated_mean':np.mean(
                        interval_uncapped_associated_ends['length']),
                    'length_total_median':np.median(fiber_ends['length']),
                    'length_uncapped_median':np.median(uncapped_fiber_ends['length']),
                    'length_capped_median':np.median(capped_fiber_ends['length']),
                    'length_growing_median':np.median(growing_fiber_ends['length']),
                    'length_associated_median':np.median(associated_fiber_ends['length']),
                    'length_associated_uncapped_median':np.median(uncapped_associated_ends['length']),
                    'length_associated_capped_median':np.median(capped_associated_ends['length']),
                    'length_associated_growing_median':np.median(growing_associated_ends['length']),
                    'length_interval_uncapped_median':np.median(interval_uncapped_ends['length']),
                    'length_interval_uncapped_associated_median':np.median(
                        interval_uncapped_associated_ends['length']),
                    'length_total_std':np.std(fiber_ends['length'], ddof=1),
                    'length_uncapped_std':np.std(uncapped_fiber_ends['length'], ddof=1),
                    'length_capped_std':np.std(capped_fiber_ends['length'], ddof=1),
                    'length_growing_std':np.std(growing_fiber_ends['length'], ddof=1),
                    'length_associated_std':np.std(associated_fiber_ends['length'], ddof=1),
                    'length_associated_uncapped_std':np.std(uncapped_associated_ends['length'], ddof=1),
                    'length_associated_capped_std':np.std(capped_associated_ends['length'], ddof=1),
                    'length_associated_growing_std':np.std(growing_associated_ends['length'], ddof=1),
                    'length_interval_uncapped_std':np.std(interval_uncapped_ends['length'], ddof=1),
                    'length_interval_uncapped_associated_std':np.std(
                        interval_uncapped_associated_ends['length'])
                    }

                summary[timepoint]['efficiency_total'] = \
                    internalization/summary[timepoint]['mass_total']
                summary[timepoint]['efficiency_uncapped'] = \
                    internalization/summary[timepoint]['mass_uncapped']
                summary[timepoint]['efficiency_capped'] = \
                    internalization/summary[timepoint]['mass_capped']
                summary[timepoint]['efficiency_growing'] = \
                    internalization/summary[timepoint]['mass_growing']
                summary[timepoint]['efficiency_associated'] = \
                    internalization/summary[timepoint]['mass_associated']
                summary[timepoint]['efficiency_associated_uncapped'] = \
                    internalization/summary[timepoint]['mass_associated_uncapped']
                summary[timepoint]['efficiency_associated_capped'] = \
                    internalization/summary[timepoint]['mass_associated_capped']
                summary[timepoint]['efficiency_associated_growing'] = \
                    internalization/summary[timepoint]['mass_associated_growing']
                summary[timepoint]['efficiency_interval_uncapped'] = \
                    internalization/summary[timepoint]['mass_interval_uncapped']
                summary[timepoint]['efficiency_interval_uncapped_associated'] = \
                    internalization/summary[timepoint]['mass_interval_uncapped_associated']

                if i == 0:
                    summary[timepoint]['nucleation_total']=summary[timepoint]['count_total']
                    summary[timepoint]['nucleation_uncapped']=summary[timepoint]['count_uncapped']
                    summary[timepoint]['nucleation_capped']=summary[timepoint]['count_capped']
                    summary[timepoint]['nucleation_growing']=summary[timepoint]['count_growing']
                    summary[timepoint]['nucleation_associated']=summary[timepoint]['count_associated']
                    summary[timepoint]['nucleation_associated_uncapped']=summary[
                        timepoint]['count_associated_uncapped']
                    summary[timepoint]['nucleation_associated_capped']=summary[
                        timepoint]['count_associated_capped']
                    summary[timepoint]['nucleation_associated_growing']=summary[
                        timepoint]['count_associated_growing']
                    summary[timepoint]['nucleation_interval_uncapped']=summary[
                        timepoint]['count_interval_uncapped']
                    summary[timepoint]['nucleation_interval_uncapped_associated']=summary[
                        timepoint]['count_interval_uncapped_associated']
                else:
                    summary[timepoint]['nucleation_total']=summary[timepoint]['count_total']-\
                        summary[last_timepoint]['count_total']
                    summary[timepoint]['nucleation_uncapped']=summary[timepoint]['count_uncapped']-\
                        summary[last_timepoint]['count_uncapped']
                    summary[timepoint]['nucleation_capped']=summary[timepoint]['count_capped']-\
                        summary[last_timepoint]['count_capped']
                    summary[timepoint]['nucleation_growing']=summary[timepoint]['count_growing']-\
                        summary[last_timepoint]['count_growing']
                    summary[timepoint]['nucleation_associated']=summary[timepoint]['count_associated']-\
                        summary[last_timepoint]['count_associated']
                    summary[timepoint]['nucleation_associated_uncapped']=summary[
                        timepoint]['count_associated_uncapped']-\
                        summary[last_timepoint]['count_associated_uncapped']
                    summary[timepoint]['nucleation_associated_capped']=summary[
                        timepoint]['count_associated_capped']-\
                        summary[last_timepoint]['count_associated_capped']
                    summary[timepoint]['nucleation_associated_growing']=summary[
                        timepoint]['count_associated_growing']-\
                        summary[last_timepoint]['count_associated_growing']
                    summary[timepoint]['nucleation_interval_uncapped']=summary[
                        timepoint]['count_interval_uncapped']-\
                        summary[last_timepoint]['count_interval_uncapped']
                    summary[timepoint]['nucleation_interval_uncapped_associated']=summary[
                        timepoint]['count_interval_uncapped_associated']-\
                        summary[last_timepoint]['count_interval_uncapped_associated']

                last_timepoint=timepoint

            #associated_fibers_alltimes = pd.concat(fiber_outputs, keys = timepoints,
            #                                       names = ['time', 'id'])
            #associated_fibers_allruns.append(associated_fibers_alltimes)

            associated_ends_alltimes = pd.concat(end_outputs, keys = timepoints,
                                                names = ['time', 'id'])
            associated_ends_allruns.append(associated_ends_alltimes)

            # outputs_alltimes = pd.concat(outputs, keys = timepoints,
            #                             names = ['time', 'id'])

            # outputs_allruns.append(outputs_alltimes)
            summary_df = pd.DataFrame.from_dict(summary, orient = 'index')
            summaries_allruns.append(summary_df)

            #print("finished parsing " + output_dir+ rundir)


        #hip1r_clusters = pd.concat(associated_fibers_allruns, keys = rundirs,
        #                            names = ['run', 'time', 'id'])

        hip1r_clusters_ends = pd.concat(associated_ends_allruns, keys = rundirs,
                                        names = ['run', 'time', 'id'])
        hip1r_clusters_ends_list.append(hip1r_clusters_ends)

        fiber_ends_summary = pd.concat(summaries_allruns, keys = rundirs,
                                    names = ['run', 'time'])
        fiber_ends_summary_list.append(fiber_ends_summary)

        print("finished parsing " + output_dir)

    hip1r_clusters_ends_allparams = pd.concat(hip1r_clusters_ends_list, keys = output_dirs,
                                    names = ['param_sweep','run', 'time', 'id'])

    fiber_ends_summary_allparams = pd.concat(fiber_ends_summary_list, keys = output_dirs,
                                    names = ['param_sweep','run', 'time'])

    return(hip1r_clusters_ends_allparams, fiber_ends_summary_allparams)

def summary_statistics(output_dirs, rundirs_allparams_df, fiber_ends_summary_allparams, solid_allparams, hip1r_bound_ends_attachment, myo_binding_events,
        full_length = 150, max_growth = 0.05, exclude_incomplete_sims = True):

    summaries_list = []

    fiber_ends_summary_allparams['growth_attenuation'] = max_growth-\
        fiber_ends_summary_allparams['growth_interval_uncapped_associated_mean']

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        summaries_dict = dict()
        for run in rundirs:
            if run == 'empty':
                continue
            if run not in fiber_ends_summary_allparams.loc[output_dir].reset_index()['run'].unique():
                print(output_dir+run+' skipped because it\'s missing')
                continue
            if run not in hip1r_bound_ends_attachment.loc[output_dir].reset_index()['run'].unique():
                print(output_dir+run+' skipped because it\'s missing')
                continue
            sim_length = len(solid_allparams.loc[output_dir].loc[run])
            if exclude_incomplete_sims == True:
                if sim_length < full_length:
                    print(output_dir+run+' skipped because it\'s incomplete')
                    continue
            gagm_95per = np.percentile(
                fiber_ends_summary_allparams.loc[output_dir].loc[
                    run]['growth_associated_growing_mean'], 95)
            summaries_dict[run] = {
                'sim_length':sim_length,
                'internalization_95_percentile': np.percentile(solid_allparams.loc[
                    output_dir].loc[run]['internalization'], 95),
                'count_total_95_percentile':np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['count_total'], 95),
                'count_total_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['count_total']),
                'count_total_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['count_total'],
                'count_total_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['count_total'].mean(),
                'count_total_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['count_total'].mean(),
                'count_associated_95per' : np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['count_associated'], 95),
                'count_associated_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['count_associated']),
                'count_associated_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['count_associated'],
                'count_associated_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['count_associated'].mean(),
                'count_associated_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['count_associated'].mean(),
                'mass_total_95per' : np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['mass_total'], 95),
                'mass_total_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['mass_total']),
                'mass_total_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['mass_total'],
                'mass_total_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['mass_total'].mean(),
                'mass_total_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['mass_total'].mean(),
                'mass_associated_95per' : np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['mass_associated'], 95),
                'mass_associated_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['mass_associated']),
                'mass_associated_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['mass_associated'],
                'mass_associated_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['mass_associated'].mean(),
                'mass_associated_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['mass_associated'].mean(),
                'growth_attenuation_sum' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['growth_attenuation'].sum(),

                'length_total_mean_95per' : np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['length_total_mean'], 95),
                'length_total_mean_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['length_total_mean']),
                'length_total_mean_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['length_total_mean'],
                'length_total_mean_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['length_total_mean'].mean(),
                'length_total_mean_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['length_total_mean'].mean(),
                'length_associated_mean_95per' : np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['length_associated_mean'], 95),
                'length_associated_mean_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['length_associated_mean']),
                'length_associated_mean_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['length_associated_mean'],
                'length_associated_mean_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['length_associated_mean'].mean(),
                'length_associated_mean_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['length_associated_mean'].mean(),

                'efficiency_total_95per' : np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['efficiency_total'], 95),
                'efficiency_total_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['efficiency_total']),
                'efficiency_total_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['efficiency_total'],
                'efficiency_total_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['efficiency_total'].mean(),
                'efficiency_total_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['efficiency_total'].mean(),
                'efficiency_associated_95per' : np.percentile(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['efficiency_associated'], 95),
                'efficiency_associated_max' : np.max(fiber_ends_summary_allparams.loc[
                    output_dir].loc[run]['efficiency_associated']),
                'efficiency_associated_final' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].iloc[-1]['efficiency_associated'],
                'efficiency_associated_last5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[10:15]['efficiency_associated'].mean(),
                'efficiency_associated_first5s_mean' : fiber_ends_summary_allparams.loc[
                    output_dir].loc[run].loc[:5]['efficiency_associated'].mean(),

                'bending_energy_associated_95per' : np.percentile(hip1r_bound_ends_attachment.loc[
                    output_dir].loc[run]['bending_energy'], 95),
                'bending_energy_associated_max' : np.max(hip1r_bound_ends_attachment.loc[
                    output_dir].loc[run]['bending_energy']),
                'bending_energy_associated_final' : hip1r_bound_ends_attachment.loc[
                    output_dir].loc[run].iloc[-1]['bending_energy'],
                'bending_energy_associated_last5s_mean' : hip1r_bound_ends_attachment.loc[
                    output_dir].loc[run].loc[10:15]['bending_energy'].mean(),
                'bending_energy_associated_first5s_mean' : hip1r_bound_ends_attachment.loc[
                    output_dir].loc[run].loc[:5]['bending_energy'].mean()
            }

            if output_dir not in myo_binding_events.reset_index()['param_sweep'].unique():
                print(output_dir+' skipped because no myo binding')
                continue
            if run not in myo_binding_events.loc[output_dir].reset_index()['run'].unique():
                print(output_dir+' '+run+' skipped because no myo binding')
                continue

            summaries_dict[run]['myo_binding_events'] = len(myo_binding_events.loc[
                    output_dir].loc[run])
            for measurement in list(myo_binding_events):
                summaries_dict[run][measurement+'_mean'] = myo_binding_events.loc[
                    output_dir].loc[run][measurement].mean()
                summaries_dict[run][measurement+'_median'] = myo_binding_events.loc[
                    output_dir].loc[run][measurement].median()
                summaries_dict[run][measurement+'_std'] = myo_binding_events.loc[
                    output_dir].loc[run][measurement].std()
                summaries_dict[run][measurement+'_max'] = myo_binding_events.loc[
                    output_dir].loc[run][measurement].max()
                summaries_dict[run][measurement+'_sum'] = myo_binding_events.loc[
                    output_dir].loc[run][measurement].sum()

        summaries_df = pd.DataFrame.from_dict(summaries_dict, orient='index')
        summaries_list.append(summaries_df)

        print("finished parsing " + output_dir)

    summaries = pd.concat(summaries_list, keys=output_dirs,
                        names=['param_sweep', 'run'])
    return(summaries)

def group_summaries(config_unique, config_groups, summaries):
    summaries_config = pd.concat([config_unique, summaries],axis=1)

    summary_groups = summaries_config.groupby(config_groups)

    grouped_summaries_list=[]
    grouped_summaries_keys=[]

    n = summary_groups['sim_length'].count()
    grouped_summaries_list.append(n)
    grouped_summaries_keys.append('sim_count')

    for statistic in list(summaries):
        stat_mean = summary_groups[statistic].mean()
        stat_std = summary_groups[statistic].std(ddof=1)
        n = summary_groups[statistic].count()
        t_statistic = stats.t.ppf(0.975, df=n-1)  # For a 95% confidence interval (two-tailed), use alpha = 0.025
        margin_of_error = t_statistic * (stat_std / np.sqrt(n))
        grouped_summaries_list.append(stat_mean)
        grouped_summaries_keys.append(statistic+'_mean')
        grouped_summaries_list.append(stat_std)
        grouped_summaries_keys.append(statistic+'_std')
        grouped_summaries_list.append(margin_of_error)
        grouped_summaries_keys.append(statistic+'_ci95')

    grouped_summaries = pd.concat(grouped_summaries_list, axis=1,
                                keys = grouped_summaries_keys).reset_index()

    grouped_summaries['ratio_associated_mass_count'] =  \
        grouped_summaries['mass_associated_last5s_mean_mean'] \
        /grouped_summaries['count_associated_last5s_mean_mean']
    grouped_summaries['distance_parameter'] = ufpN_to_dnm(
        grouped_summaries['myosin_unbinding_force'])
    grouped_summaries['distance_parameter'].replace([np.inf, -np.inf], 0, inplace=True)
    plusmyo_grouped_summaries = grouped_summaries.loc[grouped_summaries['membrane_myosin_number']>0]
    nomyo_grouped_summaries = grouped_summaries.loc[grouped_summaries['membrane_myosin_number']==0]
    motile_grouped_summaries = plusmyo_grouped_summaries.loc[
        plusmyo_grouped_summaries['myosin_max_speed']>0]
    immotile_grouped_summaries = plusmyo_grouped_summaries.loc[
        plusmyo_grouped_summaries['myosin_max_speed']==0]

    return(grouped_summaries, motile_grouped_summaries, immotile_grouped_summaries, nomyo_grouped_summaries)


def get_final_bound_hip1r(output_dirs, rundirs_allparams_df,
                          hip1r_allparams, solid_allparams):
    final_bound_hip1r_list = []

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        final_bound_hip1r_allruns = []
        for rundir in rundirs:
            if rundir == 'empty':
                continue
            timepoints = solid_allparams.loc[output_dir].loc[rundir].reset_index()['time']
            final_bound_hip1r_alltimes = []
            for timepoint in timepoints:
                final_bound_hip1r_timepoint = hip1r_allparams.loc[output_dir].loc[rundir].loc[timepoint]
                fibers = final_bound_hip1r_timepoint['fiber_id']
                abscissas = final_bound_hip1r_timepoint['abscissa']
                hip1rs = final_bound_hip1r_timepoint.reset_index()['id']

                last_abscissa = dict()
                last_abscissa[0] = (0,0)

                for hip1r, fiber, abscissa in zip(hip1rs, fibers, abscissas):
                    #print hip1r, fiber, abscissa
                    if fiber in last_abscissa.keys():
                        if abscissa > last_abscissa[fiber][-1]:
                            final_bound_hip1r_timepoint = final_bound_hip1r_timepoint.drop([last_abscissa[fiber][0]])
                            # print 'dropped '+str(last_abscissa[fiber][0])
                            last_abscissa[fiber] = (hip1r,abscissa)
                        else:
                            final_bound_hip1r_timepoint = final_bound_hip1r_timepoint.drop([hip1r])
                            # print 'dropped '+str(hip1r)
                    if fiber not in last_abscissa.keys():
                        last_abscissa[fiber] = (hip1r, abscissa)


                final_bound_hip1r_alltimes.append(final_bound_hip1r_timepoint)

            final_bound_hip1r_alltimes_df = pd.concat(final_bound_hip1r_alltimes, keys = timepoints,
                                                        names = ['time', 'hip1r_id'])
            final_bound_hip1r_allruns.append(final_bound_hip1r_alltimes_df)
            #print( "finished parsing " + rundir)
        final_bound_hip1r_allruns_df = pd.concat(final_bound_hip1r_allruns, keys = rundirs,
                                    names = ['run', 'time', 'hip1r_id'])
        final_bound_hip1r_list.append(final_bound_hip1r_allruns_df)
        print( "finished parsing " + output_dir)

    final_bound_hip1r_allparams = pd.concat(final_bound_hip1r_list, keys = output_dirs,
                                    names = ['param_sweep','run', 'time', 'hip1r_id'])
    return(final_bound_hip1r_allparams)


def bound_myosins(rundirs_allparams_df, membrane_myosin_allparams):

    myos_bound_list = []
    filtered_myo_bound = membrane_myosin_allparams.loc[membrane_myosin_allparams['state']==1]
    output_dirs =  membrane_myosin_allparams.reset_index()['param_sweep'].unique()

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        myos_bound_allruns = []
        for rundir in rundirs:
            if rundir == 'empty':
                continue
            myos_bound_run = membrane_myosin_allparams.loc[output_dir].loc[rundir]
            timepoints = myos_bound_run.reset_index()['time'].unique()
            myos_bound_alltimes = {}
            for timepoint in timepoints:
                myos_timepoint = myos_bound_run.loc[timepoint]
                myos_bound_timepoint = myos_timepoint.loc[myos_timepoint['state']==1]['state'].count()
                myos_bound_alltimes[timepoint]=myos_bound_timepoint
            myos_bound_alltimes_df = pd.Series(myos_bound_alltimes,name='bound_myosins')
            myos_bound_allruns.append(myos_bound_alltimes_df)
            #print( "finished parsing " + rundir)
        myos_bound_allruns_df = pd.concat(myos_bound_allruns, keys = rundirs,
                                    names = ['run', 'time'])
        myos_bound_list.append(myos_bound_allruns_df)
        print( "finished parsing " + output_dir)

    myos_bound_allparams = pd.concat(myos_bound_list, keys = output_dirs,
                                    names = ['param_sweep','run', 'time'])
    return(myos_bound_allparams)

def retraction_analysis(solid_allparams,end_tp=10,window=10,order=4):
    retractions_list = []
    output_dirs =  solid_allparams.reset_index()['param_sweep'].unique()

    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        retractions_allruns = []
        retractions_dict={}
        for rundir in rundirs:
            if rundir == 'empty':
                continue
            solid_run = solid_allparams.loc[output_dir].loc[rundir].loc[:end_tp]
            x = solid_run.reset_index()['time']
            if x.max() < 10:
                continue
            y = solid_run['internalization']*1000
            yhat = savgol_filter(y, window, order)
            minima = find_peaks(-yhat)[0]
            maxima = find_peaks(yhat)[0]
            if len(minima) < 1 or len(maxima) < 1:
                retraction_times=0.1*[]
                retraction_distances=[]
            elif minima[0]>maxima[0]:
                retraction_times=0.1*(minima-maxima[:len(minima)])
                retraction_distances=yhat[maxima[:len(minima)]]-yhat[minima]
            elif minima[0]<maxima[0]:
                retraction_times=0.1*(minima[1:]-maxima[:len(minima)-1])
                retraction_distances=yhat[maxima[:len(minima)-1]]-yhat[minima[1:]]
            retraction_rates = retraction_distances/retraction_times
            retractions_dict[rundir]={
                'retraction_count':len(retraction_times),
                'retraction_time_sum':sum(retraction_times),
                'retraction_distance_sum':sum(retraction_distances),
                'retraction_rate_mean':np.mean(retraction_rates),
                'retraction_rate_std':np.std(retraction_rates)
            }

        retractions_allruns_df = pd.DataFrame.from_dict(retractions_dict,orient='index')
        retractions_list.append(retractions_allruns_df)
        print( "finished parsing " + output_dir)

    retractions_allparams = pd.concat(retractions_list, keys = output_dirs,
                                    names = ['param_sweep','run'])

    return(retractions_allparams)
