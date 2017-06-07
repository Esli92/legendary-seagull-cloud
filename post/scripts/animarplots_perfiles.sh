#!/bin/bash

cd ../graficosPerfiles

cd albedo
convert -delay 100 -size 1070x780 *.png -loop 10 'albedo_animacion.gif'

cd ..
cd CAPE
convert -delay 100 -size 1070x780 *.png -loop 10 'CAPE_animacion.gif'

cd ..
cd geopotencial
convert -delay 100 -size 1070x780 *.png -loop 10 'geopotencial_animacion.gif'

cd ..
cd PBLH
convert -delay 100 -size 1070x780 *.png -loop 10 'PBLH_animacion.gif'

cd ..
cd presion
convert -delay 100 -size 1070x780 *.png -loop 10 'presion_animacion.gif'

cd ..
cd radiacion
convert -delay 100 -size 1070x780 *.png -loop 10 'radiacion_animacion.gif'

cd ..
cd temperatura
convert -delay 100 -size 1070x780 *.png -loop 10 'temperatura_animacion.gif'

cd ..
cd vientoU
convert -delay 100 -size 1070x780 *.png -loop 10 'viento_animacion.gif'

cd ..
cd vientoV
convert -delay 100 -size 1070x780 *.png -loop 10 'viento_animacion.gif'

cd ..
cd vientoMag
convert -delay 100 -size 1070x780 *.png -loop 10 'viento_animacion.gif'
