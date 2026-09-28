clear all
close all
clc

%% Import data
data = readtable('strain_sensitivity_v6_withsitechar.xlsx');
strain = data.strainMax1;
slope = data.angle;
stage = data.FailureStage;
selection = string(data{:,21});

%% plot data points
figure('Position', [10 10 750 600])
tiledlayout(2,2)
nexttile
e = data.strainMax1(data.FailureStage < 3,:);
% e = strain(stage~=3);
alpha = data.angle(data.FailureStage < 3,:);
% alpha = slope(stage~=3);
scatter(alpha,e,'k.')
hold on
% get linear fit
X = [ones(length(alpha),1) alpha];
b = X\e;
eCalc = X*b;
Rsq = 1 - sum((e - eCalc).^2)/sum((e - mean(e)).^2);
% plot linear fit
plot(alpha,eCalc,'k--')
hold on
ax = gca;
ax.FontSize = 12; 
eqn = string('\epsilon = ' + string(round(b(2),4)) + '\alpha + ' + string(round(b(1),4)));
text(48,0.15,eqn,...
    'HorizontalAlignment','right','VerticalAlignment','top')
text(48,0.14,string("R^{2} = "+round(Rsq,3)),...
    'HorizontalAlignment','right','VerticalAlignment','top')
ylabel('\epsilon_{max} [-]','FontSize',14)
xlabel('\alpha [°]','FontSize',14)
xlim([30 48])
ylim([0 0.15])

%% Derive FI
m = b(2);
FI = data.strainMax1 - m*data.angle;


%% Plot FI contours Subplot 2
nexttile
FI_range = (0.21:0.01:0.27);
ln = size(FI_range');
color = jet(ln(1));

alpha_range = [30 48];
for i=1:size(FI_range')
    y1 = m*alpha_range(1)+FI_range(i);
    y2 = m*alpha_range(2)+FI_range(i);
    FI_plot = plot(alpha_range,[y1 y2]);
    FI_plot.Color = color(i,:);
    hold on
end

for l=1:size(strain)
    disp('start of loop')
    if isequal(selection{l},'yes')
        disp('yes')
        if stage(l) == 1
            scatter(slope(l),strain(l),'k*')
        elseif stage(l) == 2
            scatter(slope(l),strain(l),'kd')
        elseif stage(l) == 4
            scatter(slope(l),strain(l),'k.')
        else
            disp('data point not plotted')
        end
    elseif isequal(selection{l},'no')
        disp('no')
        if stage(l) == 2
            scatter(slope(l),strain(l),[],[0.5 0.5 0.5],'d')
        elseif stage(l) == 4
            scatter(slope(l),strain(l),[],[0.5 0.5 0.5],'.')
        else
            disp('data point not plotted')
        end     
    else
        disp('no selection')     
    end
    disp('end of loop')
    hold on
end    

ax = gca;
ax.FontSize = 12; 
xlim([30 48])
ylim([0 0.15])
ylabel('\epsilon_{max} [-]','FontSize',14)
xlabel('\alpha [°]','FontSize',14)


%% Plot FI for failure stages Subplot 3
nexttile
scatter(stage, FI,'k.')
hold on
for i=1:size(FI_range')
    FI_plot = plot([0.5 4.5],[FI_range(i) FI_range(i)]);
    FI_plot.Color = color(i,:);
    hold on
end
ax = gca;
ax.FontSize = 12; 
xticks([1 2 3 4])
xlim([0.5 4.5])
ylabel('Transitional Slope Strain Index (TSSI)','FontSize',12)
xlabel('Failure Stage','FontSize',12)


%% Plot nr of failures with FI subplot 4
nexttile
FI_sel = FI(selection=='yes');
FI_1_2 = FI(stage<3);
n_profiles = zeros(size(FI_range));
n_total = zeros(size(FI_range));
n_stable = 0;
n_stage2 = 0;

for i=1:size(FI_range')
    for k=1:size(FI_sel)
        if FI_sel(k) > FI_range(i)
            n_profiles(i)=1+n_profiles(i);  
        end
    end
    for l=1:size(FI_1_2)
        if FI_1_2(l) > FI_range(i)
            n_total(i)=1+n_total(i);
        end
    end
end

ax = gca;
ax.FontSize = 12; 
plot(FI_range,(n_profiles/7)*100,'k.-')
hold on
plot(FI_range,(n_total/17)*100,'Color',[0.5 0.5 0.5],'Marker','.')
xlabel('Transitional Slope Strain Index (TSSI)','FontSize',12)
ylabel('% of observations','FontSize',12)


