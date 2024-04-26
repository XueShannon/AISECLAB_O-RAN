# xAPP

### the architecture currently consists of two apps fl-ric and fl-ue, currently written to work on stochastic gradient descent but training can be more generalized and with DL-Frameworks (Tensorflow, PyTorch)

## fl-ric
 - This is the xAPP on RIC which intializes PARAMS and sends DATA/DATA source to UE
 - Upon data request transmits data and calls consecutive training callbacks on UE script
 - Upon receiving weights averages them and sends to UEs to update model and train further if required (Epochs not completed)
 - allows for UEs to join in at anytime in training and shares current weights and other Params with UEs
 - allows for predict method for UE's to only get results of current model


## fl-ue
 - This is xAPP which Communicates with RIC and is situated on UE
 - upon initilizing requests DATA and other params to train on.
 - while epochs not completed will train and share weights with RIC to aggregate

 ## Execution
  - Linux :
    1. fl-ric execution
    ``` 
    $ cd fl-xapp
    $ PYTHONUNBUFFERED=1 RMR_SEED_RT=./flapp-ric/test_route.rt python ./flapp-ric/fl_ric.py 
    ```
    2. fl-ue execution 
    ```
    $ cd fl-xapp
    $ PYTHONUNBUFFERED=1 RMR_SEED_RT=./flapp-ue/test_route.rt python ./flapp-ue/fl_ue.py 
    ```
  - Docker 
    1. fl-ric
    ``` 
    $ cd flapp-ric
    $ docker build -t flric:latest -f Dockerfile .
    $ docker run --net=host flric:latest
    ```
    2. fl-enb
    ``` 
    $ cd flapp-ue
    $ docker build -t flenb:latest -f Dockerfile .
    $ docker run --net=host flue:latest
    ```
  
### Powder xApp onboarding

1. Create local docker registry to load image and tag image with local registry.
    ```
    $ docker run -d -p 5000:5000 --name registry registry:2.7

    $ docker tag flric:latest localhost:5000/flric:latest
    ```

2. Push the image
    ```
    $ docker push localhost:5000/flric:latest
    ```
3. onboard xapp config files
    ```
    $ /local/setup/oran/dms_cli onboard \
        /local/profile-public/ricapp-config.json \
        /local/setup/oran/xapp-embedded-schema.json
    ```

4. Verify App onboarding
    ```
    $ /local/setup/oran/dms_cli get_charts_list
    ```

5. Deploy App
    ```
    $ /local/setup/oran/dms_cli install \
        --xapp_chart_name=ric-app-fl --version=1.0.0 --namespace=ricxapp
    ```
6. View Outputs
    ```
    $ kubectl logs -f -n ricxapp -l app=ricxapp-ric-app-fl
    ```

# Outputs

## Ric Script
<img src = outputs\ricout.png>
<img src = outputs\ricout1.png>

## ENB Script
**eNB 1**
<img src = outputs\EPC-outputs.png>

**eNB 2**
<img src = outputs\EPC-outputs-1.png>

## POWDER Outputs

<img src = outputs\XAPP-Onboard-1.png>


 # In-progress
  - Currently the app works over a single system over localhost need to implement proper routing over n/w using E2-Interface
  - Implement proper SDL Layer and PUB-SUB
    - Currently app only uses RTS (Return to sender method) rather transmitting to nodes using Publication Subscription
 - implementation over actual network (Resourse reservation requested for tuesday 4/9)
