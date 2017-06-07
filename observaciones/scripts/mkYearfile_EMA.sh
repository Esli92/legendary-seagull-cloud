#!/bin/bash

STATION_FILES=../dataFiles/processed_ema_year


for STATION in `ls $STATION_FILES`
do

estacion=$STATION

obj_dir=../dataFiles/processed_ema_year/${estacion}/2015

cat ${obj_dir}/[0-9][0-9]_${estacion}_???_15_windSpd.* > ${obj_dir}/WS/${estacion}_WS.txt
cat ${obj_dir}/[0-9][0-9]_${estacion}_???_15_windDir.* > ${obj_dir}/WD/${estacion}_WD.txt
cat ${obj_dir}/[0-9][0-9]_${estacion}_???_15_pressure.* > ${obj_dir}/PA/${estacion}_PA.txt
cat ${obj_dir}/[0-9][0-9]_${estacion}_???_15_rain.* > ${obj_dir}/RN/${estacion}_RN.txt
cat ${obj_dir}/[0-9][0-9]_${estacion}_???_15_temp.* > ${obj_dir}/TM/${estacion}_TM.txt
cat ${obj_dir}/[0-9][0-9]_${estacion}_???_15_radiation.* > ${obj_dir}/${estacion}_RD.txt

done
