import sys, os, time    
sys.path.insert(1, '..')       
import utils

init_model = utils.model_init()
init_model.save_weights('global_models/aggregated_model_ep0.h5')
while not os.path.exists('global_models/aggregated_model_ep0.h5'):
    time.sleep(1)
utils.send_model('localhost',19191,'global_models/aggregated_model_ep0.h5')

NUM_ROUNDS = 10
NUM_DEVICES = 2
for e in range(NUM_ROUNDS):
    for n in range(NUM_DEVICES):
        utils.receive_model('localhost',19192,'local_models/')
    