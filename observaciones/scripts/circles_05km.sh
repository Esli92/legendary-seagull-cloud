#!/bin/csh -f
# Created by KA
# use chmod +x filename
# change mode to executable
set psfile = "../figures/test_circles.ps"

#ºººgmtset change individual GMT default parametersººº
gmt gmtset PROJ_LENGTH_UNIT cm
gmt gmtset MAP_FRAME_TYPE fancy
gmt gmtset MAP_GRID_CROSS_SIZE_PRIMARY 0.01i
gmt gmtset FONT_ANNOT_PRIMARY 12
gmt gmtset GMT_INTERPOLANT akima
gmt gmtset PS_MEDIA letter
gmt gmtset FORMAT_GEO_MAP D

#ooooooooooooooooooooooooooooooooooooooooooooo
#       let the fun begin....
#ooooooooooooooooooooooooooooooooooooooooooooo

gmt pscoast -R-98/-82/18/30.5 -Dh -Ia -G55/55/55 -Jm1.0 -Bf2.0a2.0/f1.0a1.0WSen -W0.5 -V -K > $psfile
echo "-94 22 5 5 5" > circle.xy
# here you add the x y location then major minor and major axis. You need to us 5 instead of a 100 they
# are already in km.
# you could also generate the position files and then use awk to add the rest. 
gmt psxy circle.xy -R -J -SE -B -O >> $psfile
echo "ploted base map" $psfile
# open $psfile
echo "****DONE****"


