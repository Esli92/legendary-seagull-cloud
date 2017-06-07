clc;
clear;

%%%%% Par?metros que se modifican *****
localizacion = 'df';%'edomex'%;%'tlaxcala';%'puebla';%'morelos'; %df, edomex, hidalgo, morelos, puebla, queretaro, tlaxcala
%estaciones = ['ecogua'; 'esncb1'; 'esncb2'; 'tezont';'semena']
estaciones = ['ACO';'AJM';'AJU';'BJU';'CHO';'CUA';'CUT';'FAC';'HGM';'MER';'MGH';'MON';'NEZ';'PED';'SAG';'SFE';'TAH';'TLA';'UAX';'UIZ';'VIF';'XAL'];
meses = ['ene';'feb';'mar';'abr';'may';'jun';'jul';'ago';'sep';'oct';'nov';'dic'];
mes_num = ['01';'02';'03';'04';'05';'06';'07';'08';'09';'10';'11';'12'];

%estacion = 'va_bra';%'psa_ma';%'pq_izt';%'nev_to';%'lag_ze';%'cer_ca';%'atlaco';%'altzom';
%estacion = 'zimapa';%'zacual';%'pachuc';%'los_ma';%'huicha';%'huejut';%'el_chi';
%estacion = 'tresma';%'tepozt';%'s_huau';'imtagu';
%estacion = %'utteca'%'teziut';%'tehuac';%'izucar';%'huauch';
%estacion = %'s_gor2';%'s_gor2';%'psa_ja';%'huimilp';
%estacion = %'la_ma1';%'huaman';
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

directorio_trabajo = '/home/alumno/Documentos/WRF/experimentos/verificacion/observaciones/limpiezaMatlab/REDMET';
directorio_programas =  '../matlab';

[i_estacion, c] = size(estaciones);
[i_meses, c] = size(meses);
porc_temp = zeros(i_estacion,12);
porc_viento = zeros(i_estacion,12);
porc_prec = zeros(i_estacion,12);

