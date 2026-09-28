close all
clear all
clc
%% Strain maps
% calculate strain to display in map view
%% Import data
fname1 = 'MPS_displ_field_PT_edited_v5.txt';
fid1 = fopen(fname1, 'r');
data = textscan(fid1, '%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f', 'delimiter',',', 'headerlines', 1);
fclose(fid1);
DIC_displ_matrix=cell2mat(data);

fname1 = 'MPS_displ_coords_manual_v2.txt';
fid1 = fopen(fname1, 'r');
data = textscan(fid1, '%f%f%f%f%f%f%f%f%f%f%f%f%f%f', 'delimiter',',', 'headerlines', 1);
fclose(fid1);
MANUAL_displ_matrix=cell2mat(data);

% define data vectors
x = [DIC_displ_matrix(:,3); MANUAL_displ_matrix(:,6)];
y = [DIC_displ_matrix(:,4); MANUAL_displ_matrix(:,7)];
ux = [DIC_displ_matrix(:,5); MANUAL_displ_matrix(:,13)];
uy = [(-1)*DIC_displ_matrix(:,6); MANUAL_displ_matrix(:,14)];

%% Set up grid
res = 9.6; % displacement map resolution
% create grid
xq = min(x):res:max(x); % vector containing x coordinates
yq = (min(y):res:max(y))'; % vector containing y coordinates
[Xq,Yq,Ux] = griddata(x,y,ux,xq,yq,'natural'); % interpolates scattered data in x,y to query points specified by xq,vq
[Uy] = griddata(x,y,uy,xq,yq,'natural');

figure
quiver(Xq,Yq,Ux,Uy,0)
axis equal

%% Get displacement gradient tensor
% initialize displacement gradient tensor
Dxx = zeros(length(yq),length(xq));
Dyy = zeros(length(yq),length(xq));

% calculate Dxx for each grid cell
for j=1:length(yq) % for each row
    for i=2:length(xq)-1 % calculate Dxx in each column
        Dxx(j,i) = (Ux(j,i+1)-Ux(j,i-1))/(2*res);
    end
end
% calculate Dyy for each grid cell
for i=1:length(xq) % for each column
    for j=2:length(yq)-1 % calculate Dyy in each row
        Dyy(j,i) = (Uy(j+1,i)-Uy(j-1,i))/(2*res);
    end
end
Dxy = Dxx; % valid if deltax = deltay
Dyx = Dyy;

Dxx(isnan(Dxx))= 0;
Dxy(isnan(Dxy))= 0;
Dyx(isnan(Dyx))= 0;
Dyy(isnan(Dyy))= 0;

%% Strain calculation
% initialise Lagrangian finite strain tensor
Exx = zeros(size(Dxx));
Eyy = zeros(size(Dyy));
Exy = zeros(size(Dxy));
% calculate strain tensor elements for each grid cell
for j=1:length(yq) % for each row
    for i=1:length(xq)
        Exx(j,i) = Dxx(j,i) + 0.5*((Dxx(j,i))^2+(Dyx(j,i))^2);
        Eyy(j,i) = Dyy(j,i) + 0.5*((Dxy(j,i))^2+(Dyy(j,i))^2);
        Exy(j,i) = 0.5*(Dxy(j,i) + Dyx(j,i) + Dxx(j,i)*Dxy(j,i) + Dyx(j,i)*Dyy(j,i));
    end
end
Eyx = Exy; 

dil = zeros(size(Dxx));
for j=1:length(yq) % for each column
    for i=2:length(xq) % calculate in each row
        e=[ Dxx(j,i) Dxy(j,i) 0;
            Dyx(j,i) Dyy(j,i) 0;
            0 0 0];
        [eps,pstrains,dilat,maxsh] = FinStrain(e,0);
        dil(j,i)=dilat;
    end
end

%% Export results
% compile results
coord_matrix = [Xq(:), Yq(:)];
displ_matrix = [Ux(:), Uy(:)];
E_matrix = [Exx(:), Eyy(:), Exy(:)];
dil_matrix = dil(:);
filler = zeros(size(dil_matrix));
data = horzcat(coord_matrix, displ_matrix, E_matrix, dil_matrix, filler);

