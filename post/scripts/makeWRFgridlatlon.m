%make lat lon pairs from WRF grid /results file
%Uses the point from the center of grid, aka, U10, V10, T, etc. 
%DO NOT USE FOR U,V or staggered variables

%read XLAT,XLONG variables
%Did you read what I said before? probably not. This program is no good for
%staggered variables.
file = 'wrfout_d03_2017-01_19';
lat_f = ncread(file,'XLAT');
lon_f = ncread(file,'XLONG');

%Why not? well, WRF uses an Arakawa grid, stupid. so, duh.
%Take only one timestep of lat/lon, as they shouldnt change over time
%...right?

lat_m = lat_f(:,:,1);
lon_m = lon_f(:,:,1);

%Well use it anyway then, do whatever you want. See if I care. 
%Now turn the matrix into a vector

%number of pairs should be latxlon
num_lat = size(lat_m,2);
num_lon = size(lon_m,1);

n = num_lat * num_lon;

cont = 1;
lat_lon = zeros(n,2);

for i=1:num_lat;
    for j=1:num_lon;
        lat_lon(cont,1) = lat_m(j,i);
        lat_lon(cont,2) = lon_m(j,i);
        cont = cont + 1;
    end
end

%all done! lets make a file for QGIS or whatever shit you want.

csvwrite('wrf_lat_lon_tol_d03.yx',lat_lon);
