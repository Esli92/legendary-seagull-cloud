clc;
clear;

%%%%% Par?metros que se modifican *****
localizacion = 'df';%'edomex'%;%'tlaxcala';%'puebla';%'morelos'; %df, edomex, hidalgo, morelos, puebla, queretaro, tlaxcala
estaciones = ['ecogua'; 'esncb1'; 'esncb2'; 'tezont';'semena']

%estacion = 'va_bra';%'psa_ma';%'pq_izt';%'nev_to';%'lag_ze';%'cer_ca';%'atlaco';%'altzom';
%estacion = 'zimapa';%'zacual';%'pachuc';%'los_ma';%'huicha';%'huejut';%'el_chi';
%estacion = 'tresma';%'tepozt';%'s_huau';'imtagu';
%estacion = %'utteca'%'teziut';%'tehuac';%'izucar';%'huauch';
%estacion = %'s_gor2';%'s_gor2';%'psa_ja';%'huimilp';
%estacion = %'la_ma1';%'huaman';
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

directorio_trabajo = '../EMAS_centro_mexico';
directorio_programas =  '../matlab'

[i_estacion, c] = size(estaciones);




for i=1:i_estacion
    directorio_procesamiento = [directorio_trabajo '/' localizacion '/' estaciones(i,:)];
    cd(directorio_procesamiento)
    anios = dir('2*');
    length(anios)
    for j=1:length(anios)
        bandera_no_data = 0;
        cd([directorio_procesamiento '/' anios(j).name])
        %Temperatura
        nombre_archivo = [localizacion '_' estaciones(i,:) '_' anios(j).name '_temperatura.mat'];
        if (str2num(anios(j).name) == 2011) || (str2num(anios(j).name) == 2013) || (str2num(anios(j).name) == 2014)
            long_matriz = 8760; 
        elseif (str2num(anios(j).name) == 2012)
            long_matriz = 8784;
        end
        temp = load(nombre_archivo);
        temp =  temp.temperatura;
        if (isempty(find(temp(:,2)==0)) == 0)
            bandera_no_data = 1;
            no_data = length(find(temp(:,2)==0))
            temp = temp(find(temp(:,2) ~= 0),:);
        end
        figure('Position', [1 1 1223 537])
        %axes('Position',[0.1,0.1,0.7,0.7])
        %posicion = [.09  .25  .8  .6]
        %posicion = [0.1, 0.2, .8  .6]
        %subplot('position',posicion);
        subplot(3,1,1)
        plot(temp(:,5),temp(:,1),'-r')
        grid on
        cadena = strcat(estaciones(i,:),' - ',anios(j).name);
        title(cadena, 'FontSize',18, 'FontWeight', 'bold');
        ylabel('Celsius', 'FontSize',18, 'FontWeight', 'bold');
        %xlabel('Month', 'FontSize',18, 'FontWeight', 'bold');
        ylim([min(temp(:,1)) 40])
        %xlim([min(temp(:,end)) max(temp(:,end))])
        %datetick('x','mm','keepticks')
        datetick('x','mmm','keepticks')
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
            total_no_data = length(total_NAN) + no_data;
        else
            total_no_data = length(total_NAN);
        end
        porcentaje_registros = (total_no_data*100)/long_matriz;
        porcentaje_registros = 100 - porcentaje_registros;
        text(min(temp(:,end))+200,35,['% of observations: ' num2str(porcentaje_registros)],'Color','black','FontSize',12,'FontWeight', 'bold');

        %Viento
        nombre_archivo = [localizacion '_' estaciones(i,:) '_' anios(j).name '_viento.mat'];
        bandera_no_data = 0;
        vient = load(nombre_archivo);
        vient = vient.viento;
        if (isempty(find(vient(:,2)==0)) == 0)
            bandera_no_data = 1;
            no_data = length(find(vient(:,2)==0))
            vient = vient(find(vient(:,2) ~= 0),:);
        end
        
        %figure
        %posicion = [0.5, 0.1, 0.4, 0.7];
        %posicion = [0.5, 0.1, .8  .6]
        %subplot('position',posicion);
        subplot(3,1,2)
        plot(vient(:,5),vient(:,1),'-k')
        grid on
        %cadena = strcat(estaciones(i,:),' - ',anios(j).name);
        %title(cadena, 'FontSize',18, 'FontWeight', 'bold');
        ylabel('Km/h', 'FontSize',18, 'FontWeight', 'bold');
        %xlabel('Month', 'FontSize',18, 'FontWeight', 'bold');
        %ylim([min(vient(:,1)-2) max(vient(:,1))])
        xlim([min(vient(:,end)) max(vient(:,end))])
        %datetick('x','mm','keepticks')
        datetick('x','mmm','keepticks')
        %datetick('x','yyyy','keeplimits')
        %set(gca,'XTick',temp(:,end-1))
        %datetick('x','mmm');
        set(gca,'FontSize',18,'FontWeight', 'bold');
        
        indices_NAN = isnan(vient(:,1));
        total_NAN = find(indices_NAN==1);
        if bandera_no_data == 1
            total_no_data = length(total_NAN) + no_data;
        else
            total_no_data = length(total_NAN);
        end
        porcentaje_registros = (total_no_data*100)/long_matriz;
        porcentaje_registros = 100 - porcentaje_registros;
        text(min(temp(:,end))+200,max(vient(:,1)),['% of observations: ' num2str(porcentaje_registros)],'Color','black','FontSize',12,'FontWeight', 'bold');

        
        %Precipitacion
        nombre_archivo = [localizacion '_' estaciones(i,:) '_' anios(j).name '_precipitacion.mat'];
        prec = load(nombre_archivo);
        prec = prec.precipitacion;
        inicio = 1;
        fin = 6;
        l = 1;
        for k=1:6:length(prec)
            nueva_prec(l,1) = sum(prec(inicio:fin,1));
            nueva_prec(l,2) = prec(inicio,5);
            l = l+1;
            inicio = fin + 1;
            fin = fin + 6; 
        end
        nombre_archivo_new = [localizacion '_' estaciones(i,:) '_' anios(j).name '_precipitacion_new.mat'];
        bandera_no_data = 0;
        save(nombre_archivo_new, 'nueva_prec');
        if (isempty(find(nueva_prec(:,2)==0)) == 0)
            bandera_no_data = 1;
            no_data = length(find(nueva_prec(:,2)==0))
            nueva_prec = nueva_prec(find(nueva_prec(:,2) ~= 0),:);
        end

        
        subplot(3,1,3)
        plot(nueva_prec(:,2),nueva_prec(:,1),'-b')
        hold on
        umbral_min_prec = zeros(length(nueva_prec),1);
        umbral_min_prec(:) = 15;
        plot(nueva_prec(:,2),umbral_min_prec,'-r')

        grid on
        %cadena = strcat(estaciones(i,:),' - ',anios(j).name);
        %title(cadena, 'FontSize',18, 'FontWeight', 'bold');
        ylabel('mm', 'FontSize',18, 'FontWeight', 'bold');
        xlabel('Month', 'FontSize',18, 'FontWeight', 'bold');
        %ylim([min(nueva_prec(:,1)) max(nueva_prec(:,1))])
        xlim([min(nueva_prec(:,end)) max(nueva_prec(:,end))])
        %datetick('x','mm','keepticks')
        datetick('x','mmm','keepticks')
        %datetick('x','yyyy','keeplimits')
        %set(gca,'XTick',temp(:,end-1))
        %datetick('x','mmm');
        set(gca,'FontSize',18,'FontWeight', 'bold');
        
        
        indices_NAN = isnan(nueva_prec(:,1));
        total_NAN = find(indices_NAN==1);
        if bandera_no_data == 1
            total_no_data = length(total_NAN) + no_data;
        else
            total_no_data = length(total_NAN);
        end
        porcentaje_registros = (total_no_data*100)/long_matriz; %VERIFICAR PARA ESTE QUE ESTE FUNCIONANDO
        porcentaje_registros = 100 - porcentaje_registros;
        text(min(temp(:,end))+200,max(nueva_prec(:,1)),['% of observations: ' num2str(porcentaje_registros)],'Color','black','FontSize',12,'FontWeight', 'bold');
        text(min(temp(:,end))+50,16,['15 mm'],'Color','black','FontSize',12,'FontWeight', 'bold');
        text(min(temp(:,end))+50,max(nueva_prec(:,1)),['maximum of ' num2str(max(nueva_prec(:,1))) ' mm'],'Color','black','FontSize',12,'FontWeight', 'bold');
        
        cd([directorio_trabajo '/graficas_matlab'])
        nombre = [localizacion '_' anios(j).name '_' estaciones(i,:)]; 
        print('-dpng', [nombre '.png'])
        close(gcf)

        clear vient temp prec nueva_prec porcentaje_registros total_NAN umbral_min_prec total_no_data
        
        
    end
    
end
