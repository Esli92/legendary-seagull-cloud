'open ../input/semana0p50/wrfout_GRADS_29-01_04_2015_d02.ctl'
*El siguiente loop hara la operacion para cada uno de los tiempos
timer = 1
*dia de inicio
day = 29
cont = 1
hora = 00

while(timer<=49)

*Para imprimir el numero de archivo sera necesario algo mas explicito mayor a 10
contador = timer+10
'set t 'timer
'set lev 1000'
'set grads off'
*para el viento
'set clevs 2 4 6 8 10'
'd u10;v10;mag(u10,v10)'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Viento a 10 m superficie (m s-1) dia 'day' 'hora'Z '
'printim ../graficos/29-01/viento/viento_'contador'_dia'day'_'hora'Z.png png white'
*para temperatura en superficie
'c'
'set gxout shaded'
'set clevs 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30'
'd t2-273.15'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Temperatura a 2m superficie (C) dia 'day' 'hora'Z '
'printim ../graficos/29-01/temp/temperatura_'contador'_dia'day'_'hora'Z.png png white'
*para la presion superficial
'c'
'set gxout shaded'
'd psfc/100'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Presion en superficie (hPa) dia 'day' 'hora'Z '
'printim ../graficos/29-01/presion/presion_'contador'_dia'day'_'hora'Z.png png white'
*para la radiacion solar
'c'
'set clevs 100 200 300 400 500 600 700 800 900 1000'
'd swdown'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Radiacion incidente onda corta (W m-2) dia 'day' 'hora'Z '
'printim ../graficos/29-01/radiacion/radiacion_'contador'_dia'day'_'hora'Z.png png white'
*para el albedo
'c'
'd albedo'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Albedo (%) dia 'day' 'hora'Z '
'printim ../graficos/29-01/albedo/albedo_'contador'_dia'day'_'hora'Z.png png white'
*para la altura de capa limite
'c'
'set clevs 100 400 700 1000 1300 1600 1900 2200 2500 2800 3100'
'd pblh'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Altura de capa limite planetaria (m) dia 'day' 'hora'Z '
'printim ../graficos/29-01/PBLH/PBLH_'contador'_dia'day'_'hora'Z.png png white'
*para temperatura
*'c'
*'set clevs 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30'
*'d t2-273.15'	
*'draw shp MEX_adm1.shp'
*'cbarn'
*'draw title Temperatura a 2m de superficie (C) dia 'day' 'hora'Z '
*'printim ../graficos/29-01/temperatura/temp_'contador'_dia'day'_'hora'Z.png png white'
*para CAPE
'c'
'd cape'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title CAPE (J Kg-1) dia 'day' 'hora'Z '
'printim ../graficos/29-01/CAPE/CAPE_'contador'_dia'day'_'hora'Z.png png white'
*para geopotencial
'c'
'set lev 500'
'd geopt'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Geopotencial a 500 hPa (m) dia 'day' 'hora'Z '
'printim ../graficos/29-01/geopotencial/geop_'contador'_dia'day'_'hora'Z.png png white'
'c'

*El proposito de este ciclo es que vaya poniendo el dia adecuado, ya que el dia cambia cada 24 tiempos.
if(timer/24 = cont)
day = day + 1
hora = 00
cont = cont+1
else
day = day
hora = hora + 1
endif

timer = timer + 1
endwhile
