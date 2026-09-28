close all
clear all
clc

%% Correlate crack density and strain (dilation)

data = readtable('strain_map_v5_with_cracklength.txt');
cracklength = data{:,11};
crackdensity = cracklength/(pi*4.8^2);
dilation = data{:,9};

figure
scatter(crackdensity, dilation,'k.')
hold on
% get linear fit
X = [ones(length(crackdensity),1) crackdensity];
b = X\dilation;
yCalc = X*b;
Rsq = 1 - sum((dilation - yCalc).^2)/sum((dilation - mean(dilation)).^2);
% plot linear fit
linear_fit = plot(crackdensity,yCalc);
linear_fit.Color = [0.7 0.7 0.7];
eqn = string('y = ' + string(b(2))) + ' x + ' + string(b(1));
text(max(crackdensity),max(dilation),eqn,...
    'HorizontalAlignment','right','VerticalAlignment','top',...
    'Color','#808080','FontSize',10)
text(max(crackdensity),max(dilation)-0.05,string("R^{2} = "+Rsq),...
    'HorizontalAlignment','right','VerticalAlignment','top',...
    'Color','#808080','FontSize',10)
xlabel('Ground crack intensity P21 [m^{-1}]')
ylabel('Dilatation [-]')
