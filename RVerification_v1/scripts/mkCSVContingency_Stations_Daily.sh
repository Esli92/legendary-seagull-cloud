#!/bin/bash

#mkVerifStatFiles_stations.sh
#Program that takes output of R scripts for verification, and creates files with station name, location and statistic values (like PC, POD, FAR). 
#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 25-Feb-2017

#------------------Requisites------------------------------------------------------------
#Results from contingency table tests


#-----------------Version---------------------------------------------------------------
#v1.0 25/Feb/17 Program is created


#----------------Known issues-----------------------------------------------------------

#-----------------Local directories----------------------------------------------------- 

DIRECTORIO_SCRIPTS=`pwd`
DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/gruposEstaciones/EMA
DIRECTORIO_SEASONS=./seasons
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables
DIRECTORIO_GRUPOS=../../observaciones/dataFiles/gruposEstaciones
INTERVALO=l24
DIRECTORIO_RESULTADOS=contingencyTables/${INTERVALO}/out/RN

#-----------------BEGIN PROGRAM--------------------------------------------------------


#Order of programs will be VAR>SEASON>STATION
VARIABLE=RN
#for VARIABLE in `ls $DIRECTORIO_VARIABLES`
#do
SEASON=HUM
	#for SEASON in `ls $DIRECTORIO_SEASONS`
	#do
		rm PC_*
		rm BIAS_*
		rm FAR_*
		rm TS_*
		for ESTACION in `ls $DIRECTORIO_ESTACIONES`
		do
			source $DIRECTORIO_ESTACIONES/$ESTACION
			TARGET=${DIRECTORIO_RESULTADOS}/contingencytable_v${VARIABLE}_s${SEASON}_g${ESTACION}.Rout
			grep -F "PC   =" $TARGET > PC.out
			head -1 PC.out > PC_15.out
			tail -1 PC.out > PC_25.out
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' PC_15.out >> PC_15.csv
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' PC_25.out >> PC_25.csv

			grep -F "BIAS =" $TARGET > BIAS.out
			head -1 BIAS.out > BIAS_15.out
			tail -1 BIAS.out > BIAS_25.out
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' BIAS_15.out >> BIAS_15.csv
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' BIAS_25.out >> BIAS_25.csv

			grep -F "FAR  =" $TARGET > FAR.out
			head -1 FAR.out > FAR_15.out
			tail -1 FAR.out > FAR_25.out
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' FAR_15.out >> FAR_15.csv
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' FAR_25.out >> FAR_25.csv

			grep -F "TS   =" $TARGET > TS.out
			head -1 TS.out > TS_15.out
			tail -1 TS.out > TS_25.out
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' TS_15.out >> TS_15.csv
			awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$ESTACION" '{print LAT, LON, $3, STAT}' TS_25.out >> TS_25.csv
		done
	#done
#done

mkdir csv/RN/${INTERVALO}
rm csv/RN/${INTERVALO}/*
mv PC_??.csv BIAS_??.csv FAR_??.csv TS_??.csv csv/RN/${INTERVALO}

