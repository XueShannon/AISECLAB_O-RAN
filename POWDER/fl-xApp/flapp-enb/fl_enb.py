import time
import json
import numpy as np
import pandas as pd
from ricxappframe.xapp_frame import RMRXapp, rmr
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

# Setting device MEID
meid = os.environ['MEID'] 
meid = bytes(meid, 'utf-8')
# Setting Params
weights = 0
epochs = 0
_epochs = 0
my_ns = 'flapp'
model = None
l1 = 0
l2 = 0

def load_data():
    '''Loads data from csibins'''
    global l1,l2
    x3_mag = np.fromfile(f'x3103/x3103-nuc3_mag.bin', dtype=np.float32)
    x3_phase = np.fromfile(f'x3103/x3103-nuc3_phase.bin', dtype=np.float32)
    x3_mag_test = np.fromfile(f'x3103/x3103-nuc3_mag_test.bin', dtype=np.float32)
    x3_phase_test = np.fromfile(f'x3103/x3103-nuc3_phase_test.bin', dtype=np.float32)


    x4_mag = np.fromfile(f'x3103/x3103-nuc4_mag.bin', dtype=np.float32)
    x4_phase = np.fromfile(f'x3103/x3103-nuc4_phase.bin', dtype=np.float32)
    x4_mag_test = np.fromfile(f'x3103/x3103-nuc4_mag_test.bin', dtype=np.float32)
    x4_phase_test = np.fromfile(f'x3103/x3103-nuc4_phase_test.bin', dtype=np.float32)

    slice_size_3 = len(x3_mag)%52
    slice_size_4 = len(x4_mag)%52
    slice_size_3_test = len(x3_mag_test)%52
    slice_size_4_test = len(x4_mag_test)%52

    if slice_size_3 != 0:
        x3_mag = x3_mag[:-slice_size_3].reshape(-1,52,1)
        x3_phase = x3_phase[:-slice_size_3].reshape(-1,52,1)
    else:
        x3_mag = x3_mag.reshape(-1,52,1)
        x3_phase = x3_phase.reshape(-1,52,1)
    if slice_size_4 != 0:
        x4_mag = x4_mag[:-slice_size_4].reshape(-1,52,1)
        x4_phase = x4_phase[:-slice_size_4].reshape(-1,52,1)
    else:
        x4_mag = x4_mag.reshape(-1,52,1)
        x4_phase = x4_phase.reshape(-1,52,1)
    
    if slice_size_3_test != 0:
        x3_mag_test = x3_mag_test[:-slice_size_3_test].reshape(-1,52,1)
        x3_phase_test = x3_phase_test[:-slice_size_3_test].reshape(-1,52,1)
    else:
        x3_mag_test = x3_mag_test.reshape(-1,52,1)
        x3_phase_test = x3_phase_test.reshape(-1,52,1)
    if slice_size_4_test != 0:
        x4_mag_test = x4_mag_test[:-slice_size_4_test].reshape(-1,52,1)
        x4_phase_test = x4_phase_test[:-slice_size_4_test].reshape(-1,52,1)
    else:
        x4_mag_test = x4_mag_test.reshape(-1,52,1)
        x4_phase_test = x4_phase_test.reshape(-1,52,1)
    
    _X_mag = np.concatenate((x3_mag, x4_mag))
    _X_phase = np.concatenate((x3_phase, x4_phase))
    _y = np.concatenate((np.zeros(len(x3_mag)), np.ones(len(x4_mag))))

    _X_mag_test = np.concatenate((x3_mag_test, x4_mag_test))
    _X_phase_test = np.concatenate((x3_phase_test, x4_phase_test))
    _y_test = np.concatenate((np.zeros(len(x3_mag_test)), np.ones(len(x4_mag_test))))


    index = np.random.permutation(len(_X_mag))
    X_mag = _X_mag[index]
    X_phase = _X_phase[index]
    y = _y[index]

    test_index = np.random.permutation(len(_X_mag_test))
    X_mag_test = _X_mag_test[test_index]
    X_phase_test = _X_phase_test[test_index]
    y_test = _y_test[test_index]

    l1 = len(X_mag//2)
    l2 = len(X_mag_test//2)

    return X_mag, X_phase, y, X_mag_test, X_phase_test, y_test

X_mag, X_phase, y, X_mag_test, X_phase_test, y_test = load_data()

def post_init(self: RMRXapp):
    '''POST Init Function, executes on running app sends serialized model object to RIC'''
    if os.path.exists('stat.csv'):
        os.remove('stat.csv')
    global epochs, model, meid, weights
    print(f'eNB Post Init: {self.healthcheck()}\neNBs Connected')
    payload = json.dumps({'REQ': 'Model'}).encode()
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
def get_model(self, summary, sbuf):
    '''Loading in the aggregatted weights received for RIC and continues training'''
    global weights, epochs, model, _epochs
    print(f'Model/Weights Received')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    epochs = jpay['epochs']
    _epochs = epochs
    _model = jpay['model']
    model = tf.keras.utils.deserialize_keras_object(_model)
    model.summary()
    weights = jpay['weights']
    if weights != 0:
        weights = [np.array(i) for i in weights]
        model.set_weights(weights)
    # print(f'Epochs Remaining: {epochs}\nTraining Model\n')
    


def train_enb(self, summary, sbuf):
    '''Initial Train Call'''
    global epochs, weights, model
    print(f'train initiate for eNB\n payload: {summary.keys()}')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    weights = jpay['weights']
    if epochs > 0:
        if weights != 0:
            weights = [np.array(i) for i in weights]
            model.set_weights(weights)
        print(f'Epochs Remaining: {epochs}\nTraining Model\n')
        train(self)
    if epochs<=0:
        if weights != 0:
            weights = [np.array(i) for i in weights]
            model.set_weights(weights)
        print('Training complete')
        model.save('rf_model.keras')
        print('Model saved')
        
        

def train(xapp: RMRXapp):
    '''trains model on remaining epochs and sends weights back to ric for averaging'''
    global weights, model, X_mag, X_phase, y, epochs, meid, _epochs,l1, l2
    print((_epochs-epochs)*1040,(_epochs-epochs+1)*1040)
    if epochs > 1:
        hist = model.fit([X_mag[(_epochs-epochs)*1040:(_epochs-epochs+1)*1040],X_phase[(_epochs-epochs)*1040:(_epochs-epochs+1)*1040]], 
                        y[(_epochs-epochs)*1040:(_epochs-epochs+1)*1040], 
                        batch_size=1, epochs=1, 
                        validation_data=([X_mag_test[(_epochs-epochs)*1040:(_epochs-epochs+1)*1040], X_phase_test[(_epochs-epochs)*1040:(_epochs-epochs+1)*1040]], y_test[(_epochs-epochs)*1040:(_epochs-epochs+1)*1040]))
    elif epochs ==1:
        hist = model.fit([X_mag, X_phase],y, batch_size=32, epochs=1, validation_data=([X_mag_test, X_phase_test], y_test))

    epochs -= 1
    stat_df = pd.DataFrame(hist.history)
    stat_df.to_csv('stat.csv', mode='a', header=False, index=False)
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
    model.save('rf_model.keras')
    


# xapp initiation
xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4561)
xapp.register_callback(get_model, 2000)
xapp.register_callback(train_enb, 2001)


xapp.run()

