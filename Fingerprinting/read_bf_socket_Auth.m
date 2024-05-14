clc;
clear all;

addpath('CSI_basic_code','CSI_basic_code_changed');
for i=11:34
    filename= ['./Day2Hometest/Card' num2str(i)];
    filename2=['./Day2RawHometest/Card' num2str(i)];
    port = 50000;
    t1 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t1.InputBufferSize = 57900292; % for 1c911 rate,577 bytes and 100,000 packets check if the seq number and NIC Id is recored
    t1.Timeout = 140;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t1);
    fprintf('Accept connection from %s\n',t1.RemoteHost);
    
    %% Trigger the client to send CSI data
%174.84.137.20
data=sin(1:3);
senddata=num2str(data);
pause;
fprintf(t1,senddata);
% Read the data send by the Clinet
%% Receive the data from the Clientwe
data1=fread(t1);
fclose(t1);
delete(t1);
tic;
CSI_DATA=read_bf_socket(data1);
toc;

%% Scale the CSI because of the Intel specification and spatianl mapping matrix

siz=length(CSI_DATA);
CSI=struct;
for i=1:siz
    csi_entry=CSI_DATA{i};
    csi=get_scaled_csi_sm(csi_entry);
    CSI(i).csi=csi;
    
    
end

%% Final DATA

[Off1,Off2,Diff]=authFunction(CSI);
save(filename,'Off1','Off2','Diff');
save(filename2,'data1','CSI_DATA','CSI');


end
system('python discret.py')


