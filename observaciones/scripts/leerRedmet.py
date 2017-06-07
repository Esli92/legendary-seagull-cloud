#leerRedmet.py 
#Programa que extrae datos de Redmet en formato .xls para despues separar sus variables y escribirlas en diferentes archivos que pueden ser leidos con mas facilidad, sin encabezado. 
#Programador Oscar Jurado
#Fecha de creacion 13 de Junio 2016

#-------------Requisitos--------------------------------------------------------------
#Para correr el programa se necesita tener la utilidad de python xlrd,csv,numpy instalados. 
#Los datos de entrada son de la red de estaciones REDMET del sistema de monitoreo atmosferico del valle de mexico (SIMAT), en formato .xls
#Formato de archivos de tal manera que exista ../dataFiles/processed_redmet

#-------------Uso---------------------------------------------------------------------
#El programa se corre desde la terminal, poniendo el nombre del archivo a procesar como entrada
#Ejemplo:
#python leerRedmet.py altzo_feb_15.xls


#----------INICIO DEL PROGRAMA--------------------------------------------------------

#Comenzamos cargando la libreria xlrd, sys, csv, numpy
import xlrd as xr
import sys
import csv
import numpy as np
import math
#-----------ABRIR ARCHIVO----------------------------------
#leemos el archivo

cl_line = sys.argv
#EMA_file = '../15REDMET/2015TMP.xls'
EMA_file = cl_line[1]
open_EMA_file = xr.open_workbook(EMA_file)
#Y ahora la primer 'hoja' de nuestro archivo
ws = open_EMA_file.sheet_by_index(0)

#Variable del archivo
var_str_p = EMA_file.split('/')[-1]
var_str = var_str_p.split('.')[0]
var_str = var_str[-3:-1]

#Obtenemos numero de filas y columnas
num_filas=ws.nrows
num_cols=ws.ncols

#---------DEFINIR VARIABLES--------------------------------
year=[]
day=[]
month=[]
hour=[]
mins=[]
sec=[]
temp = []
windDir=[]
windSpd=[]
#RH=[]
pres=[]
rain=[]
rad=[]

#--------FECHA Y HORA---------------------------------------	
#Primer columna de EMAs
dates = ws.col_values(0)
dates = dates[1:num_filas]
hours = ws.col_values(1)
hours = hours[1:num_filas]

#Use xldate function to obtain a tuple of the dates from the MS format. Since year have only one value per file, we only store them once
for line in dates:
	year,mo,da,ho,mi,se = xr.xldate_as_tuple(line,open_EMA_file.datemode)
	month.append(mo)
	day.append(da)
#Restamos uno a la hora para ser consistente con la numeracion 0-23 de las EMAs
for line in hours:
	hour.append(line-1)

#--------OBTENER NOMBRES DE ESTACIONES----------------------
#La primer fila del archivo contiene los nombres de estaciones, los guardaremos en una lista

names = ws.row_values(0)
stations = names[2:num_cols]
#Ahora iremos recorriendo de estacion en estacion

for station in range(len(stations)):

	#Sumamos dos para tomar en cuenta que las primeras dos columnas son fecha y hora)
	station_data_year = ws.col_values(station+2)
	station_data_year = station_data_year[1:num_filas]
	
	#Ahora, queremos que salga un archivo por mes, por lo que haremos:
	year_months = range(1,13,1)
	for mes in year_months:
		
		dia_mes = []
		hour_mes = []
		hour_mesUTC = []
		station_data = []
		day_indx = []
		for dia in range(len(day)):
			if month[dia] == mes:
				k = 0
				dia_mes.append(day[dia])
				hour_mes.append(hour[dia])
				station_data.append(station_data_year[dia])

		#----------ARREGLANDO EL HORARIO PARA PASAR DE TIEMPO LOCAL A UTC------------------------
		#Ya que los datos estan en hora local, necesitaremos pasarlos a horario UTC. 
		#Generamos primero una lista con las horas del dia
		day_hours_UTC = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
		day_zone_UTC = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		day_hours_UTC5 = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3,4]
		day_zone_UTC5 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2]
		day_hours_UTC6 = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,0,1,2,3,4,5]
		day_zone_UTC6 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2]
		#--------TOMANDO EN CUENTA EL HORARIO DE VERANO 2015------------------------------------
		#En el Valle de Mexico se pasa de UTC-6 a UTC-5

		DST_mon_st = 4
		DST_day_st = 5
		DST_hou_st = 2

		DST_mon_en = 10
		DST_day_en = 25
		DST_hou_en = 2

		#En este ciclo veremos si estamos dentro de un mes de horario de verano o no (NO TOMAMOS EN CUENTA EL DIA TODAVIA)
		if mes >= DST_mon_st and mes <= DST_mon_en:
			#Este es para horario de verano		
			for hora in hour_mes:
				hour_indx = day_hours_UTC.index(hora)
				day_indx.append(day_zone_UTC5[hour_indx])
				hour_UTC = day_hours_UTC5[hour_indx]
				hour_mesUTC.append(hour_UTC)

		else:
			#Este es para horario normal
			for hora in hour_mes:
				hour_indx = day_hours_UTC.index(hora)
				hour_UTC = day_hours_UTC6[hour_indx]
				hour_mesUTC.append(hour_UTC)
				day_indx.append(day_zone_UTC6[hour_indx])


		#Ahora hay que arreglar los dias con el cambio de horarios
		k = 0
		for dia_sw in day_indx:
			if dia_sw == 2:
				if dia_mes[k] == max(dia_mes):
					dia_mes[k] = 1
				else:
					dia_mes[k] = dia_mes[k]+1
				k = k + 1
			else:
				k = k + 1
		#----------ESCRIBIENDO LOS ARCHIVOS--------------------------

		#Necesitaremos hacer matrices especificas para cada archivo, esto puede ser modificado de acuerdo a lo que necesitemos.
		statPrint_b = np.zeros((len(station_data),4))
		statPrint = statPrint_b.tolist()

		#Para tener VALOR | MES | DIA | HORA
		i = 0
		for dia_a in dia_mes:
			statPrint[i][0] = station_data[i]
			if i > 48 and dia_a == 1:
				statPrint[i][1] = mes+1
			else:
				statPrint[i][1] = mes
			statPrint[i][2] = dia_a
			statPrint[i][3] = hour_mesUTC[i]

			i = i + 1

		#Y ahora lo escribimos a un archivo
		#Prueba con el modulo csv
		name_str = stations[station]
		stat_str = "../dataFiles/processed_redmet_mensual/{}_{}_{}.txt".format(mes,name_str,var_str)

		stat_file = open(stat_str,"w")
		mywriter = csv.writer(stat_file, delimiter=',')
		for line in statPrint:
			mywriter.writerow(line)
		stat_file.close()









