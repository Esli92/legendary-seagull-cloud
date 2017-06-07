#mkStationReadsSeasons.sh
#Programa para autogenerar lineas de leer ciertas estaciones para los scripts de R, de tal manera que no haya que hacerlo manual para cada estacion, usando los archivos diarios de las estaciones individuales.
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

figlet FORECAST VERIFICATION

echo "¡ATENCION! ESTE PROCESO ES MUY TARDADO, EL ESTIMADO ES DE 5 HORAS PARA TERMINAR. TE RECOMIENDO DEJAR CORRIENDO DE FONDO O ALGO ASI".
echo "CORRIENDO SCRIPTS DE R"

find ./verify_daily/${INTERVALO}/WS/04/25 -name "*.R" -exec R CMD BATCH {} \;

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
