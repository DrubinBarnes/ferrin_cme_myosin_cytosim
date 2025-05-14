
# Table of Contents

1.  [export this to other file formats](#org3f0126d)
    1.  [convert to jupyter notebook](#org7635642)
        1.  [using pandoc](#orgaf02dd1)
        2.  [using orgparse](#org5155d6d)
    2.  [export to org document](#org0de6b0d)
    3.  [export to markdown document](#org5396fa9)
2.  [figure generation index](#org6c16b38)
3.  [configuration](#org8e646f9)
    1.  [set global variables](#orgf8049c1)
    2.  [load and configure libraries](#org493e05b)
    3.  [set working directories](#orge91e2e4)
    4.  [load custom functions](#orgca6a478)
4.  [find directories that have outputs or config files](#orgfc2fffd)
5.  [report simulations](#org3a17184)
6.  [read simulation properties](#orgb47639e)
    1.  [put all properties and configs into dataframes](#org1ef892a)
    2.  [filter for properties that vary among simulations](#org339ba85)
7.  [parse results into dataframe](#org3992da3)
    1.  [fiber ends](#orgb00e806)
8.  [load in previously parsed dataframes](#org3232633)
9.  [plot results](#orgd8533dd)
    1.  [actin plus end displacement vs. time](#orgaa11a82)
        1.  [all parameters](#org4aa6685)
        2.  [final myo parameters](#orgacf6ea6)
    2.  [heat map of average velocity](#org0aae294)
    3.  [line plot of average velocity](#org8001e05)



<a id="org3f0126d"></a>

# export this to other file formats

These files are symbolically linked such that their source is the
version-controlled directory, but they can be exported from the local directory
where the analysis happens

Due to this difference in directory structure, anyone else using these scripts
will have to make sure the locations of their data are specified correctly in
the [set working directories](#orge91e2e4) section.


<a id="org7635642"></a>

## convert to jupyter notebook


<a id="orgaf02dd1"></a>

### using pandoc

this looks nice but it&rsquo;s just a big markdown block

    pandoc 6.11.6_analysis.org -o gliding_analysis_pandoc.ipynb


<a id="org5155d6d"></a>

### using orgparse

this is the only way that makes runnable python cells, though lots of formatting
doesn&rsquo;t work

    import orgparse
    import nbformat as nbf
    import re
    import base64
    
    def parse_results(results_block):
        """
        Parse the #+RESULTS: block to extract outputs.
        """
        outputs = []
        lines = results_block.strip().split("\n")
    
        for line in lines:
            if line.strip().startswith(": "):
                outputs.append(nbf.v4.new_output(output_type="stream", name="stdout", text=line[2:].strip() + "\n"))
            elif re.match(r"\[\[.*\.(png|jpg|jpeg|gif)\]\]", line.strip()):
                image_path = re.search(r"\[\[(.*\.(png|jpg|jpeg|gif))\]\]", line.strip()).group(1)
                try:
                    with open(image_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode("utf-8")
                    outputs.append(nbf.v4.new_output(
                        output_type="display_data",
                        data={"image/png": image_data},
                        metadata={}
                    ))
                except FileNotFoundError:
                    print(f"Warning: Image file not found: {image_path}")
        return outputs
    
    def convert_org_links_to_markdown(text):
        """
        Convert Org mode links to Markdown links.
        """
        text = re.sub(r"\[\[([^\]]+)\]\[([^\]]+)\]\]", r"[\2](\1)", text)
        text = re.sub(r"\[\[([^\]]+)\]\]", r"[\1](\1)", text)
        return text
    
    def org_to_ipynb(org_file, ipynb_file):
        org = orgparse.load(org_file)
        nb = nbf.v4.new_notebook()
        cells = []
    
        for node in org[1:]:
            if ":noexport:" in node.tags or (node.heading and ":noexport:" in node.heading.lower()):
                continue
    
            if node.heading:
                heading_level = "#" * node.level
                cells.append(nbf.v4.new_markdown_cell(f"{heading_level} {node.heading}"))
    
            in_code_block = False
            in_results_block = False
            code_lines = []
            markdown_lines = []
            results_block = ""
    
            for line in node.body.split("\n"):
                if line.strip().startswith("#+BEGIN_SRC python"):
                    in_code_block = True
                    if markdown_lines:
                        markdown_text = convert_org_links_to_markdown("\n".join(markdown_lines)).strip()
                        if markdown_text:
                            cells.append(nbf.v4.new_markdown_cell(markdown_text))
                        markdown_lines = []
                    continue
                elif line.strip().startswith("#+END_SRC"):
                    in_code_block = False
                    if code_lines:
                        code_cell = nbf.v4.new_code_cell("\n".join(code_lines))
                        cells.append(code_cell)
                        code_lines = []
                    continue
                elif line.strip().startswith("#+RESULTS:"):
                    in_results_block = True
                    continue
                elif in_results_block and line.strip() == ":end:":
                    in_results_block = False
                    if results_block.strip():
                        outputs = parse_results(results_block)
                        if outputs and cells:
                            cells[-1].outputs = outputs
                    results_block = ""
                elif in_code_block:
                    code_lines.append(line)
                elif in_results_block:
                    results_block += line + "\n"
                else:
                    markdown_lines.append(convert_org_links_to_markdown(line))
    
            markdown_text = convert_org_links_to_markdown("\n".join(markdown_lines)).strip()
            if markdown_text:
                cells.append(nbf.v4.new_markdown_cell(markdown_text))
    
        nb.cells = cells
        with open(ipynb_file, "w") as f:
            nbf.write(nb, f)
    
    # Convert your Org file
    org_to_ipynb("6.11.6_analysis.org",
                 "gliding_analysis_orgparse.ipynb")

    (org-babel-tangle)

    589f5bc653f83f37475df4339280d3b0

    python convert_org_to_ipynb.py


<a id="org0de6b0d"></a>

## export to org document

    (org-org-export-to-org)

    779034df5b081f6b2f77f4f5fb6522d5


<a id="org5396fa9"></a>

## export to markdown document

    (org-md-export-to-markdown)

    6e4588c0990cca7fb6ad29f883d8fb96


<a id="org6c16b38"></a>

# figure generation index

<table>


<colgroup>
<col  class="org-left">

<col  class="org-left">

<col  class="org-left">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">figure</th>
<th scope="col" class="org-left">panel</th>
<th scope="col" class="org-left">link</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">S2</td>
<td class="org-left">D</td>
<td class="org-left"><a href="#orgacf6ea6">final myo parameters</a></td>
</tr>

<tr>
<td class="org-left">S2</td>
<td class="org-left">D</td>
<td class="org-left"><a href="#org0aae294">heat map of average velocity</a></td>
</tr>

<tr>
<td class="org-left">S2</td>
<td class="org-left">D</td>
<td class="org-left"><a href="#org8001e05">line plot of average velocity</a></td>
</tr>
</tbody>
</table>


<a id="org8e646f9"></a>

# configuration


<a id="orgf8049c1"></a>

## set global variables

    #timestep = 5e-5
    report = 'no'
    replace_movies = 'no'
    save_figures = 'yes'
    save_dataframes = 'yes'


<a id="org493e05b"></a>

## load and configure libraries

    import os
    import sys
    from tabulate import tabulate
    import math
    import numpy as np
    import pandas as pd
    import shutil
    import subprocess
    from subprocess import Popen
    import datetime
    import matplotlib.pyplot as plt  # plotting
    import seaborn as sns  # nicer plotting
    from decimal import Decimal
    import matplotlib.colors as mplcolors
    import matplotlib
    from matplotlib.colors import LogNorm
    from matplotlib.colors import SymLogNorm
    from matplotlib.cm import ScalarMappable
    from matplotlib.ticker import FuncFormatter
    from scipy.stats import binned_statistic_2d
    from scipy import stats
    from scipy.signal import savgol_filter
    from scipy.signal import find_peaks
    import textwrap
    from decimal import Decimal
    from scipy.stats import binned_statistic_2d
    from scipy.stats import linregress
    from scipy.stats import sem
    from matplotlib.font_manager import FontProperties
    import matplotlib.pyplot as plt  # plotting
    import matplotlib.colors as mcolors
    from matplotlib.colors import LogNorm
    from matplotlib.colors import SymLogNorm
    plt.style.use('seaborn-v0_8-colorblind') # set plot style
    plt.cool()                          # heatmap color scheme
    matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=mcolors.TABLEAU_COLORS)
    %matplotlib inline
    
    import seaborn as sns  # nicer plotting
    sns.set_style('whitegrid')  # set plot style
    
    SMALL_SIZE = 20
    MEDIUM_SIZE = 24
    BIGGER_SIZE = 30
    
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    plt.rc('figure', figsize=[6,5]) # default figure width, height
    
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d')
    pref = date

    /home/maxferrin/miniconda3/lib/python3.10/site-packages/pandas/core/arrays/masked.py:60: UserWarning: Pandas requires version '1.3.6' or newer of 'bottleneck' (version '1.3.5' currently installed).
      from pandas.core import (
    <Figure size 640x480 with 0 Axes>


<a id="orge91e2e4"></a>

## set working directories

    #machine = 'peeks'
    machine = 'ltpbukem'
    
    if machine == 'ltpbukem':
        drive_dir = '/home/maxferrin/google_drive/'
    
    if machine == 'bizon':
        drive_dir = '/media/bizon/DATA/MFerrin/insync/'
    
    if machine == 'peeks':
        drive_dir = '/scratch/ferrin/unison_peeks/'
    
    if machine == 'drumroom':
        drive_dir = '/Users/max/google_drive/'
    
    if machine == 'mbp':
        drive_dir = '/Users/maxferrin/google_drive/'
    
    if machine == 'sobarky':
        drive_dir = '/Users/dblab/google_drive/'
    
    
    working_dir = os.path.join(drive_dir, 'grad_school/db_lab/code/analysis/20230630_6.11.6_glidingrecapitulation/')
    #working_dir = '/home/maxferrin/mount/trinity/home/google_drive/grad_school/db_lab/code/analysis/20230630_6.11.6_glidingrecapitulation/'
    cytosim_dir = os.path.join(drive_dir, 'grad_school/db_lab/code/cytosim_dblab/', machine)
    
    if machine == 'peeks':
        working_dir = '/run/media/ferrin/Volume/max/analysis/20230630_6.11.6_glidingrecapitulation/'
        cytosim_dir = '/home/ferrin/cytosim/'
    
    dataframes_dir = os.path.join(working_dir,'dataframes/')
    
    os.chdir(working_dir)
    
    if os.path.isdir('figures') == False:
        os.mkdir('figures')
    if os.path.isdir('dataframes') == False:
        os.mkdir('dataframes')


<a id="orgca6a478"></a>

## load custom functions

    # add parent folder to path
    sys.path.insert(1, '../')
    from cytosim_analysis import cytosim_analysis_functions as caf
    
    # reload custom library
    from importlib import reload
    reload(sys.modules['cytosim_analysis'])

    <module 'cytosim_analysis' from '/home/maxferrin/SynologyDrive/google_drive/grad_school/db_lab/code/analysis/20230630_6.11.6_glidingrecapitulation/../cytosim_analysis/__init__.py'>


<a id="orgfc2fffd"></a>

# find directories that have outputs or config files

    output_dirs, config_dirs = caf.find_directories()
    print(output_dirs, config_dirs)

    ['6.11.6_output'] ['6.11.6']


<a id="org3a17184"></a>

# report simulations

this crashes

    solid_allruns_allparams, properties_allruns_allparams, \
    configs_allruns_allparams, single_hip1r_allruns_allparams, \
    single_membrane_myosin_allruns_allparams, fiber_forces_allruns_allparams, \
    fiber_clusters_allruns_allparams, fiber_tensions_allruns_allparams, \
    fiber_ends_allruns_allparams, rundirs_allparams, total_runs = \
    caf.report_sims(working_dir, output_dirs, config_dirs, cytosim_dir,
    report, replace_movies)

this is better

    properties_allruns_allparams, configs_allruns_allparams, \
    fiber_ends_allruns_allparams, rundirs_allparams, \
    total_runs = caf.report_fiber_ends(
         working_dir, output_dirs, config_dirs,
         cytosim_dir, report, replace_movies)
    rundirs_allparams_df = pd.DataFrame.from_dict(rundirs_allparams, orient = 'index')
    if save_dataframes == 'yes':
        rundirs_allparams_df.to_pickle(dataframes_dir+'rundirs_allparams.pkl')

    finished reporting 6.11.6_output


<a id="orgb47639e"></a>

# read simulation properties


<a id="org1ef892a"></a>

## put all properties and configs into dataframes

    properties_allparams, config_allparams = caf.props_configs(
        output_dirs, rundirs_allparams_df,
        properties_allruns_allparams, configs_allruns_allparams)
    if save_dataframes == 'yes':
        properties_allparams.to_pickle(dataframes_dir+'properties_allparams.pkl')
        config_allparams.to_pickle(dataframes_dir+'config_allparams.pkl')


<a id="org339ba85"></a>

## filter for properties that vary among simulations

    cols = list(properties_allparams)
    nunique = properties_allparams.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    properties_unique = properties_allparams.drop(cols_to_drop, axis=1)
    #properties_unique = properties_unique.drop(labels='internalize_random_seed',axis=1)
    if save_dataframes == 'yes':
        properties_unique.to_pickle(dataframes_dir+'properties_unique.pkl')
    properties_unique.head()

<table>


<colgroup>
<col  class="org-left">

<col  class="org-right">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-right">glide<sub>random</sub><sub>seed</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>stiffness</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0012<sub>0000</sub>&rsquo;)</td>
<td class="org-right">1.29091e+09</td>
<td class="org-right">40</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0007<sub>0000</sub>&rsquo;)</td>
<td class="org-right">1.1413e+09</td>
<td class="org-right">80</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0016<sub>0000</sub>&rsquo;)</td>
<td class="org-right">9.18455e+08</td>
<td class="org-right">640</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0004<sub>0000</sub>&rsquo;)</td>
<td class="org-right">4.1467e+09</td>
<td class="org-right">640</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0005<sub>0000</sub>&rsquo;)</td>
<td class="org-right">2.63386e+07</td>
<td class="org-right">1280</td>
</tr>
</tbody>
</table>

    cols = list(config_allparams)
    nunique = config_allparams.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    config_unique = config_allparams.drop(cols_to_drop, axis=1)
    #config_unique = config_unique.drop(['membrane_myosin_position'], axis=1)
    config_unique = config_unique.astype('float')
    if save_dataframes == 'yes':
        config_unique.to_pickle(dataframes_dir+'config_unique.pkl')
    config_unique.head()

<table>


<colgroup>
<col  class="org-left">

<col  class="org-right">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>stiffness</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>number</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0012<sub>0000</sub>&rsquo;)</td>
<td class="org-right">40</td>
<td class="org-right">1e+06</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0007<sub>0000</sub>&rsquo;)</td>
<td class="org-right">80</td>
<td class="org-right">100000</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0016<sub>0000</sub>&rsquo;)</td>
<td class="org-right">640</td>
<td class="org-right">1e+06</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0004<sub>0000</sub>&rsquo;)</td>
<td class="org-right">640</td>
<td class="org-right">10000</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0005<sub>0000</sub>&rsquo;)</td>
<td class="org-right">1280</td>
<td class="org-right">10000</td>
</tr>
</tbody>
</table>


<a id="org3992da3"></a>

# parse results into dataframe


<a id="orgb00e806"></a>

## fiber ends

    ends_allparams = caf.get_fiber_ends_2d(output_dirs, rundirs_allparams_df, fiber_ends_allruns_allparams)
    
    if save_dataframes == 'yes':
        ends_allparams.to_pickle(dataframes_dir+'ends_allparams.pkl')
    
    ends_allparams.head()

    finished parsing 6.11.6_output

<table>


<colgroup>
<col  class="org-left">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-right">fiber<sub>id</sub></th>
<th scope="col" class="org-right">length</th>
<th scope="col" class="org-right">minus<sub>state</sub></th>
<th scope="col" class="org-right">minus<sub>xpos</sub></th>
<th scope="col" class="org-right">minus<sub>ypos</sub></th>
<th scope="col" class="org-right">minus<sub>xdir</sub></th>
<th scope="col" class="org-right">minus<sub>ydir</sub></th>
<th scope="col" class="org-right">plus<sub>state</sub></th>
<th scope="col" class="org-right">plus<sub>xpos</sub></th>
<th scope="col" class="org-right">plus<sub>ypos</sub></th>
<th scope="col" class="org-right">plus<sub>xdir</sub></th>
<th scope="col" class="org-right">plus<sub>ydir</sub></th>
<th scope="col" class="org-right">plus<sub>rpos</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0012<sub>0000</sub>&rsquo;, 0.1, 9)</td>
<td class="org-right">9</td>
<td class="org-right">1</td>
<td class="org-right">0</td>
<td class="org-right">4.37804</td>
<td class="org-right">-5.9312</td>
<td class="org-right">0.5723</td>
<td class="org-right">-0.82006</td>
<td class="org-right">0</td>
<td class="org-right">4.75198</td>
<td class="org-right">-6.85142</td>
<td class="org-right">0.26231</td>
<td class="org-right">-0.96498</td>
<td class="org-right">8.33806</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0012<sub>0000</sub>&rsquo;, 0.1, 5)</td>
<td class="org-right">5</td>
<td class="org-right">1</td>
<td class="org-right">0</td>
<td class="org-right">-2.78723</td>
<td class="org-right">-8.55029</td>
<td class="org-right">0.70925</td>
<td class="org-right">-0.70496</td>
<td class="org-right">0</td>
<td class="org-right">-2.39566</td>
<td class="org-right">-9.44762</td>
<td class="org-right">0.25752</td>
<td class="org-right">-0.96626</td>
<td class="org-right">9.74663</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0012<sub>0000</sub>&rsquo;, 0.1, 6)</td>
<td class="org-right">6</td>
<td class="org-right">1</td>
<td class="org-right">0</td>
<td class="org-right">1.71594</td>
<td class="org-right">7.66453</td>
<td class="org-right">0.94765</td>
<td class="org-right">-0.31929</td>
<td class="org-right">0</td>
<td class="org-right">2.60265</td>
<td class="org-right">7.2213</td>
<td class="org-right">0.75858</td>
<td class="org-right">-0.65155</td>
<td class="org-right">7.676</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0012<sub>0000</sub>&rsquo;, 0.1, 14)</td>
<td class="org-right">14</td>
<td class="org-right">5</td>
<td class="org-right">0</td>
<td class="org-right">-3.43021</td>
<td class="org-right">1.12888</td>
<td class="org-right">-0.69244</td>
<td class="org-right">0.72148</td>
<td class="org-right">0</td>
<td class="org-right">-7.83982</td>
<td class="org-right">3.42299</td>
<td class="org-right">-0.86455</td>
<td class="org-right">0.50259</td>
<td class="org-right">8.55451</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.6<sub>output</sub>&rsquo;, &rsquo;run0012<sub>0000</sub>&rsquo;, 0.1, 12)</td>
<td class="org-right">12</td>
<td class="org-right">5</td>
<td class="org-right">0</td>
<td class="org-right">3.36138</td>
<td class="org-right">6.16868</td>
<td class="org-right">0.01631</td>
<td class="org-right">-0.99988</td>
<td class="org-right">0</td>
<td class="org-right">2.42901</td>
<td class="org-right">1.27944</td>
<td class="org-right">-0.36657</td>
<td class="org-right">-0.93039</td>
<td class="org-right">2.74537</td>
</tr>
</tbody>
</table>


<a id="org3232633"></a>

# load in previously parsed dataframes

    ends_allparams = pd.read_pickle(dataframes_dir+'ends_allparams.pkl')
    rundirs_allparams_df = pd.read_pickle(dataframes_dir+'rundirs_allparams.pkl')
    rundirs_allparams_df.fillna(value='empty', inplace=True)
    properties_allparams = pd.read_pickle(dataframes_dir+'properties_allparams.pkl')
    config_allparams = pd.read_pickle(dataframes_dir+'config_allparams.pkl')
    properties_unique = pd.read_pickle(dataframes_dir+'properties_unique.pkl')
    config_unique = pd.read_pickle(dataframes_dir+'config_unique.pkl')


<a id="orgd8533dd"></a>

# plot results


<a id="orgaa11a82"></a>

## actin plus end displacement vs. time


<a id="org4aa6685"></a>

### all parameters

    num_plots = total_runs
    
    width = 6
    if width > num_plots:
        width = 1
    height = int(math.ceil(float(num_plots)/float(width)))
    
    #max_int = solid_allparams['internalization'].max()*1000
    
    # plt.figure(figsize=(4*width,3*height)) #width, height
    fig, ax = plt.subplots(nrows=height, ncols=width, sharex=True, sharey=True, figsize=(6*width,7*height))
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    fig.text(0.5, 0, 'time (s)', ha='center', size=24)
    fig.text(0, 0.5, 'barbed end displacement (μm)', va='center', rotation='vertical', size=24)
    
    plot_no = 0
    
    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        for run in rundirs:
    
            props = config_allparams.loc[output_dir].loc[run]
            #viscosity = props['internalize.cym_viscosity']
            #hip1r_off = props['strongbinder_unbinding'].split(',')[0]
    
            plot_no += 1
    
            plt.subplot(height,width,plot_no) #height, width
            for fiber_id in range(1,26):
                xdisp = ends_allparams.loc[[output_dir], [run], :, [fiber_id]]['plus_xpos']-ends_allparams.loc[(output_dir, run, 0.1, fiber_id)]['plus_xpos']
                ydisp = ends_allparams.loc[[output_dir], [run], :, [fiber_id]]['plus_ypos']-ends_allparams.loc[(output_dir, run, 0.1, fiber_id)]['plus_ypos']
                disp = np.sqrt(np.square(xdisp) + np.square(ydisp))
                x = xdisp.reset_index()['time']
                y = disp
                plt.plot(x,y)
            plt.xlim(right = 5)
            plt.ylim(top = 1.5)
            # plt.xlabel('time (s)')
            # plt.ylabel('internalization (nm)')
    
            title = output_dir+'\n'+run+'\n'
            for prop in list(config_unique):
                title += prop + ' = ' + str(props[prop]) + '\n'
    
            # for prop, value in zip(config_groups, name):
            #     title += prop + ' = ' + str(value) + '\n'
    
    
            plt.title(title)
    
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/'+pref+'_plusend_disp-vs-time_all.svg')

    /tmp/ipykernel_21790/720312654.py:30: MatplotlibDeprecationWarning: Auto-removal of overlapping axes is deprecated since 3.6 and will be removed two minor releases later; explicitly call ax.remove() as needed.
      plt.subplot(height,width,plot_no) #height, width

![img](./.ob-jupyter/8758b80dfecfb60b4157e1cd4981fb545eeed5f5.png)


<a id="orgacf6ea6"></a>

### final myo parameters

    plt.figure(figsize=[6,5])
    
    for fiber_id in range(1,26):
        xdisp = ends_allparams.loc[['6.11.6_output'], ['run0019_0000'], :, [fiber_id]]['plus_xpos']-ends_allparams.loc[('6.11.6_output', 'run0019_0000', 0.1, fiber_id)]['plus_xpos']
        ydisp = ends_allparams.loc[['6.11.6_output'], ['run0019_0000'], :, [fiber_id]]['plus_ypos']-ends_allparams.loc[('6.11.6_output', 'run0019_0000', 0.1, fiber_id)]['plus_ypos']
        disp = np.sqrt(np.square(xdisp) + np.square(ydisp))
        x = xdisp.reset_index()['time']
        y = disp
        plt.plot(x,y)
    
    plt.xlabel('Time ($s$)')
    plt.ylabel('Barbed end\ndisplacement ($\mu m$)')
    plt.tight_layout()
    
    if save_figures == 'yes':
        plt.savefig(working_dir+'figures/publish/gliding_displacement.svg')

![img](./.ob-jupyter/2e8a4a18826bb13c2239dd231ffd1cefae8305e4.png)

    config_allparams.loc[('6.11.6_output', 'run0019_0000')]

    bud_viscosity                                      1
    blobneck_viscosity                                 1
    glide_time_step                                0.001
    glide_viscosity                                  1.0
    glide_steric                                     1.0
    glide_display                            ( style=2 )
    cell_geometry                      ( periodic 10 10)
    cell_number                                    space
    actin_rigidity                                 0.041
    actin_segmentation                              0.01
    actin_display                                      {
    actin_line_width                                 2.0
    actin_line_style                                 1.0
    actin_point_size                                 8.0
    actin_point_style                                2.0
    actin_steric                                     1.0
    actin_steric_radius                            0.008
    myosin_binding_rate                              3.0
    myosin_binding_range                           0.004
    myosin_unbinding_rate                           67.6
    myosin_unbinding_force                         -3.67
    myosin_activity                               mighty
    myosin_max_speed                                 5.0
    myosin_stall_force                          100000.0
    myosin_limit_speed                               1.0
    myosin_display                { size=6; color=red; }
    membrane_myosin_hand                          myosin
    membrane_myosin_stiffness                       80.0
    membrane_myosin_activity                       fixed
    actin_number                                       5
    actin_length                                    10.0
    membrane_myosin_number                      10000000
    gliding_label                (100 pN/um stiffness -)
    gliding_point_size                               6.0
    gliding_style                                    2.0
    gliding_nb_steps                             60000.0
    gliding_nb_frames                              600.0
    Name: (6.11.6_output, run0019_0000), dtype: object


<a id="org0aae294"></a>

## heat map of average velocity

    
    results = []
    
    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        for run in rundirs:
            props = config_unique.loc[(output_dir, run)]
            stiffness = props['membrane_myosin_stiffness']
            number = props['membrane_myosin_number']
    
            fiber_velocities = []
    
            for fiber_id in range(1, 26):
                try:
                    xpos = ends_allparams.loc[[output_dir], [run], :, [fiber_id]]['plus_xpos']
                    ypos = ends_allparams.loc[[output_dir], [run], :, [fiber_id]]['plus_ypos']
                except KeyError:
                    continue  # skip missing fibers
    
                xpos = xpos.droplevel(['param_sweep', 'run', 'id'])
                ypos = ypos.droplevel(['param_sweep', 'run', 'id'])
    
                time = xpos.index.values
                if len(time) < 2:
                    continue  # skip incomplete data
    
                x0, y0 = xpos.iloc[0], ypos.iloc[0]
                disp = np.sqrt((xpos - x0)**2 + (ypos - y0)**2)
    
                # Linear regression: displacement vs. time
                slope, intercept, r_value, p_value, std_err = linregress(time, disp.values)
                fiber_velocities.append(slope)
    
            for v in fiber_velocities:
                results.append([int(stiffness), int(number), v])
    df = pd.DataFrame(results, columns=['stiffness', 'number', 'velocity'])
    
    # Group by parameter combinations
    grouped = df.groupby(['number','stiffness'])['velocity']
    means = grouped.mean().unstack()
    sems = grouped.sem().unstack()
    # Create a string array with "mean\n(±sem)" formatting
    annot_array = means.copy().astype(str)
    
    for i in means.index:
        for j in means.columns:
            mean_val = means.loc[i, j]
            sem_val = sems.loc[i, j]
            if not pd.isna(mean_val) and not pd.isna(sem_val):
                annot_array.loc[i, j] = f"{mean_val:.3f}\n(±{sem_val:.3f})"
            else:
                annot_array.loc[i, j] = ""
    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(means, annot=annot_array, fmt='', cmap='magma',
                     cbar_kws={'label': 'Mean barbed end velocity ($\\frac{\\mu m}{s}$)'})
    
    
    # Set log-style tick labels
    ax.set_yticklabels([f'$10^{{{int(np.log10(y))}}}$' for y in means.index], rotation=0)
    
    ax.invert_yaxis()
    
    plt.ylabel('Myosin molecule count')
    plt.xlabel('Myosin bond stiffness ($\\frac{pN}{\\mu m}$)')
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/publish/plusend_mean_velocity_heatmap.svg')

![img](./.ob-jupyter/1bdd22f017b344fdd705ac67d790fe01d2d7c0ee.png)


<a id="org8001e05"></a>

## line plot of average velocity

    
    results = []
    
    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        for run in rundirs:
            props = config_unique.loc[(output_dir, run)]
            stiffness = props['membrane_myosin_stiffness']
            number = props['membrane_myosin_number']
    
            fiber_velocities = []
    
            for fiber_id in range(1, 26):
                try:
                    xpos = ends_allparams.loc[[output_dir], [run], :, [fiber_id]]['plus_xpos']
                    ypos = ends_allparams.loc[[output_dir], [run], :, [fiber_id]]['plus_ypos']
                except KeyError:
                    continue  # skip missing fibers
    
                xpos = xpos.droplevel(['param_sweep', 'run', 'id'])
                ypos = ypos.droplevel(['param_sweep', 'run', 'id'])
    
                time = xpos.index.values
                if len(time) < 2:
                    continue  # skip incomplete data
    
                x0, y0 = xpos.iloc[0], ypos.iloc[0]
                disp = np.sqrt((xpos - x0)**2 + (ypos - y0)**2)
    
                # Linear regression: displacement vs. time
                slope, intercept, r_value, p_value, std_err = linregress(time, disp.values)
                fiber_velocities.append(slope)
    
            for v in fiber_velocities:
                results.append([int(stiffness), int(number), v])
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=['stiffness', 'number', 'velocity'])
    
    # Plot
    plt.figure(figsize=(8, 6))
    
    for myonumber in np.sort(config_unique['membrane_myosin_number'].unique()):
        # Filter for myosin count = 10^7
        dfnum = df[df['number'] == myonumber]
    
        # Group by stiffness
        grouped = dfnum.groupby('stiffness')['velocity']
        means = grouped.mean()
        errors = grouped.apply(sem)
    
        # Sort
        stiffness_sorted = sorted(means.index)
        means_sorted = means.loc[stiffness_sorted]
        errors_sorted = errors.loc[stiffness_sorted]
    
        plt.plot(stiffness_sorted, means_sorted,
                 label=f'$10^{{{int(np.log10(myonumber))}}}$')
        plt.fill_between(stiffness_sorted,
                        means_sorted - errors_sorted,
                        means_sorted + errors_sorted,
                        alpha=0.3)
    
    plt.xscale('log',base=2)
    #plt.xticks(stiffness_sorted, [f'$10^{{{int(np.log10(x))}}}$' for x in stiffness_sorted])
    plt.xlabel('Myosin bond stiffness ($\\frac{pN}{\\mu m}$)')
    plt.ylabel('Mean barbed end velocity ($\\frac{\\mu m}{s}$)')
    leg = plt.legend(title='Myosin\nmolecule\ncount')
    plt.setp(leg.get_title(), multialignment='center')
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/publish/plusend_mean_velocity_line.svg')

![img](./.ob-jupyter/8a5627cc2195b1518ba71a055d459b27cb4846ab.png)

