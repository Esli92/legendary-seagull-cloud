#mkDates4WRF.py
#Programa que genera datos de fechas para ser usados por WRF y bash. 
#Programador Oscar Jurado
#Fecha de creacion: 2016

#------------------Requisitos------------------------------------------------------------
#Directorio /fechas existente y de preferencia vacio. 

#-----------------Versiones---------------------------------------------------------------
#v1.0 Se crea el programa. 
#v1.2 Se genera la documentacion, se optimiza la portabilizacion

#----------------Problemas Conocidos-----------------------------------------------------
#Este programa funciona unicamente para hacer simulaciones de 48 horas, ya que los dias se recorren dos veces. 

#----------------Directorios Locales, cambiar si es necesario----------------------------

import sys
import csv

#Como la manera de obtener informacion cambia de python2 a 3 hacemos la siguiente prueba:

py3 = sys.version_info[0] > 2 #creates boolean value for test that Python major version > 2

if py3:
  year = input("Ingresa el anio de simulacion (yyyy)")
  month = input("Ingresa el mes a simular (mm)")
else:
  year = raw_input("Ingresa el anio de simulacion (yyyy)")
  month = raw_input("Ingresa el mes a simular (mm)")

year = str(year)
month = int(month)
year_str = ['01','02','03','04','05','06','07','08','09','10','11','12','01']
month_str_30 = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
month_str_31 = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
month_str_28 = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28']

month_str_30_p2 = ['03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','01','02']
month_str_31_p2 = ['03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','01','02']
month_str_28_p2 = ['03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','01','02']

if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
	month_str = month_str_31
	month_str_p2 = month_str_31_p2
	month_change = 30
elif month == 2:
	month_str = month_str_28
	month_str_p2 = month_str_28_p2
	month_change = 27
else:
	month_str = month_str_30 
	month_str_p2 = month_str_30_p2
	month_change = 29

i = 0
for day in month_str:
	AI_str = "AI={}".format(year)
	MI_str = "MI={}".format(year_str[month-1])
	DI_str = "DI={}".format(day)
	HI_str = "HI=00"
	AF_str = "AF={}".format(year)
	if int(day) < month_change:
		MF_str = "MF={}".format(year_str[month-1])
	else:
		MF_str = "MF={}".format(year_str[month])	
	DF_str = "DF={}".format(month_str_p2[i])
	HF_str = "HF=00"
	i = i + 1

	date_file_str = "fechas/{}_{}_{}_00.txt".format(year,day,year_str[month-1])
	date_file = open(date_file_str, 'w')
	date_file.write('#!/bin/bash')
	date_file.write("\n")
	date_file.write("\n")
	date_file.write(AI_str)
	date_file.write("\n")
	date_file.write(MI_str)
	date_file.write("\n")
	date_file.write(DI_str)
	date_file.write("\n")
	date_file.write(HI_str)
	date_file.write("\n")
	date_file.write("\n")
	date_file.write(AF_str)
	date_file.write("\n")
	date_file.write(MF_str)
	date_file.write("\n")
	date_file.write(DF_str)
	date_file.write("\n")
	date_file.write(HF_str)
	date_file.write("\n")


