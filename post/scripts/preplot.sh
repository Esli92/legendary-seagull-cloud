#!/bin/bash

#preplot.sh
#Programa que toma datos de entrada de grads (.ctl y .dat), genera un script .gs para graficar diversas variables y hace un gif animado.
#Programador Oscar Jurado
#Fecha de creacion: 31Mayo2016

#------------------Requisitos------------------------------------------------------------
#Script a seguir de grads, "plotWRF_template.gs". MUCHO CUIDADO AL MODIFICARLO, ya que varias lineas de sed estan ligadas a una linea en especifico de dicho programa. Modificar aqui si se cambia alla.
#Datos de salida generados con la otra utileria .pregrads.sh >> SI NO SE USO ENTONCES GENERAR DATOS DE ENTRADA DE LA SIGUIENTE MANERA:
#wrfout_GRADS_${DIA_INIT}-${DIA_FIN}_${MES_INIT}_${ANIO}_d${DOMINIO}.ctl 
#Script de animacion animarplots.sh NO MODIFICAR NUMEROS DE LINEA
#Estructura de directorios de tal manera que ../graficos exista, y que los datos de entrada esten en ../input/dirName/wrfout_GRADS---

#-----------------Versiones---------------------------------------------------------------
#v1.0 31/May/16 Se crea el programa. 
#v1.1 31/May/16 Se genera la documentacion y se hace mas verbal la salida

#----------------Problemas Conocidos-----------------------------------------------------

#----------------Directorios Locales, cambiar si es necesario----------------------------
SCRIPT_DIR=`pwd`

#En esta parte el usuario indica variables indicadoras de la simulacion a graficar
echo 'PREPLOT V1.1 -----> Indica los siguientes datos'
read -p 'Indica el dominio a graficar, 01 o 02: ' DOMINIO
read -p 'Indica la resolucion (50 o 25): ' RESOLUCION
read -p 'Indica el anio (yyyy): ' ANIO
read -p 'Indica el mes de inicio (mm): ' MES_INIT
read -p 'Indica el dia de inicio (dd): ' DIA_INIT
read -p 'Indica el dia de fin (dd): ' DIA_FIN

#En caso de que no exista, generar directorio
cp -r ../graficos/template ../graficos/${DIA_INIT}-${DIA_FIN}

#Modificar el plotWRF para que busque la entrada correcta. 
echo 'GENERANDO SCRIPT PARA GRADS'
sed '1 s:'../input/[0-9][0-9]_0p[0-9][0-9]/wrfout_GRADS_[0-9][0-9]-[0-9][0-9]_[0-9][0-9]_[0-9][0-9][0-9][0-9]_d[0-9][0-9].ctl':'../input/${MES_INIT}_0p${RESOLUCION}/wrfout_GRADS_${DIA_INIT}-${DIA_FIN}_${MES_INIT}_${ANIO}_d${DOMINIO}.ctl':g' plotWRF_template.gs > plotWRF${DIA_INIT}-${DIA_FIN}.gs_int
#Ahora para que los titulos de las graficas tengan el dia adecuado
sed '5 s/'[0-9][0-9]'/'${DIA_INIT}'/g' plotWRF${DIA_INIT}-${DIA_FIN}.gs_int > plotWRF${DIA_INIT}-${DIA_FIN}.gs

#En esta parte se modifican las salidas de las imagenes para que vayan en la carpeta adecuada
sed 's:'/[0-9][0-9]-[0-9][0-9]/':'/${DIA_INIT}-${DIA_FIN}/':mg' plotWRF${DIA_INIT}-${DIA_FIN}.gs > plotWRF${DIA_INIT}-${DIA_FIN}.gs_int
#sed '22 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs > plotWRF${DIA_INIT}-${DIA_FIN}.gs_int
#sed '31 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs_int > plotWRF${DIA_INIT}-${DIA_FIN}.gs
#sed '39 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs > plotWRF${DIA_INIT}-${DIA_FIN}.gs_int
#sed '47 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs_int > plotWRF${DIA_INIT}-${DIA_FIN}.gs
#sed '54 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs > plotWRF${DIA_INIT}-${DIA_FIN}.gs_int
#sed '62 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs_int > plotWRF${DIA_INIT}-${DIA_FIN}.gs
#sed '70 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs > plotWRF${DIA_INIT}-${DIA_FIN}.gs_int
#sed '86 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs_int > plotWRF${DIA_INIT}-${DIA_FIN}.gs
#sed '78 s:'/28-30/':'/${DIA_INIT}-${DIA_FIN}/':g' plotWRF${DIA_INIT}-${DIA_FIN}.gs > plotWRF${DIA_INIT}-${DIA_FIN}.gs_int

#Limpiar un poco
cp plotWRF${DIA_INIT}-${DIA_FIN}.gs_int plotWRF${DIA_INIT}-${DIA_FIN}.gs
rm *.gs_int

#Correr grads en modo batch para que haga las graficas, los EOD son para que no se quede trabado en la interfaz interactiva.
echo 'SE VA A CORRER GRADS EN MODO BATCH PARA GENERAR LAS GRAFICAS'
grads -blc plotWRF${DIA_INIT}-${DIA_FIN}.gs <<EOD

EOD

echo 'GRADS HA TERMINADO DE GRAFICAR. GENERANDO GIFS ANIMADOS'
#Ahora se modifica el animarplots para que busque en la carpeta adecuada, y que los titulos de las imagenes digan los dias adecuados
sed 's:'/[0-9][0-9]-[0-9][0-9]':'/${DIA_INIT}-${DIA_FIN}':mg' animarplots.sh > animarplots1.sh
sed 's:'_[0-9][0-9]-[0-9][0-9].gif':'_${DIA_INIT}-${DIA_FIN}.gif':mg' animarplots1.sh > animarplots2.sh


#Se corre el programa de animar
source animarplots2.sh

#Limpiando un poco
cd $SCRIPT_DIR

rm animarplots1.sh animarplots2.sh

cd ../graficos/${DIA_INIT}-${DIA_FIN}

#Poner todas las animaciones en un mismo directorio
rm -rf animaciones
mkdir animaciones

find . -name "*.gif" -exec cp {} animaciones \;

echo 'EL PROGRAMA HA TERMINADO. VE A ../graficas PARA ENCONTRAR LAS SALIDAS'
