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

rm *.Rout

if [ ! -d "bootstrap/out" ]
then
	mkdir bootstrap/out
fi

rm -rf bootstrap/out/*

if [ ! -d "bootstrap/figures" ]
then
	mkdir bootstrap/figures
else
	rm bootstrap/figures/*
fi

find ./bootstrap -name "*.r" -exec R CMD BATCH {} \;


for STATION in `ls $DIRECTORIO_ESTACIONES`
do
	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		if [ ! -d "bootstrap/out/${VARIABLE}" ]
		then
			mkdir bootstrap/out/${VARIABLE}
			
		fi

		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			mkdir bootstrap/out/${VARIABLE}/${SEASON}
			for ESTADISTICO in `ls $DIRECTORIO_STATS`
			do
				TARGET=R_bootstrap_${ESTADISTICO}_${SEASON}_${VARIABLE}_${STATION}.r.Rout
				mv $TARGET bootstrap/out/${VARIABLE}/${SEASON}

			done
		done
	done
done





