#!/bin/bash

DIRECTORIO_ESTACIONES=/run/media/esli/El_Jurado/WRF_stuff/observaciones/dataFiles/processed_redmet

echo 'BULK PAIRS V1.0 -----> Indica los siguientes datos'
read -p 'Indica la resolucion (5 o 25): ' RESOLUTION
read -p 'Indica el mes de simulacion (mm): ' MES
read -p 'Indica el anio (yy): ' ANIO_SHORT

cd ../../post/timeSeries/${MES}_0p${RESOLUTION}

for STATION in `ls $DIRECTORIO_ESTACIONES`
do

ln -s ${DIRECTORIO_ESTACIONES}/${STATION} .

find . -name '*.txt' -exec python ../../../observaciones/scripts/mkObsFrcstPairs.py ${STATION} {} \;



done

