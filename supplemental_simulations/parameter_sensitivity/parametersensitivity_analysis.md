
# Table of Contents

1.  [export this to other file formats](#org1d6e141)
    1.  [convert to jupyter notebook](#orga6adba2)
        1.  [using pandoc](#org574a250)
        2.  [using orgparse](#orgd1abb84)
    2.  [export to org document](#org26f3248)
    3.  [export to markdown document](#org5b2dd0c)
2.  [figure generation index](#org4b0b7f7)
3.  [configuration](#orgba16e35)
    1.  [set global variables](#org074739d)
    2.  [load and configure libraries](#orge7a594e)
    3.  [set working directories](#org7ddfeff)
    4.  [load custom functions](#orgbe7688a)
4.  [find directories that have outputs or config files](#org7a379e4)
5.  [report simulations](#orgea37811)
6.  [read in reports](#org3608e58)
7.  [read simulation properties](#org435441e)
    1.  [put all properties and configs into dataframes](#org7fa1907)
    2.  [filter for properties that vary among simulations](#orgeb929ac)
8.  [parse results into dataframe](#org5639965)
    1.  [solid positions](#org30ba405)
    2.  [all hip1r](#orgd8beb59)
    3.  [all myosin](#org394715c)
    4.  [fiber forces](#org20025a8)
    5.  [fiber ends](#org2580a94)
    6.  [merge positions with run properties/configs](#org4290ccb)
        1.  [solid](#org6c8d22c)
        2.  [myosin](#orgae952c5)
    7.  [write dataframes to file](#orgb79b510)
9.  [load in previously parsed dataframes](#org4c05d0d)
10. [Analyze 95 percentile](#org5052e5d)
11. [Analyze actin density](#orga339bfc)
    1.  [total actin at final timepoint](#org4d09508)
12. [plot results](#org3c58e2e)
    1.  [internalization](#orgc2b62da)
        1.  [all runs on separate plots](#org7fdb1d1)
        2.  [means of runs with same properties](#org22d1340)
        3.  [means of individual parameter sweeps](#orgca6230a)
    2.  [cumulative histogram](#org8c124b5)
    3.  [plot 95th percentile internalization vs. parameter sweeps](#orgc07c166)
        1.  [scatterplot overlaid points](#orgf037339)
        2.  [average scatterplot](#orgcfa367f)
        3.  [line plots](#org795746d)



<a id="org1d6e141"></a>

# export this to other file formats

These files are symbolically linked such that their source is the
version-controlled directory, but they can be exported from the local directory
where the analysis happens

Due to this difference in directory structure, anyone else using these scripts
will have to make sure the locations of their data are specified correctly in
the [set working directories](#org7ddfeff) scetion.


<a id="orga6adba2"></a>

## convert to jupyter notebook


<a id="org574a250"></a>

### using pandoc

this looks nice but it&rsquo;s just a big markdown block

    pandoc 6.11_analysis.org -o parametersensitivity_analysis_pandoc.ipynb


<a id="orgd1abb84"></a>

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
    org_to_ipynb("6.11_analysis.org",
                 "parametersensitivity_analysis_orgparse.ipynb")

    (org-babel-tangle)

    627097af9e3800a99b0fb311a0cddf83

    python convert_org_to_ipynb.py


<a id="org26f3248"></a>

## export to org document

    (org-org-export-to-org)

    046b7164b660d8e1108c4c5b2cbfd5b2


<a id="org5b2dd0c"></a>

## export to markdown document

    (org-md-export-to-markdown)

    bce56a6f62f06dc21a3b50f4c8338530


<a id="org4b0b7f7"></a>

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
<td class="org-left">E</td>
<td class="org-left"><a href="#org795746d">line plots</a></td>
</tr>

<tr>
<td class="org-left">S2</td>
<td class="org-left">F</td>
<td class="org-left"><a href="#org795746d">line plots</a></td>
</tr>

<tr>
<td class="org-left">S2</td>
<td class="org-left">G</td>
<td class="org-left"><a href="#org795746d">line plots</a></td>
</tr>

<tr>
<td class="org-left">S2</td>
<td class="org-left">H</td>
<td class="org-left"><a href="#org795746d">line plots</a></td>
</tr>
</tbody>
</table>


<a id="orgba16e35"></a>

# configuration


<a id="org074739d"></a>

## set global variables

    #timestep = 5e-5
    report = 'no'
    replace_movies = 'no'
    save_figures = 'yes'
    save_dataframes = 'yes'


<a id="orge7a594e"></a>

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
    from scipy.stats import binned_statistic_2d
    from scipy import stats
    from scipy.signal import savgol_filter
    from scipy.signal import find_peaks
    import textwrap
    from decimal import Decimal
    from scipy.stats import binned_statistic_2d
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


<a id="org7ddfeff"></a>

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
    
    
    working_dir = os.path.join(drive_dir, 'grad_school/db_lab/code/analysis/20230610_6.11_parameter_sensitivity/')
    cytosim_dir = os.path.join(drive_dir, 'grad_school/db_lab/code/cytosim_dblab/', machine)
    
    if machine == 'peeks':
        working_dir = '/run/media/ferrin/Volume/max/analysis/20230610_6.11_parameter_sensitivity/'
        cytosim_dir = '/home/ferrin/cytosim/'
    
    dataframes_dir = os.path.join(working_dir,'dataframes/')
    
    os.chdir(working_dir)
    
    if os.path.isdir('figures') == False:
        os.mkdir('figures')
    if os.path.isdir('dataframes') == False:
        os.mkdir('dataframes')


<a id="orgbe7688a"></a>

## load custom functions

    # add parent folder to path
    sys.path.insert(1, '../')
    from cytosim_analysis import cytosim_analysis_functions as caf
    
    # reload custom library
    from importlib import reload
    reload(sys.modules['cytosim_analysis'])

    <module 'cytosim_analysis' from '/home/maxferrin/SynologyDrive/google_drive/grad_school/db_lab/code/analysis/20230610_6.11_parameter_sensitivity/../cytosim_analysis/__init__.py'>


<a id="org7a379e4"></a>

# find directories that have outputs or config files

    output_dirs, config_dirs = caf.find_directories()
    print(output_dirs, config_dirs)

    ['6.11.9_output', '6.11.8_output', '6.11.4_output', '6.11.1_output', '6.11.2_output', '6.11.7_output', '6.11.3_output'] ['6.11.2', '6.11.7', '6.11.3', '6.11.8', '6.11.1', '6.11.9', '6.11.4']


<a id="orgea37811"></a>

# report simulations

    caf.report_sims(working_dir, output_dirs, cytosim_dir, report)

    starting simulations/20230504_6.6.5_myominimal_output/run0000_0000
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    Warning, a value was unused:
            | confine = 3, 0, insidecell;
            |    used : 1, 0,          1
    in
          96  set couple 0 arp2
          97  {
          98   hand1          = binder;
          99   hand2          = boundNucleator;
         100   stiffness      = 100000;
         101   diffusion      = 0.0001;
         102   confine        = 3, 0, insidecell;
         103   activity       = fork;
         104   trans_activated = 1;
         105   torque         = 0.076, 1.22;
         106  }
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    Warning, a value was unused:
            | confine = 3, 0, insidecell;
            |    used : 1, 0,          1
    in
          96  set couple 0 arp2
          97  {
          98   hand1          = binder;
          99   hand2          = boundNucleator;
         100   stiffness      = 100000;
         101   diffusion      = 0.0001;
         102   confine        = 3, 0, insidecell;
         103   activity       = fork;
         104   trans_activated = 1;
         105   torque         = 0.076, 1.22;
         106  }
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    Warning, a value was unused:
            | confine = 3, 0, insidecell;
            |    used : 1, 0,          1
    in
          96  set couple 0 arp2
          97  {
          98   hand1          = binder;
          99   hand2          = boundNucleator;
         100   stiffness      = 100000;
         101   diffusion      = 0.0001;
         102   confine        = 3, 0, insidecell;
         103   activity       = fork;
         104   trans_activated = 1;
         105   torque         = 0.076, 1.22;
         106  }
    Warning, a value was unused:
            | confine = 3, 0, insidecell;
            |    used : 1, 0,          1
    in
          96  set couple 0 arp2
          97  {
          98   hand1          = binder;
          99   hand2          = boundNucleator;
         100   stiffness      = 100000;
         101   diffusion      = 0.0001;
         102   confine        = 3, 0, insidecell;
         103   activity       = fork;
         104   trans_activated = 1;
         105   torque         = 0.076, 1.22;
         106  }
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    auto setting simul:steric_max_range=0.030
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning messages are now silent
    Warning, a value was unused:
            | confine = 3, 0, insidecell;
            |    used : 1, 0,          1
    in
          96  set couple 0 arp2
          97  {
          98   hand1          = binder;
          99   hand2          = boundNucleator;
         100   stiffness      = 100000;
         101   diffusion      = 0.0001;
         102   confine        = 3, 0, insidecell;
         103   activity       = fork;
         104   trans_activated = 1;
         105   torque         = 0.076, 1.22;
         106  }
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    Warning, a value was unused:
            | confine = 3, 0, insidecell;
            |    used : 1, 0,          1
    in
          96  set couple 0 arp2
          97  {
          98   hand1          = binder;
          99   hand2          = boundNucleator;
         100   stiffness      = 100000;
         101   diffusion      = 0.0001;
         102   confine        = 3, 0, insidecell;
         103   activity       = fork;
         104   trans_activated = 1;
         105   torque         = 0.076, 1.22;
         106  }
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    auto setting simul:steric_max_range=0.030
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is indepWarning, a value was unused:
            | confine = 3, 0, insidecell;
            |    used : 1, 0,          1
    in
          96  set couple 0 arp2
          97  {
          98   hand1          = binder;
          99   hand2          = boundNucleator;
         100   stiffness      = 100000;
         101   diffusion      = 0.0001;
         102   confine        = 3, 0, insidecell;
         103   activity       = fork;
         104   trans_activated = 1;
         105   torque         = 0.076, 1.22;
         106  }
    endent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning: hand `binder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 2380.95 kT
    warning: hand `strongbinder' overcomes high energy when binding:
            | stiffness * binding_range^2 = 8571.43 kT
    warning: The efficiency of `myosin' is low:
            | stiffness * max_speed / stall_force * unbinding_rate = 0.0147929
    warning: fiber:catastrophe_rate is independent of force (catastrophe_rate[0] == catastrophe_rate[1])
    warning messages are now silent
    finished reporting 20230504_6.6.5_myominimal_output


<a id="org3608e58"></a>

# read in reports

-   not enough memory to do all at once!
-   just fiber forces alone requires too much memory

    reports = [
        'solid',
        # 'single_hip1r',
        'single_membrane_myosin'#,
        # 'fiber_cluster',
        # 'fiber_forces',
        # 'fiber_tensions',
        # 'fiber_ends'
        ]
    
    #reports = ['solid']
    #reports = ['fiber_ends']
    
    solid_allruns_allparams, properties_allruns_allparams, \
    configs_allruns_allparams, single_hip1r_allruns_allparams, \
    single_membrane_myosin_allruns_allparams, fiber_forces_allruns_allparams, \
    fiber_clusters_allruns_allparams, fiber_tensions_allruns_allparams, \
    fiber_ends_allruns_allparams, rundirs_allparams, total_runs = \
    caf.open_reports(reports, working_dir, output_dirs, config_dirs,
    cytosim_dir, replace_movies)
    
    if save_dataframes == 'yes':
        pd.DataFrame.from_dict(rundirs_allparams, orient = 'index').to_pickle(dataframes_dir+'rundirs_allparams.pkl')

    finished reporting 6.11.9_output
    finished reporting 6.11.8_output
    finished reporting 6.11.4_output
    finished reporting 6.11.1_output
    finished reporting 6.11.2_output
    finished reporting 6.11.7_output
    finished reporting 6.11.3_output


<a id="org435441e"></a>

# read simulation properties


<a id="org7fa1907"></a>

## put all properties and configs into dataframes

    properties_allparams, config_allparams = caf.props_configs(
        output_dirs, rundirs_allparams_df,
        properties_allruns_allparams, configs_allruns_allparams)


<a id="orgeb929ac"></a>

## filter for properties that vary among simulations

    cols = list(properties_allparams)
    nunique = properties_allparams.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    properties_unique = properties_allparams.drop(cols_to_drop, axis=1)
    properties_unique = properties_unique.drop(labels='internalize_random_seed',axis=1)
    properties_unique.head()

<table>


<colgroup>
<col  class="org-left">

<col  class="org-left">

<col  class="org-left">

<col  class="org-right">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-left">myosin<sub>binding</sub></th>
<th scope="col" class="org-left">myosin<sub>unbinding</sub></th>
<th scope="col" class="org-right">myosin<sub>stall</sub><sub>force</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>stiffness</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, -3.67</td>
<td class="org-right">100</td>
<td class="org-right">100</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0004<sub>0002</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, -3.67</td>
<td class="org-right">10000</td>
<td class="org-right">100</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0007<sub>0003</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, 0</td>
<td class="org-right">10</td>
<td class="org-right">100</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0003</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, 0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0002</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, 0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
</tr>
</tbody>
</table>

    cols = list(config_allparams)
    nunique = config_allparams.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    config_unique = config_allparams.drop(cols_to_drop, axis=1)
    config_unique = config_unique.drop(['membrane_myosin_position'], axis=1)
    config_unique = config_unique.astype('float')
    config_unique.head()

<table>


<colgroup>
<col  class="org-left">

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
<th scope="col" class="org-right">myosin<sub>binding</sub><sub>rate</sub></th>
<th scope="col" class="org-right">myosin<sub>binding</sub><sub>range</sub></th>
<th scope="col" class="org-right">myosin<sub>unbinding</sub><sub>force</sub></th>
<th scope="col" class="org-right">myosin<sub>stall</sub><sub>force</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>stiffness</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>zoffset</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">-3.67</td>
<td class="org-right">100</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0004<sub>0002</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">-3.67</td>
<td class="org-right">10000</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0007<sub>0003</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">0</td>
<td class="org-right">10</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0003</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0002</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
</tr>
</tbody>
</table>


<a id="org5639965"></a>

# parse results into dataframe


<a id="org30ba405"></a>

## solid positions

    solid_allparams = caf.solid_positions(output_dirs, rundirs_allparams_df, solid_allruns_allparams)
    
    if save_dataframes == 'yes':
        solid_allparams.to_pickle(dataframes_dir+'solid_allparams.pkl')
    
    solid_allparams.head()

    finished parsing 6.11.9_output
    finished parsing 6.11.8_output
    finished parsing 6.11.4_output
    finished parsing 6.11.1_output
    finished parsing 6.11.2_output
    finished parsing 6.11.7_output
    finished parsing 6.11.3_output

<table>


<colgroup>
<col  class="org-left">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-right">xpos</th>
<th scope="col" class="org-right">ypos</th>
<th scope="col" class="org-right">zpos</th>
<th scope="col" class="org-right">rpos</th>
<th scope="col" class="org-right">internalization</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;, 0.1, 1)</td>
<td class="org-right">-0.0010335</td>
<td class="org-right">-8.14752e-05</td>
<td class="org-right">-0.395141</td>
<td class="org-right">0.00103671</td>
<td class="org-right">0.004859</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;, 0.2, 1)</td>
<td class="org-right">-0.00310684</td>
<td class="org-right">-0.00010208</td>
<td class="org-right">-0.390416</td>
<td class="org-right">0.00310852</td>
<td class="org-right">0.009584</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;, 0.3, 1)</td>
<td class="org-right">-0.00202646</td>
<td class="org-right">0.000248301</td>
<td class="org-right">-0.389811</td>
<td class="org-right">0.00204162</td>
<td class="org-right">0.010189</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;, 0.4, 1)</td>
<td class="org-right">-0.00277034</td>
<td class="org-right">0.000786084</td>
<td class="org-right">-0.388449</td>
<td class="org-right">0.00287971</td>
<td class="org-right">0.011551</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;, 0.5, 1)</td>
<td class="org-right">-0.00266495</td>
<td class="org-right">0.000313034</td>
<td class="org-right">-0.388158</td>
<td class="org-right">0.00268327</td>
<td class="org-right">0.011842</td>
</tr>
</tbody>
</table>


<a id="orgd8beb59"></a>

## all hip1r

    hip1r_allparams = caf.all_hip1r(output_dirs, rundirs_allparams, single_hip1r_allruns_allparams)
    
    hip1r_allparams.head()

    finished parsing 6.11.7_output
    finished parsing 6.11.8_output
    finished parsing 6.11.9_output

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
<th scope="col" class="org-right">state</th>
<th scope="col" class="org-right">fiber<sub>id</sub></th>
<th scope="col" class="org-right">xpos</th>
<th scope="col" class="org-right">single<sub>id</sub></th>
<th scope="col" class="org-right">ypos</th>
<th scope="col" class="org-right">zpos</th>
<th scope="col" class="org-right">xforce</th>
<th scope="col" class="org-right">yforce</th>
<th scope="col" class="org-right">zforce</th>
<th scope="col" class="org-right">abscissa</th>
<th scope="col" class="org-right">direction</th>
<th scope="col" class="org-right">scalar<sub>force</sub></th>
<th scope="col" class="org-right">rpos</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.1, 139)</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0117935</td>
<td class="org-right">139</td>
<td class="org-right">-0.0358308</td>
<td class="org-right">-0.42078</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0377218</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.1, 84)</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0159765</td>
<td class="org-right">84</td>
<td class="org-right">0.0430262</td>
<td class="org-right">-0.396362</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0458966</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.1, 34)</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">-0.0161225</td>
<td class="org-right">34</td>
<td class="org-right">0.0434512</td>
<td class="org-right">-0.404726</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0463459</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.1, 71)</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.00537152</td>
<td class="org-right">71</td>
<td class="org-right">-0.0251148</td>
<td class="org-right">-0.363301</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0256828</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.1, 112)</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0405095</td>
<td class="org-right">112</td>
<td class="org-right">0.0163722</td>
<td class="org-right">-0.407906</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0</td>
<td class="org-right">0.0436929</td>
</tr>
</tbody>
</table>


<a id="org394715c"></a>

## all myosin

    membrane_myosin_allparams = caf.all_myosin(output_dirs, rundirs_allparams, single_membrane_myosin_allruns_allparams)
    
    membrane_myosin_allparams.head()

    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[38], line 1
    ----> 1 membrane_myosin_allparams = caf.all_myosin(output_dirs, rundirs_allparams, single_membrane_myosin_allruns_allparams)
          3 membrane_myosin_allparams.head()
    
    NameError: name 'rundirs_allparams' is not defined


<a id="org20025a8"></a>

## fiber forces

    forces_allparams = caf.get_fiber_forces(output_dirs, rundirs_allparams, fiber_forces_allruns_allparams)
    
    forces_allparams.head()

    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[39], line 1
    ----> 1 forces_allparams = caf.get_fiber_forces(output_dirs, rundirs_allparams, fiber_forces_allruns_allparams)
          3 forces_allparams.head()
    
    NameError: name 'rundirs_allparams' is not defined


<a id="org2580a94"></a>

## fiber ends

    ends_allparams = caf.get_fiber_ends(output_dirs, rundirs_allparams, fiber_ends_allruns_allparams)
    
    ends_allparams.head()

    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[40], line 1
    ----> 1 ends_allparams = caf.get_fiber_ends(output_dirs, rundirs_allparams, fiber_ends_allruns_allparams)
          3 ends_allparams.head()
    
    NameError: name 'rundirs_allparams' is not defined


<a id="org4290ccb"></a>

## merge positions with run properties/configs


<a id="org6c8d22c"></a>

### solid

    solid_properties = pd.merge(properties_unique.reset_index(), solid_allparams.reset_index(),
                                on=['param_sweep', 'run'], how='outer').set_index(['param_sweep', 'run'])
    property_groups = list(properties_unique)
    solid_property_groups = solid_properties.groupby(property_groups)
    groups = property_groups + ['time']
    grouped = solid_properties.groupby(groups)
    means = grouped['internalization'].mean()
    stds = grouped['internalization'].std()

    solid_config = pd.merge(config_unique.reset_index(), solid_allparams.reset_index(),
                            on=['param_sweep', 'run'], how='outer').set_index(['param_sweep', 'run'])
    config_groups = list(config_unique)
    solid_config_groups = solid_config.groupby(config_groups)
    groups = config_groups + ['time']
    grouped = solid_config.groupby(groups)
    means = grouped['internalization'].mean()
    stds = grouped['internalization'].std()
    means.head()

    myosin_binding_range  myosin_unbinding_force  myosin_stall_force  membrane_myosin_zoffset  time
    0.0                   -3.67                   1000000.0           0.008                    0.1     0.002250
                                                                                               0.2     0.002859
                                                                                               0.3     0.003538
                                                                                               0.4     0.003025
                                                                                               0.5     0.003910
    Name: internalization, dtype: float64

    config_groups = list(config_unique)
    sweep_groups = config_groups + ['param_sweep']
    solid_sweep_groups = solid_config.groupby(sweep_groups)
    groups_sweep = sweep_groups + ['time']
    grouped_sweep = solid_config.groupby(groups_sweep)
    sweep_means = grouped_sweep['internalization'].mean()
    sweep_stds = grouped_sweep['internalization'].std()
    
    sweep_means.head()

    myosin_binding_range  myosin_unbinding_force  myosin_stall_force  membrane_myosin_zoffset  param_sweep    time
    0.0                   -3.67                   1000000.0           0.008                    6.11.7_output  0.1     0.002250
                                                                                                              0.2     0.002859
                                                                                                              0.3     0.003538
                                                                                                              0.4     0.003025
                                                                                                              0.5     0.003910
    Name: internalization, dtype: float64


<a id="orgae952c5"></a>

### myosin

    membrane_myosin_config = pd.merge(config_unique.reset_index(), membrane_myosin_allparams.reset_index(),
                            on=['param_sweep', 'run'], how='outer').set_index(['param_sweep', 'run'])
    membrane_myosin_grouped = membrane_myosin_config.groupby(groups)
    membrane_myosin_zpos_means = membrane_myosin_grouped['zpos'].mean()
    membrane_myosin_zpos_stds = membrane_myosin_grouped['zpos'].std()
    membrane_myosin_zpos_means.head()

    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[44], line 1
    ----> 1 membrane_myosin_config = pd.merge(config_unique.reset_index(), membrane_myosin_allparams.reset_index(),
          2                         on=['param_sweep', 'run'], how='outer').set_index(['param_sweep', 'run'])
          3 membrane_myosin_grouped = membrane_myosin_config.groupby(groups)
          4 membrane_myosin_zpos_means = membrane_myosin_grouped['zpos'].mean()
    
    NameError: name 'config_unique' is not defined


<a id="orgb79b510"></a>

## write dataframes to file

    if save_dataframes == 'yes':
        membrane_myosin_allparams.to_pickle(dataframes_dir+'membrane_myosin_allparams.pkl')
        means.to_pickle(dataframes_dir+'means.pkl')
        stds.to_pickle(dataframes_dir+'stds.pkl')
        sweep_means.to_pickle(dataframes_dir+'sweep_means.pkl')
        sweep_stds.to_pickle(dataframes_dir+'sweep_stds.pkl')
        pd.DataFrame.from_dict(rundirs_allparams, orient = 'index').to_pickle(dataframes_dir+'rundirs_allparams.pkl')
        properties_allparams.to_pickle(dataframes_dir+'properties_allparams.pkl')
        properties_unique.to_pickle(dataframes_dir+'properties_unique.pkl')


<a id="org4c05d0d"></a>

# load in previously parsed dataframes

    solid_allparams = pd.read_pickle(dataframes_dir+'solid_allparams.pkl')
    membrane_myosin_allparams = pd.read_pickle(dataframes_dir+'membrane_myosin_allparams.pkl')
    means = pd.read_pickle(dataframes_dir+'means.pkl')
    stds = pd.read_pickle(dataframes_dir+'stds.pkl')
    sweep_means = pd.read_pickle(dataframes_dir+'sweep_means.pkl')
    sweep_stds = pd.read_pickle(dataframes_dir+'sweep_stds.pkl')
    rundirs_allparams_df = pd.read_pickle(dataframes_dir+'rundirs_allparams.pkl')
    rundirs_allparams_df.fillna(value='empty', inplace=True)
    properties_allparams = pd.read_pickle(dataframes_dir+'properties_allparams.pkl')
    properties_unique = pd.read_pickle(dataframes_dir+'properties_unique.pkl')
    percentiles = pd.read_pickle(dataframes_dir+'percentiles.pkl')
    property_groups = list(properties_unique)

    total_runs = len(solid_allparams.groupby(['param_sweep','run']).count())
    solid_allparams.head()

<table>


<colgroup>
<col  class="org-left">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-right">xpos</th>
<th scope="col" class="org-right">ypos</th>
<th scope="col" class="org-right">zpos</th>
<th scope="col" class="org-right">internalization</th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.1, 1)</td>
<td class="org-right">-0.00101148</td>
<td class="org-right">0.00144418</td>
<td class="org-right">-0.399063</td>
<td class="org-right">0.000937</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.2, 1)</td>
<td class="org-right">-0.00171051</td>
<td class="org-right">0.0014364</td>
<td class="org-right">-0.40067</td>
<td class="org-right">-0.00067</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.3, 1)</td>
<td class="org-right">-0.00221865</td>
<td class="org-right">0.000220836</td>
<td class="org-right">-0.401077</td>
<td class="org-right">-0.001077</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.4, 1)</td>
<td class="org-right">-0.000739329</td>
<td class="org-right">-0.000674097</td>
<td class="org-right">-0.399485</td>
<td class="org-right">0.000515</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.7<sub>output</sub>&rsquo;, &rsquo;run0010<sub>0003</sub>&rsquo;, 0.5, 1)</td>
<td class="org-right">0.000122646</td>
<td class="org-right">-0.000426902</td>
<td class="org-right">-0.399866</td>
<td class="org-right">0.000134</td>
</tr>
</tbody>
</table>


<a id="org5052e5d"></a>

# Analyze 95 percentile

    percentiles = caf.get_percentiles(output_dirs, rundirs_allparams_df, solid_allparams, properties_allparams)
    
    if save_dataframes == 'yes':
        percentiles.to_pickle(dataframes_dir+'percentiles.pkl')
    percentiles.head()

<table>


<colgroup>
<col  class="org-left">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-right">95<sub>percentile</sub><sub>internalization</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;)</td>
<td class="org-right">63.3802</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0004<sub>0002</sub>&rsquo;)</td>
<td class="org-right">70.4585</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0007<sub>0003</sub>&rsquo;)</td>
<td class="org-right">78.1793</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0003</sub>&rsquo;)</td>
<td class="org-right">56.3346</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0002</sub>&rsquo;)</td>
<td class="org-right">47.9612</td>
</tr>
</tbody>
</table>


<a id="orga339bfc"></a>

# Analyze actin density


<a id="org4d09508"></a>

## total actin at final timepoint

    actin_endpoints = caf.get_actin_endpoints(output_dirs, rundirs_allparams_df, forces_allparams)
    actin_endpoints.head()

    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[49], line 1
    ----> 1 actin_endpoints = caf.get_actin_endpoints(output_dirs, rundirs_allparams_df, forces_allparams)
          2 actin_endpoints.head()
    
    NameError: name 'forces_allparams' is not defined


<a id="org3c58e2e"></a>

# plot results


<a id="orgc2b62da"></a>

## internalization


<a id="org7fdb1d1"></a>

### all runs on separate plots

    num_plots = total_runs
    
    width = 6
    if width > num_plots:
        width = 1
    height = int(math.ceil(float(num_plots)/float(width)))
    
    max_int = solid_allparams['internalization'].max()*1000
    
    # plt.figure(figsize=(4*width,3*height)) #width, height
    fig, ax = plt.subplots(nrows=height, ncols=width, sharex=True, sharey=True, figsize=(4*width,5*height))
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    fig.text(0.5, 0, 'time (s)', ha='center', size=24)
    fig.text(0, 0.5, 'internalization (nm)', va='center', rotation='vertical', size=24)
    
    plot_no = 0
    
    for output_dir in output_dirs:
        rundirs = rundirs_allparams[output_dir]
        for run in rundirs:
    
            df = solid_allparams.loc[output_dir].loc[run]
            x = df.reset_index()['time']
            y = df['internalization']*1000
            props = properties_allparams.loc[output_dir].loc[run]
            viscosity = props['internalize.cym_viscosity']
            hip1r_off = props['strongbinder_unbinding'].split(',')[0]
    
            plot_no += 1
    
            plt.subplot(height,width,plot_no) #height, width
            plt.plot(x,y)
            plt.xlim(right = 15)
            plt.ylim(top = max_int)
            # plt.xlabel('time (s)')
            # plt.ylabel('internalization (nm)')
    
            title = output_dir+'\n'+run+'\n'
            for prop in property_groups:
                title += prop + ' = ' + str(props[prop]) + '\n'
    
            # for prop, value in zip(config_groups, name):
            #     title += prop + ' = ' + str(value) + '\n'
    
    
            plt.title(title)
    
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/'+pref+'_solid_zpos-vs-time_all.png')

    /tmp/ipykernel_31531/3988983614.py:33: MatplotlibDeprecationWarning: Auto-removal of overlapping axes is deprecated since 3.6 and will be removed two minor releases later; explicitly call ax.remove() as needed.
      plt.subplot(height,width,plot_no) #height, width

![img](./.ob-jupyter/37370d2c98575b9cecedb7985ab78bc512907353.png)


<a id="org22d1340"></a>

### means of runs with same properties

    # num_plots = len(solid_property_groups)
    num_plots = len(solid_config_groups)
    
    width = 6
    if width > num_plots:
        width = 1
    height = int(math.ceil(float(num_plots)/float(width)))
    
    fig = plt.figure()
    fig.set_size_inches(4*width,4*height)
    
    commonaxis = plt.axes(frameon=False)
    commonaxis.set_xticks([])
    commonaxis.set_yticks([])
    commonaxis.yaxis.labelpad = 40 # move the labels a bit away from panels
    commonaxis.xaxis.labelpad = 40 # move the labels a bit away from panels
    commonaxis.set( xlabel = 'time (s)' )
    commonaxis.set( ylabel = 'internalization (nm)' )
    
    plot_no = 1
    plot_max = np.max(means + stds)*1000
    plot_min = np.min(means - stds)*1000
    
    for name, group in solid_config_groups:
        x = means.loc[name].reset_index()['time']
        y = means.loc[name]*1000
        std = stds.loc[name]*1000
    
        ax = fig.add_subplot(height, width, plot_no)
        ax.errorbar(x,y,std)
        ax.set_xlim(right = 15)
        ax.set_ylim(bottom = plot_min, top = plot_max)
    
        title = ''
        for prop, value in zip(config_groups, name):
            title += prop + ' = ' + str(round(value,3)) + '\n'
    
        ax.set_title(title)
        # ax2[plot_row, plot_col].set_title(title)
    
        print(plot_no)
    
        plot_no += 1
    
    plt.tight_layout()
    
    if save_figures == 'yes':
        plt.savefig(working_dir+'figures/'+pref+'_mean_solid_zpos-vs-time_all.png')

    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    11
    12
    13
    14
    15
    16
    17
    18
    19
    20
    21
    22
    23
    24
    25
    26
    27
    28
    29
    30
    31
    32

![img](./.ob-jupyter/a0ba74a131123d1a1abc8d4a6161e448cccb9c1a.png)


<a id="orgca6230a"></a>

### means of individual parameter sweeps

    for sweep in output_dirs:
        sweep_config = config_unique.loc[sweep]
        sweep_config_nunique = sweep_config.apply(pd.Series.nunique)
        cols_to_drop = sweep_config_nunique[sweep_config_nunique == 1].index
        sweep_config_unique = sweep_config.drop(cols_to_drop, axis = 1)
    
        sweep_plots = []
        for name, group in solid_sweep_groups:
            if sweep in name:
                sweep_plots.append(name)
    
        num_plots = len(sweep_plots)
    
        width = 6
        if width > num_plots:
            width = num_plots
        if num_plots == 24:
            width = 5
        height = int(math.ceil(float(num_plots)/float(width)))
    
        fig = plt.figure()
        fig.set_size_inches(4*width,4*height)
        # if height == 1:
        #     fig.set_size_inches(4*width,6*height)
        # else:
        #     fig.set_size_inches(4*width,5*height)
        fig.suptitle(sweep)
    
        commonaxis = plt.axes(frameon=False)
        commonaxis.set_xticks([])
        commonaxis.set_yticks([])
        commonaxis.yaxis.labelpad = 40 # move the labels a bit away from panels
        commonaxis.xaxis.labelpad = 60 # move the labels a bit away from panels
        commonaxis.set( xlabel = 'time (s)' )
        commonaxis.set( ylabel = 'internalization (nm)' )
    
        plot_no = 1
        plot_max = np.max(sweep_means + sweep_stds)*1000
        plot_min = np.min(sweep_means - sweep_stds)*1000
    
        for name in sweep_plots:
            x = sweep_means.loc[name].reset_index()['time']
            y = sweep_means.loc[name]*1000
            std = sweep_stds.loc[name]*1000
    
            ax = fig.add_subplot(height, width, plot_no)
            ax.errorbar(x,y,std)
            ax.set_xlim(right = 15)
            ax.set_ylim(bottom = plot_min, top = plot_max)
    
            title = ''
            for prop, value in zip(config_groups, name):
                addition = prop + ' = ' + str(round(value,3)) + '\n'
                if prop in list(sweep_config_unique):
                    title += addition
    
    
            ax.set_title(title)
    
            print(plot_no)
    
            plot_no += 1
    
        pad = 0.9 + (float(height)/100.)
        fig.tight_layout(rect=[0, 0, 1, pad])
    
        if save_figures == 'yes':
            plt.savefig(working_dir+'figures/'+pref+'_'+sweep+'_mean_solid_zpos-vs-time.png')

    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    11
    12
    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    11
    12
    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    11
    12

![img](./.ob-jupyter/e15389269386bed6f06cbfefc8b5d5969d367f35.png)
![img](./.ob-jupyter/eb6a4c3fb99911c561511edd7613651d7f026865.png)
![img](./.ob-jupyter/2bdc9279dc02c4790c382f537edc1791f8e8748f.png)


<a id="org8c124b5"></a>

## cumulative histogram

plot an example internalization and cumulative histogram

    internalization = solid_allparams.loc[output_dir].loc[run]['internalization']*1000
    y = internalization
    x = internalization.reset_index()['time']
    plt.plot(x,y)
    plt.xlabel('time (s)')
    plt.ylabel('internalization (nm)')
    
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/'+pref+'_solid_internalization_example.png')

    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexes/base.py:3802, in Index.get_loc(self, key, method, tolerance)
       3801 try:
    -> 3802     return self._engine.get_loc(casted_key)
       3803 except KeyError as err:
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/_libs/index.pyx:138, in pandas._libs.index.IndexEngine.get_loc()
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/_libs/index.pyx:165, in pandas._libs.index.IndexEngine.get_loc()
    
    File pandas/_libs/hashtable_class_helper.pxi:5745, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    File pandas/_libs/hashtable_class_helper.pxi:5753, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    KeyError: '6.11.7_output'
    
    The above exception was the direct cause of the following exception:
    
    KeyError                                  Traceback (most recent call last)
    Cell In[53], line 1
    ----> 1 internalization = solid_allparams.loc[output_dir].loc[run]['internalization']*1000
          2 y = internalization
          3 x = internalization.reset_index()['time']
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexing.py:1073, in _LocationIndexer.__getitem__(self, key)
       1070 axis = self.axis or 0
       1072 maybe_callable = com.apply_if_callable(key, self.obj)
    -> 1073 return self._getitem_axis(maybe_callable, axis=axis)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexing.py:1312, in _LocIndexer._getitem_axis(self, key, axis)
       1310 # fall thru to straight lookup
       1311 self._validate_key(key, axis)
    -> 1312 return self._get_label(key, axis=axis)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexing.py:1260, in _LocIndexer._get_label(self, label, axis)
       1258 def _get_label(self, label, axis: int):
       1259     # GH#5567 this will fail if the label is not present in the axis.
    -> 1260     return self.obj.xs(label, axis=axis)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/generic.py:4049, in NDFrame.xs(self, key, axis, level, drop_level)
       4046 self._consolidate_inplace()
       4048 if isinstance(index, MultiIndex):
    -> 4049     loc, new_index = index._get_loc_level(key, level=0)
       4050     if not drop_level:
       4051         if lib.is_integer(loc):
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexes/multi.py:3160, in MultiIndex._get_loc_level(self, key, level)
       3158         return indexer, maybe_mi_droplevels(indexer, ilevels)
       3159 else:
    -> 3160     indexer = self._get_level_indexer(key, level=level)
       3161     if (
       3162         isinstance(key, str)
       3163         and self.levels[level]._supports_partial_string_indexing
       3164     ):
       3165         # check to see if we did an exact lookup vs sliced
       3166         check = self.levels[level].get_loc(key)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexes/multi.py:3263, in MultiIndex._get_level_indexer(self, key, level, indexer)
       3259         return slice(i, j, step)
       3261 else:
    -> 3263     idx = self._get_loc_single_level_index(level_index, key)
       3265     if level > 0 or self._lexsort_depth == 0:
       3266         # Desired level is not sorted
       3267         if isinstance(idx, slice):
       3268             # test_get_loc_partial_timestamp_multiindex
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexes/multi.py:2849, in MultiIndex._get_loc_single_level_index(self, level_index, key)
       2847     return -1
       2848 else:
    -> 2849     return level_index.get_loc(key)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexes/base.py:3804, in Index.get_loc(self, key, method, tolerance)
       3802     return self._engine.get_loc(casted_key)
       3803 except KeyError as err:
    -> 3804     raise KeyError(key) from err
       3805 except TypeError:
       3806     # If we have a listlike key, _check_indexing_error will raise
       3807     #  InvalidIndexError. Otherwise we fall through and re-raise
       3808     #  the TypeError.
       3809     self._check_indexing_error(key)
    
    KeyError: '6.11.7_output'

    plt.hist(internalization, 50, cumulative=True, density=True, histtype='step')
    percentile = np.percentile(internalization, 95)
    plt.plot([percentile, percentile], [0,1], label='95th percentile')
    plt.ylabel('cumulative density')
    plt.xlabel('internalization (nm)')
    plt.legend()
    
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/'+pref+'_solid_cumhist_percentile_example.png')

    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)
    Cell In[54], line 1
    ----> 1 plt.hist(internalization, 50, cumulative=True, density=True, histtype='step')
          2 percentile = np.percentile(internalization, 95)
          3 plt.plot([percentile, percentile], [0,1], label='95th percentile')
    
    NameError: name 'internalization' is not defined

plot all cumulative histograms with 95 percentile internalization marked

    num_plots = total_runs
    
    width = 6
    height = num_plots//width + 1
    
    fig, ax = plt.subplots(nrows=height, ncols=width, sharex=True, sharey=True, figsize=(4*width,5*height))
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    fig.text(0.5, 0, 'internalization (nm)', ha='center', size=24)
    fig.text(0, 0.5, 'cumulative density', va='center', rotation='vertical', size=24)
    
    plot_no = 0
    
    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        for run in rundirs:
            if run == 'empty':
                continue
            internalization = solid_allparams.loc[output_dir].loc[run]['internalization']*1000
            props = properties_allparams.loc[output_dir].loc[run]
            viscosity = props['internalize.cym_viscosity']
            hip1r_off = props['strongbinder_unbinding'].split(',')[0]
    
            plot_no += 1
    
            plt.subplot(height,width,plot_no) #height, width
            plt.hist(internalization, 50, cumulative=True, density=True, histtype='step')
            percentile = np.percentile(internalization, 95)
            plt.plot([percentile, percentile], [0,1])
            plt.xlim(right = 100)
            #plt.ylim(top = 100)
    
            title = output_dir+'\n'+run+'\n'
            for prop in property_groups:
                title += prop + ' = ' + str(props[prop]) + '\n'
    
            plt.title(title)
    
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/'+pref+'_solid_cumhist_percentile_all.png')

    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexes/base.py:3802, in Index.get_loc(self, key, method, tolerance)
       3801 try:
    -> 3802     return self._engine.get_loc(casted_key)
       3803 except KeyError as err:
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/_libs/index.pyx:138, in pandas._libs.index.IndexEngine.get_loc()
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/_libs/index.pyx:165, in pandas._libs.index.IndexEngine.get_loc()
    
    File pandas/_libs/hashtable_class_helper.pxi:5745, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    File pandas/_libs/hashtable_class_helper.pxi:5753, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    KeyError: '6.11.7_output'
    
    The above exception was the direct cause of the following exception:
    
    KeyError                                  Traceback (most recent call last)
    Cell In[55], line 16
         13 plot_no = 0
         15 for output_dir in output_dirs:
    ---> 16     rundirs = rundirs_allparams_df.loc[output_dir]
         17     for run in rundirs:
         18         if run == 'empty':
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexing.py:1073, in _LocationIndexer.__getitem__(self, key)
       1070 axis = self.axis or 0
       1072 maybe_callable = com.apply_if_callable(key, self.obj)
    -> 1073 return self._getitem_axis(maybe_callable, axis=axis)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexing.py:1312, in _LocIndexer._getitem_axis(self, key, axis)
       1310 # fall thru to straight lookup
       1311 self._validate_key(key, axis)
    -> 1312 return self._get_label(key, axis=axis)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexing.py:1260, in _LocIndexer._get_label(self, label, axis)
       1258 def _get_label(self, label, axis: int):
       1259     # GH#5567 this will fail if the label is not present in the axis.
    -> 1260     return self.obj.xs(label, axis=axis)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/generic.py:4056, in NDFrame.xs(self, key, axis, level, drop_level)
       4054             new_index = index[loc]
       4055 else:
    -> 4056     loc = index.get_loc(key)
       4058     if isinstance(loc, np.ndarray):
       4059         if loc.dtype == np.bool_:
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/indexes/base.py:3804, in Index.get_loc(self, key, method, tolerance)
       3802     return self._engine.get_loc(casted_key)
       3803 except KeyError as err:
    -> 3804     raise KeyError(key) from err
       3805 except TypeError:
       3806     # If we have a listlike key, _check_indexing_error will raise
       3807     #  InvalidIndexError. Otherwise we fall through and re-raise
       3808     #  the TypeError.
       3809     self._check_indexing_error(key)
    
    KeyError: '6.11.7_output'

![img](./.ob-jupyter/80ed16babf458a5c0dc02057cdd39a014aabd142.png)


<a id="orgc07c166"></a>

## plot 95th percentile internalization vs. parameter sweeps

    percentiles_config = pd.concat([config_unique, percentiles],axis=1)
    percentiles_config.head()

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
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-right">myosin<sub>binding</sub><sub>rate</sub></th>
<th scope="col" class="org-right">myosin<sub>binding</sub><sub>range</sub></th>
<th scope="col" class="org-right">myosin<sub>unbinding</sub><sub>force</sub></th>
<th scope="col" class="org-right">myosin<sub>stall</sub><sub>force</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>stiffness</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>zoffset</sub></th>
<th scope="col" class="org-right">95<sub>percentile</sub><sub>internalization</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">-3.67</td>
<td class="org-right">100</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
<td class="org-right">63.3802</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0004<sub>0002</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">-3.67</td>
<td class="org-right">10000</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
<td class="org-right">70.4585</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0007<sub>0003</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">0</td>
<td class="org-right">10</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
<td class="org-right">78.1793</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0003</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
<td class="org-right">56.3346</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0002</sub>&rsquo;)</td>
<td class="org-right">3</td>
<td class="org-right">0.004</td>
<td class="org-right">0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
<td class="org-right">0.008</td>
<td class="org-right">47.9612</td>
</tr>
</tbody>
</table>

    percentiles_props = pd.concat([properties_unique, percentiles],axis=1)
    percentiles_props.head()

<table>


<colgroup>
<col  class="org-left">

<col  class="org-left">

<col  class="org-left">

<col  class="org-right">

<col  class="org-right">

<col  class="org-right">
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">&#xa0;</th>
<th scope="col" class="org-left">myosin<sub>binding</sub></th>
<th scope="col" class="org-left">myosin<sub>unbinding</sub></th>
<th scope="col" class="org-right">myosin<sub>stall</sub><sub>force</sub></th>
<th scope="col" class="org-right">membrane<sub>myosin</sub><sub>stiffness</sub></th>
<th scope="col" class="org-right">95<sub>percentile</sub><sub>internalization</sub></th>
</tr>
</thead>
<tbody>
<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0002<sub>0003</sub> (1)&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, -3.67</td>
<td class="org-right">100</td>
<td class="org-right">100</td>
<td class="org-right">63.3802</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0004<sub>0002</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, -3.67</td>
<td class="org-right">10000</td>
<td class="org-right">100</td>
<td class="org-right">70.4585</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0007<sub>0003</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, 0</td>
<td class="org-right">10</td>
<td class="org-right">100</td>
<td class="org-right">78.1793</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0003</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, 0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
<td class="org-right">56.3346</td>
</tr>

<tr>
<td class="org-left">(&rsquo;6.11.9<sub>output</sub>&rsquo;, &rsquo;run0011<sub>0002</sub>&rsquo;)</td>
<td class="org-left">3, 0.004</td>
<td class="org-left">67.6, 0</td>
<td class="org-right">1e+06</td>
<td class="org-right">100</td>
<td class="org-right">47.9612</td>
</tr>
</tbody>
</table>

    plt.scatter(percentiles_props['bud_confine'], percentiles_props['95_percentile_internalization'])

    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    File ~/miniconda3/lib/python3.10/site-packages/pandas/core/indexes/base.py:3805, in Index.get_loc(self, key)
       3804 try:
    -> 3805     return self._engine.get_loc(casted_key)
       3806 except KeyError as err:
    
    File index.pyx:167, in pandas._libs.index.IndexEngine.get_loc()
    
    File index.pyx:196, in pandas._libs.index.IndexEngine.get_loc()
    
    File pandas/_libs/hashtable_class_helper.pxi:7081, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    File pandas/_libs/hashtable_class_helper.pxi:7089, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    KeyError: 'bud_confine'
    
    The above exception was the direct cause of the following exception:
    
    KeyError                                  Traceback (most recent call last)
    Cell In[51], line 1
    ----> 1 plt.scatter(percentiles_props['bud_confine'], percentiles_props['95_percentile_internalization'])
    
    File ~/miniconda3/lib/python3.10/site-packages/pandas/core/frame.py:4102, in DataFrame.__getitem__(self, key)
       4100 if self.columns.nlevels > 1:
       4101     return self._getitem_multilevel(key)
    -> 4102 indexer = self.columns.get_loc(key)
       4103 if is_integer(indexer):
       4104     indexer = [indexer]
    
    File ~/miniconda3/lib/python3.10/site-packages/pandas/core/indexes/base.py:3812, in Index.get_loc(self, key)
       3807     if isinstance(casted_key, slice) or (
       3808         isinstance(casted_key, abc.Iterable)
       3809         and any(isinstance(x, slice) for x in casted_key)
       3810     ):
       3811         raise InvalidIndexError(key)
    -> 3812     raise KeyError(key) from err
       3813 except TypeError:
       3814     # If we have a listlike key, _check_indexing_error will raise
       3815     #  InvalidIndexError. Otherwise we fall through and re-raise
       3816     #  the TypeError.
       3817     self._check_indexing_error(key)
    
    KeyError: 'bud_confine'

    <matplotlib.collections.PathCollection at 0x1377867d0>

    percentiles_props.loc[percentiles_props['membrane_myosin_number']==0].mean()

    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    File ~/miniconda3/lib/python3.10/site-packages/pandas/core/indexes/base.py:3805, in Index.get_loc(self, key)
       3804 try:
    -> 3805     return self._engine.get_loc(casted_key)
       3806 except KeyError as err:
    
    File index.pyx:167, in pandas._libs.index.IndexEngine.get_loc()
    
    File index.pyx:196, in pandas._libs.index.IndexEngine.get_loc()
    
    File pandas/_libs/hashtable_class_helper.pxi:7081, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    File pandas/_libs/hashtable_class_helper.pxi:7089, in pandas._libs.hashtable.PyObjectHashTable.get_item()
    
    KeyError: 'membrane_myosin_number'
    
    The above exception was the direct cause of the following exception:
    
    KeyError                                  Traceback (most recent call last)
    Cell In[52], line 1
    ----> 1 percentiles_props.loc[percentiles_props['membrane_myosin_number']==0].mean()
    
    File ~/miniconda3/lib/python3.10/site-packages/pandas/core/frame.py:4102, in DataFrame.__getitem__(self, key)
       4100 if self.columns.nlevels > 1:
       4101     return self._getitem_multilevel(key)
    -> 4102 indexer = self.columns.get_loc(key)
       4103 if is_integer(indexer):
       4104     indexer = [indexer]
    
    File ~/miniconda3/lib/python3.10/site-packages/pandas/core/indexes/base.py:3812, in Index.get_loc(self, key)
       3807     if isinstance(casted_key, slice) or (
       3808         isinstance(casted_key, abc.Iterable)
       3809         and any(isinstance(x, slice) for x in casted_key)
       3810     ):
       3811         raise InvalidIndexError(key)
    -> 3812     raise KeyError(key) from err
       3813 except TypeError:
       3814     # If we have a listlike key, _check_indexing_error will raise
       3815     #  InvalidIndexError. Otherwise we fall through and re-raise
       3816     #  the TypeError.
       3817     self._check_indexing_error(key)
    
    KeyError: 'membrane_myosin_number'


<a id="orgf037339"></a>

### scatterplot overlaid points

    percentiles_props['myosin_unbinding'].fillna(value='empty', inplace=True)
    x = []
    y = []
    z = []
    for output_dir in output_dirs:
        rundirs = rundirs_allparams_df.loc[output_dir]
        for run in rundirs:
            if run == 'empty':
                continue
            myosin_unbinding = percentiles_props.loc[output_dir].loc[run]['myosin_unbinding']
            if myosin_unbinding == 'empty':
                continue
            myosin_off = float(myosin_unbinding.split(',')[0])
            myosin_catch = float(myosin_unbinding.split(',')[1])
            percentile = percentiles_props.loc[output_dir].loc[run]['95_percentile_internalization']
            x.append(myosin_off)
            y.append(myosin_catch)
            z.append(percentile)
            
    plt.scatter(x,y,c=z,alpha=0.5,linewidths=10)
    plt.xscale('symlog')
    plt.yscale('symlog')
    plt.xlabel('off-rate')
    plt.ylabel('catch bond')
    plt.gray()
    plt.colorbar()
    plt.tight_layout()
    
    if save_figures == 'yes':
      plt.savefig(working_dir+'figures/'+pref+'_95per_sweep_overlay.png')

![img](./.ob-jupyter/7ccff35d5176910ba2dacadbb8b8a2360e6e65b3.png)


<a id="orgcfa367f"></a>

### average scatterplot

    # unbinding_groups = percentiles_props.groupby(['myosin_unbinding'])
    unbinding_groups = percentiles_props.groupby(['myosin_unbinding','bud_confine'])
    summary_percentiles = pd.concat([unbinding_groups['95_percentile_internalization'].mean(),
                                     unbinding_groups['95_percentile_internalization'].std()],
                                    axis=1, keys = ['mean', 'std']).reset_index()
    summary_percentiles = pd.concat([summary_percentiles['myosin_unbinding'].str.split(', ', expand = True),
                                     summary_percentiles], axis = 1)
    summary_percentiles.columns = ['myo_off', 'myo_catch', 'myosin_unbinding', 'bud_confine',
                                   'mean_95_percentile_internalization', 'std_95_percentile_internalization']
    summary_percentiles = summary_percentiles[~summary_percentiles['myosin_unbinding'].str.contains('empty')]

    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    Cell In[103], line 2
          1 # unbinding_groups = percentiles_props.groupby(['myosin_unbinding'])
    ----> 2 unbinding_groups = percentiles_props.groupby(['myosin_unbinding','bud_confine'])
          3 summary_percentiles = pd.concat([unbinding_groups['95_percentile_internalization'].mean(),
          4                                  unbinding_groups['95_percentile_internalization'].std()],
          5                                 axis=1, keys = ['mean', 'std']).reset_index()
          6 summary_percentiles = pd.concat([summary_percentiles['myosin_unbinding'].str.split(', ', expand = True),
          7                                  summary_percentiles], axis = 1)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/frame.py:8402, in DataFrame.groupby(self, by, axis, level, as_index, sort, group_keys, squeeze, observed, dropna)
       8399     raise TypeError("You have to supply one of 'by' and 'level'")
       8400 axis = self._get_axis_number(axis)
    -> 8402 return DataFrameGroupBy(
       8403     obj=self,
       8404     keys=by,
       8405     axis=axis,
       8406     level=level,
       8407     as_index=as_index,
       8408     sort=sort,
       8409     group_keys=group_keys,
       8410     squeeze=squeeze,
       8411     observed=observed,
       8412     dropna=dropna,
       8413 )
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/groupby/groupby.py:965, in GroupBy.__init__(self, obj, keys, axis, level, grouper, exclusions, selection, as_index, sort, group_keys, squeeze, observed, mutated, dropna)
        962 if grouper is None:
        963     from pandas.core.groupby.grouper import get_grouper
    --> 965     grouper, exclusions, obj = get_grouper(
        966         obj,
        967         keys,
        968         axis=axis,
        969         level=level,
        970         sort=sort,
        971         observed=observed,
        972         mutated=self.mutated,
        973         dropna=self.dropna,
        974     )
        976 self.obj = obj
        977 self.axis = obj._get_axis_number(axis)
    
    File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/groupby/grouper.py:888, in get_grouper(obj, key, axis, level, sort, observed, mutated, validate, dropna)
        886         in_axis, level, gpr = False, gpr, None
        887     else:
    --> 888         raise KeyError(gpr)
        889 elif isinstance(gpr, Grouper) and gpr.key is not None:
        890     # Add key to exclusions
        891     exclusions.add(gpr.key)
    
    KeyError: 'bud_confine'

1.  all

        x = pd.to_numeric(summary_percentiles['myo_off'])
        y = 1/pd.to_numeric(summary_percentiles['myo_catch'])
        y.replace([np.inf, -np.inf], 0, inplace=True)
        z = pd.to_numeric(summary_percentiles['mean_95_percentile_internalization'])
        
        plt.scatter(x,y,c=z,alpha=1,linewidths=10)
        plt.xscale('symlog', linthresh=0.1)
        plt.yscale('symlog', linthresh=0.001)
        plt.xlabel('myosin unbinding rate ($s^{-1}$)')
        plt.ylabel('inverse myosin unbinding force ($pN^{-1}$)')
        plt.plasma()
        plt.colorbar(label='mean 95 percentile internalization')
        plt.tight_layout()
        
        if save_figures == 'yes':
          plt.savefig(working_dir+'figures/'+pref+'_95per_sweep_means_scatter_inverse.png')
    
        ---------------------------------------------------------------------------
        NameError                                 Traceback (most recent call last)
        Cell In[104], line 1
        ----> 1 x = pd.to_numeric(summary_percentiles['myo_off'])
              2 y = 1/pd.to_numeric(summary_percentiles['myo_catch'])
              3 y.replace([np.inf, -np.inf], 0, inplace=True)
        
        NameError: name 'summary_percentiles' is not defined

2.  split by resistance

        for bud_confine in properties_unique.bud_confine.unique():
          subset_percentiles = summary_percentiles[summary_percentiles['bud_confine']==bud_confine]
          x = pd.to_numeric(subset_percentiles['myo_off'])
          y = 1/pd.to_numeric(subset_percentiles['myo_catch'])
          y.replace([np.inf, -np.inf], 0, inplace=True)
          z = pd.to_numeric(subset_percentiles['mean_95_percentile_internalization'])
        
          plt.figure()
          plt.scatter(x,y,c=z,alpha=1,linewidths=10)
          plt.xscale('symlog', linthresh=0.1)
          plt.yscale('symlog', linthresh=0.001)
          plt.xlabel('myosin unbinding rate ($s^{-1}$)')
          plt.ylabel('inverse myosin unbinding force ($pN^{-1}$)')
          plt.plasma()
          plt.colorbar(label='mean 95 percentile internalization')
          plt.title('resistance = '+str(bud_confine))
          plt.tight_layout()
        
          if save_figures == 'yes':
            plt.savefig(working_dir+'figures/'+pref+'_95per_sweep_means_scatter_inverse_'+str(bud_confine)+'.png')
    
        ---------------------------------------------------------------------------
        AttributeError                            Traceback (most recent call last)
        Cell In[105], line 1
        ----> 1 for bud_confine in properties_unique.bud_confine.unique():
              2   subset_percentiles = summary_percentiles[summary_percentiles['bud_confine']==bud_confine]
              3   x = pd.to_numeric(subset_percentiles['myo_off'])
        
        File ~/anaconda3/envs/max_cytosim_analysis/lib/python3.11/site-packages/pandas/core/generic.py:5902, in NDFrame.__getattr__(self, name)
           5895 if (
           5896     name not in self._internal_names_set
           5897     and name not in self._metadata
           5898     and name not in self._accessors
           5899     and self._info_axis._can_hold_identifiers_and_holds_name(name)
           5900 ):
           5901     return self[name]
        -> 5902 return object.__getattribute__(self, name)
        
        AttributeError: 'DataFrame' object has no attribute 'bud_confine'


<a id="org795746d"></a>

### line plots

    xlabels = {
        'myosin_stall_force':'Myosin stall force ($pN$)',
        'membrane_myosin_zoffset':'Myosin z-offset\nfrom membrane ($\\mu m$)',
        'membrane_myosin_stiffness':'Myosin bond stiffness ($\\frac{pN}{\\mu m}$)',
        'myosin_binding_range':'Myosin binding range ($\mu m$)'
    }
    
    to_plot = [
     '6.11.9_output',
     '6.11.8_output',
     '6.11.4_output',
     '6.11.7_output'
     ]
    
    for sweep in to_plot:
        percentiles_config_sweep = percentiles_config.loc[sweep]
        sweep_config_nunique = percentiles_config_sweep.apply(pd.Series.nunique)
        cols_to_drop = sweep_config_nunique[sweep_config_nunique == 1].index
        percentiles_sweep_unique = percentiles_config_sweep.drop(cols_to_drop, axis=1)
    
        sweep_config = config_unique.loc[sweep]
        sweep_config_nunique = sweep_config.apply(pd.Series.nunique)
        cols_to_drop = sweep_config_nunique[sweep_config_nunique == 1].index
        sweep_config_unique = sweep_config.drop(cols_to_drop, axis=1)
    
        percentiles_sweep_groups = percentiles_sweep_unique.groupby(list(sweep_config_unique.columns))
        summary_percentiles_sweep = pd.concat([percentiles_sweep_groups['95_percentile_internalization'].mean(),
                                               percentiles_sweep_groups['95_percentile_internalization'].std()],
                                              axis=1, keys=['mean', 'std']).reset_index()
    
        neutral_bond = summary_percentiles_sweep.loc[summary_percentiles_sweep['myosin_unbinding_force'] == 0]
        slip_bond = summary_percentiles_sweep.loc[summary_percentiles_sweep['myosin_unbinding_force'] == 1000]
        catch_bond = summary_percentiles_sweep.loc[summary_percentiles_sweep['myosin_unbinding_force'] == -3.67]
        xcol = summary_percentiles_sweep.drop(['myosin_unbinding_force', 'mean', 'std'], axis=1).columns[0]
    
        fig, ax = plt.subplots(figsize=[7, 6])
    
        if neutral_bond.shape[0] > 0:
            ax.plot(neutral_bond[xcol], neutral_bond['mean'], label='Force-insensitive', color='tab:blue')
            ax.fill_between(neutral_bond[xcol], neutral_bond['mean'] - neutral_bond['std'], neutral_bond['mean'] + neutral_bond['std'],
                        color='tab:blue', alpha=0.3)
    
        if slip_bond.shape[0] > 0:
            ax.plot(slip_bond[xcol], slip_bond['mean'], label='Force-insensitive', color='tab:blue')
            ax.fill_between(slip_bond[xcol], slip_bond['mean'] - slip_bond['std'], slip_bond['mean'] + slip_bond['std'],
                            color='tab:blue', alpha=0.3)
    
        if catch_bond.shape[0] > 0:
            ax.plot(catch_bond[xcol], catch_bond['mean'], label='Myo5 force sensitivity', color='tab:orange')
            ax.fill_between(catch_bond[xcol], catch_bond['mean'] - catch_bond['std'], catch_bond['mean'] + catch_bond['std'],
                            color='tab:orange', alpha=0.3)
    
        ax.set_xscale('log', base=10)
        ax.set_xlabel(xlabels[xcol])
        ax.set_ylabel('Mean 95 percentile\ninternalization ($nm$)')
        ax.legend()
        plt.tight_layout()
    
        if save_figures == 'yes':
            plt.savefig(working_dir + 'figures/publish/' + sweep + '_95per_means_std_lines.svg')

![img](./.ob-jupyter/71a4a65791a9d1aae46fe59fec001f73a95084e5.png)
![img](./.ob-jupyter/32a45b1abb23468d01dbfd134d25bc67c5d29945.png)
![img](./.ob-jupyter/5f6c925ff57a545dd23e34a46990b030e705df52.png)
![img](./.ob-jupyter/1b0c9da62d1f507dd281d79e4a5f7c18d71ecb8e.png)

