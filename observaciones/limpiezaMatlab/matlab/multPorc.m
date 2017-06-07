clc
clear

load('porcentajesREDMET.mat');
for i=1:12
    data_mes = porc_temp(:,i);
    if (isempty(find(data_mes(:)==0, 1)) == 0);
     data_mes = data_mes(find(data_mes(:) ~= 0),:);
    end
    
    data_mes = data_mes./100;
    prod_temp(i) = prod(data_mes,1);
    
    
    data_mes = porc_viento(:,i);
    if (isempty(find(data_mes(:)==0, 1)) == 0);
     data_mes = data_mes(find(data_mes(:) ~= 0),:);
    end
    
    data_mes = data_mes./100;
    prod_viento(i) = prod(data_mes,1);
end

% prod_cruz_prec = zeros(1,11);
prod_cruz_temp = zeros(1,11);
prod_cruz_viento = zeros(1,11);

for i=2:12;
    
%   prod_cruz_prec(i-1) = prod_prec(1,i)*prod_prob_prec(1,i-1);
  prod_cruz_temp(i-1) = prod_temp(1,i)*prod_temp(1,i-1);
  prod_cruz_viento(i-1) = prod_viento(1,i)*prod_viento(1,i-1);
end

prob_cruz_total = prod_cruz_temp .* prod_cruz_viento;