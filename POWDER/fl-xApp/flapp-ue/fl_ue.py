from ricxappframe.xapp_frame import RMRXapp, rmr
import numpy as np
import json
import os
import time
# from sklearn.metrics import mean_squared_error
# Params
X = None
y = None
weights = 0
bias = 0
epochs = None
lr = 0.001
my_ns = 'fl_ue'


def post_init(self):
    print(f'UE Post Init: {self.healthcheck()}')
    self.rmr_send(json.dumps({'REQ':'DATA'}).encode(),1000)

    
def default_handler(self,summary,sbuf):
    print('defh')

# 2000 sends data received ack and begins Training
def get_data(self,summary,sbuf):
    global weights, bias, X, y,epochs
    print('getdata')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    print(f'Pre\nsum: {jpay}\nsbuf: {sbuf}')
    X = jpay['X']
    y = jpay['y']
    weights = jpay['weights']
    bias = jpay['bias']
    epochs = jpay['epochs']
    train(self)

def train_ue(self,summary,sbuf):
    print('trainue')
    train(self)

def train(xapp):
    global weights,bias,X,y,lr,epochs
    _ytrain =[]
    epochs -=1
    X = np.array(X)
    y = np.array(y)
    for i in range(len(X)):
        _y = bias + weights*X[i]
        dw0 = -(y[i]-_y)
        dw1 = -(X[i]*(y[i]-_y))
        bias = bias - lr*dw0
        weights = weights - lr*dw1
        _ytrain.append(_y)
    X = X.tolist()
    y = y.tolist()
    weights = weights.tolist()
    bias = bias.tolist()
    data = json.dumps({'weights':weights,'bias':bias,'epochs':epochs})
    xapp.rmr_send(data.encode(),1001)

xapp = RMRXapp(default_handler=default_handler, post_init=post_init,use_fake_sdl=True,rmr_port=4561)
xapp.register_callback(get_data,2000)
xapp.register_callback(train_ue,2001)
# xapp.register_callback(model_update,2002)
xapp.run()
# xapp.rmr_send(json.dumps({'datasend':'ping'}).encode(),1002)
