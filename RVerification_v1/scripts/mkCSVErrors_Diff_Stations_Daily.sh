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
INTERVALO=l24
TARGET_DIR=verify_daily/${INTERVALO}/out

#########-----------------------------Getting difference of values--------------------------------------------------------------------------------------------------

RES1=5
RES2=25
rm csv/TM/daily/*
rm csv/WS/daily/*
for SEASON in `ls $DIRECTORIO_SEASONS`
do
		for VARIABLE in `ls $DIRECTORIO_VARIABLES`
		do
		#VARIABLE=TM
			
			for STATION in `ls $DIRECTORIO_ESTACIONES`
			do
				for DAY in `ls $DIRECTORIO_DIAS`
				do 
					TARGET_MAE=csv/${VARIABLE}/daily/MAE_diff_${SEASON}_${VARIABLE}_${STATION}.csv
					TARGET_ME=csv/${VARIABLE}/daily/ME_diff_${SEASON}_${VARIABLE}_${STATION}.csv
					TARGET_MSE=csv/${VARIABLE}/daily/MSE_diff_${SEASON}_${VARIABLE}_${STATION}.csv
					head -1 csv_daily_header.txt > $TARGET_MAE
					head -1 csv_daily_header.txt > $TARGET_ME
					head -1 csv_daily_header.txt > $TARGET_MSE
		
					file1=${TARGET_DIR}/${SEASON}/MAE_${RES1}_${SEASON}_${VARIABLE}_${STATION}.csv
					file2=${TARGET_DIR}/${SEASON}/MAE_${RES2}_${SEASON}_${VARIABLE}_${STATION}.csv
					file3=$TARGET_MAE
					paste -d',' $file1 $file2 | awk -F',' -v OFS=',' '$1==($1+0) && $3==($3+0) {if ($2==$4) {print $1, $3, $1-$3, $2, $4}}' >> $file3 

					file1=${TARGET_DIR}/${SEASON}/MSE_${RES1}_${SEASON}_${VARIABLE}_${STATION}.csv
					file2=${TARGET_DIR}/${SEASON}/MSE_${RES2}_${SEASON}_${VARIABLE}_${STATION}.csv
					file3=$TARGET_MSE
					paste -d',' $file1 $file2 | awk -F',' -v OFS=',' '$1==($1+0) && $3==($3+0) {if ($2==$4) {print $1, $3, $1-$3, $2, $4}}' >> $file3

					file1=${TARGET_DIR}/${SEASON}/ME_${RES1}_${SEASON}_${VARIABLE}_${STATION}.csv
					file2=${TARGET_DIR}/${SEASON}/ME_${RES2}_${SEASON}_${VARIABLE}_${STATION}.csv
					file3=$TARGET_ME
					paste -d',' $file1 $file2 | awk -F',' -v OFS=',' '$1==($1+0) && $3==($3+0) {if ($2==$4) {print $1, $3, $1-$3, $2, $4}}' >> $file3
				done
			done
		done
done
