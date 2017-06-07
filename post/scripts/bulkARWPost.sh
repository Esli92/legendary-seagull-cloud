#!/bin/bash

DIRECTORIO_FECHAS=/run/media/esli/El_Jurado/WRF_stuff/observaciones/scripts/fechasAbr
RESOLUTION=25

for FECHA in `ls $DIRECTORIO_FECHAS`
do

        source $DIRECTORIO_FECHAS/$FECHA

        #From date file, we get:
        #AI=2015
        #MI=05
        #DI=30
        #HI=00
        #AF=2015
        #MF=06
        #DF=01
        #HF=00

        ANIO=$AI
        MES_INIT=$MI
        MES_FIN=$MF
        DIA_INIT=$DI
        DIA_FIN=$DF
        HORA_INIT=$HI
        HORA_FIN=$HF
        DOMINIO=02

	if [ ! -d "../../../post/input/${MES_INIT}_0p${RESOLUTION}" ]
	then
	    mkdir ../../../post/input/${MES_INIT}_0p${RESOLUTION}
	fi

        cd /home/alumno/Documentos/WRF/codigoFuente/ARWpost
        rm wrfout_*

	InputDir=/home/alumno/Documentos/WRF/experimentos/verificacion/salidas/exp02/salidas0p${RESOLUTION}_v3.8/${MES_INIT}_2015/d${DOMINIO}

        ln -s ${InputDir}/wrfout_d${DOMINIO}_${ANIO}-${MES_INIT}-${DIA_INIT}_${HORA_INIT}:00:00 .

        cp namelist.ARWpost.template namelist.ARWpost

        sed '2 s/'20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]:00:00'/'${ANIO}-${MES_INIT}-${DIA_INIT}_${HORA_INIT}:00:00'/g' namelist.ARWpost > namelist_int.ARWpost

        sed '3 s/'20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]:00:00'/'${ANIO}-${MES_FIN}-${DIA_FIN}_${HORA_FIN}:00:00'/g' namelist_int.ARWpost > namelist_int2.ARWpost

        sed '10 s:'./wrfout_d0[0-9]_':'./wrfout_d${DOMINIO}_':g' namelist_int2.ARWpost > namelist_int3.ARWpost

        sed '11 s:'[0-2][0-9]_0p[0-9][0-9]/wrfout_GRADS_[0-9][0-9]-[0-9][0-9]_[0-9][0-9]_[0-9][0-9][0-9][0-9]_d[0-9][0-9]':'${MES_INIT}_0p${RESOLUTION}/wrfout_GRADS_${DIA_INIT}-${DIA_FIN}_${MES_INIT}_${ANIO}_d${DOMINIO}':g' namelist_int3.ARWpost > namelist.ARWpost

        ./ARWpost.exe

done 

