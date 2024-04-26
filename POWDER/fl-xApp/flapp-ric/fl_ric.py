
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
WEIGHTS = 0
BIAS = 0
EPOCHS = 10
MODEL = tf.keras.Model()
my_ns = 'fl_ric'
meid = {}

def post_init(self: RMRXapp):
    '''POST Init Function, executes on running app'''
    print(f'Ric Post init {self.healthcheck()}')


def default_handler(self: RMRXapp, summary, sbuf):
    '''Default Handler : Messages of unknow mtype received at this app rmr port are forwarded here'''
    print('defh')

# 1000 calls respond data to initializes data on UE
def model_set(self:RMRXapp, summary, sbuf):
    '''Using this function to load model in RIC side.'''
    global WEIGHTS, BIAS, EPOCHS, MODEL
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    # print(json.loads(summary[rmr.RMR_MS_MSG_SOURCE]))
    print(f'Received\n{summary.keys()}')
    # Get MEID from received message and add to meid dict
    # This is used for keeping track of Connected eNB's 
    if MODEL == 0:
        MODEL = tf.keras.utils.deserialize_keras_object(jpay['model'])
        print(f'Received Model:\n')
        MODEL.summary()
    print(f'MEIDS: {meid}')
    self.rmr_send(json.dumps({'train':'train'}),mtype=2001)


def weight_avg(self:RMRXapp, summary, sbuf):
    '''Upon receiving Weights aggregates weights from all enbs and sends them back'''
    print('weightavg')
    global WEIGHTS, BIAS, EPOCHS, MODEL
    print(f'Received New Weights\n Epochs Remaining: {EPOCHS}')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    EPOCHS = int(jpay['epochs'])
    WEIGHTS = jpay['weights']
    WEIGHTS = [np.array(i) for i in WEIGHTS]
    MODEL.set_weights(WEIGHTS)
    print(EPOCHS)
    if EPOCHS != 0:
        print(f'Epoch {EPOCHS}')
        self.rmr_send(json.dumps({'Remaining': EPOCHS}).encode(), 2001)
    else:
        try:
            print(f'Training Complete\nFinal Weights:\n{WEIGHTS}')
            MODEL.save('/nfs/model.keras')
        except Exception as e:
            print(e)


xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4562)


# message_type is unique identifier to execute function from registered callbacks
xapp.register_callback(model_set, message_type=1000)
# xapp.register_callback(train_ric, message_type=1001)
xapp.register_callback(weight_avg, message_type=1001)
# xapp.register_callback(predict, message_type=1003)
xapp.registerXapp()
xapp.run()
