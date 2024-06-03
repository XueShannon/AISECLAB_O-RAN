import time
import json
import numpy as np
from ricxappframe.xapp_frame import RMRXapp, rmr
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from ricsdl.syncstorage import SyncStorage


# Setting device MEID
meid = os.environ['MEID'] = bytes('enb01', 'utf-8')

# Loading Data (Dummy Data for Development)
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0


# Setting Params
weights = 0
epochs = 10
my_ns = 'flapp'
model = None


def post_init(self: RMRXapp):
    '''POST Init Function, executes on running app sends serialized model object to RIC'''
    global epochs, model, meid, weights
    print(f'eNB Post Init: {self.healthcheck()}\neNBs Connected {self.sdl._sdl} \nsending model \n')
    serialized_model = self.sdl.get(my_ns, 'model')
    model = tf.keras.models.deserialize(serialized_model)
    weights = self.sdl.get(my_ns, 'weights')
    print(f'Model Loaded from SDL\n')
    model.summary()
    payload = json.dumps({'ACK': 'Model Loaded'}).encode()
    if model:
        sbuf = rmr.rmr_alloc_msg(vctx=self._mrc, size=len(payload),payload=payload,
                                gen_transaction_id=True, meid=meid, mtype=1000)
        for _ in range(100):
            sbuf = rmr.rmr_send_msg(self._mrc, sbuf)
            if sbuf.contents.state == 0:
                self.rmr_free(sbuf)
                break


def default_handler(self, summary, sbuf):
    '''Default Handler : Messages of unknow mtype received at this app rmr port are forwarded here'''
    print('defh')

# 2000 sends data received ack and begins Training
def get_weights(self, summary, sbuf):
    '''Loading in the aggregatted weights received for RIC and continues training'''
    global weights, bias, epochs, model
    print('getdata')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    print(f'Pre\nsum: {jpay}\nsbuf: {sbuf}')
    weights = jpay['weights']
    weights = [np.array(i) for i in weights]
    model.set_weights(weights)
    train(self)


def train_enb(self, summary, sbuf):
    '''Initial Train Call'''
    global epochs, weights, model
    print(f'train initiate for eNB\n payload: {summary.keys()}')
    weights = self.sdl.get(my_ns, 'weights')
    
    epochs = self.sdl.get(my_ns, 'epochs')
    if epochs > 0:
        if weights != 0:
            weights = [np.array(i) for i in weights]
            model.set_weights(weights)
            print(f'Epochs Remaining: {epochs}\nTraining Model\n')
            train(self)
        elif weights == 0:
            weights = [np.array(i) for i in weights]
            model.set_weights(weights)
            print(f'Epochs Remaining: {epochs}\nTraining Model\n')
            train(self)

def train(xapp: RMRXapp):
    '''trains model on remaining epochs and sends weights back to ric for averaging'''
    global weights, model, x_train, x_test, y_train, y_test, epochs, meid
    model.fit(x_train, y_train, batch_size=32, epochs=1, validation_split=0.2)
    weights = model.get_weights()
    weights = [i.tolist() for i in weights]
    payload = json.dumps({'weights': weights}).encode()
    sbuf = rmr.rmr_alloc_msg(vctx=xapp._mrc, size=len(payload), payload=payload,
                             gen_transaction_id=True, meid=meid, mtype=1001)
    for _ in range(100):
        sbuf = rmr.rmr_send_msg(xapp._mrc, sbuf)
        if sbuf.contents.state == 0:
            xapp.rmr_free(sbuf)
            break
    
    
    
    
    # data = json.dumps({'weights': weights, 'epochs': epochs})
    # xapp.rmr_send(data.encode(), 1001)


# xapp initiation
xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4561)
xapp.register_callback(get_weights, 2000)
xapp.register_callback(train_enb, 2001)
# xapp.register_callback(model_update,2002)
xapp.run()