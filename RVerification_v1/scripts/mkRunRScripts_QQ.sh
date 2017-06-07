#!/bin/bash

#mkRunQQ
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
DIRECTORIO_VARIABLES=../../observaciones/dataFiles/variables_cont
INTERVALO=l24


figlet QQ PLOTS

echo "I WILL NOW ATTEMPT TO RUN THE SCRIPTS USING R CMD BATCH, PLEASE WAIT!!. THIS OPERATION COULD TAKE A FEW MINUTES"


echo "Here, have a random quote while you wait"
cowsay -f "$(ls /usr/share/cows/ | sort -R | head -1)" "$(fortune -s)"

find ./readStation/qq -name "*.R" -exec R CMD BATCH {} \;


figlet DONE 
