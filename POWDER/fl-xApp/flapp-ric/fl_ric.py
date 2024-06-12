
import json
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv1D, Flatten, Dense, Concatenate
from tensorflow.keras.models import Model
from ricxappframe.xapp_frame import RMRXapp, rmr
from ricxappframe.util.constants import Constants
from ricsdl.syncstorage import SyncStorage


# os.environ['RMR_SEED_RT']='test_route.rt'
# os.environ[Constants.CONFIG_PATH]='init/flapp-config.json'
# os.environ[Constants.CONFIG_FILE_ENV] = 'init/flapp-config.json'
WEIGHTS = 0 # Placeholder for weights
EPOCHS = 5  # Placeholder for epochs
my_ns = 'flapp'


# Model Setup
# Define input layers
input1 = Input(shape=(52,1), name='magnitude')
input2 = Input(shape=(52,1), name='phase')

# Conv1D processing for Magnitude
x1 = Conv1D(filters=16, kernel_size=3, activation='relu', name='magitude_conv')(input1)
x1 = Flatten()(x1)

# Conv1D processing for Phase
x2 = Conv1D(filters=16, kernel_size=3, activation='relu', name='phase_conv')(input2)
x2 = Flatten()(x2)

# Concatenate the processed inputs
concatenated = Concatenate()([x1, x2])

# Add dense layers for classification
x = Dense(32, activation='relu')(concatenated)
output = Dense(1, activation='sigmoid')(x)

# Create the model
model = Model(inputs=[input1, input2], outputs=output, name='rf_fingerprinting')

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# serializes model to dictionary object
serialized_model = tf.keras.utils.serialize_keras_object(model)
meid = set() # Placeholder for MEID
WEIGHTARRAY=[]  # List store weights received from eNBs and aggregated them on weight_avg
def post_init(self: RMRXapp):
    global WEIGHTS, EPOCHS, serialized_model
    '''POST Init Function, executes on running app'''
    print(f'Ric Post init {self.healthcheck()}\nSDL : {self.sdl._sdl}\nPosting Model to SDL')
    self.sdl.set(my_ns, 'model', serialized_model)
    self.sdl.set(my_ns, 'epochs', EPOCHS)
    self.sdl.set(my_ns, 'weights', WEIGHTS)
    self.logger.info(f'Model Posted to SDL')
    # payload = json.dumps({'PING': 'PONG'}).encode()
    # self.rmr_send(payload, 2000)
    print(f'Model Posted to SDL')
    


def default_handler(self: RMRXapp, summary, sbuf):
    '''Default Handler : Messages of unknow mtype received at this app rmr port are forwarded here'''
    print('defh')

# 1000 calls respond data to initializes data on UE
def model_set(self:RMRXapp, summary, sbuf):
    '''This Function Receives Acknowledgement from eNBs and intializes training on eNBs'''
    global WEIGHTS, EPOCHS, serialized_model, meid
    print(f'Model Set Called\n received from eNBs\n{summary[rmr.RMR_MS_PAYLOAD]}')
    print('Model:\n')
    model.summary()
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])

    meid.add(summary[rmr.RMR_MS_MEID])
    print(f'Connected enbs : {meid}')
    if 'REQ' in jpay:
        print('Sending Model to eNBs')
        payload = json.dumps({'model': serialized_model, 'epochs': EPOCHS, 'weights': WEIGHTS}).encode()
        sbuf = rmr.rmr_alloc_msg(vctx=self._mrc, size=len(payload), payload=payload,
                                 gen_transaction_id=True, meid=b'RIC01', mtype=2000)
        for _ in range(100):
            sbuf = rmr.rmr_send_msg(self._mrc, sbuf)
            if sbuf.contents.state == 0:
                self.rmr_free(sbuf)
                break
        print('Model Sent to eNBs')
        

def weight_avg(self:RMRXapp, summary, sbuf):
    '''Upon receiving Weights aggregates weights from all enbs and sends them back'''
    print('weightavg')
    global WEIGHTS, EPOCHS,WEIGHTARRAY, meid, my_ns
    
    print(f'Received New Weights\nEpochs Remaining: {EPOCHS}')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    if EPOCHS > 0:
        # loads in individual weights and adds to weightsarray
        _WEIGHTS = jpay['weights']
        # _WEIGHTS = [np.array(i) for i in _WEIGHTS]
        WEIGHTARRAY.append(_WEIGHTS)
        Avg_weights =[]
        Avg_layer = []
        if (len(meid)==len(WEIGHTARRAY)):
            print('Aggregating Weights')
            EPOCHS -= 1
            for i in range(len(WEIGHTARRAY[0])):
                for j in range(len(WEIGHTARRAY)):
                    Avg_layer.append(WEIGHTARRAY[j][i])
                Avg_weights.append(np.mean(Avg_layer, axis=0))
                Avg_layer = []
            print(f'Epochs Remaining: {EPOCHS}\nWeights Aggregated\n')
    WEIGHTS = [i.tolist() for i in Avg_weights]
    self.sdl.set(my_ns, 'epochs', EPOCHS)
    self.sdl.set(my_ns, 'weights', WEIGHTS)
    payload = json.dumps({'weights': WEIGHTS, 'epochs': EPOCHS}).encode()
    sbuf = rmr.rmr_alloc_msg(vctx=self._mrc, size=len(payload), payload=payload,
                             gen_transaction_id=True, meid=b'RIC1', mtype=2001)
    for _ in range(100):
        sbuf = rmr.rmr_send_msg(self._mrc, sbuf)
        if sbuf.contents.state == 0:
            self.rmr_free(sbuf)
            break

# xapp initiation
xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4562)


# message_type is unique identifier to execute function from registered callbacks
xapp.register_callback(model_set, message_type=1000)
xapp.register_callback(weight_avg, message_type=1001)
xapp.run()
