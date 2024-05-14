csi_trace = read_bf_file('EthernetTesting.dat');
siz= length(csi_trace);
resultOrig=struct;

for i=1:siz
csi_entry = csi_trace{i};
csi = get_scaled_csi_sm(csi_entry);
resultOrig(i).csi=csi;
end
a=0;