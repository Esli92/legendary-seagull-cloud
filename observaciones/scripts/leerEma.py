#leerEma.py 
#Programa que extrae datos de EMA's en formato .xls para despues separar sus variables y escribirlas en diferentes archivos que pueden ser leidos con mas facilidad, sin encabezado. 
#Programador Oscar Jurado
#Fecha de creacion 7 de Junio 2016

#-------------Requisitos--------------------------------------------------------------
#Para correr el programa se necesita tener la utilidad de python xlrd,csv,numpy instalados. 
#Los datos de entrada son de Estaciones Automatizadas (EMA) del Servicio Meteorologico Nacional de Mexico, en formato .xls
#Formato de archivos de tal manera que exista ../dataFiles/processed

#-------------Uso---------------------------------------------------------------------
#El programa se corre desde la terminal, poniendo el nombre del archivo a procesar como entrada
#Ejemplo:
#python leerEma.py altzo_feb_15.xls
#Se recomienda usar en conjunto con la utileria 'processAll' para facilitar su uso.

#------------Versiones----------------------------------------------------------------
#v1.0 7/Jun/2016 Se crea el programa. 
#v2.0 8/Jun/2016 Se arregla un error en donde si el archivo de entrada tenia celdas vacias el programa no podia ejecutarse. Dichas celdas ahora se reemplazan con -99
#v2.1 8/Jun/2016 Se agrega presion a las variables de salida, a los nombres de archivos de salida ahora se agrega el mes en numero al principio
#v2.2 13/Jun/2016 Se arregla un problema en donde la presion era imprimida con una columna de mas. 

#-----------Problemas conocidos--------------------------------------------------------
#La precipitacion acumulada no toma en cuenta el primer valor del archivo, por ser de una hora correspondiente al mes anterior. 
#El folder ../dataFiles/processed debe existir para que no truene el programa

#----------INICIO DEL PROGRAMA--------------------------------------------------------

#Comenzamos cargando la libreria xlrd, sys, csv, numpy
import xlrd as xr
import sys
import csv
import numpy as np
#-----------ABRIR ARCHIVO----------------------------------
#leemos el archivo

cl_line = sys.argv
#EMA_file = 'altzo_feb_15.xls'
EMA_file = cl_line[1]
open_EMA_file = xr.open_workbook(EMA_file)
#Y ahora la primer 'hoja' de nuestro archivo
ws = open_EMA_file.sheet_by_index(0)

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

#--------ARREGLANDO DATOS FALTANTES------------------------
#Los archivos a veces contienen celdas vacias, lo que causara errores en el programa. Por esto es necesario cambiar los vacios por un valor generico, en este caso -99 para indicar que no hay valor

for row in range(1,num_filas,1):
	row_2_test = ws.row_types(row,1,10)
	col = 1
	for test in row_2_test:
		if test == 0:
			#ws.put_cell(row,col,xr.XL_CELL_NUMBER, -99, ws.cell_xf_index(row,col))
			ws._cell_types[row][col] = xr.XL_CELL_NUMBER
			ws._cell_values[row][col] = -99.0
			col = col+1
		else:
			col = col+1
			

#--------FECHA Y HORA---------------------------------------	
#Primer columna de EMAs
dates = ws.col_values(0)
dates = dates[1:num_filas]

#Use xldate function to obtain a tuple of the dates from the MS format. Since year and month have only one value per file, we only store them once
for line in dates:
	year,month,da,ho,mi,se = xr.xldate_as_tuple(line,open_EMA_file.datemode)
	day.append(da)
	hour.append(ho)
	mins.append(mi)

#Ya que WRF saca datos horarios, nos es de interes obtener valores cada hora. Para esto hacemos un indice que nos diga donde estan los datos horarios.
HourIndex = [i for i,x in enumerate(mins) if x == 0]
#Redefiniendo dias y todo eso con el nuevo indice
day = [day[i] for i in HourIndex]
hour = [hour[i] for i in HourIndex]
mins = [mins[i] for i in HourIndex]

#--------TEMPERATURA---------------------------------------
#Guardamos primero todos los datos de temperatura
tempTodos = ws.col_values(5)
#Quitamos el encabezado 
tempTodos = tempTodos[1:num_filas]
#Y nos quedamos solo con los valores que queremos
temp = [tempTodos[i] for i in HourIndex]

#---------VIENTO--------------------------------------------
#Guardamos datos de direccion y rapidez
DirTodos = ws.col_values(1)
RapTodos = ws.col_values(3)
#Quitando el encabezado
DirTodos = DirTodos[1:num_filas]
RapTodos = RapTodos[1:num_filas]
#Quitando valores no horarios
windDir = [DirTodos[i] for i in HourIndex]
windSpd = [RapTodos[i] for i in HourIndex]

#----------RADIACION------------------------------------------
#Guardamos todos los datos
RadTodos = ws.col_values(9)
#Quitando encabezado
RadTodos = RadTodos[1:num_filas]
#Quitando valores no horarios
rad = [RadTodos[i] for i in HourIndex]

