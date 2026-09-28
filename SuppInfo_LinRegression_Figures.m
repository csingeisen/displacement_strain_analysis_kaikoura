clear all
close all
clc

%% Input
data = readtable('strain_sensitivity_v6_withsitechar.xlsx');
data.slopeAv(isnan(data.slopeAv(:)))=0;
num_data = height(data);

dmax_coeff = readtable('d_max_OLS_v3.csv');
dmax_coeff{:,:}(isnan(dmax_coeff{:,:}))=0;
num_models_dmax = height(dmax_coeff);
TSDI=zeros(num_data,num_models_dmax);

for i=1:num_models_dmax        %
    TSDI(:,i)=data.dMax - (dmax_coeff.angle(i).*data.angle+...
        dmax_coeff.convexityMax(i)*data.convexityMax+...
        dmax_coeff.slopeInc(i)*data.slopeInc+...
        dmax_coeff.slopeAv(i)*data.slopeAv+...
        dmax_coeff.slopeMax(i)*data.slopeMax+...
        dmax_coeff.fRupt(i)*data.fRupt+...
        dmax_coeff.fActive(i)*data.fActive+...
        dmax_coeff.h(i)*data.h...
        );
end

emax_coeff = readtable('e_max_OLS_v3.csv');
emax_coeff{:,:}(isnan(emax_coeff{:,:}))=0;
num_models_emax = height(emax_coeff);
TSSI=zeros(num_data,num_models_emax);

for i=1:num_models_emax
    TSSI(:,i)=data.strainMax1 - (emax_coeff.angle(i).*data.angle+...
        emax_coeff.convexityMax(i)*data.convexityMax+...
        emax_coeff.slopeInc(i)*data.slopeInc+...
        emax_coeff.slopeAv(i)*data.slopeAv+...
        emax_coeff.slopeMax(i)*data.slopeMax+...
        emax_coeff.fRupt(i)*data.fRupt+...
        emax_coeff.fActive(i)*data.fActive+...
        emax_coeff.h(i)*data.h...
        );
end

% Plot TSDI for different models
figure
for i=1:num_models_dmax
    subplot(9,5,i)
    scatter(data.FailureStage, TSDI(:,i),'k.')
    hold on
    xlim([0.5 4.5])
    title(append(string(i)))
    text(4.5,max(TSDI(:,i)),string(round(dmax_coeff.r2_adj(i),3)),...
    'HorizontalAlignment','right','VerticalAlignment','top','Color','red')
end

% Plot TSSI for different models
figure
for i=1:num_models_dmax
    subplot(9,5,i)
    scatter(data.FailureStage, TSSI(:,i),'k.')
    hold on
    xlim([0.5 4.5])
    title(append(string(i)))
    text(4.5,max(TSSI(:,i)),string(round(emax_coeff.r2_adj(i),3)),...
    'HorizontalAlignment','right','VerticalAlignment','top','Color','red')    
end

% Identify single variable models
singlevar_models_dmax = [32 33 34 36 38 40 43 44];
singlevar_models_emax = [1 11 12 35 40 41 43 44];

%% Barplot R2 results
figure
subplot(2,1,1)
b1 = bar(dmax_coeff.r2_adj,'FaceColor','flat'); %,'k'
for i=1:length(singlevar_models_dmax)
    b1.CData(singlevar_models_dmax(i),:) = [0 0.8 0.8];
end
ylabel('adjusted R^{2}')
ylim([-0.1 1.1])
xlim([0.5 num_models_dmax+0.5])

subplot(2,1,2)
%bar(emax_coeff.r2,'k')
b2 = bar(emax_coeff.r2_adj,'FaceColor','flat'); %,'k'
for i=1:length(singlevar_models_emax)
    b2.CData(singlevar_models_emax(i),:) = [0 0.8 0.8];
end
ylabel('adjusted R^{2}')
ylim([-0.1 1.1])
xlim([0.5 num_models_emax+0.5])

%% 
figure
for i=1:10
    subplot(2,5,i)
    scatter(data.FailureStage, TSDI(:,i),'k.')
    hold on
    xlim([0.5 4.5])
    title(append(string(i)))% 'Model Rank ',
    text(4.5,max(TSDI(:,i)),string(round(dmax_coeff.r2_adj(i),3)),...
    'HorizontalAlignment','right','VerticalAlignment','top','Color','red','FontSize',12)
    ax = gca;
    ax.FontSize = 12; 
end

figure
for i=1:10
    subplot(2,5,i)
    scatter(data.FailureStage, TSSI(:,i),'k.')
    hold on
    xlim([0.5 4.5])
    title(append(string(i))) %'Model Rank ',
    text(4.5,max(TSSI(:,i)),string(round(emax_coeff.r2_adj(i),3)),...
    'HorizontalAlignment','right','VerticalAlignment','top','Color','red','FontSize',12)   
    ax = gca;
    ax.FontSize = 12; 
end


%% Single variable linear correlations
% figure
% subplot(3,1,1)
% scatter(data.angle,data.strainMax1)
% subplot(3,1,2)
% scatter(data.fActive,data.strainMax1)
% subplot(3,1,3)
% scatter(data.slopeMax,data.strainMax1)

