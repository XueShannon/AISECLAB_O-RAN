function [Off1,Off2,Diff_of_Diff] = authFunction(CSI)
result=struct;
for k=1:length(CSI)
    C=CSI(k).csi;
    for i=1:3
        %% handle one wrapping
        csi= angle(squeeze(C(:,i,:))); % 3 x 1 x 30 (three antennas at one rx)
        phsplot = unwrap(csi.');
        %% again handel wrapping across antenna
        for antIdForPhs = 1:3 % yesle across antenna handle gareyeo
            if  phsplot(1,antIdForPhs) - phsplot(1,1) > pi
                phsplot(:,antIdForPhs) = phsplot(:,antIdForPhs) - 2*pi;
            elseif phsplot(1,antIdForPhs) - phsplot(1,1) < -pi
                phsplot(:,antIdForPhs) = phsplot(:,antIdForPhs) + 2*pi;
            end
        end
        
        ph1=phsplot(1:15,1); % the transmitter1 phase
        ph2=wrev(phsplot(16:end,1));
        ph_a=(ph1+ph2)/2; %% this step removes the pdd and sto
        
        ph1=phsplot(1:15,2);
        ph2=wrev(phsplot(16:end,2));
        ph_b=(ph1+ph2)/2; %% this step removes the pdd and sto
        
        ph1=phsplot(1:15,3);
        ph2=wrev(phsplot(16:end,3));
        ph_c=(ph1+ph2)/2; %% this step removes the pdd and sto
         R(i).P_TX1(:,k)=ph_a; % i= 1, receiver 1 is the TX1
          R(i). P_TX2(:,k)=ph_b;
        R(i).P_TX3(:,k)=ph_c;
        
    end
end


%% Phase difference 
R1_TX21=R(1).P_TX2-R(1).P_TX1; % three tx antenna with rx 1
R2_TX21=R(2).P_TX2-R(2).P_TX1; % three tx antenna with rx 2
R3_TX21=R(3).P_TX2-R(3).P_TX1; % three tx antenna with rx 3


R1_TX32=R(1).P_TX3-R(1).P_TX2; % three tx antenna with rx 1
R2_TX32=R(2).P_TX3-R(2).P_TX2; % three tx antenna with rx 2
R3_TX32=R(3).P_TX3-R(3).P_TX2; % three tx antenna with rx 3

%% take the average of subcarriers in the Middle for antenna 1 and 2

R1_off1=mean(R1_TX21(10:15,:),1); % these readings are in radians
R2_off1=mean(R2_TX21(10:15,:),1);
R3_off1=mean(R3_TX21(10:15,:),1);

R1_off2=mean(R1_TX32(10:15,:),1);
R2_off2=mean(R2_TX32(10:15,:),1);
R3_off2=mean(R3_TX32(10:15,:),1);

%%

  R1_O1 = rad2deg(angle(exp(1i*R1_off1)));
  R2_O1 = rad2deg(angle(exp(1i*R2_off1)));
  R3_O1 = rad2deg(angle(exp(1i*R3_off1)));
  
    R1_O2 = rad2deg(angle(exp(1i*R1_off2)));
  R2_O2 = rad2deg(angle(exp(1i*R2_off2)));
  R3_O2 = rad2deg(angle(exp(1i*R3_off2)));
  
  %%
  
  Off1= [R1_O1; R2_O1; R3_O1].';

Off2 = [R1_O2; R2_O2; R3_O2].';

%% Third reflection handle
% % Off1
 for i=1:size(Off1,2)
for c=1:size(Off1,1)
    if Off1(c,i)>90 
        Off1(c,i)=Off1(c,i)-180;
     elseif Off1(c,i)<-90 
        Off1(c,i)=Off1(c,i)+180;
    end
end
 end
% 
% % Off2
for i=1:size(Off2,2)
 for c=1:size(Off2,1)
     if Off2(c,i)>90 
         Off2(c,i)=Off2(c,i)-180;
     elseif Off2(c,i)<-90 
         Off2(c,i)=Off2(c,i)+180;
     end
 end
 end
R1_O1=Off1(:,1);
R2_O1=Off1(:,2);
R3_O1=Off1(:,3);
R1_O2=Off2(:,1);
R2_O2=Off2(:,2);
R3_O2=Off2(:,3);
 
Diff_of_Diff = Off2-Off1;

end