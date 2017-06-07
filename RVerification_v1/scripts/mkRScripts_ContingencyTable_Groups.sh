#!/bin/bash

#mkContingencyTableTestsR
#Program to automaticaly generate contingencytabletest.R programs, changing the input file to be the proper one. 

#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 11-Sep-2016

#------------------Requisites------------------------------------------------------------
#contingencytabletest.R.template file on same directory


#-----------------Version---------------------------------------------------------------
#v1.0 11/Sep/16 Program is created
#v2.0 Nov/16 Added Taylor diagrams with plotrix, improved labels on conditional quantile, translated to spanish

#----------------Known issues-----------------------------------------------------------

#-----------------Local directories----------------------------------------------------- 

DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/estaciones
DIRECTORIO_SEASONS=./seasons
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables
DIRECTORIO_GRUPOS=../../observaciones/dataFiles/gruposEstaciones
INTERVALO=l24
#-----------------BEGIN PROGRAM--------------------------------------------------------

#Lets begin by creating directory to put the R scripts in

if [ ! -d "contingencyTables" ]
then
	mkdir contingencyTables
fi

#Order of programs will be VAR>SEASON>GROUP

for VARIABLE in `ls $DIRECTORIO_VARIABLES`
do
	if [ ! -d "contingencyTables/${INTERVALO}" ]
	then
		mkdir contingencyTables/${INTERVALO}
	fi

	mkdir contingencyTables/${INTERVALO}/${VARIABLE}

	for SEASON in `ls $DIRECTORIO_SEASONS`
	do
		source $DIRECTORIO_SEASONS/$SEASON

		for GRUPO in `ls $DIRECTORIO_GRUPOS`
		do
			if [ "$VARIABLE" = TM ]; then
				TARGET=contingencyTables/${INTERVALO}/${VARIABLE}/contingencytable_v${VARIABLE}_s${SEASON}_g${GRUPO}.R
				sed 's:'SEASON':'${SEASON}':g' contingencytabletest.R.templateTM > contingency.pre1
				sed 's:'VARIABLE':'${VARIABLE}':g' contingency.pre1 > contingency.pre2
				sed 's:'MINCLIM':'${MINCLIM}':g' contingency.pre2 > contingency.pre1
				sed 's:'MEANCLIM':'${MEANCLIM}':g' contingency.pre1 > contingency.pre2
				sed 's:'MAXCLIM':'${MAXCLIM}':g' contingency.pre2 > contingency.pre1
				sed 's:'INTERVAL':'${INTERVALO}':g' contingency.pre1 > contingency.pre2
				sed 's:'GROUP':'${GRUPO}':g' contingency.pre2 > ${TARGET}
			elif [ "$VARIABLE" = RN ]; then
				TARGET=contingencyTables/${INTERVALO}/${VARIABLE}/contingencytable_v${VARIABLE}_s${SEASON}_g${GRUPO}.R
				sed 's:'SEASON':'${SEASON}':g' contingencytabletest.R.templateRN > contingency.pre1
				sed 's:'VARIABLE':'${VARIABLE}':g' contingency.pre1 > contingency.pre2
				sed 's:'INTERVAL':'${INTERVALO}':g' contingency.pre2 > contingency.pre1
				sed 's:'GROUP':'${GRUPO}':g' contingency.pre1 > ${TARGET}
			fi
			rm contingency.pre1
			rm contingency.pre2
		done
	done
done

echo "Scripts for R are done, find them in the directory called contingencyTables" 
