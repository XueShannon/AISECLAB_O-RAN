



%% Build a TCP Server and wait for connection
RX1=1;
RX2=0;
RX3=0;
RX4=0;
RX5=0;
RX6=0;
RX7=0;
RX8=0;

%% Create 8 sockets for 8 clients
if(RX1)
    port = 4001;
    t1 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t1.InputBufferSize = 60000000;
    t1.Timeout = 15;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t1);
    fprintf('Accept connection from %s\n',t1.RemoteHost);
end
if(RX2)
    port = 4002;
    t2 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t2.InputBufferSize = 300000;
    t2.Timeout = 35;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t2);
    fprintf('Accept connection from %s\n',t2.RemoteHost);
end
if(RX3)
       port = 4003;
    t3 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t3.InputBufferSize = 300000;
    t3.Timeout = 35;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t3);
    fprintf('Accept connection from %s\n',t3.RemoteHost);
end
if(RX4)
       port = 4004;
    t4 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t4.InputBufferSize = 300000;
    t4.Timeout = 35;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t4);
    fprintf('Accept connection from %s\n',t4.RemoteHost);
end
if(RX5)
       port = 4005;
    t5 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t5.InputBufferSize = 300000;
    t5.Timeout = 35;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t5);
    fprintf('Accept connection from %s\n',t5.RemoteHost);
end
if(RX6)
       port = 4006;
    t6 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t6.InputBufferSize = 300000;
    t6.Timeout = 35;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t6);
    fprintf('Accept connection from %s\n',t6.RemoteHost);
end
if(RX7)
       port = 4007;
    t7 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t7.InputBufferSize = 300000;
    t7.Timeout = 35;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t7);
    fprintf('Accept connection from %s\n',t7.RemoteHost);
end
if(RX8)
       port = 4008;
    t8 = tcpip('0.0.0.0', port, 'NetworkRole', 'server');
    t8.InputBufferSize = 300000;
    t8.Timeout = 35;
    fprintf('Waiting for connection on port %d\n',port);
    fopen(t8);
    fprintf('Accept connection from %s\n',t8.RemoteHost);
end
%% Trigger the client to send CSI data
tic
data=sin(1:3);
senddata=num2str(data);
pause;
fprintf(t1,senddata);
% Read the data send by the Clinet
tic
data1=fread(t1);
toc;
display("its not blocking");

fprintf(t2,senddata);
data2=fread(t2);

% fprintf(t3,senddata);
% data3=fread(t3);
% 
% fprintf(t4,senddata);
% data4=fread(t4);
% 
% fprintf(t5,senddata);
% data5=fread(t5);
% 
% fprintf(t6,senddata);
% data6=fread(t6);
% 
% fprintf(t7,senddata);
% data7=fread(t7);
% 
% fprintf(t8,senddata);
% data8=fread(t8);
% toc
% stop=0

    
%% Close file
    fclose(t1);
    delete(t1);
    fclose(t2);
    delete(t2);
    
%% format the CSI
read_bf_socket(data1);

