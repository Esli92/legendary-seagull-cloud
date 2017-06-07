#!/bin/bash

#preplot.sh
#Programa que toma datos de entrada de WRF crudos, modifica los parametros necesarios de ARWpost y ejecuta ARWpost
#Programador Oscar Jurado
#Fecha de creacion: 31Mayo2016

#------------------Requisitos------------------------------------------------------------
#Script a seguir de ARWpost, "namelist.ARWpost.template". MUCHO CUIDADO AL MODIFICARLO, ya que varias lineas de sed estan ligadas a una linea en especifico de dicho programa. Modificar aqui si se cambia alla.
#Datos de salida generados con WRF
#Plantilla namelist.ARWpost.template existente 
#Estructura de directorios adecuada al programa

#-----------------Versiones---------------------------------------------------------------
#v1.0 31/May/16 Se crea el programa. 
#v1.2 31/May/16 Se genera la documentacion, se optimiza la portabilizacion

#----------------Problemas Conocidos-----------------------------------------------------

#----------------Directorios Locales, cambiar si es necesario----------------------------
ARWPOST=/home/alumno/Documentos/WRF/codigoFuente/ARWpost
#Directorio de datos de entrada
InputDir=~/Documentos/WRF/experimentos/verificacion/salidas/exp02_abr/salidas0p5_v3.8

read -p 'Indica el dominio a graficar, 01 o 02: ' DOMINIO
read -p 'Indica el anio: ' ANIO
read -p 'Indica el mes de inicio: ' MES_INIT
read -p 'Indica el mes de fin: ' MES_FIN
read -p 'Indica el dia de inicio: ' DIA_INIT
read -p 'Indica el dia de fin: ' DIA_FIN
read -p 'Indica la hora de inicio de simulacion: ' HORA_INIT 
read -p 'Indica la hora de fin para graficar: ' HORA_FIN

cd $ARWPOST

rm wrfout_*


ln -s ${InputDir}/wrfout_d${DOMINIO}_${ANIO}-${MES_INIT}-${DIA_INIT}_${HORA_INIT}:00:00 .

cp namelist.ARWpost namelist.ARWpost.Backup

sed '2 s/'20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]:00:00'/'${ANIO}-${MES_INIT}-${DIA_INIT}_${HORA_INIT}:00:00'/g' namelist.ARWpost.template > namelist_int.ARWpost

sed '3 s/'20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]:00:00'/'${ANIO}-${MES_FIN}-${DIA_FIN}_${HORA_FIN}:00:00'/g' namelist_int.ARWpost > namelist_int2.ARWpost

sed '10 s:'./wrfout_d0[0-9]_':'./wrfout_d${DOMINIO}_':g' namelist_int2.ARWpost > namelist_int3.ARWpost

sed '11 s:'~/Documentos/WRF/experimentos/verificacion/post/input/wrfout_GRADS_[0-9][0-9]-[0-9][0-9]_[0-9][0-9]_[0-9][0-9][0-9][0-9]_d[0-9][0-9]':'~/Documentos/WRF/experimentos/verificacion/post/input/wrfout_GRADS_${DIA_INIT}-${DIA_FIN}_${MES_INIT}_${ANIO}_d${DOMINIO}':g' namelist_int3.ARWpost > namelist.ARWpost

./ARWpost.exe
