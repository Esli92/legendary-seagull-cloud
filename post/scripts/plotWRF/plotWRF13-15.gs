'open ../input/08_0p25/wrfout_GRADS_13-15_08_2015_d02.ctl'
*El siguiente loop hara la operacion para cada uno de los tiempos
timer = 1
*dia de inicio
day = 13
cont = 1
hora = 00
'define raincount = 0'
* These are the BLUE shades
'set rgb 16 2 37 75'
'set rgb 17 21 58 97'
'set rgb 18 41 79 119'
'set rgb 19 60 101 141'
'set rgb 20 80 122 163'
'set rgb 21 99 143 185'
'set rgb 22 119 165 207'
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
'printim ../graficos/13-15/viento/viento_'contador'_dia'day'_'hora'Z.png png white'
*para temperatura en superficie
'c'
'set gxout shaded'
'set clevs 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30'
'd t2-273.15'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Temperatura a 2m superficie (C) dia 'day' 'hora'Z '
'printim ../graficos/13-15/temp/temperatura_'contador'_dia'day'_'hora'Z.png png white'
*para la presion superficial
'c'
'set gxout shaded'
'd psfc/100'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Presion en superficie (hPa) dia 'day' 'hora'Z '
'printim ../graficos/13-15/presion/presion_'contador'_dia'day'_'hora'Z.png png white'
*para la radiacion solar
'c'
'set clevs 100 200 300 400 500 600 700 800 900 1000'
'd swdown'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Radiacion incidente onda corta (W m-2) dia 'day' 'hora'Z '
'printim ../graficos/13-15/radiacion/radiacion_'contador'_dia'day'_'hora'Z.png png white'
*para el albedo
'c'
'd albedo'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Albedo (%) dia 'day' 'hora'Z '
'printim ../graficos/13-15/albedo/albedo_'contador'_dia'day'_'hora'Z.png png white'
*para la altura de capa limite
'c'
'set clevs 100 400 700 1000 1300 1600 1900 2200 2500 2800 3100'
'd pblh'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Altura de capa limite planetaria (m) dia 'day' 'hora'Z '
'printim ../graficos/13-15/PBLH/PBLH_'contador'_dia'day'_'hora'Z.png png white'


*para Precipitacion
'c'
'set clevs 0.5 1 2 3 4 5 6'
'set ccols 0 22 21 20 19 18 17 16'
'define totalrain = rainc+rainsh+rainnc-raincount'
'define raincount = rainc+rainsh+rainnc'
'd totalrain'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Precipitacion acumulada horaria (mm) dia 'day' 'hora'Z '
'printim ../graficos/13-15/PP/PP_'contador'_dia'day'_'hora'Z.png png white'
*para geopotencial
'c'
'set lev 500'
'd geopt'
'cbarn'
'draw shp MEX_adm1.shp'
'draw title Geopotencial a 500 hPa (m) dia 'day' 'hora'Z '
'printim ../graficos/13-15/geopotencial/geop_'contador'_dia'day'_'hora'Z.png png white'
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
