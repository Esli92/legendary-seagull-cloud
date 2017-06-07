#!/bin/bash
#PBS -l nodes=2:ppn=16
#PBS -N WPS_WRF_Month

#run_Unificado
#Program to automatize GFS data downloads, both resolutions. Needs date input.
#Programmer: Oscar Jurado (ojurado@atmosfera.unam.mx)
#Program created on: June 9 2016

#Revisions:
#v1.0 9/Jun/16 Created program. Unified three diferent scripts: GFS_0p5_downl.sh; run_WPS_WRF_ioa2_8.sh; pregrads.sh
#v2.0 17/Jun/16 Created auxiliary program in python to create dates and use in the script
#v3.0 21/Jun/16 Added part to download 0p25 GFS input data, but need environment variable $RESOLUTION to work. 
#Use: ./run_Unificado.sh
#User will be prompt for input regarding dates of simulation.
#Example: ./run_Unificado.sh

#-------------------------------------------------------------------------------------
#-----------------GLOBAL INPUT--------------------------------------------------------
#-------------------------------------------------------------------------------------

DIRECTORIO_FECHAS=./GFSfechas
read -p 'Indica la resolucion de simulacion, 50 o 25: ' RESOLUTION

#-------------------------------------------------------------------------------------
#-----------------DATE INPUT----------------------------------------------------------
#-------------------------------------------------------------------------------------

for FECHA in `ls $DIRECTORIO_FECHAS`
do

	source $DIRECTORIO_FECHAS/$FECHA
	contador=1
	#From date file, we get:
	#AI=2015
	#MI=05
	#DI=30
	#HI=00
	#AF=2015
	#MF=06
	#DF=01
	#HF=00

	Year=$AI
	Year_st=$AI
	Year_en=$AF
	Month=$MI
	Month_en=$MF
	Day_st=$DI
	Day=$DI
	Day_en=$DF
	Hour=$HI
	Forecast=48


	#--------------------------------------------------------------------------------------
	#----- ------------GFS DATA DOWNLOAD---------------------------------------------------
	#--------------------------------------------------------------------------------------


	#Test if we want 0p5 or 0p25 input data

	if [ $RESOLUTION -eq 50 ]; then

	#--------------------------------------------------------------------------------------
	#----- ------------GFS DATA DOWNLOAD 0p50----------------------------------------------
	#--------------------------------------------------------------------------------------
	DATA_DIR=exp02_0p5
	cd /storage/ioa/esli/GFS_DATA/${DATA_DIR}
	rm gfs_4_*
	#AUTOMATIC SECTION
	echo `date`: Descargando archivos de entrada
	fHour=0

	while [ $fHour -lt $Forecast ]; do

		if [ $fHour -lt 10 ]; then
		        wget ftp://nomads.ncdc.noaa.gov/GFS/Grid4/${Year}${Month}/${Year}${Month}${Day}/gfs_4_${Year}${Month}${Day}_${Hour}00_00${fHour}.grb2
		else
		        wget ftp://nomads.ncdc.noaa.gov/GFS/Grid4/${Year}${Month}/${Year}${Month}${Day}/gfs_4_${Year}${Month}${Day}_${Hour}00_0${fHour}.grb2
		fi

	let fHour=$fHour+3
	done

	#Last file download:
	wget ftp://nomads.ncdc.noaa.gov/GFS/Grid4/${Year}${Month}/${Year}${Month}${Day}/gfs_4_${Year}${Month}${Day}_${Hour}00_0${fHour}.grb2

	rm -rf ${Day}${Month}${Year}
	mkdir ${Day}${Month}${Year}
	mv gfs_4_${Year}${Month}${Day}_${Hour}00* ${Day}${Month}${Year}

	#--------------------------------------------------------------------------------------
	#----- ------------GFS DATA DOWNLOAD 0p25----------------------------------------------
	#--------------------------------------------------------------------------------------	
	elif [ $RESOLUTION -eq 25 ]; then
	
	DATA_DIR=exp02_0p25
	cd /storage/ioa/esli/GFS_DATA/${DATA_DIR}
	opts="-N"
	passwd=9cfsrz687yrv
	num_chars=`echo "$passwd" |awk '{print length($0)}'`
	if [ $num_chars -eq 0 ]; then
	 echo "You need to set your password before you can continue"
	 echo " see the documentation in the script"
	 #exit 1
	 fi
	num=1
	newpass=""
	while [ $num -le $num_chars ]
	 do
	 c=`echo "$passwd" |cut -b${num}-${num}`
	 if [ "$c" == "&" ]; then
	 c="%26";
	 elif [ "$c" == "?" ]; then
	 c="%3F"
	 elif [ "$c" == "=" ]; then
	 c="%3D"
	 fi
	 newpass="$newpass$c"
	((num++))
	 done
	export passwd="$newpass"
	export cert_opt=""
	if [ "$passwd" == "xxxxxx" ]; then
	 echo "You need to set your password before you can continue"
	 echo " see the documentation in the script"
	 exit
	fi
	#
	# authenticate - NOTE: You should only execute this command ONE TIME.
	# Executing this command for every data file you download may cause
	# your download privileges to be suspended.
	#To ensure this doesnt happen we use a special counter
	wget $cert_opt -O auth_status.rda.ucar.edu --save-cookies auth.rda.ucar.edu.$$ --post-data="email=ojurado@ciencias.unam.mx&passwd=$passwd&action=login" https://rda.ucar.edu/cgi-bin/login

	# download the file(s)
	# NOTE: if you get 403 Forbidden errors when downloading the data files, check
	# the contents of the file 'auth_status.rda.ucar.edu'
	rm gfs.*
	#AUTOMATIC SECTION
	echo `date`: Descargando archivos de entrada
	fHour=0

	while [ $fHour -lt $Forecast ]; do

		if [ $fHour -lt 10 ]; then
		        wget $cert_opt $opts --load-cookies auth.rda.ucar.edu.$$ http://rda.ucar.edu/data/ds084.1/${Year}/${Year}${Month}${Day}/gfs.0p25.${Year}${Month}${Day}${Hour}.f00${fHour}.grib2 
		else
		        wget $cert_opt $opts --load-cookies auth.rda.ucar.edu.$$ http://rda.ucar.edu/data/ds084.1/${Year}/${Year}${Month}${Day}/gfs.0p25.${Year}${Month}${Day}${Hour}.f0${fHour}.grib2
		fi

	let fHour=$fHour+3
	done

	#Last file download:
	wget $cert_opt $opts --load-cookies auth.rda.ucar.edu.$$ http://rda.ucar.edu/data/ds084.1/${Year}/${Year}${Month}${Day}/gfs.0p25.${Year}${Month}${Day}${Hour}.f0${fHour}.grib2

	#
	# clean up
	rm auth.rda.ucar.edu.* auth_status.rda.ucar.edu
	rm -rf ../../input/${Day}${Month}${Year}
	mkdir ../../input/${Day}${Month}${Year}
	mv gfs.0p25.${Year}${Month}${Day}${Hour}.* ../../input/${Day}${Month}${Year}
	fi

done

