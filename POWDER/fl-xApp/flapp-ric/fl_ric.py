from ricxappframe.xapp_frame import RMRXapp, rmr
from ricxappframe.util.constants import Constants
import numpy as np
import json
import os
os.environ['RMR_SEED_RT']='test_route.rt'
# os.environ[Constants.CONFIG_PATH]='init/flapp-config.json'
os.environ[Constants.CONFIG_FILE_ENV] = 'init/flapp-config.json'
WEIGHTS = 0
BIAS = 0
EPOCHS = 10
my_ns = 'fl_ric'
np.random.seed(58)
X = 2.5 * np.random.randn(100) + 1.5
y = 2 + 0.3 * X + 0.5 * np.random.randn(100)
X = X.reshape(-1, 1).tolist()
y = y.reshape(-1, 1).tolist()


def post_init(self):
    print(f'Ric Post init {self.healthcheck()}')
    


def default_handler(self, summary, sbuf):
    print('defh')

# 1000 calls respond data to initializes data on UE
def data_send(self,summary,sbuf):
    global WEIGHTS,BIAS, EPOCHS
    print(f'Sending Current Model Weights \nsummary:{summary}')
    data = {'weights':WEIGHTS,'bias':BIAS,'epochs':EPOCHS}
    self.rmr_rts(sbuf,json.dumps(data).encode(),2000)
    # self.rmr_free(sbuf)
    print(f'sent: {data} to ue')

def weight_avg(self,summary,sbuf):
    print('weightavg')
    global WEIGHTS,BIAS, EPOCHS
    print(f'weights: {summary}')
    jpay = json.loads(summary[rmr.RMR_MS_PAYLOAD])
    EPOCHS = int(jpay['epochs'])
    print(EPOCHS)
    if EPOCHS !=0:
        print(f'Epoch {EPOCHS}')
        self.rmr_send(json.dumps({'cont':'cont'}).encode(),2001)
    else:
        print('Training Complete')
        



xapp = RMRXapp(default_handler=default_handler,
               post_init=post_init, use_fake_sdl=True, rmr_port=4562)


# message_type is unique identifier to execute function from registered callbacks
xapp.register_callback(data_send, message_type=1000)
# xapp.register_callback(train_ric, message_type=1001)
xapp.register_callback(weight_avg, message_type=1001)
# xapp.register_callback(predict, message_type=1003)
xapp.registerXapp()
xapp.run()
# TODO: rmr route creation
# docker.io/nexuseli18/aiseclab-flapp:flric
