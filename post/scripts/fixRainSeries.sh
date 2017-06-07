#!/bin/bash

#This program takes the raw time series for precipitacion (which has accumulated rain) and fixes it to get accumulated rain each hour. 

#for the header 

DIRECTORIO_ESTACIONES=../timeSeries/stationFiles
DIRECTORIO_MESES=../../observaciones/scripts/meses
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones

for RESOLUCION in `ls $DIRECTORIO_RESOLUCIONES`
do
for MES in `ls $DIRECTORIO_MESES`
do
	DIRECTORIO_FECHAS=fechas/fechas${MES}
	for FECHA in `ls $DIRECTORIO_FECHAS`
	do
		source $DIRECTORIO_FECHAS/$FECHA
		DIA=${DI}
		for ESTACION in `ls $DIRECTORIO_ESTACIONES`
		do

			head -1 header.txt > ../timeSeries/${MES}_0p${RESOLUCION}/${ESTACION}/2015/${ESTACION}_${DIA}_${MES}_15_RA.txt
			awk '
				NR==1{old = $4; next}
				{print $1, $2, $3, $4 - old; old = $4} 
			' ../timeSeries/${MES}_0p${RESOLUCION}/${ESTACION}/2015/${ESTACION}_${DIA}_${MES}_15_RN.txt >> ../timeSeries/${MES}_0p${RESOLUCION}/${ESTACION}/2015/${ESTACION}_${DIA}_${MES}_15_RA.txt
		done
	done
done
done
