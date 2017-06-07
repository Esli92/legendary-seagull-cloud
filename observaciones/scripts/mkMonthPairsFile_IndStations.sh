#!/bin/bash

#Programa para unir todos los archivos de pares de observaciones en un solo archivo para usar en R. Genera un archivo mensual de todo

echo 'BULK PAIRS ALL V2.0 -----> Indica los siguientes datos'
#read -p 'Indica la resolucion (5 o 25): ' RESOLUTION
#read -p 'Indica el mes de simulacion (mm): ' MES


DIRECTORIO_VARIABLES=../dataFiles/variables
DIRECTORIO_ESTACIONES=../dataFiles/estaciones
DIRECTORIO_RESOLUCIONES=./resoluciones
DIRECTORIO_MESES=./meses

for MES in `ls $DIRECTORIO_MESES`
do

	for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
	do

		PAIR_FILES=../dataFiles/pares/l24h/0p${RESOLUTION}/${MES}

		if [ ! -d "${PAIR_FILES}/monthlyPairs" ]
		then
			mkdir ${PAIR_FILES}/monthlyPairs
		else
			rm -rf ${PAIR_FILES}/monthlyPairs
			mkdir ${PAIR_FILES}/monthlyPairs
		fi	

		HEADER_SAMPLE=header_sample.txt
		#cd $PAIR_FILES

		#VARIABLE=TM
		for ESTACION in `ls $DIRECTORIO_ESTACIONES`
		do
			for VARIABLE in `ls $DIRECTORIO_VARIABLES`
			do

				rm ${PAIR_FILES}/${ESTACION}_${VARIABLE}_m${MES}.txt 

				head -1 ${HEADER_SAMPLE} > ${PAIR_FILES}/${ESTACION}_${VARIABLE}_m${MES}.pre; tail -n +2 -q ${PAIR_FILES}/ObsFct_Pairs_${VARIABLE}_${ESTACION}*  >> ${PAIR_FILES}/${ESTACION}_${VARIABLE}_m${MES}.pre

				awk 'BEGIN { FS = "," }; $4 != -99 {print $1","$2","$3","$4","$5}' ${PAIR_FILES}/${ESTACION}_${VARIABLE}_m${MES}.pre >> ${PAIR_FILES}/${ESTACION}_${VARIABLE}_m${MES}.txt

				mv ${PAIR_FILES}/${ESTACION}_${VARIABLE}_m${MES}.txt ${PAIR_FILES}/monthlyPairs
				rm ${PAIR_FILES}/${ESTACION}_${VARIABLE}_m${MES}.pre
			done
		done

		#Para hacer un archivo con TODOS los pares de TODAS las estaciones del mes

	done
done
