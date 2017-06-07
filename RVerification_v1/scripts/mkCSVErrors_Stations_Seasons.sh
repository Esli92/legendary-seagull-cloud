#!/bin/bash

#mkVerifStatFiles_contData.sh
#Program that takes output of R scripts for verification, and creates files with station name, location and statistic values (like MAE,ME,MSE). 
#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 25-Feb-2017

#------------------Requisites------------------------------------------------------------
#Results from verification tests with continuous data
#verify directory

#-----------------Version---------------------------------------------------------------
#v1.0 25/Feb/17 Program is created


#----------------Known issues-----------------------------------------------------------

#-----------------Local directories----------------------------------------------------- 

DIRECTORIO_SCRIPTS=`pwd`
DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/estaciones
DIRECTORIO_SEASONS=./seasons
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables
DIRECTORIO_GRUPOS=../../observaciones/dataFiles/gruposEstaciones


#-----------------BEGIN PROGRAM--------------------------------------------------------

#Example of result directory
#verify/out/${RESOLUTION}/${VARIABLE}/${SEASON}

rm *.csv

for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
do
	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			head -1 csv_header.txt > MAE_${RESOLUTION}_${SEASON}_${VARIABLE}.csv
			head -1 csv_header.txt > ME_${RESOLUTION}_${SEASON}_${VARIABLE}.csv
			head -1 csv_header.txt > MSE_${RESOLUTION}_${SEASON}_${VARIABLE}.csv
			for STATION in `ls $DIRECTORIO_ESTACIONES`
			do
				source $DIRECTORIO_ESTACIONES/$STATION
				TARGET=verify/out/${RESOLUTION}/${VARIABLE}/${SEASON}/R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${SEASON}_${STATION}.Rout
				grep -F "MAE               =" $TARGET > MAE_${RESOLUTION}_${SEASON}_${VARIABLE}.out
				awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$STATION" '{print LAT, LON, $3, STAT}' MAE_${RESOLUTION}_${SEASON}_${VARIABLE}.out >> MAE_${RESOLUTION}_${SEASON}_${VARIABLE}.csv

				source $DIRECTORIO_ESTACIONES/$STATION
				TARGET=verify/out/${RESOLUTION}/${VARIABLE}/${SEASON}/R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${SEASON}_${STATION}.Rout
				grep -F "ME                =" $TARGET > ME_${RESOLUTION}_${SEASON}_${VARIABLE}.out
				awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$STATION" '{print LAT, LON, $3, STAT}' ME_${RESOLUTION}_${SEASON}_${VARIABLE}.out >> ME_${RESOLUTION}_${SEASON}_${VARIABLE}.csv

				source $DIRECTORIO_ESTACIONES/$STATION
				TARGET=verify/out/${RESOLUTION}/${VARIABLE}/${SEASON}/R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${SEASON}_${STATION}.Rout
				grep -F "MSE               =" $TARGET > MSE_${RESOLUTION}_${SEASON}_${VARIABLE}.out
				awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$STATION" '{print LAT, LON, $3, STAT}' MSE_${RESOLUTION}_${SEASON}_${VARIABLE}.out >> MSE_${RESOLUTION}_${SEASON}_${VARIABLE}.csv
			done
		done
	
		if [ ! -d "csv/${VARIABLE}/seasonal" ]
		then
			mkdir csv/${VARIABLE}/seasonal
		else
			rm csv/${VARIABLE}/seasonal/*
		fi

		if [ ! -d "csv/${VARIABLE}/seasonal/${RESOLUTION}" ]
		then
			mkdir csv/${VARIABLE}/seasonal/${RESOLUTION}
			mv *_TM.csv csv/${VARIABLE}/seasonal/${RESOLUTION}
		else
			rm csv/${VARIABLE}/seasonal/${RESOLUTION}/*
			mv *_${VARIABLE}.csv csv/${VARIABLE}/seasonal/${RESOLUTION}
		fi
	done
done

rm *.out



