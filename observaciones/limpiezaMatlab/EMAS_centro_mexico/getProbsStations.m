clc
clear

load('porcentajes.mat')

prod_cruz_prec = zeros(1,11);
prod_cruz_temp = zeros(1,11);
prod_cruz_viento = zeros(1,11);

for i=2:12;
    
  prod_cruz_prec(i-1) = prod_prob_prec(1,i)*prod_prob_prec(1,i-1);
  prod_cruz_temp(i-1) = prod_prob_temp(1,i)*prod_prob_temp(1,i-1);
  prod_cruz_viento(i-1) = prod_prob_viento(1,i)*prod_prob_viento(1,i-1);
end

prob_cruz_total = prod_cruz_prec .* prod_cruz_temp .* prod_cruz_viento;