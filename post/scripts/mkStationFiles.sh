#!/bin/bash

#mkStationFiles.sh
#Programa que genera archivos con el nombre de cada estacion y su latitud longitud para ser usado con otras utilerias. 
#Fecha de creacion: 04Agosto2016

#------------------Requisitos------------------------------------------------------------

#-----------------Versiones---------------------------------------------------------------
#v1.0 04/Ago/16 Se crea el programa. 

#EMAS
#DIRECTORIO_ESTACIONES=/run/media/esli/El_Jurado/WRF_stuff/observaciones/dataFiles/processed_ema_year
#REDMET
DIRECTORIO_ESTACIONES=/run/media/esli/El_Jurado/WRF_stuff/observaciones/dataFiles/processed_redmet
cd ../timeSeries/stationFiles

for STATION in `ls $DIRECTORIO_ESTACIONES`
do

touch $STATION
echo "LAT=" >> $STATION
echo "LON=" >> $STATION

done
