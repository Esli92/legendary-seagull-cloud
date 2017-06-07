#!/bin/bash

#mkVerifStatFiles_contData.sh
#Program that takes output of R scripts for verification, and creates a file for each station with its statistic values for each MES (like MAE,ME,MSE). 
#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 25-Feb-2017

#------------------Requisites------------------------------------------------------------
#Results from verification tests with continuous data
#verify_daily directory

#-----------------Version---------------------------------------------------------------
#v1.0 25/Feb/17 Program is created


#----------------Known issues-----------------------------------------------------------

#-----------------Local directories----------------------------------------------------- 

DIRECTORIO_SCRIPTS=`pwd`
DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/estaciones
DIRECTORIO_MESES=../../observaciones/scripts/meses
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables_cont
DIRECTORIO_GRUPOS=../../observaciones/dataFiles/gruposEstaciones
DIRECTORIO_DIAS=../../observaciones/scripts/days
DIRECTORIO_SEASONS=./seasons
DIRECTORIO_STATS=./stats
INTERVALO=l24


#-----------------BEGIN PROGRAM--------------------------------------------------------

#Example of result directory
#bootstrap/out/VAR/SEASON/R_bootstrap_MSE_HUM_WS_VIF.r.Rout

rm *.out 
rm *.out?

if [ ! -d "csv/boot" ]
then
	mkdir csv/boot	
fi

rm -rf csv/boot/*
 
for STAT in `ls $DIRECTORIO_STATS`
do
	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		if [ ! -d "csv/boot/${VARIABLE}" ]
		then
			mkdir csv/boot/${VARIABLE}	
		fi
		RES_DIR=csv/boot/${VARIABLE}
		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			head -1 csv_header.txt > ${RES_DIR}/${STAT}_${SEASON}_${VARIABLE}_sigtest.csv
			head -1 csv_boot_header.txt > ${RES_DIR}/${STAT}_${SEASON}_${VARIABLE}.csv

			for STATION in `ls $DIRECTORIO_ESTACIONES`
			do
			source $DIRECTORIO_ESTACIONES/$STATION

					TARGET=bootstrap/out/${VARIABLE}/${SEASON}/R_bootstrap_${STAT}_${SEASON}_${VARIABLE}_${STATION}.r.Rout
					grep -F "[1,]" $TARGET > ${STAT}_${SEASON}_${VARIABLE}.out
					awk -F' ' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$STATION" '{print LAT, LON, $2, STAT}' ${STAT}_${SEASON}_${VARIABLE}.out >> ${RES_DIR}/${STAT}_${SEASON}_${VARIABLE}_sigtest.csv
					grep -F "[1]" $TARGET | awk '{print $2}' > ${STAT}_${SEASON}_${VARIABLE}.outm
					grep -F "95%" $TARGET | awk -F'(' '{print $2}' | awk '{print $2}' > ${STAT}_${SEASON}_${VARIABLE}.outu
					grep -F "95%" $TARGET | awk -F'(' '{print $2}' | awk -F',' '{print $1}' > ${STAT}_${SEASON}_${VARIABLE}.outl
					paste -d',' ${STAT}_${SEASON}_${VARIABLE}.outm ${STAT}_${SEASON}_${VARIABLE}.outu ${STAT}_${SEASON}_${VARIABLE}.outl > ${STAT}_${SEASON}_${VARIABLE}.out
					awk -F',' -v OFS=',' -v LAT="$LAT" -v LON="$LON" -v STAT="$STATION" '{print LAT, LON, $3, $2, $1, STAT}' ${STAT}_${SEASON}_${VARIABLE}.out >> ${RES_DIR}/${STAT}_${SEASON}_${VARIABLE}.csv
			done
		done
	done
done

rm *.out
rm *.out?
