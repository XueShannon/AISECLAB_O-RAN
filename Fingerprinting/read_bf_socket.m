function ret= read_bf_socket(d1)

len=length(d1); % length of the total data

%% Initialize variables
ret = cell(ceil(len/95),1);     % Holds the return values - 1x1 CSI is 95 bytes big, so this should be upper bound
cur = 1;                        % Current offset into file
count = 0;                      % Number of records output
broken_perm = 0;                % Flag marking whether we've encountered a broken CSI yet
triangle = [1 3 6];             % What perm should sum to for 1,2,3 antennas
d=0;
%%
%% Process all entries in file
% Need 3 bytes -- 2 byte size field and 1 byte code
while cur < (len - 580)
    
   l1=bitshift(d1(cur),8);
   l2=d1(cur+1);
   field_len=l1+l2;
   code=d1(cur+2);
   cur=cur+3;
  
   
   %% two code types 193 and 187
   d=d+1;
   if(code==193)
       bytes=d1(cur:d*(field_len-1)+d*3);%4:576
       cur=cur+field_len-1;
       
   end
   if(code==187)
       bytes=d1(cur:d*(field_len-1)+d*3);%4:576
       cur=cur+field_len-1;
       
       
   end
   
   %% process the csi data
   if(code==187)
       count=count+1;
       ret{count}=read_bfee_changed(uint8(bytes));
       ret{count}.NID=dec2hex(ret{count}.NID);  %CHANGED;

       perm = ret{count}.perm;
      Nrx = ret{count}.Nrx;
      NID=dec2hex(ret{count}.NID);

        if Nrx == 1 % No permuting needed for only 1 antenna
            continue;
        end
   
   if sum(perm) ~= triangle(Nrx) % matrix does not contain default values
            if broken_perm == 0
                broken_perm = 1;
                fprintf('WARN ONCE: Found CSI (%s) with Nrx=%d and invalid perm=[%s]\n', filename, Nrx, int2str(perm));
            end
        else
            ret{count}.csi(:,perm(1:Nrx),:) = ret{count}.csi(:,1:Nrx,:);
        end
     ret{count}.csi(:,perm(1:Nrx),:) = ret{count}.csi(:,1:Nrx,:);
   
end
end
ret=ret(1:count);
end
