
import json
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv1D, Flatten, Dense, Concatenate
from tensorflow.keras.models import Model
from ricxappframe.xapp_frame import RMRXapp, rmr
from ricxappframe.util.constants import Constants
import time

WEIGHTS = 0 # Placeholder for weights
EPOCHS = 5  # Placeholder for epochs
my_ns = 'flapp'


'''Model Architecture'''
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
# serializes model to dictionary object for transmitting
serialized_model = tf.keras.utils.serialize_keras_object(model) 

'''Communicating MEIDs'''
meid = set() 

'''Weights from MEIDs'''
WEIGHTARRAY=[]  


def post_init(self: RMRXapp):
    global WEIGHTS, EPOCHS, serialized_model
    '''POST Init Function, executes on running app'''
    print(f'Ric Post init {self.healthcheck()}\nSDL : {self.sdl._sdl}\nPosting Model to SDL')
    self.sdl.set(my_ns, 'M', serialized_model)
    self.sdl.set(my_ns, 'E', EPOCHS)
    self.sdl.set(my_ns, 'W', WEIGHTS)
    self.logger.info(f'Model Posted to SDL')
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
    # model.summary()
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])

    meid.add(summary[rmr.RMR_MS_MEID])
    print(f'Connected enbs : {meid}')

    # If a base station requests model, sends model to the base station
    if 'REQ' in jpay:
        print('Sending Model to eNBs')
        payload = json.dumps({'model': serialized_model, 'epochs': EPOCHS, 'weights': WEIGHTS}).encode()
        self.rmr_rts(sbuf, payload,2000)
        print('Model Sent to eNBs')
    if len(meid)>1:
        print('Training Started')
        payload_2 = json.dumps({'weights': WEIGHTS, 'epochs': EPOCHS}).encode()
        time.sleep(2)
        x=self.rmr_send(payload_2, 2001)
        print(x)
        time.sleep(2)
        y=self.rmr_send(payload_2, 3001)
        print(y)
        time.sleep(1)

    

def weight_avg(self:RMRXapp, summary, sbuf):
    '''Upon receiving Weights aggregates weights from all enbs and sends them back'''
    print('Weight Average Called\n')
    global WEIGHTS, EPOCHS,WEIGHTARRAY, meid, my_ns
    
    print(f'Received New Weights from {summary[rmr.RMR_MS_MEID]}\nEpochs Remaining: {EPOCHS}')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    if EPOCHS > 0:
        # loads in individual weights and adds to weightsarray
        _WEIGHTS = jpay['weights']
        _WEIGHTS = [np.array(i) for i in _WEIGHTS]
        WEIGHTARRAY.append(_WEIGHTS)
        Avg_weights =[]
        Avg_layer = []
        if (len(meid)==len(WEIGHTARRAY)) and (len(meid)>1):
        # if (len(meid)==len(WEIGHTARRAY)):
            print('Aggregating Weights')
            EPOCHS -= 1
            for i in range(len(WEIGHTARRAY[0])):
                for j in range(len(WEIGHTARRAY)):
                    Avg_layer.append(WEIGHTARRAY[j][i])
                Avg_weights.append(np.mean(Avg_layer, axis=0))
                Avg_layer = []
            print(f'Aggregation Complete Sending Weights to eNBs\nEpochs Remaining: {EPOCHS}\nWeights Aggregated\n')
            WEIGHTS = [i.tolist() for i in Avg_weights]
            self.sdl.set(my_ns, 'E', EPOCHS)
            self.sdl.set(my_ns, 'W', WEIGHTS)
            payload = json.dumps({'weights': WEIGHTS, 'epochs': EPOCHS}).encode()
            self.rmr_send(payload, 2001)
            self.rmr_send(payload, 3001)
            WEIGHTARRAY=[]
        if EPOCHS == 0:
            payload = json.dumps({'weights': WEIGHTS}).encode()
            self.rmr_send(payload, 2001)
            time.sleep(2)
            self.rmr_send(payload, 3001)
            self.sdl.set(my_ns, 'W', WEIGHTS)
            print('Training Complete. Model saved to SDL')

# xapp initiation
xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4562)


# message_type is unique identifier to execute function from registered callbacks
xapp.register_callback(model_set, message_type=1000)
xapp.register_callback(weight_avg, message_type=1001)


xapp.run()