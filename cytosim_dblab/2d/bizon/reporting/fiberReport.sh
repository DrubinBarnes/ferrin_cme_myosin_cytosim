#!/bin/bash
# this script runs two python scripts given a particular name of the folder to report. Reports simulation outputs.

# give it an argument of the folder your analysis is in.

# cd ..

# pwd
# PATH=$PATH:.
# echo $1

echo "running simulation fiber reporting"

python /Users/mathewakamatsu/Documents/Drubin\ Lab/Modeling/cytosim_current/cytosim/reporting/reportFiberProperties.py "$1"

echo "reporting bud internalization over time"

python /Users/mathewakamatsu/Documents/Drubin Lab/Modeling/cytosim_current/cytosim/reporting/convertReportToTrajectories3D_attached.py "$1"

echo "done!"

