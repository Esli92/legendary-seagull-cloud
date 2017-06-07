#!/bin/bash

#mkVerifStatFiles_stations.sh
#Program that takes R scripts for contingency table verifications and runs the output. 
#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 25-Feb-2017

#------------------Requisites------------------------------------------------------------
#Results from contingency table tests


#-----------------Version---------------------------------------------------------------
#v1.0 25/Feb/17 Program is created


#----------------Known issues-----------------------------------------------------------

#-----------------Local directories----------------------------------------------------- 

DIRECTORIO_SCRIPTS=./contingencyTables
DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/gruposEstaciones/EMA
DIRECTORIO_SEASONS=./seasons
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables
DIRECTORIO_GRUPOS=../../observaciones/dataFiles/gruposEstaciones
INTERVALO=l24

#-----------------BEGIN PROGRAM--------------------------------------------------------

cd ${DIRECTORIO_SCRIPTS}/${INTERVALO}
find . -name "*.R" -exec R CMD BATCH {} \;

	if [ ! -d "out" ]
	then
		mkdir out
	else
		rm -rf out
		mkdir out
	fi

mv *.Rout out/ 

mkdir out/TM
mkdir out/RN

mv out/*_vRN_* out/RN 
mv out/*_vTM_* out/TM 
