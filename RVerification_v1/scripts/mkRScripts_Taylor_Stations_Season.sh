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
DIRECTORIO_BALSAS=../../observaciones/dataFiles/gruposEstaciones/CuBal
DIRECTORIO_ESTACIONES=../../observaciones/dataFiles/estaciones
DIRECTORIO_SEASONS=../../observaciones/scripts/seasons
DIRECTORIO_RESOLUCIONES=../../observaciones/scripts/resoluciones
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables_cont

#Vamos a ir de RES>VAR>SEAS>STAT

rm readStation/taylor/*.R

figlet TAYLOR DIAGRAM
echo "GENERATING R SCRIPTS FOR THE TAYLOR DIAGRAMS, PLEASE WAIT!"
for SEASON in `ls $DIRECTORIO_SEASONS`
do

	for VARIABLE in `ls $DIRECTORIO_VARIABLES`
	do
		
			RESOLUTION=5
			
			TARGET=readStation/taylor/R_scriptLines_${VARIABLE}_${SEASON}.R
			cat taylor_header_${VARIABLE}.h > $TARGET
			sed 's/'RESOLUTION'/'${RESOLUTION}'/g' $TARGET > ${TARGET}.p
			sed 's/'SEASON'/'${SEASON}'/g' ${TARGET}.p > $TARGET
			sed 's/'VARIABLE'/'${VARIABLE}'/g' ${TARGET} > ${TARGET}.p
			cat ${TARGET}.p > $TARGET
			rm ${TARGET}.p

		for STATION in `ls $DIRECTORIO_ESTACIONES`
		do

			for RESOLUTION in `ls $DIRECTORIO_RESOLUCIONES`
			do

				sed 's/'RESOLUTION'/'${RESOLUTION}'/g' readStationTaylor.template > readStation.pre
				sed 's/'SEASON'/'${SEASON}'/g' readStation.pre > readStation.pre2
				sed 's/'STATION'/'${STATION}'/g' readStation.pre2 > readStation.pre
				sed 's/'VARIABLE'/'${VARIABLE}'/g' readStation.pre > readStation.pre2
				if [ -e "${DIRECTORIO_BALSAS}/${STATION}" ]
				then
					sed 's/'SHAPE'/'17'/g' readStation.pre2 > readStation.pre
				else
					sed 's/'SHAPE'/'19'/g' readStation.pre2 > readStation.pre
				fi

				if [ ${RESOLUTION} == 25 ]
				then
					sed 's/'COLOR'/'red'/g' readStation.pre > readStation.pre2
				else
					sed 's/'COLOR'/'blue'/g' readStation.pre > readStation.pre2
				fi
				cat readStation.pre2 >> $TARGET
				rm readStation.pre readStation.pre2
			done
		done
		tail -2 taylor_tail.txt >> $TARGET
	done
done

echo "THE SCRIPTS ARE READY, FIND THEM IN ReadStation/taylor"
echo "I WILL NOW ATTEMPT TO RUN THE SCRIPTS USING R CMD BATCH, PLEASE WAIT!!. THIS OPERATION COULD TAKE A FEW MINUTES"
rm *.Rout

echo "Here, have a random quote while you wait"
cowsay -f "$(ls /usr/share/cows/ | sort -R | head -1)" "$(fortune -s)"

find ./readStation/taylor -name "*.R" -exec R CMD BATCH {} \;


mv *.Rout plots/out

cd plots/taylor

for FILE in `ls`
do
	convert ${FILE} -fuzz 1% -trim +repage ${FILE}
done

figlet DONE

