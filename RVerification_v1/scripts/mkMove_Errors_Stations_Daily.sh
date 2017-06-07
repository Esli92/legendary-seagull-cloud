#!/bin/bash

#mkMove
#Programa para mover archivos resultantes de mkRScripts_Errors_Stations_Daily.sh
#Programador Oscar Jurado
#Fecha de creacion: Feb/2017

#------------------Requisitos------------------------------------------------------------
#Directorio de estaciones a usar
#Archivos con datos estacionales en pares obs/pron para cada estacion

#-----------------Versiones---------------------------------------------------------------
#v1.0 Se crea el programa. 


#----------------Problemas Conocidos-----------------------------------------------------


#----------------Directorios Locales, cambiar si es necesario----------------------------
DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/estaciones
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables_cont
DIRECTORIO_MESES=../../observaciones/scripts/meses
DIRECTORIO_DIAS=../../observaciones/scripts/days
DIRECTORIO_MESES_SIM=meses_sim
INTERVALO=l24

mkdir verify_daily/${INTERVALO}/out

for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
do
	mkdir verify_daily/${INTERVALO}/out/${RESOLUTION}
	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
	mkdir verify_daily/${INTERVALO}/out/${RESOLUTION}/${VARIABLE}
		for MES in `ls $DIRECTORIO_MESES`
		do
		mkdir verify_daily/${INTERVALO}/out/${RESOLUTION}/${VARIABLE}/${MES}
			for STATION in `ls $DIRECTORIO_ESTACIONES`
			do
				for DAY in `ls $DIRECTORIO_DIAS`
				do
				mv R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${MES}_${DAY}_${STATION}.Rout verify_daily/${INTERVALO}/out/${RESOLUTION}/${VARIABLE}/${MES}
				done
			done
		done
	done
done

figlet DONE
