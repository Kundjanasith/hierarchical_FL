import sys, os, time, glob, copy
sys.path.insert(1, '..')       
import utils

local_ip = ['10.10.100.33', '10.10.100.34']
init_model = utils.model_init()
init_model.save_weights('global_models/aggregated_model_ep0.h5')
while not os.path.exists('global_models/aggregated_model_ep0.h5'):
    time.sleep(1)
utils.broadcast_model(local_ip,19191,'global_models/aggregated_model_ep0.h5')

NUM_ROUNDS = 10
NUM_DEVICES = 2
for e in range(NUM_ROUNDS):
    for n in range(NUM_DEVICES):
        utils.receive_model('localhost',19192,'local_models/')
    arr = []
    for p in glob.glob('local_models/*_ep%d.h5'%e):
        model = utils.model_init()
        model.load_weights(p)
        arr.append(copy.deepcopy(model.get_weights()))
    arr_avg = utils.aggregated(arr)
    aggregated_model = utils.init_model()
    aggregated_model.set_weights(arr_avg)
    aggregated_model.save_weights('global_models/aggregated_model_ep%d.h5'%(e+1))
    utils.broadcast_model(local_ip,19191,'global_models/aggregated_model_ep%d.h5'%(e+1))

    