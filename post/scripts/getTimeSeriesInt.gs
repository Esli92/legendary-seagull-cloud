'open /home/esli/Documentos/WRF/experimentos/verificacion/input/20092015_0p5/gfs.0p5.2015092000.fall.ctl'

*ESTACION ACO
'set lat 19.525995'
'set lon -98.9120'

'set gxout print'
'set prnopts %6.2f 1 1'
write('ACO_02_05_15_TM.txt', 'HOUR,   LON,    LAT,    WSFRCST')
write('ACO_02_05_15_WS.txt', 'HOUR,   LON,    LAT,    WSFRCST')
*write('ACO_02_05_15_RN.txt', 'HOUR,   LON,    LAT,    WSFRCST')

'q dims'


tmax=17

say 'T time-points: 'tmax

t=1

while(t<=tmax)

    'set t 't
*    'd rainc+rainsh+rainnc'

*     tmp=sublin(result,2)
*     tmp=subwrd(tmp,1)

*    Get Lat/Lon Data

*     'q dims'
*     lons=sublin(result,2)
*     lats=sublin(result,3)
*     lon=subwrd(lons,6)
*     lat=subwrd(lats,6)

*    Save data to file
*    Note the "append", so to add to the file instead of overwriting it

*    write('ACO_02_05_15_RN.txt', t-1',    'lon',    'lat',    'tmp,append)


    'c'
    'd tmp2m-273.15'

     tmp=sublin(result,2)
     tmp=subwrd(tmp,1)

*    Get Lat/Lon Data

     'q dims'
     lons=sublin(result,2)
     lats=sublin(result,3)
     lon=subwrd(lons,6)
     lat=subwrd(lats,6)

*    Save data to file
*    Note the "append", so to add to the file instead of overwriting it

     write('ACO_02_05_15_TM.txt', (t-1)*3',    'lon',    'lat',    'tmp,append)


    'c'
    'd mag(ugrd10m,vgrd10m)'

     tmp=sublin(result,2)
     tmp=subwrd(tmp,1)

*    Get Lat/Lon Data

     'q dims'
     lons=sublin(result,2)
     lats=sublin(result,3)
     lon=subwrd(lons,6)
     lat=subwrd(lats,6)

*    Save data to file
*    Note the "append", so to add to the file instead of overwriting it

     write('ACO_02_05_15_WS.txt', (t-1)*3',    'lon',    'lat',    'tmp,append)


  t=t+1
endwhile 
