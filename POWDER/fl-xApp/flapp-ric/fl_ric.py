
import json
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from ricxappframe.xapp_frame import RMRXapp, rmr
from ricxappframe.util.constants import Constants
from ricsdl.syncstorage import SyncStorage


# os.environ['RMR_SEED_RT']='test_route.rt'
# os.environ[Constants.CONFIG_PATH]='init/flapp-config.json'
# os.environ[Constants.CONFIG_FILE_ENV] = 'init/flapp-config.json'
WEIGHTS = 0 # Placeholder for weights
EPOCHS = 0  # Placeholder for epochs
MODEL = 0   # Placeholder for model
my_ns = 'flapp'

# SDL wrapper to store and retrieve data
sdl = SyncStorage()
# Model Setup
model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10)
])
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

# serializes model to dictionary object
serialized_model = tf.keras.utils.serialize_keras_object(model)
meid = set() # Placeholder for MEID
WEIGHTARRAY=[]  # List store weights received from eNBs and aggregated them on weight_avg
def post_init(self: RMRXapp):
    global WEIGHTS
    '''POST Init Function, executes on running app'''
    print(f'Ric Post init {self.healthcheck()}\nSDL : {self.sdl._sdl}\nPosting Model to SDL')
    self.sdl.set(my_ns, 'model', serialized_model)
    self.sdl.set(my_ns, 'epochs', 10)
    self.sdl.set(my_ns, 'weights', WEIGHTS)
    self.logger.info(f'Model Posted to SDL')
    print(f'Model Posted to SDL')
    model.summary()


def default_handler(self: RMRXapp, summary, sbuf):
    '''Default Handler : Messages of unknow mtype received at this app rmr port are forwarded here'''
    print('defh')

# 1000 calls respond data to initializes data on UE
def model_set(self:RMRXapp, summary, sbuf):
    '''This Function Receives Acknowledgement from eNBs and intializes training on eNBs'''
    global WEIGHTS, EPOCHS, MODEL, WEIGHTARRAY, sdl, meid
    print(f'Model Set Called\n received from eNBs\n{summary[rmr.RMR_MS_PAYLOAD]}')
    
    
    if EPOCHS !=0:
    # calling Train at eNBs
        payload = json.dumps({'ACK': f'Model Set at {summary[rmr.RMR_MS_MEID]}'}).encode()
        sbuf = rmr.rmr_alloc_msg(vctx=self._mrc, size=len(payload),payload=payload,
                                gen_transaction_id=True, meid=b'RIC', mtype=2001)
        for _ in range(100):
            sbuf = rmr.rmr_send_msg(self._mrc, sbuf)
            if sbuf.contents.state == 0:
                self.rmr_free(sbuf)
                break
        EPOCHS -= 1
        self.sdl.set(my_ns, 'epochs', EPOCHS)
    else:
        print('Training Complete')
        MODEL.save('model.keras')
        payload = json.dumps({'ACK': 'Training Complete'}).encode()
        sbuf = rmr.rmr_alloc_msg(vctx=self._mrc, size=len(payload),payload=payload,
                                gen_transaction_id=True, meid=b'RIC', mtype=2001)
        for _ in range(100):
            sbuf = rmr.rmr_send_msg(self._mrc, sbuf)
            if sbuf.contents.state == 0:
                self.rmr_free(sbuf)
                break
    
    


def weight_avg(self:RMRXapp, summary, sbuf):
    '''Upon receiving Weights aggregates weights from all enbs and sends them back'''
    print('weightavg')
    global WEIGHTS, EPOCHS, MODEL,WEIGHTARRAY, sdl
    
    print(f'Received New Weights\nEpochs Remaining: {EPOCHS}')
    # jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    # EPOCHS -= 1
    # # loads in individual weights and adds to weightsarray
    # _WEIGHTS = jpay['weights']
    # _WEIGHTS = [np.array(i) for i in _WEIGHTS]
    # WEIGHTARRAY.append(_WEIGHTS)
    
    # # upon receiveing 'n' number of weights in array(2 here) averages the weights
    # # and sends back weights and epochs remaining to eNBs
    # if len(WEIGHTARRAY)==2:
    #     WEIGHTS=[np.mean([arr1, arr2], axis=0) for arr1, arr2 in zip(WEIGHTARRAY[0], WEIGHTARRAY[1])]
    #     MODEL.set_weights(WEIGHTS)
    #     WEIGHTARRAY=[]
    #     WEIGHTS = [i.tolist() for i in WEIGHTS]
    #     print(EPOCHS)
    #     if EPOCHS != 0:
    #         print(f'Epoch {EPOCHS}')
    #         self.rmr_send(json.dumps({'epochs': EPOCHS, 'weights':WEIGHTS}).encode(), 2001)
    #     else:
    #         try:
    #             print(f'Training Complete\nFinal Weights:\n{WEIGHTS}')
    #             MODEL.save('model.keras')
    #         except Exception as e:
    #             print(e)
    
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    EPOCHS -= 1
    # loads in individual weights and adds to weightsarray
    _WEIGHTS = jpay['weights']
    _WEIGHTS = [np.array(i) for i in _WEIGHTS]
    WEIGHTARRAY.append(_WEIGHTS)
    if len(meid)==len(WEIGHTARRAY):
        WEIGHTS = np.mean(WEIGHTARRAY, axis=0)
        WEIGHTS = [i.tolist() for i in WEIGHTS]
        self.sdl.set(my_ns, 'weights', WEIGHTS)


# xapp initiation
xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=False, rmr_port=4562)


# message_type is unique identifier to execute function from registered callbacks
xapp.register_callback(model_set, message_type=1000)
# xapp.register_callback(train_ric, message_type=1001)
xapp.register_callback(weight_avg, message_type=1001)
# xapp.register_callback(predict, message_type=1003)
xapp.run()