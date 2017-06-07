%plot Time Series from obs/for pairs.
clear all
close all

%First load the appropiate time series:
i = 1;
%Change the next line to the station you want to use. 
station='UAX';
%Choose between TM or WS as var. DONT USE ANYTHING ELSE. 
var='WS';

if (var=='TM')
    var_str = 'grados C';
else
    var_str = 'm/s';
end

for str = {'ALL','SEC','SEF','HUM'}
    season=str{1};
    path_5=sprintf('l24h/0p5/seasonal/%s/',season);
    path_25=sprintf('l24h/0p25/seasonal/%s/',season);
    
    station_file=sprintf('%s_%s_%s.txt',station,season,var);
    
    file1 = strcat(path_5,station_file);
    file2 = strcat(path_25,station_file);
    
    sys_str = sprintf('wc -l %s',file1);
    [nol nol] = system(sys_str);
    nol = str2num(strtok(nol));
    
    [mes5,dia5,hora5,obs5,pron5] = importTS(file1,2, nol);
    
    anio = (zeros(length(mes5),1) + 2015);
    mins = (zeros(length(mes5),1));
    
    time5{i} = datetime([anio,mes5,dia5,hora5,mins,mins]);
    obs5_a{i} = obs5(:);
    for5_a{i} = pron5(:);
    
    sys_str = sprintf('wc -l %s',file2);
    [nol nol] = system(sys_str);
    nol = str2num(strtok(nol));
    
    [mes25,dia25,hora25,obs25,pron25] = importTS(file2,2, nol);
    
    anio = (zeros(length(mes25),1) + 2015);
    mins = (zeros(length(mes25),1));
    time25{i} = datetime([anio,mes25,dia25,hora25,mins,mins]);
    obs25_a{i} = obs25(:);
    for25_a{i} = pron25(:);

    i = i+1;
end

obs5_ALL = obs5_a{1};
obs5_SEC = obs5_a{2};
obs5_SEF = obs5_a{3};
obs5_HUM = obs5_a{4};

obs25_ALL = obs25_a{1};
obs25_SEC = obs25_a{2};
obs25_SEF = obs25_a{3};
obs25_HUM = obs25_a{4};

for25_ALL = for25_a{1};
for25_SEC = for25_a{2};
for25_SEF = for25_a{3};
for25_HUM = for25_a{4};

for5_ALL = for5_a{1};
for5_SEC = for5_a{2};
for5_SEF = for5_a{3};
for5_HUM = for5_a{4};

time25_ALL = time25{1};
time25_SEC = time25{2};
time25_SEF = time25{3};
time25_HUM = time25{4};

time5_ALL = time5{1};
time5_SEC = time5{2};
time5_SEF = time5{3};
time5_HUM = time5{4};
%%
close all

% figure()
% plot(time5_ALL,obs5_ALL,'LineWidth',1.5)
% hold on
% plot(time5_ALL,for5_ALL)
% plot(time25_ALL,for25_ALL)
% hold off
% title 'Serie de tiempo de temperatura para la estación Encb02, usando resolución de CI de 0.5 grados. Temporada de lluvias.'
% xlabel 'Tiempo'
% ylabel(var_str)
% legend('Observación','Pronóstico')
% ax = gca;
% lis = linspace(datenum(time5_ALL(1)),datenum(time5_ALL(end)),30);
% ax.XTick = lis;
% datetick('x','dd','keepticks')


lis_HUM = linspace(datenum(time5_HUM(1)),datenum(time5_HUM(end)),10);
lis_SEC = linspace(datenum(time5_SEC(1)),datenum(time5_SEC(end)),10);
lis_SEF = linspace(datenum(time5_SEF(1)),datenum(time5_SEF(end)),10);
figure()


ymin=5*(floor(min(obs5_SEC)/5));
ymax=5*(ceil(max(obs5_SEC)/5));

subplot(3,2,1)
plot(time5_SEC,obs5_SEC,'b','LineWidth',1.5)
hold on
plot(time5_SEC,for5_SEC,'r')
hold off
ylabel(var_str)
title 'Temporada seca cálida, resolución 0.5'
ylim([ymin ymax])
ax = gca;
ax.XTick = lis_SEC;
datetick('x','mm/dd','keepticks')

subplot(3,2,2)
plot(time25_SEC,obs25_SEC,'b','LineWidth',1.5)
hold on
plot(time25_SEC,for25_SEC,'r')
hold off
ylabel(var_str)
title 'Temporada seca cálida, resolución 0.25'
ylim([ymin ymax])
ax = gca;
ax.XTick = lis_SEC;
datetick('x','mm/dd','keepticks')

ymin=5*(floor(min(for5_HUM)/5));
ymax=5*(ceil(max(for5_HUM)/5));

subplot(3,2,3)
plot(time5_HUM,obs5_HUM,'b','LineWidth',1.5)
hold on
plot(time5_HUM,for5_HUM,'r')
hold off
ylabel(var_str)
title 'Temporada húmeda, resolución 0.5'
ylim([ymin ymax])
ax = gca;
ax.XTick = lis_HUM;
datetick('x','mm/dd','keepticks')

subplot(3,2,4)
plot(time25_HUM,obs25_HUM,'b','LineWidth',1.5)
hold on
plot(time25_HUM,for25_HUM,'r')
hold off
ylabel(var_str)
title 'Temporada húmeda, resolución 0.25'
ylim([ymin ymax])
ax = gca;
ax.XTick = lis_HUM;
datetick('x','mm/dd','keepticks')

ymin=5*(floor(min(obs5_SEF)/5));
ymax=5*(ceil(max(obs5_SEF)/5));

subplot(3,2,5)
plot(time5_SEF,obs5_SEF,'b','LineWidth',1.5)
hold on
plot(time5_SEF,for5_SEF,'r')
hold off
ylabel(var_str)
title 'Temporada seca fria, resolución 0.5'
ylim([ymin ymax])
ax = gca;
ax.XTick = lis_SEF;
datetick('x','mm/dd','keepticks')

subplot(3,2,6)
plot(time25_SEF,obs25_SEF,'b','LineWidth',1.5)
hold on
plot(time25_SEF,for25_SEF,'r')
hold off
ylabel(var_str)
title 'Temporada seca fria, resolución 0.25'
ylim([ymin ymax])
ax = gca;
ax.XTick = lis_SEF;
datetick('x','mm/dd','keepticks');

station_tit = sprintf('Series de tiempo de Temperatura para la estación %s',station);
h = figtitle(station_tit);
set(h);

file_name = sprintf('../figures/TS_stat_%s_seas_%s.png',station,season);


h=gcf;

set(h,'PaperOrientation','landscape');

set(h,'PaperUnits','normalized');

set(h,'PaperPosition', [0 0 1.5 1]);

print(gcf, '-dpng', file_name);