% export results
T = array2table(data);
T.Properties.VariableNames(1:9) = {'x','y','Ux','Uy','Exx','Eyy','Exy',...
    'Dilation','filler'};
writetable(T,'strain_map_results_v5.txt', 'Delimiter', ',')

%% Plot strain results

% plot dilatation
figure
pcolor(Xq,Yq,dil)
axis equal
colormap(jet)
h = colorbar;
h = colorbar('Limits',[-0.5 .5]);
set(gca,'CLim',[-0.5 0.5])

%% Allmendinger 2011 Finite Strain function
function [eps,pstrains,dilat,maxsh] = FinStrain(e,frame) 
%FinStrain computes finite strain from an input displacement 
%gradient tensor 
% 
% [eps,pstrains,dilat,maxsh] = FinStrain(e,frame) % 
% e = 3 x 3 Lagrangian or Eulerian displacement gradient tensor 
% frame = Reference frame. Enter 0 for undeformed (Lagrangian) state, or 
% 1 for deformed (Eulerian) state
% eps = 3 x 3 Lagrangian or Eulerian strain tensor 
% pstrains = 3 x 3 matrix with magnitude (column 1), trend (column 2) and % 
% plunge (column 3) of maximum (row 1), intermediate (row 2), and minimum (row 3) elongations
% dilat = dilatation 
% maxsh = 1 x 2 vector with max. shear strain and orientation with 
% respect to maximum principal strain direction. Only valid in 2D
% % NOTE: Output angles are in radians % 
% FinStrain uses function CartToSph 
%Initialize variables 
eps = zeros(3,3); 
pstrains = zeros(3,3); 
maxsh = zeros(1,2); 
%Compute strain tensor (Eqs. 9.4 and 9.5) 
for i=1:3 
    for j=1:3 
        eps(i,j)=0.5*(e(i,j)+e(j,i)); 
        for k=1:3 
            %If undeformed reference frame: Lagrangian strain tensor
            if frame == 0 
                eps(i,j) = eps(i,j) + 0.5*(e(k,i)*e (k,j));
            %If deformed reference frame: Eulerian strain tensor 
            elseif frame == 1 
                eps(i,j) = eps(i,j) - 0.5*(e(k,i)*e (k,j));
            end
        end
    end
end
%Compute principal elongations and orientations. Here we use the MATLAB 
%function eig 
[V,D] = eig(eps); %Principal elongations 
for i=1:3 
    ind = 4-i; 
    %Magnitude 
    %If undeformed reference frame: Lagrangian strain tensor (Eq. 9.14) 
    if frame == 0 
        pstrains(i,1) = sqrt(1.0+2.0*D(ind,ind))-1.0;
    %If deformed reference frame: Eulerian strain tensor (Eq. 9.16) 
    elseif frame == 1 
        pstrains(i,1) = sqrt(1.0/(1.0-2.0*D(ind, ind)))-1.0;
    end
    %Orientations 
    [pstrains(i,2),pstrains(i,3)] = CartToSph(V(1, ind),V(2,ind),V(3,ind));
end
%dilatation (Eq. 9.18) 
dilat = (1.0+pstrains(1,1))*(1.0+pstrains(2,1))*(1.0+pstrains(3,1)) - 1.0; 
%Maximum shear strain: This only works if plane strain 
lmax = (1.0+pstrains(1,1))^2; %Maximum quadratic elongation 
lmin = (1.0+pstrains(3,1))^2; %Minimum quadratic elongation 
%Maximum shear strain: Ragan (1967) Eq. 3.46 
maxsh(1,1) = (lmax-lmin)/(2.0*sqrt(lmax*lmin)); 
%Angle of maximum shear strain with respect to maximum principal strain 
%Ragan (1967) Eq. 3.45 
%If undeformed reference frame 
if frame == 0 
    maxsh(1,2) = pi/4.0;
%If deformed reference frame 
elseif frame == 1 
    maxsh(1,2) = atan(sqrt(lmin/lmax));
end
end


