#!/bin/bash

#Programa para unir todos los archivos de pares de observaciones en un solo archivo para usar en R. Genera archivos estacionales para estaciones individuales.

echo 'BULK PAIRS ALL V3.0 -----> INICIANDO PROGRAMA'
#read -p 'Indica la resolucion (5 o 25): ' RESOLUTION
#read -p 'Indica el mes de simulacion (mm): ' MES

DIRECTORIO_VARIABLES=../dataFiles/variables
DIRECTORIO_ESTACIONES=../dataFiles/estaciones
DIRECTORIO_RESOLUCIONES=./resoluciones
DIRECTORIO_MESES=./meses
DIRECTORIO_SEASONS=./seasons
HEADER_SAMPLE=header_sample.txt
INTERVALO=l24

for SEASON in `ls $DIRECTORIO_SEASONS`
do

	for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
	do

		for STATION in `ls $DIRECTORIO_ESTACIONES` 
		do 

			for VARIABLE in `ls $DIRECTORIO_VARIABLES`
			do 

				PAIR_FILES_S=../dataFiles/pares/${INTERVALO}h/0p${RESOLUTION}/seasonal/${SEASON}
				rm $PAIR_FILES_S/${STATION}_${SEASON}_${VARIABLE}.txt
				head -1 ${HEADER_SAMPLE} > $PAIR_FILES_S/${STATION}_${SEASON}_${VARIABLE}.txt

				for MES in `ls $DIRECTORIO_SEASONS/$SEASON` 
				do

					PAIR_FILES=../dataFiles/pares/${INTERVALO}h/0p${RESOLUTION}/${MES}/monthlyPairs/${STATION}_${VARIABLE}_m${MES}.txt

					tail -n +2 -q ${PAIR_FILES} >> ${PAIR_FILES_S}/${STATION}_${SEASON}_${VARIABLE}.txt
				done
			done
		done
	done

done

echo 'BULK PAIRS ALL V3.0 -----> EL PROGRAMA HA FINALIZADO, PUEDES ENCONTRAR LAS SALIDAS EN ../dataFiles/pares/${INTERVALO}h/RESOLUTION/seasonal/'
