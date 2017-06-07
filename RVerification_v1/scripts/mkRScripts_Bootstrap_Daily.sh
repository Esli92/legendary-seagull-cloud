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


#########-----------------------------Generating R scripts-----------------------------------------
#Target Dir example: "./csv/VARIABLE/daily/ESTADISTICO_diff_SEASON_VARIABLE_STATION.csv"

if [ ! -d "bootstrap/" ]
then
	mkdir bootstrap
fi

rm -rf bootstrap/*
for STATION in `ls $DIRECTORIO_ESTACIONES`
do
	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		if [ ! -d "bootstrap/${VARIABLE}" ]
		then
			mkdir bootstrap/${VARIABLE}
		fi

		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			for ESTADISTICO in `ls $DIRECTORIO_STATS`
			do
				TARGET=bootstrap/${VARIABLE}/R_bootstrap_${ESTADISTICO}_${SEASON}_${VARIABLE}_${STATION}.r
				sed 's/'VARIABLE'/'${VARIABLE}'/g' Rbootstrap.r.template > boot.pre1
				sed 's/'SEASON'/'${SEASON}'/g' boot.pre1 > boot.pre2
				sed 's/'ESTADISTICO'/'${ESTADISTICO}'/g' boot.pre2 > boot.pre1
				sed 's/'STATION'/'${STATION}'/g' boot.pre1 > $TARGET
			done
		done
	done
done





