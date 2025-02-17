INPUT=$1

while [ ${#INPUT} -lt 4 ]; do
  INPUT="0$INPUT"
done
echo $INPUT
