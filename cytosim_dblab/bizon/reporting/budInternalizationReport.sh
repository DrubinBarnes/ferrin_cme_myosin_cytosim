#!/bin/bash
# this script runs two python scripts given a particular name of the folder to report. Reports simulation outputs.

# give it an argument of the folder your analysis is in.

# cd ..

# pwd
# PATH=$PATH:.
# echo $1

echo "running simulation reporting"

python /Users/mathewakamatsu/Documents/Drubin\ Lab/Modeling/cytosim_current/cytosim/reporting/reportMultiple3D_current.py "$1"

echo "reporting bud internalization over time"

python /Users/mathewakamatsu/Documents/Drubin\ Lab/Modeling/cytosim_current/cytosim/reporting/convertReportToTrajectoriesSolid.py "$1"

echo "done!"

