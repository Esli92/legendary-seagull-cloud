#!/bin/bash

STATION_FILES=../dataFiles/processed_redmet
obj_dir_to=../dataFiles/processed_redmet_mensual



for STATION in `ls $STATION_FILES`
do

estacion=$STATION


obj_dir=../dataFiles/processed_redmet/${estacion}/2015
cat ${obj_dir_to}/[0-9][0-9]_${estacion}_WS.* > ${obj_dir}/WS/${estacion}_WS.txt
cat ${obj_dir_to}/[0-9][0-9]_${estacion}_WS.* > ${obj_dir}/WD/${estacion}_WD.txt
cat ${obj_dir_to}/[0-9][0-9]_${estacion}_PA.* > ${obj_dir}/PA/${estacion}_PA.txt
cat ${obj_dir_to}/[0-9][0-9]_${estacion}_TM.* > ${obj_dir}/TM/${estacion}_TM.txt

done
