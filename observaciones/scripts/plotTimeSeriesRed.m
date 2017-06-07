%Graficar series de tiempo de REDMET para ver si estan desfasadas
close all
clear all

%El archivo con los datos considerando horario de verano
file_Ver = '../dataFiles/processed_redmet/CUA/2015/TM/CUA_TM.txt';
%El archivo con datos originales
file_Ori = '../dataFiles/processed_redmet_LOCAL/CUA/2015/TM/CUA_TM.txt';

%Cargamos ambos archivos
CUA_Ver = load(file_Ver);
CUA_Ori = load(file_Ori);

%Queremos solo la temperatura de ambos
Temp_Ver = CUA_Ver(:,1);
Temp_Ori = CUA_Ori(:,1);

%Cosas del tiempo
MoV = CUA_Ver(:,2);
DaV = CUA_Ver(:,3);
HoV = CUA_Ver(:,4);

MoO = CUA_Ori(:,2);
DaO = CUA_Ori(:,3);
HoO = CUA_Ori(:,4);

n = length(CUA_Ver);

% for i=1:n;
%     if HoV(i)==0
%         HoV(i) = 24;
%     end
%     if HoO(i)==0
%         HoO(i) = 24;
%     end
% end

dateNum_V = zeros(n,1);
dateNum_O = zeros(n,1);

dateStrings_V = cell(n,1);
dateStrings_O = cell(n,1);

dateVec_V = [];
dateVec_O = [];
%Convertir a datenum para el datestring
for i=1:n;
    dateVec_V = [dateVec_V;2015,MoV(i),DaV(i),HoV(i),00,00];
    dateVec_O = [dateVec_O;2015,MoO(i),DaO(i),HoO(i),00,00];
    dateNum_V(i) = datenum(dateVec_V(i,:));
    dateNum_O(i) = datenum(dateVec_O(i,:));
    dateStrings_V(i) = {datestr(dateNum_V(i))};
    dateStrings_O(i) = {datestr(dateNum_O(i))};
end

%dateNum_V = datetime(dateVec_V);
%dateNum_O = datetime(dateVec_O);
tsV = timeseries(Temp_Ver,dateNum_V);
tsO = timeseries(Temp_Ori,dateNum_O);





figure()
hold on
plot(tsV,'-k')
%datetick('x',0)
plot(tsO,'-r')

%%
%PRONOSTICOS

%archivo con pronosticos y observaciones (sospecho que estan desfasados)
pair_file = '../dataFiles/pares/24h/0p5/04/ObsFct_Pairs_TM_CUA_4_4_15.txt';
delimiter = ',';
headerline = 1;
pairs = importdata('../dataFiles/pares/24h/0p5/04/ObsFct_Pairs_TM_CUA_4_4_15.txt',delimiter,headerline);

