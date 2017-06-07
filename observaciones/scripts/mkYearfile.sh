#!/bin/bash

cd ../dataFiles/processed

obj_dir=../year_files
mkdir ${obj_dir}

estacion=ecogu
cat [0-9][0-9]_${estacion}_???_15_windSpd.* > ${obj_dir}/${estacion}_windSpd.txt
cat [0-9][0-9]_${estacion}_???_15_windDir.* > ${obj_dir}/${estacion}_windDir.txt
cat [0-9][0-9]_${estacion}_???_15_pressure.* > ${obj_dir}/${estacion}_pressure.txt
cat [0-9][0-9]_${estacion}_???_15_rain.* > ${obj_dir}/${estacion}_rain.txt
cat [0-9][0-9]_${estacion}_???_15_temp.* > ${obj_dir}/${estacion}_temp.txt
cat [0-9][0-9]_${estacion}_???_15_radiation.* > ${obj_dir}/${estacion}_radiation.txt