#----------PRESION---------------------------------------------
#Guardamos todos los datos
PresTodos = ws.col_values(7)
#Quitando encabezado
PresTodos = PresTodos[1:num_filas]
#Quitando valores no horarios
pres = [PresTodos[i] for i in HourIndex]


#----------PRECIPITACION ACUMULADA-----------------------------
#Guardamos todos los datos
RainTodos = ws.col_values(8)
#Quitando encabezado
RainTodos = RainTodos[1:num_filas]
#Ahora, la precipitacion es un caso especial, porque debemos tomar el acumulado horario, no el valor instantaneo
#El siguiente loop va iterando en todos los indices horarios, para armar una lista intermedia para sumar valores, no toma en cuenta el primer valor por ser de una hora anterior al 2015.
for i in range(len(HourIndex)-1):
	PrecAcum = 0
	for index in range(HourIndex[i]+1,HourIndex[i+1]+1,1):
		PrecAcum = PrecAcum + RainTodos[index]
		if PrecAcum < 0:
			PrecAcum = -99
	rain.append(PrecAcum)


#----------ESCRIBIENDO LOS ARCHIVOS--------------------------

#Necesitaremos hacer matrices especificas para cada archivo, esto puede ser modificado de acuerdo a lo que necesitemos.
tempPrint_b = np.zeros((len(temp),4))
tempPrint = tempPrint_b.tolist()

rainPrint_b = np.zeros((len(rain),4))
rainPrint = rainPrint_b.tolist()

dirPrint_b = np.zeros((len(temp),4))
dirPrint = dirPrint_b.tolist()

rapPrint_b = np.zeros((len(temp),4))
rapPrint = tempPrint_b.tolist()

radPrint_b = np.zeros((len(temp),4))
radPrint = radPrint_b.tolist()

presPrint_b = np.zeros((len(temp),4))
presPrint = presPrint_b.tolist()

#Para tener VALOR | ANIO | MES | DIA 
i = 0
for dia in day:
	tempPrint[i][0] = temp[i]
	tempPrint[i][1] = month
	tempPrint[i][2] = dia
	tempPrint[i][3] = hour[i]
		
	dirPrint[i][0] = windDir[i]
	dirPrint[i][1] = month
	dirPrint[i][2] = dia
	dirPrint[i][3] = hour[i]
	
	rapPrint[i][0] = windSpd[i]
	rapPrint[i][1] = month
	rapPrint[i][2] = dia
	rapPrint[i][3] = hour[i]
	
	radPrint[i][0] = rad[i]
	radPrint[i][1] = month
	radPrint[i][2] = dia
	radPrint[i][3] = hour[i]

	presPrint[i][0] = pres[i]
	presPrint[i][1] = month
	presPrint[i][2] = dia
	presPrint[i][3] = hour[i]
	
	i = i + 1

i = 0
for precip in rain:
	rainPrint[i][0] = precip
	rainPrint[i][1] = month
	rainPrint[i][2] = day[i]
	rainPrint[i][3] = hour[i]
	i = i + 1

#Y ahora lo escribimos a un archivo
#Prueba con el modulo csv
name_str_p = EMA_file.split('/')[-1]
name_str = name_str_p.split('.')[0]
temp_str = "../dataFiles/processed/{}_{}_temp.txt".format(month,name_str)
rain_str = "../dataFiles/processed/{}_{}_rain.txt".format(month,name_str)
dir_str = "../dataFiles/processed/{}_{}_windDir.txt".format(month,name_str)
rap_str = "../dataFiles/processed/{}_{}_windSpd.txt".format(month,name_str)
rad_str = "../dataFiles/processed/{}_{}_radiation.txt".format(month,name_str)
pres_str = "../dataFiles/processed/{}_{}_pressure.txt".format(month,name_str)


temp_file = open(temp_str,"w")
mywriter = csv.writer(temp_file, delimiter=',')
for line in tempPrint:
	mywriter.writerow(line)
temp_file.close()


rain_file = open(rain_str,"w")
mywriter = csv.writer(rain_file, delimiter=',')
for line in rainPrint:
	mywriter.writerow(line)
rain_file.close()

dir_file = open(dir_str,"w")
mywriter = csv.writer(dir_file, delimiter=',')
for line in dirPrint:
	mywriter.writerow(line)
dir_file.close()

rap_file = open(rap_str,"w")
mywriter = csv.writer(rap_file, delimiter=',')
for line in rapPrint:
	mywriter.writerow(line)
rap_file.close()

rad_file = open(rad_str,"w")
mywriter = csv.writer(rad_file, delimiter=',')
for line in radPrint:
	mywriter.writerow(line)
rad_file.close()

pres_file = open(pres_str,"w")
mywriter = csv.writer(pres_file, delimiter=',')
for line in presPrint:
	mywriter.writerow(line)
pres_file.close()
























