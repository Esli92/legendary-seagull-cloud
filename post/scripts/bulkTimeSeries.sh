#!/bin/bash

#bulkTimeSeries.sh
#Programa que toma datos de entrada de grads (.ctl y .dat), genera un script .gs para obtener series de tiempo de diversos puntos, usando el PUNTO MAS CERCANO a lo indicado.
#Programador Oscar Jurado
#Fecha de creacion: 20Julio2016

#------------------Requisitos------------------------------------------------------------
#Script a seguir de grads, "getTimeSeries.gs.template"
#Datos de salida generados con la otra utileria .pregrads.sh >> SI NO SE USO ENTONCES GENERAR DATOS DE ENTRADA DE LA SIGUIENTE MANERA:
#wrfout_GRADS_${DIA_INIT}-${DIA_FIN}_${MES_INIT}_${ANIO}_d${DOMINIO}.ctl 
#Directorio de fechas del mes a simular

#-----------------Versiones---------------------------------------------------------------
#v1.0 20/Jul/16 Se crea el programa. 
#v2.0 Se anade un modulo para hacer las series de Tiempo para cada estacion para cada tiempo del mes elegido. 
#v2.1 Se mejora un poco la documentacion. 
#v3.0 Se modifico el sistema para que ahora genere archivos para 3 variables en vez de una: TM,WS,RN.
#----------------Problemas Conocidos-----------------------------------------------------

#----------------Directorios Locales, cambiar si es necesario----------------------------

DIRECTORIO_ESTACIONES=../timeSeries/stationFiles

#Solicitar al usuario datos de mes y resolucion

echo 'BULK TIME SERIES V1.0 -----> Indica los siguientes datos'
echo 'Toma en cuenta que las fechas salen de un directorio fijo'
read -p 'Indica la resolucion (5 o 25): ' RESOLUTION
read -p 'Indica el mes de simulacion (mm): ' MES
read -p 'Indica el anio (yy): ' ANIO_SHORT
#Lo mas importante, el directorio de fechas
DIRECTORIO_FECHAS=fechas/fechas${MES}
 
#Empezamos quitando todo
rm -rf ../timeSeries/${MES}_0p${RESOLUTION}
cp -r ../timeSeries/template ../timeSeries/${MES}_0p${RESOLUTION}

for FECHA in `ls $DIRECTORIO_FECHAS`
do

	for STATION in `ls $DIRECTORIO_ESTACIONES`
	do

	source $DIRECTORIO_ESTACIONES/$STATION
        source $DIRECTORIO_FECHAS/$FECHA

        ANIO=$AI
        MES_INIT=$MI
        MES_FIN=$MF
        DIA_INIT=$DI
        DIA_FIN=$DF
        HORA_INIT=$HI
        HORA_FIN=$HF
        DOMINIO=02

	if [ ! -d "../timeSeries/${MES_INIT}_0p${RESOLUTION}" ]
	then
	    mkdir ../timeSeries/${MES_INIT}_0p${RESOLUTION}
	fi

	InputDir=${MES}_0p${RESOLUTION}/wrfout_GRADS_${DI}-${DF}_${MI}_${AI}_d${DOMINIO}.ctl

	sed '1 s:'[0-9][0-9]_0p[0-9][0-9]/wrfout_GRADS_[0-9][0-9]-[0-9][0-9]_[0-9][0-9]_[0-9][0-9][0-9][0-9]_d[0-9][0-9].ctl':'${InputDir}':g' getTimeSeries.gs.template > getTimeSeries.gs
	sed '1 s:'[0-9][0-9]_0p[0-9]/wrfout_GRADS_[0-9][0-9]-[0-9][0-9]_[0-9][0-9]_[0-9][0-9][0-9][0-9]_d[0-9][0-9].ctl':'${InputDir}':g' getTimeSeries.gs.template > getTimeSeries.gs	

	sed '4 s:[0-9]\+.[0-9]\+:'${LAT}':g' getTimeSeries.gs > getTimeSeriesInt.gs
	sed '5 s:\-[0-9][0-9].[0-9]\+:'${LON}':g' getTimeSeriesInt.gs > getTimeSeries.gs

	#sed '11 s:[a-zA-Z]\+_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_:'${STATION}_${DI}_${MI}_${ANIO_SHORT}_':g' getTimeSeries.gs > getTimeSeriesInt.gs
	sed 's:[a-zA-Z]\+_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_:'${STATION}_${DI}_${MI}_${ANIO_SHORT}_':g' getTimeSeriesInt.gs > getTimeSeries.gs

	#Correr grads en modo batch para que haga las graficas, los EOD son para que no se quede trabado en la interfaz interactiva.

	echo 'SE VA A CORRER GRADS EN MODO BATCH PARA GENERAR LAS GRAFICAS'
	grads -bpcx getTimeSeries.gs 

	#Limpiar un poco
	mv *.txt ../timeSeries/${MES_INIT}_0p${RESOLUTION}/${STATION}/2015

	done

done
