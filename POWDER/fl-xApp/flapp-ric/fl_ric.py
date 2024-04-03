from ricxappframe.xapp_frame import RMRXapp, rmr, Xapp
import numpy as np
import json
import os



# PLAN is to use a Reactive Xapp (RMRXapp) rather than XApp since
# it allows for different callbacks instead of a single infinite loop run

WEIGHTS = None
BIAS = None
EPOCHS = 100
my_ns = 'fl_ric'

def post_init(self):
    '''Post init function this function is invoked to x-app loading
    self: xapp object'''
    '''TODO: get intitalize setup'''
    # print('RIC FL-APP iniitiated')
    # self.logger.info('RIC FL-APP iniitiated')
    print(f'RIC XAPP post_init called \nStatus: {self.healthcheck()}')
    self.logger.info(f'RIC XAPP post_init called \nStatus: {self.healthcheck()}')
    # self.rmr_send(json.dumps({'Conn Check':'Conn Check'}).encode(),5858)


def default_handler(self, summary, sbuf):
    '''Default Handler for xapp is invoked on calling message of unregistered callback m_type
    TODO: Handling unknown message type'''
    self.logger.info('Default Handler Called')
    print(f'Default Handler Received: {summary}')
    self.rmr_free(sbuf)

# 1000 calls respond data to initializes data on UE
def data_send(self, summary, sbuf):
    '''Callback for data transfer 
    on calling this function will comminucate the data to train on'''
    global EPOCHS, WEIGHTS, BIAS
    self.logger.info(f'data_send called: {summary}')
    print(f"data_send called {json.loads(summary[rmr.RMR_MS_PAYLOAD])}")

    np.random.seed(58)
    X = 2.5 * np.random.randn(100) + 1.5
    y = 2 + 0.3 * X + 0.5 * np.random.randn(100)
    X = X.reshape(-1, 1).tolist()
    y = y.reshape(-1, 1).tolist()
    if (WEIGHTS is not None) and (BIAS is not None):
        data = {'data': {'X': X, 'y': y, 'epochs': EPOCHS,
                        'weights': WEIGHTS, 'bias': BIAS}}
        self.rmr_send(json.dumps(data).encode(),2000)
    else:
        print('Sending Without Weights:\nNone Found')
        data = {'data': {'X': X, 'y': y, 'epochs': EPOCHS}}
        self.rmr_send(json.dumps(data).encode(), 2000)
    self.logger.info(f'Sent data: {data}')
    print(f'Sent Payload: {data}')
        # self.rmr_free(sbuf)

# 1001 calls get_data to intitalize data at UE side
def weight_avg(self, summary, sbuf):
    '''This function will average out the weights received and send back to UEs to train'''
    global WEIGHTS, BIAS, EPOCHS
    allweights = []
    allbias = []
    mse = []
    for (summary, sbuf) in self.rmr_get_messages():
        jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
        allweights.append(jpay['weights'])
        allbias.append(jpay['bias'])
        EPOCHS = jpay['epochs']
        mse.append(jpay['mse'])
        self.rmr_free(sbuf)
    WEIGHTS = np.array(allweights).mean(axis=0)
    BIAS = np.array(allbias).mean(axis=0)
    if EPOCHS > 0:
        self.rmr_send(json.dumps({'weights':WEIGHTS,'bias':BIAS}).encode(),2001)
    else:
        self.logger.info(f'Training Complete\nWeights: {WEIGHTS}\nBias: {BIAS}')
        print(f'Training Complete\nWeights: {WEIGHTS}\nBias: {BIAS}')

# 1002
def train(self, summary, sbuf):
    '''Training Initiation func'''
    global EPOCHS
    print(f'Received Train Call : {summary}')
    for (summary, sbuf) in self.rmr_get_messages():
        self.logger.info(f'Received: {summary}')
        jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
        if 'ACK' in jpay:
            if (WEIGHTS is not None) and (BIAS is not None):
                self.rmr_send(json.dumps({'weights':WEIGHTS,'bias':BIAS,'epochs': EPOCHS}).encode(), 2001)
            else:
                self.rmr_send(json.dumps({'epochs': EPOCHS}).encode(), 2001)
            self.logger.info(f'Data sent Begining Training')
            print(f'Data sent Begining Training')
        self.rmr_free(sbuf)

# 1003
def predict(self, summary, sbuf):
    '''This Function can be used for predictions from global models'''
    for (summary, sbuf) in self.rmr_get_messages():
        self.logger.info(f'Received :{summary} ')
        jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
        X = jpay['X']
        weights = jpay['weights']
        bias = jpay['bias']
        # TODO: new_mtype
        self.rmr_rts(sbuf, new_payload=json.dumps(
            {'Value: ': (bias+X.dot(weights))}))
        self.rmr_free(sbuf)


xapp = RMRXapp(default_handler=default_handler,post_init=post_init, use_fake_sdl=True,rmr_port=4562)


# message_type is unique identifier to execute function from registered callbacks
xapp.register_callback(data_send, message_type=1000)
xapp.register_callback(weight_avg, message_type=1001)
xapp.register_callback(train, message_type=1002)
xapp.register_callback(predict, message_type=1003)
xapp.run()
# TODO: rmr route creation