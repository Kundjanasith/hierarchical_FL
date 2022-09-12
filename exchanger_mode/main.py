import sys, os, time, glob, copy, configparser, socket 
sys.path.insert(1, '..')       
import utils


local_ip = ['10.10.100.33', '10.10.100.4']
global_ip = '10.10.100.33'

NUM_ROUNDS = 10000
for e in range(NUM_ROUNDS):
    for ip in local_ip:
        while not os.path.exists('aggregated_models/%s_ep%d.h5'%(ip,ep_counter)):
            time.sleep(5)
    arr = []
    for ip in local_ip:
        model = utils.model_init()
        model.load_weights('aggregated_models/%s_ep%d.h5'%(ip,ep_counter)):
        arr.append(copy.deepcopy(model.get_weights()))
    arr_avg = utils.aggregated(arr)
    exchanged_model = utils.model_init()
    exchanged_model.set_weights(arr_avg)
    aggregated_model.save_weights('exchanged_models/exchanged_model_ep%d.h5'%(e+1))
    utils.broadcast_model(local_ip,19190,'exchanged_models/exchanged_model_ep%d.h5'%(e+1))




        
