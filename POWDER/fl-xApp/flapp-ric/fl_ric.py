
import json
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from ricxappframe.xapp_frame import RMRXapp, rmr
from ricxappframe.util.constants import Constants
# os.environ['RMR_SEED_RT']='test_route.rt'
# os.environ[Constants.CONFIG_PATH]='init/flapp-config.json'
# os.environ[Constants.CONFIG_FILE_ENV] = 'init/flapp-config.json'
WEIGHTS = 0 # Placeholder for weights
EPOCHS = 0  # Placeholder for epochs
MODEL = 0   # Placeholder for model
my_ns = 'fl_ric'
meid = {}
WEIGHTARRAY=[]  # List store weights received from eNBs and aggregated them on weight_avg
def post_init(self: RMRXapp):
    '''POST Init Function, executes on running app'''
    print(f'Ric Post init {self.healthcheck()}')


def default_handler(self: RMRXapp, summary, sbuf):
    '''Default Handler : Messages of unknow mtype received at this app rmr port are forwarded here'''
    print('defh')

# 1000 calls respond data to initializes data on UE
def model_set(self:RMRXapp, summary, sbuf):
    '''Using this function to load model in RIC side.
    If model exists then sends current weights and remaining training epochs'''
    global WEIGHTS, BIAS, EPOCHS, MODEL
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    # print(json.loads(summary[rmr.RMR_MS_MSG_SOURCE]))
    print(f'Received\n{summary.keys()}')
    # Get MEID from received message and add to meid dict
    # This is used for keeping track of Connected eNB's 
    print(f'MEIDS: {meid}')
    if MODEL == 0:
        MODEL = tf.keras.utils.deserialize_keras_object(jpay['model'])
        print(f'Received Model:\n')
        MODEL.summary()
    if EPOCHS==0:
        EPOCHS = jpay['epochs']
    if WEIGHTS!=0:
        _weights = [i.tolist() for i in WEIGHTS]
        self.rmr_send(json.dumps({'epochs': EPOCHS, 'weights':_weights}).encode(),mtype=2001)
    else:
        self.rmr_send(json.dumps({'epochs': EPOCHS}).encode(),mtype=2001)


def weight_avg(self:RMRXapp, summary, sbuf):
    '''Upon receiving Weights aggregates weights from all enbs and sends them back'''
    print('weightavg')
    global WEIGHTS, BIAS, EPOCHS, MODEL,WEIGHTARRAY
    
    print(f'Received New Weights\nEpochs Remaining: {EPOCHS}')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    EPOCHS -= 1
    # loads in individual weights and adds to weightsarray
    _WEIGHTS = jpay['weights']
    _WEIGHTS = [np.array(i) for i in _WEIGHTS]
    WEIGHTARRAY.append(_WEIGHTS)
    
    # upon receiveing 'n' number of weights in array(2 here) averages the weights
    # and sends back weights and epochs remaining to eNBs
    if len(WEIGHTARRAY)==2:
        WEIGHTS=[np.mean([arr1, arr2], axis=0) for arr1, arr2 in zip(WEIGHTARRAY[0], WEIGHTARRAY[1])]
        MODEL.set_weights(WEIGHTS)
        WEIGHTARRAY=[]
        WEIGHTS = [i.tolist() for i in WEIGHTS]
        print(EPOCHS)
        if EPOCHS != 0:
            print(f'Epoch {EPOCHS}')
            self.rmr_send(json.dumps({'epochs': EPOCHS, 'weights':WEIGHTS}).encode(), 2001)
        else:
            try:
                print(f'Training Complete\nFinal Weights:\n{WEIGHTS}')
                MODEL.save('model.keras')
            except Exception as e:
                print(e)


# xapp initiation
xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4562)


# message_type is unique identifier to execute function from registered callbacks
xapp.register_callback(model_set, message_type=1000)
# xapp.register_callback(train_ric, message_type=1001)
xapp.register_callback(weight_avg, message_type=1001)
# xapp.register_callback(predict, message_type=1003)
xapp.run()