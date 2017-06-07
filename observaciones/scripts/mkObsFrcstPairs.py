#mkObsFrcstPair.py
#Programa que toma datos procesados de estaciones (EMA,REDMET) asi como series de tiempo de WRF y genera un archivo de pares observacion-pronostico para ser usado en la verificacion 
#Programador Oscar Jurado
#Fecha de creacion 5 de Julio 2016

#-------------Requisitos--------------------------------------------------------------
#Para correr el programa se necesita tener la utilidad de python xlrd,csv,numpy instalados. 
#Los datos de entrada deben provenir de archivos procesados con programa leerEma.py, leerRedmet.py y mkTimeSeriesWRF.sh 
#Formato de archivos de tal manera que exista ../dataFiles/pairs

#-------------Uso---------------------------------------------------------------------
#El programa se corre desde la terminal, poniendo el nombre de los archivos como entrada en este orden: 1)Archivo de estacion 2)Archivo WRF
#Ejemplo:
#python mkObsFrcstPair.py ACO_TM.txt CCA_27_TEMP.txt
#Se recomienda usar en conjunto con la utileria 

#------------Versiones----------------------------------------------------------------
#v1.0 5/Jul/2016 Se crea el programa. 


#-----------Problemas conocidos--------------------------------------------------------
#b01 -- El programa requiere que el archivo de inicio wrf tenga un nombre muy particular, el cual creo que aun no esta automatizado

#----------INICIO DEL PROGRAMA--------------------------------------------------------

#Comenzamos cargando la libreria sys, csv, numpy
import sys
import csv
import numpy as np

#-----------ABRIR ARCHIVO----------------------------------
#leemos el archivo

cl_line = sys.argv

#Lineas usadas en el debug 
#OBS_file_name = 'altzom_TM.txt'
#WRF_file_name = 'altzom_14_12_15_TM.txt'
	
OBS_file_name = cl_line[1]
WRF_file_name = cl_line[2]

#Abrir los archivos
OBS_file = open(OBS_file_name, "r")
WRF_file = open(WRF_file_name, "r")
#Y ahora lo pasamos a una lista
obs_lines = OBS_file.readlines()
wrf_lines = WRF_file.readlines()

#Cerramos el archivo ya que no lo necesitamos
OBS_file.close()
WRF_file.close()

#Guardamos la variable para el futuro, quitando primero el nombre de estacion y luego el .txt
var_name_str = OBS_file_name.split('_')
var_name = var_name_str[1]
var_name_str = var_name.split('.')
var_name = var_name_str[0]

#Quitamos el encabezado del archivo WRF
wrf_num = len(wrf_lines)
wrf_lines = wrf_lines[1:wrf_num]

#Debemos ahora pasar el contenido de las listas de strings a flotantes

obs_list = []
for line in obs_lines:
	obs_lines_split = [x.strip() for x in line.split(',')]
	obs_lines_split = [float(i) for i in obs_lines_split]
	obs_list.append(obs_lines_split)

wrf_list = []
for line in wrf_lines:
	wrf_lines_split = [x.strip() for x in line.split(',')]
	wrf_lines_split = [float(i) for i in wrf_lines_split]
	wrf_list.append(wrf_lines_split)


#Ahora, buscamos en donde la primer fecha del archivo WRF concuerda con el de observaciones. 
#para recordar los archivos estan de la siguiente manera:
#OBSERVACIONES: dato,	mes,	dia,	hora
#WRF:		hora,	lon,	lat,	dato

#Para obtener el mes y dia del archivo WRF usaremos la informacion del nombre de archivo. 
#Nos aprovechamos de que tiene formato dd_mm_yy
wrf_date = WRF_file_name.split('_')
#Quitamos lo que no es un numero para poder convertirlo a flotantes
#Primero guardamos el nombre de la estacion
wrf_station_name = wrf_date[0]
wrf_station_name = wrf_station_name[2:len(wrf_station_name)]
wrf_date = wrf_date[1:4]
wrf_date = [float(i) for i in wrf_date]
#Tenemos ahora en wrf_date = [dd, mm, yy]
wrf_month = wrf_date[1]
wrf_day = wrf_date[0]

#Busquemos entonces donde se empalma el mes

ind = 0
for line in obs_list:
	if wrf_month != line[1]:
		ind = ind + 1
	else:
		break
	
#Rehacemos para tener solo los datos que queremos
obs_mes_in = obs_list[ind:len(obs_list)+1]

#El siguiente loop buscara en el valor de mes para cada linea de datos viendo que sea el mismo que los datos wrf. Cuando esto ocurra, se reescribira la variable obs_mes con solo estos valores.
fid = 0
try:
	while wrf_month == obs_mes_in[fid][1]:
		fid = fid + 1
except:
	pass
obs_mes = obs_mes_in[0:fid]

#Ahora ajustamos el dia

#El siguiente loop buscara en el valor de dia para cada linea de datos viendo que sea el mismo que los datos wrf. Cuando esto ocurra, se reescribira la variable obs_day con solo estos valores.
did = 0
while wrf_day != obs_mes[did][2]:
	did = did + 1
 
obs_day = obs_mes[did:len(obs_mes)+1]

#Llegamos a una encrucijada, ya que existen varias maneras de acomodar los datos en este punto. 

#Primer metodo, empalmando solo las primeras 24 horas:

#Considerando que en vez de hora 24 hay hora 0, tomamos hasta la hora 23
horas_empalme = 23

#El siguiente loop buscara en el valor de hora para cada linea de datos viendo hasta donde son las primeras 24 horas. Cuando esto ocurra, se reescribira la variable obs_day con solo estos valores.
dfd = 0
while horas_empalme != obs_day[dfd][3]:
	dfd = dfd + 1

obs_day = obs_day[0:dfd+1]

#Para evitar problemas futuros, hacemos lo mismo con los datos WRF, con tal de ser consistentes.
dfh = 0
while horas_empalme != wrf_list[dfh][0]:
	dfh = dfh + 1

wrf_day_sim = wrf_list[0:dfh+1]

#Es momento ya de hacer el empalme entre archivos. Queremos que tengan el siguiente formato final:
#MES DIA HORA OBSERVACION PRONOSTICO 

pair_list_b = np.zeros((len(obs_day),5))
pair_list = pair_list_b.tolist()

w = 0
for line in obs_day:
	pair_list[w][0] = wrf_month
	pair_list[w][1] = wrf_day
	pair_list[w][2] = line[3]
	pair_list[w][3] = line[0]
	pair_list[w][4] = wrf_day_sim[w][3]
	w = w + 1

wrf_day = int(wrf_day)
wrf_month = int(wrf_month)

#Ahora escribimos esto a un archivo nuevo
file_str = "../../../../../observaciones/dataFiles/pares/24h/ObsFct_Pairs_{}_{}_{}_{}_15.txt".format(var_name,wrf_station_name,wrf_day+10,wrf_month)

#DEBUG_LINE:
#file_str = "../dataFiles/pares/24h/ObsFct_Pairs_{}_{}_{}_{}_15.txt".format(var_name,wrf_station_name,wrf_day,wrf_month)

pair_file = open(file_str,'w')
mywriter = csv.writer(pair_file, delimiter=',')

header_str = ["MES","DIA","HORA","OBSERVACION","PRONOSTICO"]
mywriter.writerow(header_str)

for line in pair_list:
	mywriter.writerow(line)
pair_file.close()








