#!/bin/bash

#Programa para unir todos los archivos de pares de observaciones en un solo archivo para usar en R. Genera archivos estacionales para grupos de estaciones.

echo 'BULK PAIRS ALL V3.0 -----> INICIANDO PROGRAMA'
#read -p 'Indica la resolucion (5 o 25): ' RESOLUTION
#read -p 'Indica el mes de simulacion (mm): ' MES

DIRECTORIO_VARIABLES=../dataFiles/variables
DIRECTORIO_ESTACIONES=../dataFiles/estaciones
DIRECTORIO_RESOLUCIONES=./resoluciones
DIRECTORIO_GRUPOS=../dataFiles/gruposEstaciones
DIRECTORIO_MESES=./meses
DIRECTORIO_SEASONS=./seasons
HEADER_SAMPLE=header_sample.txt

for SEASON in `ls $DIRECTORIO_SEASONS`
do

	for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
	do
		for VARIABLE in `ls $DIRECTORIO_VARIABLES`
		do
			for GRUPO in `ls ${DIRECTORIO_GRUPOS}` 
			do 

				PAIR_FILES_S=../dataFiles/pares/24h/0p${RESOLUTION}/seasonal/${SEASON}
				rm $PAIR_FILES_S/${GRUPO}_${SEASON}_${VARIABLE}.txt
				rm $PAIR_FILES_S/${GRUPO}_stationFile.txt
				head -1 ${HEADER_SAMPLE} > $PAIR_FILES_S/${GRUPO}_${SEASON}_${VARIABLE}.txt
				touch $PAIR_FILES_S/${GRUPO}_stationFile.txt
				for STATION in `ls $DIRECTORIO_GRUPOS/${GRUPO}`
				do 

					for MES in `ls $DIRECTORIO_SEASONS/$SEASON` 
					do

						PAIR_FILES=../dataFiles/pares/24h/0p${RESOLUTION}/${MES}/monthlyPairs/${STATION}_${VARIABLE}_m${MES}.txt

						tail -n +2 -q ${PAIR_FILES} >> ${PAIR_FILES_S}/${GRUPO}_${SEASON}_${VARIABLE}.txt
						echo "${GRUPO} has ${STATION} for ${MES} month in season ${SEASON}" >> ${PAIR_FILES_S}/${GRUPO}_stationFile.txt
					done
				done
			done
		done
	done

done

echo 'BULK PAIRS ALL V3.0 -----> EL PROGRAMA HA FINALIZADO, PUEDES ENCONTRAR LAS SALIDAS EN ../dataFiles/pares/24h/RESOLUTION/seasonal/'
