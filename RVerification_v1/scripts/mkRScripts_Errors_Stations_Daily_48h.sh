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
INTERVALO=48

#Vamos a ir de RES>VAR>SEAS>STAT

rm *.Rout

if [ ! -d "verify_daily/" ]
then
	mkdir verify_daily
fi


if [ ! -d "verify_daily/${INTERVALO}" ]
then
	mkdir verify_daily/${INTERVALO}
fi

rm -rf verify_daily/${INTERVALO}/*

for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
do

	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
	mkdir verify_daily/${INTERVALO}/${VARIABLE}
		for MES in `ls $DIRECTORIO_MESES`
		do
		source $DIRECTORIO_MESES/$MES
			for DAY in `ls $DIRECTORIO_DIAS`
			do

				for STATION in `ls $DIRECTORIO_ESTACIONES`
				do

						sed 's/'RESOLUTION'/'${RESOLUTION}'/g' readStationVerify_daily.template > readStation.pre
						sed 's/'MES'/'${MES}'/g' readStation.pre > readStation.pre2
						sed 's/'STATION'/'${STATION}'/g' readStation.pre2 > readStation.pre
						sed 's/'VARIABLE'/'${VARIABLE}'/g' readStation.pre > readStation.pre2
						sed 's/'INTERVALO'/'${INTERVALO}'/g' readStation.pre2 > readStation.pre
						sed 's/'DAY'/'${DAY}'/g' readStation.pre > readStation.pre2
						sed 's/'NUES'/'${MESIM}'/g' readStation.pre2 > readStation.pre
						cat readStation.pre >> verify_daily/${INTERVALO}/R_scriptLines_0p${RESOLUTION}_${VARIABLE}_${MES}_${DAY}_${STATION}.R
						rm readStation.pre readStation.pre2
				done
			done
		done
			mv verify_daily/${INTERVALO}/*_${VARIABLE}_* verify_daily/${INTERVALO}/${VARIABLE}
			for MES in `ls $DIRECTORIO_MESES`
			do
				mkdir verify_daily/${INTERVALO}/${VARIABLE}/${MES}
				mv verify_daily/${INTERVALO}/${VARIABLE}/*_${MES}_* verify_daily/${INTERVALO}/${VARIABLE}/${MES}
				mkdir verify_daily/${INTERVALO}/${VARIABLE}/${MES}/${RESOLUTION}
				mv verify_daily/${INTERVALO}/${VARIABLE}/${MES}/*_0p${RESOLUTION}_* verify_daily/${INTERVALO}/${VARIABLE}/${MES}/${RESOLUTION}
			done
	done
	
done

find ./verify_daily/${INTERVALO}/ -name "*.R" -exec R CMD BATCH {} \;

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

