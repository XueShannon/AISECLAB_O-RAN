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
    2. fl-ue
    ``` 
    $ cd flapp-ue
    $ docker build -t flue:latest -f Dockerfile .
    $ docker run --net=host flue:latest
    ```

# Outputs

## Ric Script
<img src = outputs\ricout.png>
<img src = outputs\ricout1.png>

## UE Script
<img src = outputs\UEside.png>

 # In-progress
  - Currently the app works over a single system over localhost need to implement proper routing over n/w using E2-Interface
  - Implement proper SDL Layer and PUB-SUB
    - Currently app only uses RTS (Return to sender method) rather transmitting to nodes using Publication Subscription
 - implementation over actual network (Resourse reservation requested for tuesday 4/9)
