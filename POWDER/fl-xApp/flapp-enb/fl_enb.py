import time
import json
import numpy as np
from ricxappframe.xapp_frame import RMRXapp, rmr
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
# from sklearn.metrics import mean_squared_error

# Loading Data
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

# Setting Params
weights = 0
epochs = 10
my_ns = 'fl_ue'

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


def post_init(self: RMRXapp):
    '''POST Init Function, executes on running app sends serialized model object to RIC'''
    global serialized_model, model, epochs
    print(f'eNB Post Init: {self.healthcheck()}\neNBs Connected {self.get_list_enb_ids()} \nsending model \n')
    model.summary()

    payload = json.dumps({'model': serialized_model,'epochs': epochs}).encode()
    # self.rmr_send(json.dumps({'model':serialized_model}).encode(),1000)
    
    # this is a workaround of above commented line helps to register meid and sub-id 
    # in message payload helps to keep track of participating nodes on RIC side
    sbuf = rmr.rmr_alloc_msg(vctx=self._mrc, size=len(payload),payload=payload,
                             gen_transaction_id=True, meid=b'enb01', mtype=1000)
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
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    epochs = jpay['epochs']
    if 'weights' in jpay:
        weights = [np.array(i) for i in jpay['weights']]
        model.set_weights(weights)
    train(self)


def train(xapp: RMRXapp):
    '''trains model on remaining epochs and sends weights back to ric for averaging'''
    global weights, model, x_train, x_test, y_train, y_test, epochs
    if epochs > 0:
        model.fit(x_train, y_train, batch_size=32,
                  epochs=1, validation_split=0.2)
        epochs -= 1
        weights = model.get_weights()
        weights = [i.tolist() for i in weights]
        payload = json.dumps({'weights': weights, 'epochs': epochs}).encode()
        
        
        sbuf = rmr.rmr_alloc_msg(vctx=xapp._mrc, size=len(payload), payload=payload,
                                 gen_transaction_id=True, meid=b'enb01', mtype=1001)
        for _ in range(100):
            sbuf = rmr.rmr_send_msg(xapp._mrc, sbuf)
            if sbuf.contents.state == 0:
                xapp.rmr_free(sbuf)
                break
    else:
        print(model.evaluate(x_test,y_test))
    # data = json.dumps({'weights': weights, 'epochs': epochs})
    # xapp.rmr_send(data.encode(), 1001)


# xapp initiation
xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4561)
xapp.register_callback(get_weights, 2000)
xapp.register_callback(train_enb, 2001)
# xapp.register_callback(model_update,2002)
xapp.run()