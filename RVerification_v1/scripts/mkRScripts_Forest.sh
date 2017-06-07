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
#Target Dir example: "./csv/boot/VARIABLE/ESTADISTICO_SEASON_VARIABLE.csv"

if [ ! -d "forest/" ]
then
	mkdir forest
fi

rm -v forest/*


	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do

		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			for ESTADISTICO in `ls $DIRECTORIO_STATS`
			do
				TARGET=forest/R_forest_${ESTADISTICO}_${SEASON}_${VARIABLE}.r
				sed 's/'VARIABLE'/'${VARIABLE}'/g' forestplot_boot.template > boot.pre1
				sed 's/'SEASON'/'${SEASON}'/g' boot.pre1 > boot.pre2
				
				if [ $ESTADISTICO = "MSE" ]
				then
					LOW=-3
					UP=3
					STATUS=ECM
				elif [ $ESTADISTICO = "MAE" ] 
				then
					LOW=-0.1
					UP=0.1
					STATUS=EMA
				else
					LOW=-0.05
					UP=0.05
					STATUS=EM
				fi
				sed 's/'ABA'/'${LOW}'/g' boot.pre2 > boot.pre1
				sed 's/'ARR'/'${UP}'/g' boot.pre1 > boot.pre2
				sed 's/'STATUS'/'${STATUS}'/g' boot.pre2 > boot.pre1
				sed 's/'ESTADISTICO'/'${ESTADISTICO}'/g' boot.pre1 > boot.pre2

				csvfile=./csv/boot/${VARIABLE}/${ESTADISTICO}_${SEASON}_${VARIABLE}.csv
				#string=\(
				source station_topo_types.sh
				i=1
				awk -F',' '{if (NR!=1) {print $6}}' $csvfile | while read line
				do
					source station_topo_types.sh
					tempvar="$(grep -F "$line" station_topo_types.sh | awk -F"=" '{print $2}')"
					if [ $i = "1" ]
					then
						string=\(${tempvar}
						stringk=\(${tempvar}k
						i=2
					else
						string=${string},${tempvar}
						stringk=${stringk},${tempvar}k
					fi
					echo $string > string_file.txt
					echo $stringk > stringk_file.txt
				done 

					string="$(cat string_file.txt)"
					string=${string}\)

					stringk="$(cat stringk_file.txt)"
					stringk=${stringk}\)
					#echo $stringk

				sed 's/'STORING'/'${string}'/g' boot.pre2 > boot.pre1


				sed -r "s:"CIRC":"1":g" boot.pre1 > boot.pre2
				sed -r "s:"DIAM":"2":g" boot.pre2 > boot.pre1
				sed -r "s:"TRIANG":"3":g" boot.pre1 > $TARGET
			done
		done
	done






