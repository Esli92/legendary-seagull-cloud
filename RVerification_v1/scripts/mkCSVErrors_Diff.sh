#!/bin/bash

#mkDiffRes.sh
#Program that takes two csv files and makes the difference from the third column, used for difference in resolutions.
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
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables_cont
DIRECTORIO_GRUPOS=../../observaciones/dataFiles/gruposEstaciones
RES_1=25
RES_2=5

#-----------------BEGIN PROGRAM--------------------------------------------------------

#Example of result directory
#verify/out/${RESOLUTION}/${VARIABLE}/${SEASON}

rm csv/*_diff_*

for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			head -1 csv_header.txt > csv/MAE_diff_${SEASON}_${VARIABLE}.csv
			head -1 csv_header.txt > csv/ME_diff_${SEASON}_${VARIABLE}.csv
			head -1 csv_header.txt > csv/MSE_diff_${SEASON}_${VARIABLE}.csv
			
			file1=csv/MAE_${RES_1}_${SEASON}_${VARIABLE}.csv
			file2=csv/MAE_${RES_2}_${SEASON}_${VARIABLE}.csv
			file3=csv/MAE_diff_${SEASON}_${VARIABLE}.csv
			paste $file1 $file2 | awk -F',' -v OFS=',' 'function abs(v) {return v < 0 ? -v : v}  {if (NR!=1) {print $1, $2, $3-$6, $7}}' >> $file3 

			file1=csv/ME_${RES_1}_${SEASON}_${VARIABLE}.csv
			file2=csv/ME_${RES_2}_${SEASON}_${VARIABLE}.csv
			file3=csv/ME_diff_${SEASON}_${VARIABLE}.csv
			paste $file1 $file2 | awk -F',' -v OFS=',' 'function abs(v) {return v < 0 ? -v : v}  {if (NR!=1) {print $1, $2, abs($3-$6), $7}}' >> $file3 

			file1=csv/MSE_${RES_1}_${SEASON}_${VARIABLE}.csv
			file2=csv/MSE_${RES_2}_${SEASON}_${VARIABLE}.csv
			file3=csv/MSE_diff_${SEASON}_${VARIABLE}.csv
			paste $file1 $file2 | awk -F',' -v OFS=',' 'function abs(v) {return v < 0 ? -v : v}  {if (NR!=1) {print $1, $2, $3-$6, $7}}' >> $file3 
		done
	done


