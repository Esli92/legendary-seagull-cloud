#!/bin/bash

#Programa para plotear el Valle de Mexico junto con las estaciones EMA del SMN usando GMT.
#Programador: Oscar Jurado
#Fecha de creacion: 23 Junio 2016


#Comenzamos haciendo el mapa del valle de Mexico en proyeccion de Mercator

psfile=ValleMex.ps

rm $psfile

makecpt -Chot -T0/3000/100 > hotElevation.cpt

pscoast -R-100.5/-97.8/18.2/20.2 -JM6i -Df -P -B0.5g5 -G20/150/240 -N1/thickest -N2/thinnest -K > $psfile

psxy EMAS_ValleMex.xyz -R -J -ChotElevation.cpt -Sc0.5 -O  >> $psfile
