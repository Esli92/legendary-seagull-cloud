#!/bin/bash
#processPairs.sh
#Programa que toma datos de observaciones (REDMET o EMA) junto con su correspondiente pronostico hecho por WRF y los pone en pares para la verificacion
#Programador Oscar Jurado
#Fecha de creacion: Julio 2016

#------------------Requisitos------------------------------------------------------------
#Datos procesados de WRF y observaciones. 
#WRF: Series de tiempo echas con mkTimeSeries
#Obs: Series de tiempo anuales 

#-----------------Versiones---------------------------------------------------------------
#v1.0 31/May/16 Se crea el programa. 
#v1.2 31/May/16 Se genera la documentacion, se optimiza la portabilizacion
#v2.0 Oct/16 Se agrega modo debugging, se arregla problema con diferentes variables, se asegura que funcionan todas las variables. 

#----------------Problemas Conocidos-----------------------------------------------------

#----------------Directorios Locales, cambiar si es necesario----------------------------
DIRECTORIO_DATOS=/home/esli/Documentos/WRF/experimentos/verificacion/observaciones
ANIO_SHORT='15'
#Activar lo siguiente para hacer debugging (0 = desactivado)
DEBUG_MODE=false
DIRECTORIO_SCRIPTS=`pwd`

DIRECTORIO_VARIABLES=${DIRECTORIO_DATOS}/dataFiles/variables
DIRECTORIO_SALIDAS=${DIRECTORIO_DATOS}/dataFiles/pares/24h
DIRECTORIO_RESOLUCIONES=${DIRECTORIO_SCRIPTS}/resoluciones
DIRECTORIO_MESES=${DIRECTORIO_SCRIPTS}/meses

echo 'BULK PAIRS V3.0 -----> INICIANDO PROGRAMA'
#read -p 'Indica la resolucion (5 o 25): ' RESOLUTION
#read -p 'Indica el mes de simulacion (mm): ' MES
#read -p 'Indica el anio (yy): ' ANIO_SHORT
#read -p 'Elige sistema de estaciones a usar, 01 - Redmet; 02 - EMA (XX): ' CHOICE
for MES in `ls $DIRECTORIO_MESES`
do
echo '-----------INICIANDO MES-----------------------'
for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
do

	cd $DIRECTORIO_SALIDAS
	if [ ! -d "0p${RESOLUTION}" ]
	then
		mkdir 0p${RESOLUTION}
	fi

	if [ ! -d "0p${RESOLUTION}/${MES}" ]
	then
		mkdir 0p${RESOLUTION}/${MES}
	else
		rm -rf 0p${RESOLUTION}/${MES}
		mkdir 0p${RESOLUTION}/${MES}
	fi

	for CHOICE in `seq 1 2`;
	do

	if [ $CHOICE == 2 ]
	then
		DIRECTORIO_ESTACIONES=${DIRECTORIO_DATOS}/dataFiles/processed_ema_year
	else
		DIRECTORIO_ESTACIONES=${DIRECTORIO_DATOS}/dataFiles/processed_redmet
	fi



		if [ "$DEBUG_MODE" = false ]; then
			for STATION in `ls $DIRECTORIO_ESTACIONES`
			do
			WRF_DATA_DIR=/home/esli/Documentos/WRF/experimentos/verificacion/post/timeSeries/${MES}_0p${RESOLUTION}/${STATION}/20${ANIO_SHORT}
			cd $WRF_DATA_DIR

			#Para cuando tenga todas las variables
				for VARIABLE in `ls $DIRECTORIO_VARIABLES`
				do
				rm ${STATION}_${VARIABLE}.txt
				ln -s ${DIRECTORIO_ESTACIONES}/${STATION}/20${ANIO_SHORT}/${VARIABLE}/${STATION}_${VARIABLE}.txt .
		
				if [ "$VARIABLE" = TM ]; then
					find . -name '*TM.txt' -exec python ../../../../../observaciones/scripts/mkObsFrcstPairs.py ${STATION}_${VARIABLE}.txt {} \;
				elif [ "$VARIABLE" = WS ]; then
					find . -name '*WS.txt' -exec python ../../../../../observaciones/scripts/mkObsFrcstPairs.py ${STATION}_${VARIABLE}.txt {} \;
					echo 'nothing to do here either!' 
				elif [ "$VARIABLE" = RN ]; then
					echo ${STATION}_${VARIABLE}_${MES}
					find . -name '??????_??_??_??_RA.txt' -exec python ../../../../../observaciones/scripts/mkObsFrcstPairs.py ${STATION}_${VARIABLE}.txt {} \;
				fi

				rm ${STATION}_${VARIABLE}.txt
				mv ${DIRECTORIO_SALIDAS}/ObsFct_Pairs_${VARIABLE}_${ESTACION}* ${DIRECTORIO_SALIDAS}/0p${RESOLUTION}/${MES}
				done


			done

		else
			#PARA MODO DEBUGGING
			STATION=ecogua
			WRF_DATA_DIR=/home/esli/Documentos/WRF/experimentos/verificacion/post/timeSeries/${MES}_0p${RESOLUTION}/${STATION}/20${ANIO_SHORT}
			cd $WRF_DATA_DIR

			VARIABLE=TM 
			rm ${STATION}_${VARIABLE}.txt
			ln -s ${DIRECTORIO_ESTACIONES}/${STATION}/20${ANIO_SHORT}/${VARIABLE}/${STATION}_${VARIABLE}.txt .

			find . -name '*TM.txt' -exec python ../../../../../observaciones/scripts/mkObsFrcstPairs.py ${STATION}_${VARIABLE}.txt {} \;
			
			rm ${STATION}_${VARIABLE}.txt
			
			cd $WRF_DATA_DIR
			mv ${DIRECTORIO_SALIDAS}/ObsFct_Pairs_${VARIABLE}_${ESTACION}* ${DIRECTORIO_SALIDAS}/0p${RESOLUTION}/${MES}
		fi
	done

	#cd $DIRECTORIO_SCRIPTS
	#source mkAllPairsFile.sh ${RESOLUTION} ${MES}
done

done

