load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"

a = addfile("wrfout_d02_2015-05-29_00:00:00","r")

;COORDENADAS DE LA ESTACION
  maxlat = 19.52599555
  minlon = -99.082420

  opt = True
  loc  = wrf_user_ll_to_ij(a,minlon,maxlat,opt)
;print(loc)
  latlon = wrf_user_ij_to_ll(a,loc(0),loc(1),opt)
print(latlon)
latslons = (/latlon(0),latlon(1)/)
alist=[/latslons/]
print(latslons)
write_table("LatLonStations.txt","w",alist,"%16.5f%16.5f")


