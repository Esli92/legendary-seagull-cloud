#!/bin/bash

#Programa para unir todos los archivos de pares de observaciones en un solo archivo para usar en R. Genera archivos estacionales de todas las estaciones.

echo 'BULK PAIRS ALL V3.0 -----> INICIANDO PROGRAMA'
#read -p 'Indica la resolucion (5 o 25): ' RESOLUTION
#read -p 'Indica el mes de simulacion (mm): ' MES

DIRECTORIO_VARIABLES=../dataFiles/variables
DIRECTORIO_ESTACIONES=../dataFiles/estaciones
DIRECTORIO_RESOLUCIONES=./resoluciones
DIRECTORIO_MESES=./meses
DIRECTORIO_SEASONS=./seasons
INTERVALO=l24

for MES in `ls $DIRECTORIO_MESES`
do 

	for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
	do 
		PAIR_FILES=../dataFiles/pares/${INTERVALO}h/0p${RESOLUTION}/${MES}	
		HEADER_SAMPLE=header_sample.txt

		for VARIABLE in `ls $DIRECTORIO_VARIABLES`
		do
			#ALL station files
			rm ${PAIR_FILES}/monthlyPairs/ALL_${VARIABLE}_m${MES}.txt
			head -1 ${HEADER_SAMPLE} > ${PAIR_FILES}/monthlyPairs/ALL_${VARIABLE}_m${MES}.pre
			tail -n +2 -q ${PAIR_FILES}/monthlyPairs/*_${VARIABLE}_m${MES}.txt  >> ${PAIR_FILES}/monthlyPairs/ALL_${VARIABLE}_m${MES}.pre
			awk 'BEGIN { FS = "," }; $4 != -99 {print $1","$2","$3","$4","$5}' ${PAIR_FILES}/monthlyPairs/ALL_${VARIABLE}_m${MES}.pre >> ${PAIR_FILES}/monthlyPairs/ALL_${VARIABLE}_m${MES}.txt
			rm ${PAIR_FILES}/monthlyPairs/ALL_${VARIABLE}_m${MES}.pre
			#REDMET only
			rm ${PAIR_FILES}/monthlyPairs/RED_${VARIABLE}_m${MES}.txt
			head -1 ${HEADER_SAMPLE} > ${PAIR_FILES}/monthlyPairs/RED_${VARIABLE}_m${MES}.pre
			tail -n +2 -q ${PAIR_FILES}/monthlyPairs/???_${VARIABLE}_m${MES}.txt  >> ${PAIR_FILES}/monthlyPairs/RED_${VARIABLE}_m${MES}.pre
			awk 'BEGIN { FS = "," }; $4 != -99 {print $1","$2","$3","$4","$5}' ${PAIR_FILES}/monthlyPairs/RED_${VARIABLE}_m${MES}.pre >> ${PAIR_FILES}/monthlyPairs/RED_${VARIABLE}_m${MES}.txt
			rm ${PAIR_FILES}/monthlyPairs/RED_${VARIABLE}_m${MES}.pre
			#EMA only
			rm ${PAIR_FILES}/monthlyPairs/EMA_${VARIABLE}_m${MES}.txt
			head -1 ${HEADER_SAMPLE} > ${PAIR_FILES}/monthlyPairs/EMA_${VARIABLE}_m${MES}.pre
			tail -n +2 -q ${PAIR_FILES}/monthlyPairs/??????_${VARIABLE}_m${MES}.txt  >> ${PAIR_FILES}/monthlyPairs/EMA_${VARIABLE}_m${MES}.pre
			awk 'BEGIN { FS = "," }; $4 != -99 {print $1","$2","$3","$4","$5}' ${PAIR_FILES}/monthlyPairs/EMA_${VARIABLE}_m${MES}.pre >> ${PAIR_FILES}/monthlyPairs/EMA_${VARIABLE}_m${MES}.txt
			rm ${PAIR_FILES}/monthlyPairs/EMA_${VARIABLE}_m${MES}.pre
		done
	done
done

for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
do
	PAIR_FILES=../dataFiles/pares/${INTERVALO}h/0p${RESOLUTION}
		if [ ! -d "${PAIR_FILES}/seasonal" ]
		then
			mkdir ${PAIR_FILES}/seasonal
		else
			rm -rf ${PAIR_FILES}/seasonal
			mkdir ${PAIR_FILES}/seasonal
		fi
	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			mkdir ${PAIR_FILES}/seasonal/${SEASON}
			PAIR_FILES_S=../dataFiles/pares/${INTERVALO}h/0p${RESOLUTION}/seasonal/${SEASON}
			rm $PAIR_FILES_S/ALL_${SEASON}_${VARIABLE}.txt
			head -1 ${HEADER_SAMPLE} > $PAIR_FILES_S/ALL_${SEASON}_${VARIABLE}.txt
			rm $PAIR_FILES_S/RED_${SEASON}_${VARIABLE}.txt
			head -1 ${HEADER_SAMPLE} > $PAIR_FILES_S/RED_${SEASON}_${VARIABLE}.txt
			rm $PAIR_FILES_S/EMA_${SEASON}_${VARIABLE}.txt
			head -1 ${HEADER_SAMPLE} > $PAIR_FILES_S/EMA_${SEASON}_${VARIABLE}.txt
			for MES in `ls $DIRECTORIO_SEASONS/$SEASON`
			do
				tail -n +2 -q ${PAIR_FILES}/${MES}/monthlyPairs/ALL_${VARIABLE}_m${MES}.txt  >> ${PAIR_FILES_S}/ALL_${SEASON}_${VARIABLE}.txt
				tail -n +2 -q ${PAIR_FILES}/${MES}/monthlyPairs/RED_${VARIABLE}_m${MES}.txt  >> ${PAIR_FILES_S}/RED_${SEASON}_${VARIABLE}.txt
				tail -n +2 -q ${PAIR_FILES}/${MES}/monthlyPairs/EMA_${VARIABLE}_m${MES}.txt  >> ${PAIR_FILES_S}/EMA_${SEASON}_${VARIABLE}.txt
			done
	done	done
done
