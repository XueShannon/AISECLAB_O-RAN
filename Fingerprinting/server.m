clear all
close all
clc
using_client_1=1
using_client_2=1
if(using_client_1)
    t1 = tcpip('localhost', 5005, 'NetworkRole', 'server');
    set(t1, 'InputBufferSize', 1024);
    fopen(t1);
end
if(using_client_2)
    t2 = tcpip('localhost', 5006, 'NetworkRole', 'server');
    set(t2, 'InputBufferSize', 1024);
    fopen(t2);
end



data = sin(1:3)

while(1)
    senddata=num2str(data);
    if(using_client_1)
        fprintf(t1, senddata)    % fprintf, write data to text file. fwrite, write data to binary file
        while (get(t1, 'BytesAvailable') ==0)  % block the program until bytesavailable
        end
        DataReceived1 = fscanf(t1)
        Numeceived1=str2num(DataReceived1)
    end
    if(using_client_2)
        fprintf(t2, senddata)
        while (get(t2, 'BytesAvailable') ==0)
        end
        DataReceived2 = fscanf(t2)
        Numeceived2=str2num(DataReceived2)
    end
    pause(0.01);
end