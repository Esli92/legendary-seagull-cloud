#mkStationReadsSeasons.sh
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
DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/estaciones
DIRECTORIO_SEASONS=../../observaciones/scripts/seasons
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables

#Vamos a ir de RES>VAR>SEAS>STAT

for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
do

	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		
		for SEASON in `ls $DIRECTORIO_SEASONS`
		do
			
			rm readStation/R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${SEASON}.txt
			touch readStation/R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${SEASON}.txt

			for STATION in `ls $DIRECTORIO_ESTACIONES`
			do

				sed 's/'RESOLUTION'/'${RESOLUTION}'/g' readStation.template > readStation.pre
				sed 's/'SEASON'/'${SEASON}'/g' readStation.pre > readStation.pre2
				sed 's/'STATION'/'${STATION}'/g' readStation.pre2 > readStation.pre
				sed 's/'VARIABLE'/'${VARIABLE}'/g' readStation.pre > readStation.pre2
				cat readStation.pre2 >> readStation/R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${SEASON}.txt
				rm readStation.pre readStation.pre2
			done
		done
	done
done