for i=1:i_estacion
    directorio_procesamiento = [directorio_trabajo '/' localizacion '/' estaciones(i,:)];
    cd(directorio_procesamiento)
    anios = dir('2*');
    length(anios)
    for j=1:12
        bandera_no_data = 0;
        cd([directorio_procesamiento '/' anios(1).name])
        %Temperatura
        nombre_archivo = [mes_num(j,:) '_' estaciones(i,:) '_TM.txt'];
        if exist(nombre_archivo,'file')
            %if (str2num(anios(1).name) == 2011) || (str2num(anios(1).name) == 2013) || (str2num(anios(1).name) == 2014) || (str2num(anios(1).name) == 2015)
            %long_matriz = 8760;
            %elseif (str2num(anios(1).name) == 2012)
            %long_matriz = 8784;
            %end
            temp = load(nombre_archivo);
            datenums = datenum(2015,temp(:,2),temp(:,3),temp(:,4),0,0);
            temp(:,5) = datenums(:);
            long_matriz = length(temp);
            
            if (isempty(find(temp(:,1)==-99, 1)) == 0)
                bandera_no_data = 1;
                no_data = length(find(temp(:,1)==-99));
                %temp = temp(find(temp(:,1) ~= -99),:);
                missIndex = find(temp(:,1)==-99);
                temp(missIndex) = NaN;
            end
            
            if no_data < length(temp)
                figure('Position', [1 1 1223 537])
                %axes('Position',[0.1,0.1,0.7,0.7])
                %posicion = [.09  .25  .8  .6]
                %posicion = [0.1, 0.2, .8  .6]
                %subplot('position',posicion);
                subplot(2,1,1)
                plot(temp(:,5),temp(:,1),'-r')
                grid on
                cadena = strcat(estaciones(i,:),' - ',meses(j,:));
                title(cadena, 'FontSize',18, 'FontWeight', 'bold');
                ylabel('Celsius', 'FontSize',18, 'FontWeight', 'bold');
                %xlabel('Month', 'FontSize',18, 'FontWeight', 'bold');
                ylim([min(temp(:,1)) 40])
                %xlim([min(temp(:,end)) max(temp(:,end))])
                %datetick('x','mm','keepticks')
                datetick('x','dd','keepticks')
                %datetick('x','yyyy','keeplimits')
                %set(gca,'XTick',temp(:,end-1))
                %datetick('x','mmm');
                set(gca,'FontSize',18,'FontWeight', 'bold');
                
                %EjeX=[-99.5 -099 -98.5];
                %EjeY=[ 0 10 20 30 40];
                %set(gca,'XTick',EjeX);
                %set(gca,'XTicklabel',{'99? 30?W'; '99W'; '98? 30?W'},'FontSize',18, 'FontWeight', 'bold');
                
                %set(gca,'YTick',EjeY);
                %set(gca,'YTicklabel',{' 0'; '10'; '20'; '30'; '40'},'FontSize',18, 'FontWeight', 'bold');
                
                
                indices_NAN = isnan(temp(:,1));
                total_NAN = find(indices_NAN==1);
                if bandera_no_data == 1
                    total_no_data = length(total_NAN);
                else
                    total_no_data = length(total_NAN);
                end
                porcentaje_registros = (total_no_data*100)/long_matriz;
                porcentaje_registros = 100 - porcentaje_registros;
                %text(min(temp(:,end))+200,35,['% of observations: ' num2str(porcentaje_registros)],'Color','black','FontSize',12,'FontWeight', 'bold');
                text(min(temp(:,5)),30,['% of observations: ' num2str(porcentaje_registros)],'Color','black','FontSize',12,'FontWeight', 'bold');
                porc_temp(i,j) = porcentaje_registros;
                %Viento
                nombre_archivo = [mes_num(j,:) '_' estaciones(i,:) '_WS.txt'];
                bandera_no_data = 0;
                vient = load(nombre_archivo);
                datenums = datenum(2015,vient(:,2),vient(:,3),vient(:,4),0,0);
                vient(:,5) = datenums(:);
                if (isempty(find(vient(:,1)==-99, 1)) == 0)
                    bandera_no_data = 1;
                    no_data = length(find(vient(:,1)==-99));
                    %vient = vient(find(vient(:,1) ~= -99),:);
                    missIndex = find(vient(:,1)==-99);
                    vient(missIndex) = NaN;
                end
                
                %figure
                %posicion = [0.5, 0.1, 0.4, 0.7];
                %posicion = [0.5, 0.1, .8  .6]
                %subplot('position',posicion);
                subplot(2,1,2)
                plot(vient(:,5),vient(:,1),'-k')
                grid on
                %cadena = strcat(estaciones(i,:),' - ',anios(1).name);
                %title(cadena, 'FontSize',18, 'FontWeight', 'bold');
                ylabel('Km/h', 'FontSize',18, 'FontWeight', 'bold');
                %xlabel('Month', 'FontSize',18, 'FontWeight', 'bold');
                %ylim([min(vient(:,1)-2) max(vient(:,1))])
                xlim([min(vient(:,end)) max(vient(:,end))])
                %datetick('x','mm','keepticks')
                datetick('x','dd','keepticks')
                %datetick('x','yyyy','keeplimits')
                %set(gca,'XTick',temp(:,end-1))
                %datetick('x','mmm');
                set(gca,'FontSize',18,'FontWeight', 'bold');
                
                indices_NAN = isnan(vient(:,1));
                total_NAN = find(indices_NAN==1);
                if bandera_no_data == 1
                    total_no_data = length(total_NAN);
                else
                    total_no_data = length(total_NAN);
                end
                porcentaje_registros = (total_no_data*100)/long_matriz;
                porcentaje_registros = 100 - porcentaje_registros;
                text(min(temp(:,5))+10,max(vient(:,1))-5,['% of observations: ' num2str(porcentaje_registros)],'Color','black','FontSize',12,'FontWeight', 'bold');
                porc_viento(i,j) = porcentaje_registros;
                
                %             %Precipitacion
                %             nombre_archivo = [mes_num(j,:) '_' estaciones(i,:) '_' meses(j,:) '_15' '_rain.txt'];
                %             prec = load(nombre_archivo);
                %             datenums = datenum(2015,prec(:,2),prec(:,3),prec(:,4),0,0);
                %             prec(:,5) = datenums(:);
                %
                %             nueva_prec(:,1) = prec(:,1);
                %             nueva_prec(:,2) = prec(:,5);
                %             %         inicio = 1;
                %             %         fin = 6;
                %             %         l = 1;
                %             %         for k=1:6:length(prec)
                %             %             nueva_prec(l,1) = sum(prec(inicio:fin,1));
                %             %             nueva_prec(l,2) = prec(inicio,5);
                %             %             l = l+1;
                %             %             inicio = fin + 1;
                %             %             fin = fin + 6;
                %             %         end
                %             nombre_archivo_new = [mes_num(j,:) '_' estaciones(i,:) '_' meses(j,:) '_15' '_precipitacion_new.mat'];
                %             bandera_no_data = 0;
                %             save(nombre_archivo_new, 'nueva_prec');
                %             if (isempty(find(nueva_prec(:,1)==-99, 1)) == 0)
                %                 bandera_no_data = 1;
                %                 no_data = length(find(nueva_prec(:,1)==-99));
                %                 %nueva_prec = nueva_prec(find(nueva_prec(:,1) ~= -99),:);
                %                 missIndex = find(nueva_prec(:,1)==-99);
                %                 nueva_prec(missIndex) = NaN;
                %             end
                %
                %
                %             subplot(3,1,3)
                %             plot(nueva_prec(:,2),nueva_prec(:,1),'-b')
                %             hold on
                %             umbral_min_prec = zeros(length(nueva_prec),1);
                %             umbral_min_prec(:) = 10;
                %             plot(nueva_prec(:,2),umbral_min_prec,'-r')
                %
                %             grid on
                %             %cadena = strcat(estaciones(i,:),' - ',anios(1).name);
                %             %title(cadena, 'FontSize',18, 'FontWeight', 'bold');
                %             ylabel('mm', 'FontSize',18, 'FontWeight', 'bold');
                %             xlabel('Month', 'FontSize',18, 'FontWeight', 'bold');
                %             %ylim([min(nueva_prec(:,1)) max(nueva_prec(:,1))])
                %             xlim([min(nueva_prec(:,end)) max(nueva_prec(:,end))])
                %             %datetick('x','mm','keepticks')
                %             datetick('x','dd','keepticks')
                %             %datetick('x','yyyy','keeplimits')
                %             %set(gca,'XTick',temp(:,end-1))
                %             %datetick('x','mmm');
                %             set(gca,'FontSize',18,'FontWeight', 'bold');
                %
                %
                %             indices_NAN = isnan(nueva_prec(:,1));
                %             total_NAN = find(indices_NAN==1);
                %             if bandera_no_data == 1
                %                 total_no_data = length(total_NAN);
                %             else
                %                 total_no_data = length(total_NAN);
                %             end
                %             porcentaje_registros = (total_no_data*100)/long_matriz; %VERIFICAR PARA ESTE QUE ESTE FUNCIONANDO
                %             porcentaje_registros = 100 - porcentaje_registros;
                %             text(min(temp(:,5))+5,max(nueva_prec(:,1)),['% of observations: ' num2str(porcentaje_registros)],'Color','black','FontSize',12,'FontWeight', 'bold');
                %             %text(min(temp(:,5))+10,11,['10 mm'],'Color','black','FontSize',12,'FontWeight', 'bold');
                %             text(min(temp(:,5))+15,max(nueva_prec(:,1)),['maximum of ' num2str(max(nueva_prec(:,1))) ' mm'],'Color','black','FontSize',12,'FontWeight', 'bold');
                %             porc_prec(i,j) = porcentaje_registros;
                
                cd([directorio_trabajo '/graficas_matlab'])
                nombre = [localizacion '_' mes_num(j,:) '_' estaciones(i,:)];
                print('-dpng', [nombre '.png'])
                close(gcf)
                
                clear vient temp prec nueva_prec porcentaje_registros total_NAN umbral_min_prec total_no_data
            end
        end
    end
    
end
