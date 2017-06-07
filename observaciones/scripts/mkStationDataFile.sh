#mkStationDataFile
#Programa para autogenerar lineas de leer ciertas estaciones para los scripts de R, de tal manera que no haya que hacerlo manual para cada estacion
#Programador Oscar Jurado
#Fecha de creacion: Nov/2016

#------------------Requisitos------------------------------------------------------------
#Directorio de estaciones a usar
#Archivos con datos estacionales en pares obs/pron para cada estacion

#-----------------Versiones---------------------------------------------------------------
#v1.0 Se crea el programa. 


#----------------Problemas Conocidos-----------------------------------------------------


#----------------Directorios Locales, cambiar si es necesario----------------------------
DIRECTORIO_ESTACIONES=../dataFiles/estaciones
DIRECTORIO_SEASONS=../scripts/seasons
DIRECTORIO_RESOLUCIONES=../scripts/resoluciones
DIRECTORIO_VARIABLES=../dataFiles/variables

rm stationLatLonFiles.txt
touch stationLatLonFiles.txt

for STATION in `ls $DIRECTORIO_ESTACIONES`
do
	source $DIRECTORIO_ESTACIONES/$STATION
	#Obtenemos LAT,LON
	echo $STATION,$LAT,$LON >> stationLatLonFiles.txt
done

