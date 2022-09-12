import sys, os, time, glob, copy, configparser, socket, ast
sys.path.insert(1, '..')       
import utils

config = configparser.ConfigParser()
config.read('../config.ini')

aggregator_ip = []
for group in ast.literal_eval(config['TRAINING']['GROUPS']):
    aggregator_ip.append(config[group]['AGGREGATOR_IP'])
num_communication_rounds = int(config['TRAINING']['NUM_COMMUNICATION_ROUNDS'])
hostname = socket.gethostname()

init_model = utils.model_init()
init_model.save_weights('exchanged_models/model_ep%d.h5'%(0))
while not os.path.exists('exchanged_models/model_ep%d.h5'%(0)):
    time.sleep(10)
utils.broadcast_model(aggregator_ip,19191,'exchanged_models/model_ep%d.h5'%(0), 'exchanged_models')

for e in range(1,num_communication_rounds):
    while True:
        if len(glob.glob('aggregated_models/*_ep%d.h5'%(e))) == len(aggregator_ip):
            break
    arr = []
    for p in glob.glob('aggregated_models/*_ep%d.h5'%(e)):
        model = utils.model_init()
        while not os.path.exists(p):
            try:
                model.load_weights(p)
            except:
                pass
        arr.append(copy.deepcopy(model.get_weights()))
    arr_avg = utils.aggregated(arr)
    exchanged_model = utils.model_init()
    exchanged_model.set_weights(arr_avg)
    exchanged_model.save_weights('exchanged_models/model_ep%d.h5'%(e))
    utils.broadcast_model(aggregator_ip,19191,'exchanged_models/model_ep%d.h5'%(e), 'exchanged_models')




        
