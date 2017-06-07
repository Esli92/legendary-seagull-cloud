#!/bin/bash

#mkWRF_Station_Points.sh

#This program takes lat lon info from met ground stations, uses such info to locate the nearest index point in a WRF grid and returns the lat lon coordinate of the WRF grid points in a text file. 
#Programmer Oscar Jurado (ojurado@ciencias.unam.mx)
#Creation date: 21-Feb-2017

#------------------Requisites------------------------------------------------------------
#WRF output file containing XLAT,XLONG.
#The station coordinate files should be in ../dataFiles/estaciones they should have the station name as file name, and a line with LAN and LON environment variables. 
#NCL MUST be installed
#transpose-awk.sh script in same dir
#-----------------Version---------------------------------------------------------------
#v1.0 20/Nov/16 Program is created
#v2.0 22/Nov/16 Python is changed for CDO and AWK, that are much faster.
#----------------Known issues-----------------------------------------------------------
#Very slow when dealing with a lot of met data. (fixed in v2.0)
#Requires that user knows nuber of values per timestep and manualy changes for file. 

#-----------------Local directories----------------------------------------------------- 
SCRIPT_DIR=`pwd`
STATION_DIR=../dataFiles/estaciones

#----------------Dependencies used-----------------------------------------------------


#-----------------BEGIN PROGRAM--------------------------------------------------------

rm LatLonStations.txt 
rm LatLonStations.xyt
rm LatLonStat
rm LatLonStations_final.txt

for STATION in `ls $STATION_DIR`
do

source $STATION_DIR/$STATION

sed '8 s:[0-9][0-9].[0-9][0-9]:'${LAT}':g' FindWRFIndex.template > FindWRFIndex.temp
sed '9 s:-[0-9][0-9].[0-9][0-9]:'${LON}':g' FindWRFIndex.temp > FindWRFIndex.ncl 

ncl FindWRFIndex.ncl

./transpose-awk.sh LatLonStations.txt > LatLonStations.xyt

awk -v titulo="$STATION" '{print $0, titulo}' LatLonStations.xyt >> LatLonStat


done

awk -F" " -v OFS=',' '{print $1,$2,$3}' LatLonStat > LatLonStations_final.txt
