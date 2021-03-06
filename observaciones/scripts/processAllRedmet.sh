#!/bin/bash


rm -rf ../dataFiles/processed_redmet_mensual
mkdir ../dataFiles/processed_redmet_mensual

cd ../15REDMET

find . -name '*.xls' -exec python ../scripts/leerRedmet.py {} \;


cd ../dataFiles/processed_redmet_mensual


#Perl rename
#rename -f 's:(?<!\d)\d_:0$&:g' *.txt
#rename -f 's:_5R:_RH:g' *.txt
#rename -f 's:_5P:_PA:g' *.txt

#Linux rename

ls ?_* | sed -e 'p;s:[0-9]_:0&:' | xargs -n2 mv
rename _5R _RH *.txt
rename _5P _PA *.txt
