#!/bin/bash

cd ../graficos/01-03

cd albedo
convert -delay 100 -size 1070x780 *.png -loop 10 'albedo_animacion_01-03.gif'

cd ..
cd PP
convert -delay 100 -size 1070x780 *.png -loop 10 'PP_animacion_01-03.gif'

cd ..
cd geopotencial
convert -delay 100 -size 1070x780 *.png -loop 10 'geopotencial_animacion_01-03.gif'

cd ..
cd PBLH
convert -delay 100 -size 1070x780 *.png -loop 10 'PBLH_animacion_01-03.gif'

cd ..
cd presion
convert -delay 100 -size 1070x780 *.png -loop 10 'presion_animacion_01-03.gif'

cd ..
cd radiacion
convert -delay 100 -size 1070x780 *.png -loop 10 'radiacion_animacion_01-03.gif'

cd ..
cd temp
convert -delay 100 -size 1070x780 *.png -loop 10 'temperatura_animacion_01-03.gif'

cd ..
cd viento
convert -delay 100 -size 1070x780 *.png -loop 10 'viento_animacion_01-03.gif'
