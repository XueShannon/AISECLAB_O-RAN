from ricxappframe.xapp_frame import RMRXapp, rmr
import numpy as np
import json
import os
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
    '''On instantiation UE will query for current status get weights 
    and data if they exist and train from that point'''
    print(f'UE-FL-APP initiated: {self.healthcheck()}')
    self.logger.info(f'UE FL-APP initiated: {self.healthcheck()}')
    
    # Data Request calls data_send at RIC
    self.rmr_send(json.dumps({'REQ':'data request'}).encode(),1000)
    print(f'Data Request Sent:')
    self.sdl_set(my_ns, "REQ", 'data request')
    self.logger.info(self.sdl_get(my_ns, "REQ"))
    self.logger.info(self.sdl_find_and_get(my_ns, "RE"))
    self.sdl_delete(my_ns, "REQ")
    self.logger.info(self.sdl_get(my_ns, "REQ"))
    # rmr receive
    for (summary, sbuf) in self.rmr_get_messages():
        # summary is a dict that contains bytes so we can't use json.dumps on it
        # so we have no good way to turn this into a string to use the logger unfortunately
        # print is more "verbose" than the ric logger
        # if you try to log this you will get: TypeError: Object of type bytes is not JSON serializable
        print("ping: {0}".format(summary))
        self.rmr_free(sbuf)
    
def default_handler(self,summary,sbuf):
    '''Default handler for xapp'''
    self.logger.info('Default Handler Called')
    print(f'Default Handler Received: {summary}')
    self.rmr_free(sbuf)

# 2000 sends data received ack and begins Training
def get_data(self,summary,sbuf):
    '''Getting Data'''
    self.logger.info(f'Data Received: {summary}')
    print(f'Data Received: {summary}')
    global X,y,epochs
    self.logger.info(f'Received: {summary}')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    X = jpay['data']['X']
    y = jpay['data']['y']
    epochs = jpay['data']['epochs']
    
    self.rmr_send(json.dumps({'ACK':'Data Received'}).encode(),1002)
    self.rmr_free(sbuf)


# 2001
def train(self,summary,sbuf):
    '''training func '''
    global X,y,weights,bias,epochs
    _ytrain = []
    for (summary,sbuf) in self.rmr_get_messages():
        self.logger.info(f'Received: {summary}') 
        print(f'Received: {summary}')
        jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
        epochs = jpay['epochs']
        if ('weights' in jpay) and ('bias' in jpay):
            weights = jpay['weights']
            bias = jpay['bias']
        self.rmr_free(sbuf)
    epochs -=1
    if epochs >0:
        for i in range(len(X)):
            _y = bias + weights*X[i]
            
            # gradients
            dw0 = -(y[i]-_y)
            dw1 = -(X[i]*(y[i]-_y))
            bias = bias - lr*dw0
            weights = weights - lr*dw1
            _ytrain.append(_y)
    mse = np.mean((np.array(y)-np.array(_ytrain))**2)
    self.rmr_send(json.dumps({'weights':weights,'bias':bias,'mse':mse,'epochs':epochs}).encode(),1001)
    self.rmr_free(sbuf)

# 2002
def model_update():
    '''Updating Model'''
    print('Please not here')

def validation_metric(self,summary,sbuf):
    '''valid func for generating model eval metrics'''

xapp = RMRXapp(default_handler=default_handler, post_init=post_init,use_fake_sdl=True,rmr_port=4561)
xapp.register_callback(get_data,2000)
xapp.register_callback(train,2001)
xapp.register_callback(model_update,2002)
xapp.run()